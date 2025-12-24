# 🚀 Guía para Subir tu Proyecto a GitHub

Parece que **Git no está instalado** o no se detecta en tu terminal actual. Sigue estos pasos para configurar todo.

## Paso 1: Instalar Git

1. Descarga Git para Windows aquí: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Ejecuta el instalador.
   - Puedes dejar todas las opciones por defecto (Next, Next, Next...).
   - **Importante:** Asegúrate de que la opción "Git from the command line and also from 3rd-party software" esté marcada (suele serlo por defecto).
3. Una vez instalado, **cierra esta terminal y abre una nueva** para que reconozca el comando.

## Paso 2: Configuración Inicial (Solo una vez)

Abre tu terminal (PowerShell o CMD) y configura tu usuario:

```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

## Paso 3: Crear el Repositorio en GitHub

1. Ve a [https://github.com/new](https://github.com/new).
2. Nombre del repositorio: `pv-signal-mini-lab`.
3. Descripción: "PV Signal Detection Tool using Streamlit".
4. Visibilidad: **Public** o **Private** (tu elección).
5. **NO** marques "Initialize with README", .gitignore o License (ya los tenemos localmente).
6. Haz clic en **Create repository**.

## Paso 4: Subir tu Código

Copia y pega estos comandos en tu terminal, uno por uno:

> Asegúrate de estar en la carpeta del proyecto:
> `cd c:\Users\DELL\OneDrive\Documentos\Antigravity\pv-signal-mini-lab`

```powershell
# 1. Inicializar Git
git init

# 2. Agregar todos los archivos
git add .

# 3. Hacer el primer commit
git commit -m "Initial commit: PV Signal Mini-Lab v1.0"

# 4. Renombrar la rama principal a 'main'
git branch -M main

# 5. Conectar con GitHub (REEMPLAZA TU_USUARIO)
# Copia la URL que te dio GitHub en el paso anterior. Debería verse así:
git remote add origin https://github.com/TU_USUARIO/pv-signal-mini-lab.git

# 6. Subir el código
git push -u origin main
```

## Solución de Problemas Comunes

- **"git command not found"**: Reinicia tu computadora si cerrar la terminal no funcionó.
- **Errores de autenticación**: Al hacer `git push`, te pedirá usuario y contraseña.
  - Si usas autenticación moderna, puede que se abra una ventana del navegador para iniciar sesión.
  - Si no, usa un [Personal Access Token](https://github.com/settings/tokens) como contraseña.
