# Cómo correr esto en Termux (Android)

Funciona bien en Termux, con dos condiciones: tener el token de GitHub puesto
y estar en la copia correcta del repo.

---

## 1. Instalar lo básico

```bash
pkg update && pkg upgrade
pkg install python git
python -V     # 3.10 o superior
```

Clona y entra:

```bash
git clone https://github.com/veraemy154-rgb/sub-agente.git
cd sub-agente
git checkout arena/01a0a513-sub-agente
```

Si ya lo tenías clonado, sincronízalo antes de nada (ver sección 3).

---

## 2. El token de GitHub (importante en móvil)

Sin token, GitHub permite **60 peticiones por hora**. En una IP de datos
móviles eso se agota en minutos, y cuando se agota el escáner devuelve errores
en lugar de datos.

1. Crea el token en **github.com/settings/tokens** → *Generate new token (classic)*.
   No necesitas marcar ningún permiso: basta con el token público para leer datos públicos.
2. Configúralo:

```bash
export GITHUB_TOKEN=ghp_tu_token_aqui

# para que quede fijo entre sesiones:
echo 'export GITHUB_TOKEN=ghp_tu_token_aqui' >> ~/.bashrc
source ~/.bashrc
```

3. Comprueba que funciona:

```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/rate_limit | head -20
```

Debe decir `"limit": 5000`.

---

## 3. Si tu copia está modificada (IMPORTANTE)

Si al correr `python run.py leads` ves prioridades `MEDIA`/`BAJA` en lugar de
`P1`/`P2`/`P3`, o señales como *"issues abiertos sin triage"*, **no estás
ejecutando el código de esta rama**: alguien modificó `app/icp.py` o
`app/leadgen.py` en tu copia.

Compruébalo:

```bash
git log --oneline -1        # debe empezar por d09366f o posterior
git status -sb              # debe decir "nothing to commit"
git diff --stat             # debe salir vacío
```

Para arreglarlo:

```bash
# 1. Ver exactamente qué se cambió (opcional, por si quieres recuperar algo)
git diff

# 2. Descartar los cambios locales y volver a la versión buena
git fetch origin
git reset --hard origin/arena/01a0a513-sub-agente
```

> `reset --hard` **borra** tus cambios locales. Si prefieres guardarlos antes:
> `git stash` los aparta y `git stash pop` los recupera.

Después confirma que la señal fantasma desapareció:

```bash
grep -rn "issues abiertos" app/ ; echo "si no sale nada, estás en la versión correcta"
```

---

## 4. Uso diario

```bash
cd ~/sub-agente

python run.py scan owner/repo                  # auditar uno
python run.py leads --lang python --top 8      # buscar prospectos
python run.py pipeline hoy                     # seguimientos del día
python run.py pipeline ls                      # el tablero
```

Consejos para móvil:

- **Usa `--por-lang` bajo (8–12)** y `--delay 1.0`: en datos móviles las corridas
  grandes tardan mucho y gastan batería.
- **Corre las búsquedas grandes con wifi.**
- Si la pantalla se apaga, el proceso se corta: usa `termux-wake-lock` antes de
  una corrida larga y `termux-wake-unlock` al terminar.
- Los resultados quedan en `out/`. Ese directorio está en `.gitignore`, así que
  nunca se sube: tus prospectos y clientes se quedan en el teléfono.

---

## 5. Errores típicos en Termux

| Error | Causa y arreglo |
|---|---|
| `ModuleNotFoundError: No module named fastapi` | Solo hace falta para la API. El CLI (`run.py`) funciona sin instalar nada |
| `Limite de tasa alcanzado` | Falta o está mal el `GITHUB_TOKEN` (sección 2) |
| `No se pudo leer out/leads.json` | Aún no corriste `run.py leads` |
| Salen repos famosos (transformers, yt-dlp) | Tu copia está desactualizada: haz `git reset --hard` (sección 3) |
| `Permission denied` al escribir | Ejecuta `termux-setup-storage` y trabaja dentro de `~/` |
| La corrida se corta a mitad | Pantalla bloqueada: usa `termux-wake-lock` |

---

## 6. Sincronizar entre el móvil y el PC

El flujo sano es: **el PC es la fuente de verdad y el móvil solo lee.**

```bash
# en Termux, antes de usar
git pull origin arena/01a0a513-sub-agente
```

Si editas código en el móvil, súbelo:

```bash
git add -A && git commit -m "cambio desde el movil"
git push origin arena/01a0a513-sub-agente
```

Pero evita editar los filtros (`app/icp.py`, `app/leadgen.py`) desde dos sitios:
es exactamente cómo se termina con dos versiones distintas del mismo criterio.
