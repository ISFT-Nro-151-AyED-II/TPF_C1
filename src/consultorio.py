import sys
import sqlite3
from pathlib import Path
# closing permite manejar conexiones y cursores de manera segura, cerrándolos automáticamente.
from contextlib import closing 


class Consultorio:
    def __init__(self):
        # Resolución de estado para persistencia de datos físicos.
        if getattr(sys, 'frozen', False):
            # sys.executable apunta a la ruta real de tu SacaMuela.exe (ej: disco D:).
            base_dir = Path(sys.executable).parent
        else:
            # Entorno local.
            base_dir = Path(__file__).resolve().parent.parent

        self.ruta_db = base_dir / "database" / "consultorio.db"
        
        # Se garantiza que la carpeta de la base de datos exista en el sistema de archivos.
        self.ruta_db.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_db()

    def _conectar(self) -> sqlite3.Connection:
        # Método protegido que encapsula el driver. 
        # Si a futuro se migra a PostgreSQL o MySQL, solo se toca este método.
        return sqlite3.connect(self.ruta_db)

    def _inicializar_db(self):
        # DDL: Se plasma el esquema físico basado en las reglas de dominio del Hito 0.
        # DNI es PRIMARY KEY para asegurar la unicidad 
        # (no pueden existir dos pacientes con el mismo DNI).
        query = """
        CREATE TABLE IF NOT EXISTS pacientes (
            dni TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
        """
        try:
            # Se garantiza que la conexión se cierre automáticamente al salir del bloque 'with'.
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
        except sqlite3.Error as e:
            # Captura pasiva: si el motor de DB falla desde el inicio, se registra en consola.
            # La interfaz no maneja este nivel de error estructural.
            print(f"Error crítico estructural en DB: {e}")

    def registrar_paciente(self, dni: str, nombre: str, apellido: str, telefono: str) -> bool:
        # Programación defensiva: Se usan consultas parametrizadas (?) estrictamente
        # para delegar la sanitización a SQLite y bloquear ataques de SQL Injection.
        query = "INSERT INTO pacientes (dni, nombre, apellido, telefono) VALUES (?, ?, ?, ?)"
        try:
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (dni, nombre, apellido, telefono))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Se dispara si se viola la regla PRIMARY KEY (el DNI ya existe).
            return False
        except sqlite3.Error:
            # Cualquier otro fallo de E/S.
            return False

    def listar_pacientes(self) -> list:
        # Consulta de solo lectura. Retorna una lista de tuplas para poblar el Treeview.
        query = "SELECT dni, nombre, apellido, telefono FROM pacientes"
        try:
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def buscar_paciente_por_dni(self, dni: str) -> tuple:
        # Retorna la tupla del paciente si existe, o None. Útil para validar existencias
        # antes de intentar una modificación o baja.
        query = "SELECT dni, nombre, apellido, telefono FROM pacientes WHERE dni = ?"
        try:
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (dni,))
                return cursor.fetchone()
        except sqlite3.Error:
            return None

    def modificar_paciente(self, dni: str, nombre: str, apellido: str, telefono: str) -> bool:
        # UPDATE filtrado estrictamente por PK. 
        query = "UPDATE pacientes SET nombre = ?, apellido = ?, telefono = ? WHERE dni = ?"
        try:
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (nombre, apellido, telefono, dni))
                conn.commit()
                # rowcount asegura que realmente se modificó un registro (el DNI existía).
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def eliminar_paciente(self, dni: str) -> bool:
        # Baja física del registro. Mismo control con rowcount para validar que 
        # no se devuelva True sobre un intento de borrado "fantasma".
        query = "DELETE FROM pacientes WHERE dni = ?"
        try:
            with closing(self._conectar()) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (dni,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False