from datetime import date
import oracledb
from dominio.empleado import Empleado
from dominio.excepciones import EmpleadoYaExisteException, ErrorBaseDeDatosException
from infraestructura.conexion import obtener_conexion

class EmpleadoRepositorio:
    
    def guardar(self, empleado: Empleado):
        """
        paso 1, 2 y 3: Transaccion atomica (todo o nada):Ambas inserciones se hacen bajo la misma conexion.
        Si ocurre un error, se realiza rollback eexplicito. Manejo de execpiones especificas de Oracle
        (ORA-00001: unique constraint violated)
        """
        conn = None
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            # 1. Insertar en tabla persona
            cursor.execute(
                "INSERT INTO persona (rut, nombre) VALUES (:1, :2)",
            (empleado.rut, empleado.nombre)
            )
            #2. Insertar en tabla empleado
            cursor.execute(
            "INSERT INTO empleado (rut, fecha_ingreso, sueldo_base, activo) VALUES (:1, :2, :3, :4)",
            (empleado.rut, empleado.fecha_ingreso, empleado.sueldo_base, empleado.activo),
            )
            # Si ambas consultas fueron exitosas, se aprueba la transacción (Todo)
            conn.commit()
            return empleado
        except oracledb.DatabaseError as e:
            if conn:
                conn.rollback()  # Operacion todo o nada (Nada)
            error, = e.args
            #Ora-00001: Restricción única violada(Clave primaria duplicada)
            if error.code == 1:
                raise EmpleadoYaExisteException(f"El RUT {empleado.rut} ya existe en la base de datos.") from e
            else:
                raise ErrorBaseDeDatosException(f"Error inesperado en la base de datos: {error.message}") from e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _fila_a_empleado(fila):
        fecha = fila[2]
        if isinstance(fecha, str):
            fecha_obj = date.fromisoformat(fecha[:10])
        else:
            fecha_obj = fecha.date() if hasattr(fecha, 'date') else fecha
            
        return Empleado(
            rut=fila[0],
            nombre=fila[1],
            fecha_ingreso=fecha_obj,
            sueldo_base=fila[3],
            activo=fila[4] if len(fila) > 4 else 1
        )

    def obtener(self, rut: str):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                fila = cursor.execute(
            """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
            FROM empleado e JOIN persona p ON p.rut = e.rut 
            WHERE e.rut = :1""",
            (rut,),
            ).fetchone()
            return self._fila_a_empleado(fila) if fila else None
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al obtener el empleado: {error.message}") from e

    def listar(self, nombre_contiene=None):
        sql = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
            FROM empleado e JOIN persona p ON p.rut = e.rut 
            WHERE e.activo = 1"""
        params = []
        if nombre_contiene:
            sql += " AND UPPER(p.nombre) LIKE UPPER(:1)"
            params.append(f"%{nombre_contiene}%")
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                filas = cursor.execute(sql, params).fetchall()
            return [self._fila_a_empleado(f) for f in filas]
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al listar empleados: {error.message}") from e
        
    def actualizar(self, empleado: Empleado):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                cursor.execute("UPDATE empleado SET sueldo_base = :1 WHERE rut = :2",
                (empleado.sueldo_base, empleado.rut),
                )
                conn.commit()
                return cursor.rowcount
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al actualizar el empleado: {error.message}") from e


    def eliminar(self, rut: str):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                cursor.execute("UPDATE empleado SET activo = 0 WHERE rut = :1", (rut,))
                conn.commit()
                return cursor.rowcount > 0
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al eliminar el empleado: {error.message}") from e