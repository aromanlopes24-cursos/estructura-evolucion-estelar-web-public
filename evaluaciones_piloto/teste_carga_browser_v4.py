#!/usr/bin/env python3
"""EEE v1.3.1: browser load test v4 with independent student failures and database audit (synthetic DEMO only).
Keep this file beside evaluaciones.py. Does not modify the live application or its database.
"""
import argparse
import asyncio
import json
import math
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from evaluation_config import load_config
from evaluation_engine import assignment, verify_export
from preparar_demo import create, demo_rows

ROOT = Path(__file__).resolve().parent


def log(message):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {message}', file=sys.stderr, flush=True)


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def redact(message, code=''):
    text = str(message)
    if code:
        text = text.replace(code, '[REDACTADO]')
    return re.sub(r'(?<![\w-])[A-Za-z0-9_-]{32,128}(?![\w-])', '[REDACTADO]', text)[:2000]


def form_with(page, button):
    return page.locator('[data-testid="stForm"]').filter(
        has=page.get_by_role('button', name=button, exact=True))


def field(scope, label, textarea=False):
    # Streamlit labels can have extra accessibility text or hidden controls;
    # scope to the widget, then select the actual editable element.
    testid = 'stTextArea' if textarea else 'stTextInput'
    return scope.locator(f'[data-testid="{testid}"]').filter(
        has_text=label).locator('textarea' if textarea else 'input')


async def checkbox(scope, label):
    # BaseWeb/Streamlit often hides the native input under a styled label.
    # Click the visible label, not the potentially non-interactable input.
    widget = scope.locator('[data-testid="stCheckbox"]').filter(
        has_text=label)
    inp = widget.locator('input[type="checkbox"]')
    await widget.locator('label').wait_for(state='visible')
    if not await inp.is_checked():
        await widget.locator('label').click()
    from playwright.async_api import expect
    await expect(inp).to_be_checked()


async def radio_option(page, text):
    label = page.locator('[data-testid="stRadio"] label').filter(
        has=page.get_by_text(text, exact=True))
    await label.click()
    from playwright.async_api import expect
    await expect(label.locator('input[type="radio"]')).to_be_checked()


def p95(xs):
    return round(sorted(xs)[math.ceil(.95*len(xs))-1], 3) if xs else None


async def download_bytes(page, label, timeout, on_failure):
    # Only retry a failed transport, never a failed integrity or identity check.
    from playwright.async_api import Error
    for number in (1, 2):
        try:
            async with page.expect_download(timeout=timeout*1000) as info:
                await page.get_by_role('button', name=label, exact=True).click()
            download = await info.value
            failure = await asyncio.wait_for(download.failure(), timeout)
            if failure:
                raise Error(f'Download.failure: {failure}')
            path = await asyncio.wait_for(download.path(), timeout)
            return Path(path).read_bytes()
        except (Error, asyncio.TimeoutError) as exc:
            on_failure(number, exc)
            if number == 2:
                raise
            await asyncio.sleep(0.75)


def audit_database(path, cfg, n):
    # Audit the isolated synthetic DB before its temporary directory is removed.
    # Do not export tokens, RUTs, email addresses, answers or keys in the report.
    if not path.is_file():
        return {'passed': False, 'error': 'Banco de teste não encontrado'}
    with sqlite3.connect(path) as c:
        c.row_factory = sqlite3.Row
        integrity = c.execute('PRAGMA quick_check').fetchone()[0]
        rows = [dict(r) for r in c.execute('SELECT attempt_id,rut,name,email,finalized_at,questions,answers FROM attempts')]
    by_rut = {r['rut']: r for r in rows}
    failures, orders, ratios, ids = [], set(), set(), set()
    complete = finalized = 0
    for i, (rut, mail) in enumerate(demo_rows(n), 1):
        row = by_rut.get(rut)
        if row is None:
            failures.append({'student': i, 'issue': 'missing_attempt'})
            continue
        bank = assignment(cfg, rut)
        answers = {q['id']: (q['options'][0]['id'] if q['type']=='choice' else str(i+1) if q['type']=='numeric' else f'Respuesta ficticia del estudiante {i:02d}') for q in bank}
        questions = json.loads(row['questions'])
        actual = json.loads(row['answers'])
        if row['finalized_at']:
            finalized += 1
        else:
            failures.append({'student': i, 'issue': 'not_finalized'})
        if actual == answers:
            complete += 1
        else:
            failures.append({'student': i, 'issue': 'answers_mismatch',
                             'saved_question_ids': sorted(actual),
                             'missing_question_ids': sorted(set(answers) - set(actual)),
                             'different_question_ids': sorted(k for k in set(answers)&set(actual) if answers[k]!=actual[k]),
                             'unexpected_question_ids': sorted(set(actual)-set(answers))})
        if questions != bank or row['email'] != mail or row['name'] != f'Estudiante ficticio {i:02d}':
            failures.append({'student': i, 'issue': 'identity_or_assignment_mismatch'})
        orders.add(tuple(q['id'] for q in questions))
        ratios.add(next((q.get('parameters',{}).get('radio_B_sobre_A') for q in questions if q['id']=='P03'), None))
        ids.add(row['attempt_id'])
    passed = integrity == 'ok' and len(rows)==n and finalized==complete==len(orders)==len(ratios)==len(ids)==n and not failures and None not in ratios
    return {'passed': passed, 'sqlite_quick_check': integrity, 'attempts': len(rows), 'finalized': finalized,
            'exact_answer_sets': complete, 'unique_orders': len(orders), 'unique_numeric_parameters': len(ratios),
            'unique_attempts': len(ids), 'issues': failures}


class PhaseGate:
    """Release participants when every student has arrived or withdrawn.

    An individual failure does not cancel the other students' test. A gate
    timeout releases waiting students but is recorded as a test deviation.
    All mutations run synchronously on the same asyncio event loop.
    """
    def __init__(self, n, name):
        self.expected = set(range(1, n+1))
        self.arrived = set()
        self.withdrawn = set()
        self.missing_at_timeout = set()
        self.name = name
        self.event = asyncio.Event()
        self.timed_out = False
        self.release_count = None

    def release(self):
        if not self.event.is_set():
            self.release_count = len(self.arrived)
            self.event.set()
            log(f'Barreira {self.name}: liberada com {self.release_count}/{len(self.expected)} participantes; '
                f'falhas anteriores={len(self.withdrawn)}; timeout={self.timed_out}')

    def check(self):
        if self.expected <= self.arrived | self.withdrawn:
            self.release()

    def withdraw(self, i):
        if i not in self.arrived and i not in self.withdrawn:
            self.withdrawn.add(i)
            self.check()

    async def wait(self, i, timeout):
        self.arrived.add(i)
        self.check()
        try:
            await asyncio.wait_for(self.event.wait(), timeout)
        except asyncio.TimeoutError:
            if not self.event.is_set():
                self.timed_out = True
                self.missing_at_timeout = self.expected - self.arrived - self.withdrawn
                self.release()

    def summary(self):
        return {'expected': len(self.expected), 'arrived': len(self.arrived),
                'released_together': self.release_count,
                'withdrawn_students': sorted(self.withdrawn), 'timed_out': self.timed_out,
                'missing_at_timeout': sorted(self.missing_at_timeout),
                'full_barrier': self.release_count == len(self.expected) and not self.timed_out}


async def run_test(url, n, cfg, out, timeout, visible, verbose):
    from playwright.async_api import async_playwright
    ready, final_gate = PhaseGate(n, "acesso"), PhaseGate(n, "finalização")
    latency = []
    by_stage = {}
    download_latency = {}
    download_failures = []
    async with async_playwright() as p:
        override = os.getenv('EEE_CHROMIUM')
        bundled = Path(p.chromium.executable_path)
        path = override or (str(bundled) if bundled.is_file() else
                            shutil.which('chromium') or shutil.which('chromium-browser'))
        log(f'Chromium: {path or "Playwright (padrão)"}; {n} sessão(ões); timeout={timeout}s')
        browser = await p.chromium.launch(headless=not visible, executable_path=path or None)
        log(f'Chromium iniciado; versão {browser.version}')
        async def student(i, rut, mail):
            ctx = page = None
            stage, code = 'contexto', ''
            expected = {}
            question_id = None
            def step(s):
                nonlocal stage
                stage = s
                if verbose or s in ('abrir página', 'iniciar: aguardar código', 'finalização: aguardar confirmação'):
                    log(f'E{i:02d} | {s}')
            async def timed(action_label, action, wait_label, wait):
                step(action_label)
                start = time.perf_counter()
                await action()
                step(wait_label)
                await wait()
                elapsed = time.perf_counter() - start
                latency.append(elapsed)
                by_stage.setdefault(action_label, []).append(elapsed)
            async def get_file(kind, label):
                step(f'{kind}: baixar')
                started = time.perf_counter()
                def failed(number, exc):
                    detail = redact(exc, code)
                    download_failures.append({'student': i, 'kind': kind, 'try': number, 'detail': detail})
                    log(f'E{i:02d} | {kind}: transferência falhou (tentativa {number}/2): {detail}')
                data = await download_bytes(page, label, timeout, failed)
                download_latency.setdefault(kind, []).append(time.perf_counter() - started)
                return data
            async def new_page():
                nonlocal ctx, page
                ctx = await browser.new_context(accept_downloads=True)
                page = await ctx.new_page()
                page.set_default_timeout(timeout * 1000)
                page.set_default_navigation_timeout(max(timeout, 60) * 1000)
                page.on('pageerror', lambda e: log(f'E{i:02d} | JavaScript: {redact(e, code)}'))
            async def open_demo():
                step('abrir página')
                response = await page.goto(url, wait_until='domcontentloaded')
                if response is not None and not response.ok:
                    raise RuntimeError(f'HTTP {response.status}')
                step('aguardar aviso DEMO')
                await page.get_by_text('Modo DEMO — sólo estudiantes ficticios.', exact=False).wait_for(timeout=max(timeout, 60)*1000)
                step('aguardar formulário de identificação')
                await form_with(page, 'Iniciar práctica').wait_for(state='visible')
            try:
                await new_page()
                await open_demo()
                bank = assignment(cfg, rut)
                new = form_with(page, 'Iniciar práctica')
                step('preencher nome')
                await field(new, 'Nombre y apellido(s)').fill(f'Estudiante ficticio {i:02d}')
                step('preencher RUT')
                await field(new, 'RUT').fill(rut)
                step('preencher e-mail')
                await field(new, 'Correo institucional').fill(mail)
                step('marcar declaração de autoria')
                await checkbox(new, 'Declaro que soy el estudiante identificado y que realizo personalmente esta actividad.')
                step('barreira de acesso')
                await ready.wait(i, max(120, timeout*3))
                await timed('iniciar: clicar', lambda: new.get_by_role('button', name='Iniciar práctica', exact=True).click(),
                            'iniciar: aguardar código', lambda: page.get_by_role('heading', name='Guarde su código de recuperación', exact=True).wait_for())
                step('ler código de recuperação')
                pre = page.locator('pre:visible').filter(has_text=re.compile(r'^[A-Za-z0-9_-]{32,128}\s*$')).first
                await pre.wait_for()
                code = (await pre.inner_text()).strip()
                if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', code):
                    raise AssertionError('Código de recuperação não encontrado')
                step('confirmar código guardado')
                await checkbox(page, 'He guardado el código de recuperación.')
                def heading(index):
                    return page.get_by_role('heading', name=f'Pregunta {index+1} de {len(bank)} · {bank[index]["title"]}', exact=True)
                review = page.get_by_role('heading', name='Revisión antes de la entrega', exact=True)
                await timed('começar questões: clicar', lambda: page.get_by_role('button', name='Comenzar las preguntas', exact=True).click(),
                            'começar questões: aguardar primeira', lambda: heading(0).wait_for())
                for j, q in enumerate(bank):
                    question_id = q['id']
                    step(f'pergunta {j+1}: aguardar enunciado')
                    await heading(j).wait_for()
                    if q.get('figure'):
                        step(f'pergunta {j+1}: aguardar figura')
                        image = page.locator('[data-testid="stImage"] img:visible').first
                        await image.wait_for()
                        await asyncio.wait_for(image.evaluate('(img) => img.decode()'), timeout)
                    step(f'pergunta {j+1}: preencher resposta')
                    if q['type'] == 'choice':
                        value = q['options'][0]['id']
                        await radio_option(page, 'A. ' + q['options'][0]['text'])
                    elif q['type'] == 'numeric':
                        value = str(i+1)
                        await field(page, 'Respuesta numérica (punto o coma decimal)').fill(value)
                    else:
                        value = f'Respuesta ficticia del estudiante {i:02d}'
                        await field(page, 'Su respuesta', textarea=True).fill(value)
                    expected[q['id']] = value
                    last = j == len(bank)-1
                    button = 'Guardar e ir a revisión →' if last else 'Guardar y siguiente →'
                    target = review if last else heading(j+1)
                    await timed(f'pergunta {j+1}: salvar', lambda: page.get_by_role('button', name=button, exact=True).click(),
                                f'pergunta {j+1}: aguardar transição', lambda: target.wait_for())
                    if j == 1:
                        step('reconexão: fechar contexto')
                        await ctx.close()
                        await new_page()
                        await open_demo()
                        step('reconexão: abrir aba')
                        await page.get_by_role('tab', name='Recuperar un intento', exact=True).click()
                        resume = form_with(page, 'Recuperar')
                        step('reconexão: preencher código')
                        await field(resume, 'Código de recuperación').fill(code)
                        # A locator belongs to its original page. Rebuild all persistent locators.
                        review = page.get_by_role('heading', name='Revisión antes de la entrega', exact=True)
                        await timed('reconexão: recuperar', lambda: resume.get_by_role('button', name='Recuperar', exact=True).click(),
                                    'reconexão: aguardar revisão', lambda: review.wait_for())
                        step('reconexão: conferir duas respostas')
                        await page.get_by_text(f'2 de {len(bank)} preguntas respondidas', exact=True).wait_for()
                        await timed('reconexão: retomar', lambda: page.get_by_role('button', name='Volver a la primera pendiente', exact=True).click(),
                                    'reconexão: aguardar terceira pergunta', lambda: heading(2).wait_for())
                backup = await get_file('respaldo', 'Descargar respaldo de respuestas guardadas (.json)')
                step('respaldo: verificar')
                bp = verify_export(backup, cfg, True)
                if (bp['kind'] != 'respaldo' or bp['answered'] != len(bank)
                    or bp['student']['rut'] != rut or bp['student']['email'] != mail
                    or {q['id']:q['answer'] for q in bp['items']} != expected):
                    raise AssertionError('Respaldo incorreto')
                step('finalização: marcar confirmação')
                await checkbox(form_with(page, 'Finalizar y generar archivo'), 'Confirmo que deseo entregar estas respuestas de forma definitiva.')
                step('barreira de finalização')
                await final_gate.wait(i, max(120, timeout*3))
                await timed('finalização: clicar', lambda: page.get_by_role('button', name='Finalizar y generar archivo', exact=True).click(),
                            'finalização: aguardar confirmação', lambda: page.get_by_text('Práctica finalizada.', exact=False).wait_for())
                download = await get_file('entrega', 'Descargar archivo de entrega (.json)')
                step('entrega: verificar HMAC, identificação e respostas')
                payload = verify_export(download, cfg)
                assert payload['student']['rut'] == rut and payload['student']['email'] == mail
                assert payload['answered'] == len(bank) and {q['id']:q['answer'] for q in payload['items']} == expected
                log(f'E{i:02d} | OK: entrega válida')
                return {'ok': True, 'student': i, 'order': [q['id'] for q in payload['items']], 'attempt': payload['attempt_id']}
            except Exception as exc:
                detail = redact(exc, code)
                log(f'E{i:02d} | FALHA em {stage}: {type(exc).__name__}: {detail}')
                # Mark this student as withdrawn; let the other students finish.
                ready.withdraw(i)
                final_gate.withdraw(i)
                diagnostic = {'ok': False, 'student': i, 'stage': stage, 'question_id': question_id,
                              'error': type(exc).__name__, 'detail': detail}
                if page is not None and not page.is_closed():
                    try:
                        screenshot = out / f'falha_E{i:02d}.png'
                        await page.screenshot(path=str(screenshot), timeout=5000)
                        diagnostic['screenshot'] = str(screenshot)
                        alerts = await page.locator('[data-testid="stAlert"]:visible').all_inner_texts()
                        diagnostic['visible_alerts'] = [redact(a, code) for a in alerts]
                        diagnostic['visible_headings'] = [redact(h, code) for h in await page.get_by_role('heading').all_inner_texts()]
                        diagnostic['visible_buttons'] = [redact(b, code) for b in await page.locator('button:visible').all_inner_texts()]
                    except Exception as err:
                        diagnostic['diagnostic_error'] = type(err).__name__
                return diagnostic
            finally:
                ready.withdraw(i)
                final_gate.withdraw(i)
                if ctx:
                    try:
                        await ctx.close()
                    except Exception as err:
                        log(f'E{i:02d} | aviso ao fechar contexto: {type(err).__name__}: {redact(err, code)}')
        try:
            results = await asyncio.gather(*(student(i,r,e) for i,(r,e) in enumerate(demo_rows(n),1)))
        finally:
            await browser.close()
    successes = [r for r in results if r['ok']]
    p95_seconds = p95(latency)
    orders = len({tuple(r['order']) for r in successes})
    attempts = len({r['attempt'] for r in successes})
    functional_passed = len(successes) == n and orders == n and attempts == n and len(latency) == n*10
    first_try_deliveries = sum(r['student'] not in {f['student'] for f in download_failures if f['kind']=='entrega'} for r in successes)
    synchronization = {'access': ready.summary(), 'finalization': final_gate.summary()}
    passed = (functional_passed and not download_failures and p95_seconds is not None and p95_seconds <= 3
              and all(v['full_barrier'] for v in synchronization.values()))
    return {'sessions': n, 'valid_deliveries': len(successes), 'first_try_deliveries': first_try_deliveries,
            'unique_orders': orders, 'unique_attempts': attempts, 'measured_actions': len(latency), 'p95_seconds': p95_seconds,
            'target_p95_seconds': 3, 'functional_passed': functional_passed, 'passed': passed,
            'latency_by_stage': {k: {'count':len(v), 'p95_seconds':p95(v)} for k,v in sorted(by_stage.items())},
            'download_latency': {k: {'count':len(v), 'p95_seconds':p95(v)} for k,v in sorted(download_latency.items())},
            'download_failures': download_failures, 'synchronization': synchronization,
            'errors': [r for r in results if not r['ok']]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sesiones', type=int, default=1)
    ap.add_argument('--url', help='Sólo instancia DEMO dedicada y vacía; nunca producción.')
    ap.add_argument('--timeout', type=int, default=45, help='Timeout de cada operación, en segundos.')
    ap.add_argument('--visible', action='store_true', help='Abrir Chromium visiblemente (sólo una sesión).')
    ap.add_argument('--verbose', action='store_true', help='Mostrar cada paso incluso con múltiples sesiones.')
    args = ap.parse_args()
    if not 1 <= args.sesiones <= 50 or not 5 <= args.timeout <= 180:
        ap.error('1–50 sesiones; timeout 5–180 segundos.')
    if args.visible and args.sesiones != 1:
        ap.error('--visible requiere --sesiones 1.')
    out = ROOT / 'diagnosticos_browser' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    out.mkdir(parents=True, mode=0o700, exist_ok=False)
    log(f'Diagnósticos locais (dados fictícios): {out}')
    def execute(url, cfg):
        return asyncio.run(run_test(url,args.sesiones,cfg,out,args.timeout,args.visible,args.verbose or args.sesiones<=3))
    try:
        if args.url:
            cfg = load_config()
            if cfg.mode != 'demo' or not all(cfg.roster.get(r)==e for r,e in demo_rows(args.sesiones)):
                raise RuntimeError('Configuração remota deve ser DEMO com lista fictícia correspondente.')
            report = execute(args.url,cfg)
            report['server_audit'] = None  # Remote DB must be audited separately by the operator.
        else:
            with tempfile.TemporaryDirectory(prefix='eee-browser-') as d:
                root = Path(d)
                roster,key = create(root)
                port = free_port()
                url = f'http://127.0.0.1:{port}'
                env = dict(os.environ,EEE_MODE='demo',EEE_ROSTER_PATH=str(roster),EEE_KEY_PATH=str(key),EEE_ROSTER_CSV='',EEE_SIGNING_KEY='',EEE_EVAL_DB=str(root/'test.sqlite3'),EEE_PROFESSOR_EMAIL='')
                cfg = load_config(env.get)
                log(f'Iniciando servidor isolado: {url}')
                with (out/'server.log').open('w',encoding='utf-8') as server_log:
                    proc = subprocess.Popen([sys.executable,'-m','streamlit','run',str(ROOT/'evaluaciones.py'),'--server.address','127.0.0.1','--server.port',str(port),'--server.headless','true','--browser.gatherUsageStats','false'],cwd=ROOT,env=env,stdout=server_log,stderr=subprocess.STDOUT)
                    try:
                        deadline = time.monotonic()+60
                        while time.monotonic()<deadline:
                            if proc.poll() is not None:
                                raise RuntimeError(f'Servidor encerrou ({proc.returncode}); consulte server.log.')
                            try:
                                with urllib.request.urlopen(url+'/_stcore/health',timeout=1) as response:
                                    if response.status == 200:
                                        break
                            except OSError:
                                time.sleep(.5)
                        else:
                            raise RuntimeError('Servidor não respondeu; consulte server.log.')
                        log('Servidor respondeu ao health check. Iniciando navegador.')
                        report = execute(url,cfg)
                        report['server_audit'] = audit_database(root/'test.sqlite3',cfg,args.sesiones)
                        report['passed'] = report['passed'] and report['server_audit']['passed']
                    finally:
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill();proc.wait()
    except Exception as exc:
        log(f'FALHA de infraestrutura: {type(exc).__name__}: {redact(exc)}')
        report = {'sessions':args.sesiones,'passed':False,'errors':[{'stage':'infraestrutura','error':type(exc).__name__,'detail':redact(exc)}]}
    report['diagnostics_dir'] = str(out)
    (out/'resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    return report['passed']


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
