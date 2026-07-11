import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path

# Desacoplamiento total: importamos la capa de datos.
from consultorio import Consultorio

class FormularioOdontologico:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestión Odontológica - Saca Muela")
        
        # Bloqueo de dimensiones para garantizar que la imagen de fondo y el layout no se rompan.
        self.root.geometry("800x600")
        self.root.resizable(False, False) 
        
        # Inyección de dependencia implícita: Se instancia el motor de base de datos.
        self.db = Consultorio()

        # Variables de control de Tkinter (equivalente a los estados para enlazar con los Entry).
        self.txt_dni = tk.StringVar()
        self.txt_nombre = tk.StringVar()
        self.txt_apellido = tk.StringVar()
        self.txt_telefono = tk.StringVar()

        self._inicializar_interfaz()

    def _inicializar_interfaz(self):
        # Enrutamiento dinámico: detecta si corre desde el .exe o desde el código fuente.
        if getattr(sys, 'frozen', False):
            # PyInstaller desempaqueta los assets (--add-data) en sys._MEIPASS.
            base_dir = Path(sys._MEIPASS)
        else:
            # Entorno de desarrollo local.
            base_dir = Path(__file__).resolve().parent.parent
        ruta_imagen = base_dir / "assets" / "saca_muela_fondo.png"

        try:
            # Pillow maneja el resize forzado a 800x600 con anti-aliasing (LANCZOS).
            imagen_original = Image.open(ruta_imagen)
            imagen_redimensionada = imagen_original.resize((800, 600), Image.Resampling.LANCZOS)
            self.imagen_fondo = ImageTk.PhotoImage(imagen_redimensionada)

            # Z-index 0: Se ubica la imagen al fondo absoluto usando place().
            fondo_label = tk.Label(self.root, image=self.imagen_fondo)
            fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            # Captura pasiva: si el asset no existe, la app debe levantar igual (resiliencia).
            print(f"Advertencia UX: No se pudo cargar el fondo. Razón: {e}")

        # Se delega la construcción de los nodos visuales.
        self._crear_pestanias()

    def _crear_pestanias(self):
        # El Notebook enruta la vista en dos contextos lógicos: Gestión y Lectura.
        self.notebook = ttk.Notebook(self.root)
        
        # Se usa place para crear una "tarjeta" flotante centrada.
        # relx y rely en 0.5 ubican el ancla en el centro exacto de la ventana (400, 300).
        # Se limita el tamaño a 600x400 píxeles para dejar un margen amplio donde se vea el fondo.
        self.notebook.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        tab_gestion = ttk.Frame(self.notebook)
        tab_listado = ttk.Frame(self.notebook)

        self.notebook.add(tab_gestion, text="Gestión de Pacientes (CRUD)")
        self.notebook.add(tab_listado, text="Listado General")

        # =========================================
        #  CONSTRUCCIÓN DE PESTAÑA: GESTIÓN (CRUD)
        # =========================================
        frame_form = ttk.LabelFrame(tab_gestion, text="Datos del Paciente", padding=20)
        frame_form.pack(pady=20, padx=20, fill="x")

        # Layout en grilla para mantener alineación en el formulario.
        ttk.Label(frame_form, text="DNI (Solo números):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frame_form, textvariable=self.txt_dni).grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(frame_form, text="Nombre:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame_form, textvariable=self.txt_nombre).grid(row=1, column=1, sticky="ew", padx=10)

        ttk.Label(frame_form, text="Apellido:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame_form, textvariable=self.txt_apellido).grid(row=2, column=1, sticky="ew", padx=10)

        ttk.Label(frame_form, text="Teléfono (Obligatorio):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame_form, textvariable=self.txt_telefono).grid(row=3, column=1, sticky="ew", padx=10)

        frame_botones = ttk.Frame(tab_gestion)
        frame_botones.pack(pady=10)

        # Enlace de eventos (listeners) a los métodos de clase.
        ttk.Button(frame_botones, text="Registrar Alta", command=self._ejecutar_alta).grid(row=0, column=0, padx=5)
        ttk.Button(frame_botones, text="Buscar por DNI", command=self._ejecutar_busqueda).grid(row=0, column=1, padx=5)
        ttk.Button(frame_botones, text="Modificar", command=self._ejecutar_modificacion).grid(row=0, column=2, padx=5)
        ttk.Button(frame_botones, text="Eliminar (Baja)", command=self._ejecutar_baja).grid(row=0, column=3, padx=5)
        ttk.Button(frame_botones, text="Limpiar Campos", command=self._limpiar_campos).grid(row=0, column=4, padx=5)

        # ==================================
        #  CONSTRUCCIÓN DE PESTAÑA: LISTADO
        # ==================================
        columnas = ("dni", "nombre", "apellido", "telefono")
        self.tabla_pacientes = ttk.Treeview(tab_listado, columns=columnas, show="headings")
        
        self.tabla_pacientes.heading("dni", text="DNI")
        self.tabla_pacientes.heading("nombre", text="Nombre")
        self.tabla_pacientes.heading("apellido", text="Apellido")
        self.tabla_pacientes.heading("telefono", text="Teléfono")

        scrollbar = ttk.Scrollbar(tab_listado, orient=tk.VERTICAL, command=self.tabla_pacientes.yview)
        self.tabla_pacientes.configure(yscroll=scrollbar.set)

        self.tabla_pacientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        ttk.Button(tab_listado, text="Refrescar Listado", command=self._ejecutar_consulta_general).pack(pady=10)
        
        # Poblar la tabla al arrancar la app.
        self._ejecutar_consulta_general()

    def _validar_inputs(self, dni: str, nombre: str, apellido: str, telefono: str, requiere_todo: bool = True) -> bool:
        # Lógica de validación centralizada. Retorna False ante el primer fallo (Early Return).
        if not dni:
            self._mostrar_alerta("Error de Validación", "El campo DNI es obligatorio.", es_error=True)
            return False
        if not dni.isdigit():
            self._mostrar_alerta("Error de Validación", "El DNI debe contener solo números.", es_error=True)
            return False

        # Para buscar o borrar, solo se exige el DNI. Para alta/modificación, se exigen todos los campos.
        if requiere_todo:
            if not nombre or not apellido:
                self._mostrar_alerta("Error de Validación", "Nombre y Apellido son obligatorios.", es_error=True)
                return False
            if not telefono:
                self._mostrar_alerta("Error de Validación", "El Teléfono es obligatorio.", es_error=True)
                return False

        return True

    def _ejecutar_alta(self):
        # Extracción de strings limpios de los StringVars.
        d, n, a, t = self.txt_dni.get().strip(), self.txt_nombre.get().strip(), self.txt_apellido.get().strip(), self.txt_telefono.get().strip()
        
        if not self._validar_inputs(d, n, a, t): return

        # Delegación a la capa de datos.
        if self.db.registrar_paciente(d, n, a, t):
            self._mostrar_alerta("Éxito", "Paciente registrado correctamente.", es_error=False)
            self._limpiar_campos()
            self._ejecutar_consulta_general()
        else:
            self._mostrar_alerta("Error", "No se pudo registrar. ¿El DNI ya existe?", es_error=True)

    def _ejecutar_busqueda(self):
        d, n, a, t = self.txt_dni.get().strip(), self.txt_nombre.get().strip(), self.txt_apellido.get().strip(), self.txt_telefono.get().strip()
        
        # Se sobreescribe requiere_todo a False porque solo se necesita el DNI para buscar.
        if not self._validar_inputs(d, n, a, t, requiere_todo=False): return

        paciente = self.db.buscar_paciente_por_dni(d)
        
        if paciente:
            self.txt_dni.set(paciente[0])
            self.txt_nombre.set(paciente[1])
            self.txt_apellido.set(paciente[2])
            self.txt_telefono.set(paciente[3])
            self._mostrar_alerta("Búsqueda", "Paciente encontrado. Datos cargados.", es_error=False)
        else:
            self._mostrar_alerta("Búsqueda", "No se encontró ningún paciente con ese DNI.", es_error=True)

    def _ejecutar_modificacion(self):
        d, n, a, t = self.txt_dni.get().strip(), self.txt_nombre.get().strip(), self.txt_apellido.get().strip(), self.txt_telefono.get().strip()
        
        if not self._validar_inputs(d, n, a, t): return

        # Chequeo de integridad: Se fuerza a que el usuario no intente modificar un DNI inexistente.
        if not self.db.buscar_paciente_por_dni(d):
            self._mostrar_alerta("Error", "El paciente no existe. Utilice el alta.", es_error=True)
            return

        if self.db.modificar_paciente(d, n, a, t):
            self._mostrar_alerta("Éxito", "Datos actualizados correctamente.", es_error=False)
            self._limpiar_campos()
            self._ejecutar_consulta_general()
        else:
            self._mostrar_alerta("Error", "Fallo de persistencia al actualizar.", es_error=True)

    def _ejecutar_baja(self):
        d, n, a, t = self.txt_dni.get().strip(), self.txt_nombre.get().strip(), self.txt_apellido.get().strip(), self.txt_telefono.get().strip()
        
        if not self._validar_inputs(d, n, a, t, requiere_todo=False): return

        # Patrón de diseño de interacción: Confirmación destructiva obligatoria.
        if messagebox.askyesno("Confirmar Baja", f"¿Eliminar de forma irreversible al DNI {d}?"):
            if self.db.eliminar_paciente(d):
                self._mostrar_alerta("Éxito", "Paciente eliminado del sistema.", es_error=False)
                self._limpiar_campos()
                self._ejecutar_consulta_general()
            else:
                self._mostrar_alerta("Error", "El DNI no existe en el sistema.", es_error=True)

    def _ejecutar_consulta_general(self):
        # Purga de nodos gráficos actuales en el Treeview.
        for row in self.tabla_pacientes.get_children():
            self.tabla_pacientes.delete(row)
            
        # Re-inyección de la estructura de datos traída desde SQLite.
        for p in self.db.listar_pacientes():
            self.tabla_pacientes.insert("", tk.END, values=p)

    def _mostrar_alerta(self, titulo: str, mensaje: str, es_error: bool):
        # Wrapper de abstracción sobre messagebox.
        if es_error:
            messagebox.showerror(titulo, mensaje)
        else:
            messagebox.showinfo(titulo, mensaje)

    def _limpiar_campos(self):
        # Reseteo de estados.
        self.txt_dni.set("")
        self.txt_nombre.set("")
        self.txt_apellido.set("")
        self.txt_telefono.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = FormularioOdontologico(root)
    root.mainloop()