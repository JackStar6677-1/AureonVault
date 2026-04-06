# AureonVault

AureonVault es un explorador de archivos experimental para Windows con una interfaz de escritorio propia en Python/Tkinter y un prototipo web conservado dentro del mismo repositorio.

La idea del proyecto no es competir con el Explorador de Windows como reemplazo total, sino probar una interfaz con identidad visual marcada, navegación rápida, panel de detalle, filtro inmediato y herramientas de conveniencia para recorrer carpetas del equipo desde una app más controlada.

## Que contiene este repositorio

Este repo guarda dos aproximaciones del mismo experimento:

- una aplicacion de escritorio nativa escrita en Python y Tkinter
- un MVP web local dentro de `prototype_web/`, mantenido como referencia del camino anterior

La app principal actual es la version de escritorio.

## Objetivo del proyecto

El objetivo de AureonVault es explorar una experiencia de administracion de archivos con estas prioridades:

- interfaz claramente personalizada y no genica
- acceso rapido a ubicaciones comunes de Windows
- lectura comoda del contenido de carpetas
- vista de detalle para el elemento seleccionado
- acciones utiles sin salir de la app
- un entorno visual pensado para sesiones largas en escritorio

## Funciones principales

La aplicacion Python incluye:

- deteccion de unidades disponibles del sistema
- barra lateral con accesos rapidos a carpetas frecuentes
- breadcrumbs para navegar por la ruta actual
- listado ordenado de carpetas y archivos
- filtro por nombre en tiempo real
- panel de detalle del elemento seleccionado
- vista previa de archivos de texto cuando aplica
- apertura del archivo o carpeta seleccionada
- opcion de revelar el elemento en el Explorador de Windows
- terminal integrada para lanzar comandos desde la carpeta actual
- acceso para abrir una terminal administrativa en la ubicacion activa

## Stack

- Python
- Tkinter para la interfaz principal
- APIs del sistema de archivos de Windows
- Node.js + Express en el prototipo web

## Estructura del repositorio

```text
AureonVault/
|-- app.py
|-- run_aureonvault.bat
|-- README.md
`-- prototype_web/
    |-- package.json
    |-- package-lock.json
    |-- server.js
    `-- src/
        |-- index.html
        |-- renderer.js
        `-- styles.css
```

## Archivo por archivo

- `app.py`
  Aplicacion principal. Construye la UI, gestiona la navegacion, el filtro, la vista de detalle, la consola integrada y las acciones de abrir o revelar archivos.
- `run_aureonvault.bat`
  Lanzador rapido para Windows. Intenta abrir la app con `pythonw` y hace fallback a `python`.
- `prototype_web/server.js`
  Servidor Express del prototipo web local.
- `prototype_web/src/`
  HTML, logica cliente y estilos del MVP anterior.

## Como ejecutar la app principal

Requisitos recomendados:

- Windows
- Python 3.10 o superior

Ejecucion directa:

```powershell
cd C:\Users\Jack\Documents\GitHub\Experimentos\AureonVault
python app.py
```

Tambien puedes abrir:

```text
run_aureonvault.bat
```

## Como ejecutar el prototipo web

Requisitos:

- Node.js 18 o superior recomendado

Instalacion:

```powershell
cd C:\Users\Jack\Documents\GitHub\Experimentos\AureonVault\prototype_web
npm install
```

Ejecucion:

```powershell
npm start
```

## Estado actual

Este proyecto esta en fase experimental. La implementacion de escritorio ya concentra la idea principal, mientras que `prototype_web/` queda en el repo como registro del prototipo previo.

No esta pensado todavia como administrador de archivos de uso empresarial ni como sustituto completo del Explorador de Windows. Es un laboratorio de interfaz, flujo y herramientas locales.

## Seguridad y alcance

- No intenta subir archivos a la nube ni conectarse a servicios externos.
- Trabaja con rutas locales del equipo.
- El repositorio ignora dependencias locales como `node_modules`, caches de Python y archivos de entorno.

## Casos de uso razonables

- experimentar con una UI de gestion de archivos distinta a la nativa
- revisar rapidamente contenido de carpetas comunes
- abrir o revelar archivos desde una interfaz personalizada
- usar el repo como base para futuros experimentos de file manager en Windows

## Posibles siguientes pasos

- operaciones de copiar, mover y renombrar desde la interfaz
- pestañas o paneles dobles
- favoritos editables por el usuario
- miniaturas mas ricas para imagenes y documentos
- empaquetado como ejecutable para Windows
