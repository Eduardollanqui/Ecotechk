"""
===============================================================================
ASIGNATURA: Programación Orientada a Objeto Seguro (TI3021)
EVALUACIÓN: Evaluación Formativa 2 (EF2) - Unidad 2
PROYECTO: Optimización del Sistema de Gestión Interna en EcoTech Solutions
===============================================================================
CUMPLIMIENTO DE CRITERIOS DE EVALUACIÓN:
- 2.1.1.G.1: Definición total de clases del diagrama UML.
- 2.1.1.G.2: Representación exacta de relaciones (Herencia, Agregación, Asociación, Dependencia).
- 2.1.2.G.3: Encapsulamiento con propiedades (getters/setters y atributos protegidos).
- 2.1.2.G.4: Reutilización de código evitando duplicación mediante super() e interfaces abstractas.
- 2.1.3.G.5: Uso de la librería oficial 'oracledb' para conectar a Oracle Database.
- 2.1.3.G.6: Implementación de prueba de conexión exitosa con la BD.

RELACIONES DEL DIAGRAMA:
- Herencia:    Administrador -> Usuario | Empleado -> Usuario | Gerente -> Empleado
InformePDF, InformeExcel -> Informe
- Agregación:  Departamento <>-- Empleado (1 a 0..*) | Empleado <>-- RegistroTiempo (1 a 0..*)
- Asociación:  Empleado 0..* -- 0..* Proyecto, con clase de asociación AsignacionProyecto
Gerente 1 -- 1 Departamento (DIRIGE) | Departamento 1 -- 0..* Informe
- Dependencia: Administrador ..> Empleado (gestiona) | Administrador ..> Informe (genera)
Informe ..> RegistroTiempo (use)
===============================================================================
"""

from abc import ABC, abstractmethod
from datetime import date
import os

import oracledb
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env (DB_USER, DB_PASSWORD, ...)


# =============================================================================
# CONEXIÓN A BASE DE DATOS (ORACLE)
# =============================================================================
class ConexionBD:
    """Gestiona la conexión con Oracle Database usando la librería oficial oracledb.

    Las credenciales NO se escriben en el código: se leen desde el archivo .env
    (que debe estar en el .gitignore).
    """

    _HOST = os.getenv("DB_HOST", "localhost")
    _PORT = int(os.getenv("DB_PORT", "1521"))
    _SERVICE_NAME = os.getenv("DB_SERVICE", "XEPDB1")
    _USER = os.getenv("DB_USER")
    _PASSWORD = os.getenv("DB_PASSWORD")

    @classmethod
    def obtener_conexion(cls):
        """Implementa y prueba la conexión a Oracle. Devuelve la conexión o None."""
        if not cls._USER or not cls._PASSWORD:
            print("[ERROR DE CONEXIÓN] Faltan DB_USER o DB_PASSWORD en el archivo .env")
            return None
        try:
            dsn_str = f"{cls._HOST}:{cls._PORT}/{cls._SERVICE_NAME}"
            conexion = oracledb.connect(user=cls._USER, password=cls._PASSWORD, dsn=dsn_str)
            print("[CONEXIÓN EXITOSA] Conectado a Oracle Database en", dsn_str)
            return conexion
        except oracledb.Error as error:
            print(f"[ERROR DE CONEXIÓN] No se pudo conectar a Oracle BD: {error}")
            return None


# =============================================================================
# MODELO DE CLASES UML
# =============================================================================

# --- 1. CLASE ABSTRACTA USUARIO ---
class Usuario(ABC):
    """<<abstracta>> USUARIO. Base de Administrador y Empleado (2.1.2.G.3 / 2.1.2.G.4)."""

    def __init__(self, id_usuario: str, nombre_usuario: str, contrasena_hash: str):
        self._id_usuario = id_usuario
        self._nombre_usuario = nombre_usuario
        self._contrasena_hash = contrasena_hash

    @property
    def id_usuario(self) -> str:
        return self._id_usuario

    @property
    def nombre_usuario(self) -> str:
        return self._nombre_usuario

    @nombre_usuario.setter
    def nombre_usuario(self, nuevo_nombre: str):
        if len(nuevo_nombre.strip()) > 0:
            self._nombre_usuario = nuevo_nombre

    def iniciar_sesion(self) -> bool:
        print(f"Usuario {self._nombre_usuario} ha iniciado sesión.")
        return True

    def cerrar_sesion(self) -> None:
        print(f"Usuario {self._nombre_usuario} ha cerrado sesión.")

    @abstractmethod
    def verificar_permisos(self) -> bool:
        """Cada tipo de usuario define sus propios permisos."""


# --- 2. ADMINISTRADOR (hereda de Usuario) ---
class Administrador(Usuario):
    """ADMINISTRADOR. Depende de Empleado (gestiona) y de Informe (genera)."""

    def __init__(self, id_usuario: str, nombre_usuario: str, contrasena_hash: str,
        id_administrador: str):
        super().__init__(id_usuario, nombre_usuario, contrasena_hash)
        self._id_administrador = id_administrador
        self._contador_informes = 0

    def verificar_permisos(self) -> bool:
        return True  # El administrador tiene permisos totales

    def registrar_empleado(self, empleado: "Empleado") -> None:
        print(f"[ADMIN] Registrando al empleado '{empleado.nombre}' en el sistema.")

    def generar_informe(self, tipo: str) -> "Informe":
        """Crea un informe del formato pedido ('pdf' o 'excel') y lo devuelve."""
        self._contador_informes += 1
        id_informe = f"INF-{self._contador_informes:02d}"
        formatos = {"pdf": InformePDF, "excel": InformeExcel}
        clase = formatos.get(tipo.lower())
        if clase is None:
            raise ValueError(f"Tipo de informe no soportado: {tipo}")
        print(f"[ADMIN] Generando informe {id_informe} de tipo: {tipo}")
        return clase(id_informe, tipo, date.today())


# --- 3. EMPLEADO (hereda de Usuario) ---
class Empleado(Usuario):
    """EMPLEADO. Agrega RegistroTiempo y se asocia con Proyecto vía AsignacionProyecto."""

    def __init__(self, id_usuario: str, nombre_usuario: str, contrasena_hash: str,
        id_empleado: int, nombre: str, direccion: str, telefono: str,
        email: str, salario: float, fecha_inicio: date):
        super().__init__(id_usuario, nombre_usuario, contrasena_hash)
        self._id_empleado = id_empleado
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._email = email
        self._salario = salario
        self._fecha_inicio = fecha_inicio
        self._departamento = None      # 0..1 -> puede ser None
        self._asignaciones = []        # asociación con Proyecto (vía AsignacionProyecto)
        self._registros = []           # agregación 0..* RegistroTiempo

    # --- Propiedades (encapsulamiento) ---
    @property
    def id_empleado(self) -> int:
        return self._id_empleado

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, nuevo_salario: float):
        if nuevo_salario >= 0:
            self._salario = nuevo_salario

    @property
    def departamento(self):
        return self._departamento

    @departamento.setter
    def departamento(self, departamento) -> None:
        self._departamento = departamento

    @property
    def registros(self) -> list:
        return list(self._registros)

    @property
    def proyectos(self) -> list:
        return [a.proyecto for a in self._asignaciones]

    def verificar_permisos(self) -> bool:
        return True

    # --- Departamento ---
    def asignar_departamento(self, departamento: "Departamento") -> None:
        departamento.asignar_empleado(self)

    def reasignar_departamento(self, departamento: "Departamento") -> None:
        if self._departamento is None:
            departamento.asignar_empleado(self)
        else:
            self._departamento.reasignar_empleado(self, departamento)

    # --- Proyectos ---
    def asignar_proyecto(self, proyecto: "Proyecto", rol: str = "Colaborador",
        horas_dedicadas: float = 0.0) -> None:
        proyecto.asignar_empleado(self, rol, horas_dedicadas)

    def desasignar_proyecto(self, proyecto: "Proyecto") -> None:
        proyecto.desasignar_empleado(self)

    def _agregar_asignacion(self, asignacion: "AsignacionProyecto") -> None:
        self._asignaciones.append(asignacion)

    def _quitar_asignacion(self, asignacion: "AsignacionProyecto") -> None:
        self._asignaciones.remove(asignacion)

    # --- Registro de tiempo ---
    def registrar_tiempo(self, registro: "RegistroTiempo") -> None:
        if registro.validar_entrada_horas() and registro.guardar_registro():
            self._registros.append(registro)
            print(f"Registrando {registro.horas_trabajadas} hrs trabajadas para {self._nombre}.")
        else:
            print(f"[ERROR] Registro inválido para {self._nombre}: las horas deben ser > 0.")

    def total_horas(self) -> float:
        return sum(r.horas_trabajadas for r in self._registros)


# --- 3b. GERENTE (hereda de Empleado) ---
class Gerente(Empleado):
    """GERENTE. Es un Empleado que dirige un Departamento (relación DIRIGE 1 a 1)."""

    def __init__(self, id_usuario: str, nombre_usuario: str, contrasena_hash: str,
    id_empleado: int, nombre: str, direccion: str, telefono: str,
    email: str, salario: float, fecha_inicio: date):
        super().__init__(id_usuario, nombre_usuario, contrasena_hash, id_empleado, nombre,
            direccion, telefono, email, salario, fecha_inicio)
        self._departamento_dirigido = None

    @property
    def departamento_dirigido(self):
        return self._departamento_dirigido

    @departamento_dirigido.setter
    def departamento_dirigido(self, departamento) -> None:
        self._departamento_dirigido = departamento

    def gestionar_departamento(self) -> None:
        if self._departamento_dirigido is None:
            print("[GERENTE] No dirige ningún departamento.")
        else:
            print(f"[GERENTE] Gestionando departamento {self._departamento_dirigido.nombre}.")

    def aprobar_informe(self, informe: "Informe") -> None:
        print(f"[GERENTE] Informe '{informe.id_informe}' aprobado correctamente.")


# --- 4. DEPARTAMENTO ---
class Departamento:
    """DEPARTAMENTO. Dirigido por un Gerente (1 a 1), agrega Empleados (0..*) y asocia Informes."""

    def __init__(self, id_departamento: str, nombre: str, gerente: Gerente):
        self._id_departamento = id_departamento
        self._nombre = nombre
        self._gerente = gerente
        gerente.departamento_dirigido = self   # relación DIRIGE en ambos sentidos
        self._empleados = []                   # agregación 0..*
        self._informes = []                    # asociación 1 a 0..* con Informe

    @property
    def id_departamento(self) -> str:
        return self._id_departamento

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def gerente(self) -> Gerente:
        return self._gerente

    @property
    def empleados(self) -> list:
        return list(self._empleados)

    @property
    def informes(self) -> list:
        return list(self._informes)

    def crear_departamento(self) -> None:
        print(f"Departamento {self._nombre} creado.")

    def editar_departamento(self, nuevo_nombre: str) -> None:
        self._nombre = nuevo_nombre
        print(f"Departamento actualizado al nuevo nombre: {self._nombre}")

    def buscar_departamento(self, nombre: str):
        return self if self._nombre.lower() == nombre.lower() else None

    def eliminar_departamento(self) -> None:
        for empleado in self._empleados:
            empleado.departamento = None
        self._empleados.clear()
        print(f"Departamento {self._nombre} eliminado.")

    def asignar_empleado(self, empleado: Empleado) -> None:
        if empleado in self._empleados:
            print(f"El empleado {empleado.nombre} ya pertenece a {self._nombre}.")
            return
        self._empleados.append(empleado)
        empleado.departamento = self
        print(f"Empleado {empleado.nombre} añadido al departamento {self._nombre}.")

    def reasignar_empleado(self, empleado: Empleado, nuevo_departamento: "Departamento") -> None:
        if empleado in self._empleados:
            self._empleados.remove(empleado)
            nuevo_departamento.asignar_empleado(empleado)
            print(f"Empleado {empleado.nombre} reasignado desde {self._nombre} "
                f"hacia {nuevo_departamento.nombre}.")

    def agregar_informe(self, informe: "Informe") -> None:
        self._informes.append(informe)
        print(f"Informe {informe.id_informe} asociado al departamento {self._nombre}.")


# --- 5. PROYECTO Y CLASE DE ASOCIACIÓN ---
class AsignacionProyecto:
    """ASIGNACION DE PROYECTO. Clase de asociación entre Empleado y Proyecto."""

    def __init__(self, id_asignacion: str, fecha_asignacion: date, rol: str,
        horas_dedicadas: float, empleado: Empleado, proyecto: "Proyecto"):
        self._id_asignacion = id_asignacion
        self._fecha_asignacion = fecha_asignacion
        self._rol = rol
        self._horas_dedicadas = horas_dedicadas
        self._empleado = empleado
        self._proyecto = proyecto

    @property
    def id_asignacion(self) -> str:
        return self._id_asignacion

    @property
    def rol(self) -> str:
        return self._rol

    @property
    def horas_dedicadas(self) -> float:
        return self._horas_dedicadas

    @property
    def empleado(self) -> Empleado:
        return self._empleado

    @property
    def proyecto(self) -> "Proyecto":
        return self._proyecto


class Proyecto:
    """PROYECTO. Se relaciona con Empleado (0..* a 0..*) mediante AsignacionProyecto."""

    def __init__(self, id_proyecto: str, nombre: str, descripcion: str, fecha_inicio: date):
        self._id_proyecto = id_proyecto
        self._nombre = nombre
        self._descripcion = descripcion
        self._fecha_inicio = fecha_inicio
        self._asignaciones = []

    @property
    def id_proyecto(self) -> str:
        return self._id_proyecto

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def empleados(self) -> list:
        return [a.empleado for a in self._asignaciones]

    @property
    def asignaciones(self) -> list:
        return list(self._asignaciones)

    def crear_proyecto(self) -> None:
        print(f"[PROYECTO] Proyecto '{self._nombre}' registrado exitosamente en el sistema.")

    def editar_proyecto(self, nuevo_nombre: str, nueva_descripcion: str) -> None:
        self._nombre = nuevo_nombre
        self._descripcion = nueva_descripcion
        print(f"[PROYECTO] Proyecto ID {self._id_proyecto} actualizado a: {self._nombre}")

    def _buscar_asignacion(self, empleado: Empleado):
        for asignacion in self._asignaciones:
            if asignacion.empleado is empleado:
                return asignacion
        return None

    def asignar_empleado(self, empleado: Empleado, rol: str = "Colaborador",
        horas_dedicadas: float = 0.0) -> None:
        if self._buscar_asignacion(empleado) is not None:
            print(f"[PROYECTO] El empleado {empleado.nombre} ya forma parte de este proyecto")
            return
        asignacion = AsignacionProyecto(
            f"ASG-{self._id_proyecto}-{empleado.id_empleado}",
            date.today(), rol, horas_dedicadas, empleado, self)
        self._asignaciones.append(asignacion)
        empleado._agregar_asignacion(asignacion)
        print(f"[PROYECTO] Empleado {empleado.nombre} asignado correctamente "
        f"al proyecto {self._nombre} como {rol}.")

    def desasignar_empleado(self, empleado: Empleado) -> None:
        asignacion = self._buscar_asignacion(empleado)
        if asignacion is None:
            print(f"[PROYECTO] El empleado {empleado.nombre} no se encuentra asignado a este proyecto")
            return
        self._asignaciones.remove(asignacion)
        empleado._quitar_asignacion(asignacion)
        print(f"[PROYECTO] Empleado {empleado.nombre} removido del proyecto {self._nombre}")

    def eliminar_proyecto(self) -> None:
        for asignacion in self._asignaciones:
            asignacion.empleado._quitar_asignacion(asignacion)
        self._asignaciones.clear()
        print(f"[PROYECTO] Proyecto '{self._nombre}' eliminado del sistema")


# --- 6. REGISTRO TIEMPO ---
class RegistroTiempo:
    """REGISTRO TIEMPO. Agregado por Empleado (0..*)."""

    def __init__(self, id_registro: str, fecha: date, horas_trabajadas: float,
        descripcion_tarea: str):
        self._id_registro = id_registro
        self._fecha = fecha
        self._horas_trabajadas = horas_trabajadas
        self._descripcion_tarea = descripcion_tarea

    @property
    def horas_trabajadas(self) -> float:
        return self._horas_trabajadas

    def guardar_registro(self) -> bool:
        return True

    def validar_entrada_horas(self) -> bool:
        return 0 < self._horas_trabajadas <= 24

    def obtener_detalle(self) -> str:
        return f"Registro [{self._id_registro}]: {self._horas_trabajadas} hrs - {self._descripcion_tarea}"


# --- 7. INFORME (ABSTRACTA) Y SUS HERENCIAS ---
class Informe(ABC):
    """<<abstracta>> INFORME. Depende de RegistroTiempo ('Use'). Polimorfismo vía generar_reporte."""

    def __init__(self, id_informe: str, tipo_informe: str, fecha_de_informe: date):
        self._id_informe = id_informe
        self._tipo_informe = tipo_informe
        self._fecha_de_informe = fecha_de_informe

    @property
    def id_informe(self) -> str:
        return self._id_informe

    @staticmethod
    def _total_horas(registros) -> float:
        return sum(r.horas_trabajadas for r in (registros or []))

    @abstractmethod
    def generar_reporte(self, registros=None) -> str:
        """Genera el reporte usando (dependencia) una lista de RegistroTiempo."""


class InformePDF(Informe):
    """INFORME PDF (hereda de Informe)."""

    def generar_reporte(self, registros=None) -> str:
        return (f"Reporte PDF [{self._id_informe}] generado el {self._fecha_de_informe}. "
                f"Horas totales: {self._total_horas(registros)}")

    def exportar_a_pdf(self) -> None:
        print(f"Exportando informe {self._id_informe} a archivo .pdf...")


class InformeExcel(Informe):
    """INFORME EXCEL (hereda de Informe)."""

    def generar_reporte(self, registros=None) -> str:
        return (f"Reporte Excel [{self._id_informe}] generado el {self._fecha_de_informe}. "
                f"Horas totales: {self._total_horas(registros)}")

    def exportar_a_excel(self) -> None:
        print(f"Exportando informe {self._id_informe} a archivo .xlsx...")


# =============================================================================
# EJECUCIÓN Y VALIDACIÓN COMPLETA DE RÚBRICA (MAIN)
# =============================================================================
if __name__ == "__main__":
    print("\n==============================================")
    print("   PRUEBA DE VALIDACIÓN  - ECOTECH SOLUTIONS   ")
    print("==============================================\n")

    # 1. Conexión a Oracle
    print("--- PASO 1: Prueba de Conexión a Oracle BD ---")
    conexion = ConexionBD.obtener_conexion()
    if conexion:
        conexion.close()
        print("Cierre de conexión verificado.\n")
    else:
        print("Nota: revisa el archivo .env y que la base local esté corriendo.\n")

    # 2. Herencia, agregación y asociación
    print("--- PASO 2: Instanciación e Interacción de Clases UML ---")
    gerente = Gerente("U001", "gerente_roberto", "pass_hash_1", 100, "Roberto Soto",
        "Concepción", "911111111", "roberto@ecotech.cl", 1500000.0, date.today())
    admin = Administrador("U002", "admin_edu", "pass_hash_2", "ADM-01")

    dept_ti = Departamento("DEP-01", "Tecnologías de la Información", gerente)
    gerente2 = Gerente("U004", "gerente_marta", "pass_hash_4", 102, "Marta Rojas",
        "Talcahuano", "922222222", "marta@ecotech.cl", 1400000.0, date.today())
    dept_op = Departamento("DEP-02", "Operaciones", gerente2)   # un gerente por departamento (1 a 1)
    emp1 = Empleado("U003", "nelson", "pass_hash_3", 101, "Nelson Llanquileo", "Coronel",
                    "912345678", "nelson@ecotech.cl", 950000.0, date.today())

    admin.registrar_empleado(emp1)
    emp1.asignar_departamento(dept_ti)
    emp1.reasignar_departamento(dept_op)
    gerente.gestionar_departamento()
    gerente2.gestionar_departamento()

    proyecto = Proyecto("PRY-01", "Optimización Interna", "Mejora del sistema", date.today())
    proyecto.crear_proyecto()
    emp1.asignar_proyecto(proyecto, "Desarrollador", 20.0)
    emp1.asignar_proyecto(proyecto)  # duplicado: debe avisar

    reg_tiempo = RegistroTiempo("REG-1001", date.today(), 8.0, "Desarrollo de clases POO")
    emp1.registrar_tiempo(reg_tiempo)
    print(reg_tiempo.obtener_detalle())
    print(f"Horas totales de {emp1.nombre}: {emp1.total_horas()}")

    # 3. Polimorfismo, abstracción y dependencias
    print("\n--- PASO 3: Generación de Informes (PDF / Excel) ---")
    informes = [admin.generar_informe("pdf"), admin.generar_informe("excel")]
    for informe in informes:
        dept_op.agregar_informe(informe)
        print(informe.generar_reporte(emp1.registros))   # polimorfismo
        gerente2.aprobar_informe(informe)
    informes[0].exportar_a_pdf()
    informes[1].exportar_a_excel()

    try:
        Informe("X", "abstracto", date.today())
    except TypeError as error:
        print(f"[OK] Informe es abstracta y no se puede instanciar: {error}")

    print("\nPruebas finalizadas con éxito.")
