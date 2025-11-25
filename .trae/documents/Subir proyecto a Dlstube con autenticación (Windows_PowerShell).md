## Objetivo
- Subir el proyecto al repositorio `https://github.com/Mariomt1994/Dlstube.git` y forzar el flujo de autenticación para completar el push.

## Pasos previos
1. Verificar estado actual y cancelar cualquier rebase pendiente:
   - `git status`
   - Si aparece “rebase in progress”: `git rebase --abort`
2. Asegurar remoto correcto:
   - `git remote set-url origin https://github.com/Mariomt1994/Dlstube.git`
   - `git remote -v`
3. Asegurar `.gitignore` adecuado (ya creado) y quitar del índice cualquier venv rastreado:
   - `git rm -r --cached scripts/.venv`
   - `git add .gitignore`
   - `git commit -m "chore: add .gitignore and stop tracking local venv"`

## Subida con autenticación (HTTPS)
1. Intentar push directo para disparar Git Credential Manager:
   - `git push -u origin main`
   - Se abrirá ventana de login en el navegador; inicia sesión con GitHub y autoriza.
2. Si el remoto rechaza por historia diferente (“non-fast-forward”):
   - `git fetch origin main`
   - `git pull origin main --rebase`
   - Resolver conflictos (si los hay), por ejemplo mantener tu `main.py`:
     - Edita, luego `git add main.py`
     - `git rebase --continue`
   - `git push -u origin main`
3. Si deseas usar token (PAT) en lugar de navegador:
   - Crea un PAT con scope `repo` en GitHub.
   - Cuando pida credenciales: Usuario = tu usuario GitHub, Contraseña = PAT.

## Alternativa SSH (evita prompts futuros)
1. Generar clave SSH:
   - `ssh-keygen -t ed25519 -C "tu_email"`
   - Copiar `C:\Users\MARSHALL\.ssh\id_ed25519.pub` a GitHub → Settings → SSH keys → New SSH key.
2. Cambiar remoto a SSH:
   - `git remote set-url origin git@github.com:Mariomt1994/Dlstube.git`
   - `git push -u origin main`

## Verificación
- `https://github.com/Mariomt1994/Dlstube` debe mostrar los archivos del proyecto.
- `git log -n 3` y `git status` deben estar limpios.

## Nota
- Si el push insiste en rechazar por historia, confirma que quieres sobrescribir el remoto (y usar `git push --force-with-lease`).
- Puedo ejecutar los comandos inmediatamente tras tu confirmación para completar el flujo y la autenticación en navegador.