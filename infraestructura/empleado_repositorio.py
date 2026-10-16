from datetime import date
from dominio.empleado import Empleado
from infraestructura.conexion import obtener_conexion

class EmpleadoRepositorio:
    
    def guardar(self, empleado: Empleado):
        with obtener_conexion() as conn, conn.cursor() as cursor:
            # Insertar en tabla persona
            cursor.execute(
                "INSERT INTO persona (rut, nombre) VALUES (:1, :2)",
                (empleado.rut, empleado.nombre),
            )
            # Insertar en tabla empleado
            cursor.execute(
                "INSERT INTO empleado (rut, fecha_ingreso, sueldo_base, activo) VALUES (:1, :2, :3, :4)",
                (empleado.rut, empleado.fecha_ingreso, empleado.sueldo_base, empleado.activo),
            )
            conn.commit()
        return empleado

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
        with obtener_conexion() as conn, conn.cursor() as cursor:
            fila = cursor.execute(
                """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
                FROM empleado e JOIN persona p ON p.rut = e.rut 
                WHERE e.rut = :1""",
                (rut,),
            ).fetchone()
        return self._fila_a_empleado(fila) if fila else None

    def listar(self, nombre_contiene=None):
        sql = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
                FROM empleado e JOIN persona p ON p.rut = e.rut 
                WHERE e.activo = 1"""
        params = []
        if nombre_contiene:
            sql += " AND p.nombre LIKE :1"
            params.append(f"%{nombre_contiene}%")
            
        with obtener_conexion() as conn, conn.cursor() as cursor:
            filas = cursor.execute(sql, params).fetchall()
        return [self._fila_a_empleado(f) for f in filas]

    def actualizar(self, empleado: Empleado):
        with obtener_conexion() as conn, conn.cursor() as cursor:
            cursor.execute(
                "UPDATE empleado SET sueldo_base = :1 WHERE rut = :2",
                (empleado.sueldo_base, empleado.rut),
            )
            conn.commit()
            rowcount = cursor.rowcount
        return rowcount

    def eliminar(self, rut: str):
        with obtener_conexion() as conn, conn.cursor() as cursor:
            cursor.execute("UPDATE empleado SET activo = 0 WHERE rut = :1", (rut,))
            conn.commit()
            rowcount = cursor.rowcount
        return rowcount > 0