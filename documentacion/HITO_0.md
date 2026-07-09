# HITO 0: Especificaciones de Requerimientos

**Proyecto:** Sistema de Gestión de Consultorio Odontológico “Saca Muela” 🦷


## 1. Requerimientos Funcionales

El sistema deberá permitir la gestión completa (CRUD) de los pacientes mediante las siguientes funcionalidades:

* **Registrar Paciente (Alta):** Ingresar al sistema los datos personales y de contacto de un nuevo paciente.

* **Listar Pacientes (Consulta general):** Visualizar un registro completo de todos los pacientes alojados en la base de datos.

* **Buscar Paciente (Consulta específica):** Filtrar o localizar a un paciente particular utilizando su número de DNI como parámetro de búsqueda.

* **Modificar Paciente (Actualización):** Editar y sobreescribir los datos de un paciente previamente registrado en el sistema.

* **Eliminar Paciente (Baja):** Remover de forma permanente el registro de un paciente de la base de datos.


## 2. Requerimientos No Funcionales

Restricciones técnicas y estándares de calidad que el sistema debe cumplir estrictamente:

* **Separación de Capas:** La lógica de acceso a datos (`consultorio.py`) debe estar completamente desacoplada de la interfaz gráfica (`formulario_odontologico.py`).
  
* **Interfaz y Experiencia de Usuario (UX):** La aplicación debe contar con un diseño intuitivo gestionado mediante pestañas (`ttk.Notebook` de Tkinter) que separe visualmente las distintas operaciones.
  
* **Robustez y Manejo de Errores:** Aplicación de programación defensiva. El sistema debe validar el tipado y la longitud de las entradas del usuario (inputs), y capturar excepciones mediante bloques `try...except` para evitar caídas de la aplicación (crashes), notificando al usuario mediante cuadros de alerta (MessageBox).
  
* **Eficiencia de Persistencia:** Las transacciones a la base de datos (`sqlite3`) deben ejecutarse cerrando la conexión y el cursor de forma segura tras cada petición para evitar bloqueos del archivo `.db`.
  
* **Portabilidad:** El sistema debe estar preparado para ser empaquetado en un archivo ejecutable `.exe` para su distribución en entornos Windows.


## 3. Requerimientos de Dominio

Reglas lógicas inherentes al modelo de negocio del consultorio odontológico:

* **Unicidad de Entidad:** El Documento Nacional de Identidad (DNI) actúa como identificador unívoco (Clave Primaria / UNIQUE). Es imposible registrar dos pacientes con el mismo DNI.

* **Disponibilidad para Turnos:** El campo "Teléfono" es obligatoriamente requerido (NOT NULL). Sin este dato, el consultorio no puede coordinar ni confirmar turnos, por lo que el sistema debe bloquear el alta si está vacío.

* **Validación de Identidad:** Los campos "Nombre", "Apellido" y "DNI" son de carga obligatoria. El DNI debe contener exclusivamente caracteres numéricos.