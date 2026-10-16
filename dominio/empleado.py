from dominio.persona import Persona

class Empleado(Persona):
    def __init__(self, rut: str, nombre: str, fecha_ingreso: str, sueldo_base: float):
        super().__init__(rut, nombre)
        self.fecha_ingreso = fecha_ingreso
        self.sueldo_base = sueldo_base
        self.registros = []
        self.departamento = None

    def registrar_hora(self, registro):
        self.registros.append(registro)

    def total_horas(self) -> float:
        return sum(reg.horas_trabajadas for reg in self.registros)

    def __str__(self) -> str:
        return f"Empleado: {self.nombre}, | RUT: {self.rut} | Sueldo: {self.sueldo_base:,.0f}"
    