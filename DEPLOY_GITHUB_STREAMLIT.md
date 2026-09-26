# Publicación — GitHub + Streamlit Community Cloud

## Arquitectura recomendada

Mantener el **repositorio GitHub privado** y publicar la aplicación Streamlit
como pública para los estudiantes.

Esto mantiene el código fuente fuera de un repositorio público, pero permite
compartir la URL de la aplicación.

## 1. Crear release limpia

Desde la raíz de la web local:

```bash
./tools/prepare_release.sh
```

Se crea:

```text
../estructura_evolucion_estelar_web_release_v1_2
```

No contiene:
- `.venv`;
- `_patches`;
- caches Python;
- archivos temporales locales.

## 2. Crear repositorio Git

```bash
cd ../estructura_evolucion_estelar_web_release_v1_2

git init
git branch -M main
git add .
git commit -m "Estructura y Evolución Estelar Web v1.2"
```

### Si usa GitHub CLI

Después de autenticar `gh`:

```bash
gh repo create estructura-evolucion-estelar-web \
  --private \
  --source=. \
  --remote=origin \
  --push
```

### Si crea el repositorio por la web de GitHub

Crie um repositório privado vazio e depois:

```bash
git remote add origin <URL_DO_REPOSITORIO>
git push -u origin main
```

## 3. Streamlit Community Cloud

1. Abra `share.streamlit.io`.
2. Conecte a conta GitHub.
3. Se o repositório for privado, conceda ao Streamlit acesso a repositórios privados.
4. `Create app`.
5. Escolha `Yup, I have an app`.
6. Selecione:
   - repository: o repositório criado;
   - branch: `main`;
   - entrypoint: `app.py`.
7. Em `Advanced settings`, use **Python 3.12**.
8. Não há secrets necessários nesta versão.
9. Escolha o subdomínio desejado.
10. `Deploy`.

## 4. Visibilidade para estudantes

Um app criado a partir de repositório privado começa privado. Nas configurações
do app, altere-o para público se quiser distribuí-lo livremente aos estudantes.

Assim:
- GitHub: privado;
- aplicativo: público;
- acesso dos estudantes: somente pela URL `*.streamlit.app`.

## 5. Atualizações futuras

Depois do primeiro deploy:

```bash
git add .
git commit -m "Descrição da atualização"
git push
```

O Community Cloud acompanha o repositório e atualiza o app após os commits.

## 6. Segurança

Nunca colocar credenciais em Git.

Se no futuro forem adicionados serviços externos:
- usar `.streamlit/secrets.toml` somente localmente;
- manter esse arquivo no `.gitignore`;
- inserir os secrets nas configurações do Streamlit Cloud.
