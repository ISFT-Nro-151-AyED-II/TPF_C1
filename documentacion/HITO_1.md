# HITO 1: Diseño del Sistema (UML)

**Proyecto:** Sistema de Gestión de Consultorio Odontológico “Saca Muela” 🦷

Este documento detalla el modelado de comportamiento y la estructura estática del sistema, justificando las decisiones algorítmicas y arquitectónicas tomadas para cumplir con los requerimientos planteados en la fase inicial.


## 1. Análisis del Diagrama de Casos de Uso

**Archivo de referencia:** [casos_de_uso.drawio](../diagramas/casos_de_uso.drawio)

El diagrama de casos de uso define las interacciones esperadas entre el actor (Personal del Consultorio) y el sistema. La justificación técnica de este diseño radica en la modularidad de los flujos de ejecución:

*   **Actor y Operaciones Directas:** El usuario interactúa de manera frontal con las operaciones que componen el ciclo de vida del dato (CRUD): *Registrar Paciente*, *Listar Pacientes*, *Modificar Paciente* y *Eliminar Paciente*. Además, puede ejecutar consultas aisladas mediante *Buscar Paciente por DNI*.
  
*   **Aislamiento de Reglas (Relaciones `<<include>>`):**

    *   **`Validar Reglas de Dominio`:** Se extrajo la validación como un módulo independiente, forzando a que las acciones de Alta y Modificación dependan estrictamente de él (`<<include>>`). Arquitectónicamente, esto evita la duplicación de código y asegura que ninguna transacción a la base de datos se intente si no se cumple con la unicidad del DNI o la obligatoriedad del teléfono.
  
    *   **`Buscar Paciente por DNI`:** Modificar o eliminar un registro exige conocer el estado previo de la entidad. Por ello, estas operaciones incluyen (`<<include>>`) al caso de uso de búsqueda de forma imperativa para localizar la tupla exacta antes de ejecutar un comando `UPDATE` o `DELETE`.


## 2. Análisis del Diagrama de Clases

**Archivo de referencia:** [diagrama_clases.drawio](../diagramas/diagrama_clases.drawio)

Este diagrama plasma el esqueleto del software, fundamentado en el requerimiento de implementar una separación estricta de capas donde la lógica SQL y la interfaz gráfica estén totalmente desacopladas.

*   **Clase `formulario_odontologico` (Capa de Presentación / UI):**

    *   **Responsabilidad:** Controlar la interacción con el usuario y dibujar la vista.
  
    *   **Atributos:** Administra el ciclo de vida de los componentes gráficos, instanciando `ttk.Notebook` para la navegación por pestañas, `ttk.Treeview` para el listado, y variables de control (`tk.StringVar`) para interceptar la entrada de texto.
  
    *   **Métodos:** Contiene controladores de eventos (ej. `ejecutar_alta`, `ejecutar_baja`). Fundamentalmente, aloja rutinas como `validar_inputs` y `mostrar_alerta`, asegurando un nivel primario de robustez y UX antes de delegar la información a la capa inferior. No contiene ninguna instrucción SQL.

*   **Clase `consultorio` (Capa de Datos / DAO):**

    *   **Responsabilidad:** Persistencia, gestión del motor SQLite y reglas de negocio pesadas.

    *   **Métodos:** Expone funciones puras que reciben parámetros nativos de Python (`str`) y devuelven estructuras de datos primitivas (`boolean`, `list`, `tuple`). El método privado `- conectar()` encapsula el manejo del conector, abriendo y cerrando las transacciones para proteger el archivo de la base de datos.
  
    *   **Desacople:** Esta clase es "ciega" a la interfaz. Ignora por completo la existencia de Tkinter, lo que significa que en el futuro podría conectarse a una API web o a una interfaz por consola sin modificar una sola línea de su código interno.

*   **Relación de Dependencia:**

    *   La línea punteada en el diagrama expone que `formulario_odontologico` requiere y consume los servicios de `consultorio`. La relación es estrictamente unidireccional, garantizando el cumplimiento de la rúbrica de evaluación arquitectónica.