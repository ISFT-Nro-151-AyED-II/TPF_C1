# HITO 2: Codificación (Implementación) y Arquitectura

**Proyecto:** Sistema de Gestión de Consultorio Odontológico “Saca Muela” 🦷

Este documento detalla el proceso de implementación del sistema, justificando las decisiones algorítmicas, la configuración del entorno y la estrategia de empaquetado. El desarrollo se centró en aplicar principios de ingeniería de software para garantizar robustez, escalabilidad y una estricta separación de responsabilidades.

---

## 1. Aislamiento del Entorno (.venv) y Dependencias

Para evitar conflictos de versiones y asegurar la reproducibilidad del código en cualquier máquina, el desarrollo se aisló completamente utilizando el módulo nativo `venv`.

1. **Creación:** Se generó el entorno ejecutando `python -m venv .venv` en la raíz del proyecto.

2. **Activación:** Se habilitó mediante `.venv\Scripts\activate`.

3. **Instalación de Módulos:** Se utilizó `pip` para instalar exclusivamente las dependencias no nativas necesarias para la vista y la compilación, registradas en `requirements.txt`:

   * `Pillow`: Obligatorio para el renderizado y redimensionamiento escalado (anti-aliasing) de la imagen de fondo en Tkinter.
  
   * `pyinstaller`: Herramienta de empaquetado para compilar el código fuente a un binario ejecutable (`.exe`) nativo de Windows.

---

## 2. Arquitectura de Directorios

Se estructuró el repositorio para separar lógicamente los recursos estáticos, la persistencia, la documentación y el código fuente. Esta decisión técnica evita el "código espagueti" a nivel de sistema de archivos:

* **`assets/`**: Aislamiento de recursos gráficos (imágenes, iconos).

* **`database/`**: Carpeta destinada a alojar el estado del sistema (`consultorio.db`).

* **`documentacion/` y `diagramas/`**: Archivos de soporte teórico y modelado UML.

* **`src/`**: Directorio estricto para la lógica de la aplicación (`consultorio.py` y `formulario_odontologico.py`).

### 📂 Estructura del Proyecto

```text
📂 D:\Repositorios de GitHub\ISFT N°151\Algoritmos y Estructuras de Datos II\Trabajos Prácticos\TPF_C1\
├── 📁 assets\
│   ├── 🖼️ saca_muela_fondo.png         # Recursos gráficos (iconos .ico, logos, fondos .png, etc)
│   ├── 🖼️ saca_muela_icono.ico      
│   └── 🖼️ saca_muela_logo.png
│                         
├── 📁 database\                       # Almacenamiento de la Base de Datos
│   └── ⛃ consultorio.db               # Archivo SQLite (generado en ejecución, ignorado en git si es de prueba)
│                 
├── 📁 diagramas\                       # Modelado del sistema
│   ├── 📊 casos_de_uso.drawio
│   └── 📊 diagrama_clases.drawio                      
│   
├── 📁 documentacion\                   # Respaldos teóricos de cada fase
│   ├── 📝 HITO_0.md                    # Especificaciones de requerimientos funcionales, no funcionales y de dominio
│   ├── 📝 HITO_1.md                    # Explicación técnica y decisiones de diseño del UML
│   └── 📝 HITO_2.md                    # Documentación sobre la arquitectura del código y el CRUD
│
├── 📂 src\                             # Código fuente aislado
│   ├── 📘 consultorio.py               # Capa de Datos/SQL (DAO)
│   └── 📘 formulario_odontologico.py   # Capa UI / Main (Tkinter)
│
├── 🗑️ .gitignore                       # Configurado para ignorar /venv, __pycache__, y la DB de pruebas
│
├── ⚙️ compilame.bat                    # Script de automatización de build (llamada a PyInstaller)
├── 📝 requirements.txt                 # Dependencias del proyecto (ej: pyinstaller, pillow)
└── 📝 README.md                        # Resumen ejecutivo, índice, instrucciones de compilación y estructura
```
---

## 3. Enfoque Técnico: Capa de Datos (`consultorio.py`)

Este módulo implementa el patrón DAO (Data Access Object). Su única responsabilidad es interactuar con el motor SQLite.

* **Prevención de fugas de memoria:** Se implementó `contextlib.closing` envolviendo las llamadas a `_conectar()` en bloques `with`. Esto garantiza matemáticamente que los cursores y la conexión a la base de datos se cierren automáticamente al finalizar cada transacción (incluso si ocurre una excepción), evitando el error crítico `database is locked`.

* **Resolución dinámica de estado (sys.frozen):** El constructor de la clase intercepta el contexto de ejecución evaluando `sys.frozen`. Si el sistema corre como `.exe`, sitúa el archivo `.db` en la carpeta física raíz junto al binario (`sys.executable`), protegiendo la persistencia de datos de las purgas de carpetas temporales del SO.

* **Programación Defensiva (SQLi):** Todas las operaciones CRUD (Alta, Baja, Modificación) delegan la sanitización de inputs al driver de SQLite mediante el uso estricto de consultas parametrizadas (`?`), bloqueando inyecciones SQL.

---

## 4. Enfoque Técnico: Capa de Presentación (`formulario_odontologico.py`)

La interfaz visual fue construida con `tkinter` y `ttk`, actuando como cliente directo de la capa de datos.

* **Renderizado en Entornos Empaquetados:** Al igual que el motor de base de datos, la UI evalúa `sys.frozen`. Si el programa está compilado, enruta la búsqueda de los *assets* (imagen de fondo) hacia el directorio temporal de extracción de PyInstaller (`sys._MEIPASS`), evitando caídas de la aplicación por "File Not Found".

* **Gestión de Geometría Espacial (`place` vs `pack`):** Para evitar que el gestor de grillas deformara el diseño, se fijó la ventana estáticamente en 800x600 píxeles. Se utilizó `.place()` para el `ttk.Notebook`, anclándolo en el centro exacto de la pantalla (`relx=0.5, rely=0.5`) con dimensiones limitadas a 600x400. Esto permite visualizar la tarjeta de pestañas flotando sobre el fondo renderizado por `Pillow`.

* **Validación Temprana (Early Return):** El método `_validar_inputs()` intercepta la lógica antes de ejecutar cualquier transacción. Si un campo requerido está vacío o el DNI contiene caracteres no numéricos, se aborta la ejecución y se notifica al usuario, ahorrando ciclos de procesamiento y accesos innecesarios a disco.

---

## 5. Automatización de Compilación (`compilame.bat`)

Se desarrolló un script Batch para estandarizar el proceso de *build*. Al ejecutarse con el entorno `.venv` activado, realiza las siguientes operaciones secuenciales:

1. Verifica la existencia de PyInstaller en el entorno.

2. Invoca el compilador con *flags* específicos: `--onefile` (empaqueta todo en un solo binario), `--windowed` (suprime la consola del SO), y `--add-data` (inyecta la carpeta `assets/` dentro del ejecutable).

3. Reubica automáticamente el archivo `SacaMuela.exe` final desde la subcarpeta temporal `/dist` hacia la raíz del proyecto.

4. Purga y elimina de forma silenciosa la basura temporal de compilación (`build/`, `dist/`, `SacaMuela.spec`) para mantener limpio el repositorio.

---

## 6. Simulación de Ejecución y Pruebas de Robustez

A continuación, se demuestran los flujos principales del sistema verificando las barreras defensivas implementadas.

**Prueba 1: Alta de Paciente (Flujo Ideal)**

* **Input UI:** DNI: `35123456`, Nombre: `José`, Apellido: `Coder`, Teléfono: `223-154-8888`.
* **Click en:** `Registrar Alta`.
* **Proceso:** La validación local pasa. El DAO ejecuta el `INSERT`.
* **Salida UI:** MessageBox(Info) -> `"Paciente registrado correctamente."` La tabla se refresca mostrando la tupla inyectada.

**Prueba 2: Violación de Dominio (DNI duplicado)**

* **Input UI:** DNI: `35123456` (ya existente), Nombre: `Silvana`, Apellido: `Brujilda`, Teléfono: `223-456-7890`.
* **Click en:** `Registrar Alta`.
* **Proceso:** La validación local pasa. El DAO intenta el `INSERT`. SQLite dispara `IntegrityError` (PRIMARY KEY violation). El método en `consultorio.py` captura la excepción y retorna `False`.
* **Salida UI:** MessageBox(Error) -> `"No se pudo registrar. ¿El DNI ya existe?"`

**Prueba 3: Intercepción Defensiva (Input Inválido)**

* **Input UI:** DNI: `A456`, Nombre: `Leandro`, Apellido: `Elgorra`, Teléfono: `223-111-2222`.
* **Click en:** `Registrar Alta` o `Buscar por DNI`.
* **Proceso:** El método `_validar_inputs` detecta la falla mediante `.isdigit()`. Aborta el flujo antes de invocar al objeto `self.db`.
* **Salida UI:** MessageBox(Error) -> `"El DNI debe contener solo números."`

**Prueba 4: Baja Destructiva Controlada**

* **Input UI:** DNI: `35123456` (Solo se requiere el DNI).
* **Click en:** `Eliminar (Baja)`.
* **Proceso:** La UI pausa la ejecución y solicita confirmación expresa del usuario mediante `messagebox.askyesno`.
* **Salida UI:** Modal -> `"¿Eliminar de forma irreversible al DNI 35123456?"`. Al confirmar (Yes), se delega al DAO, se ejecuta el comando `DELETE` físico y se actualiza el listado en el TreeView.
