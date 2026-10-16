class Departamento:
    def __init__(self,nombre:str):
        self.nombre = nombre
        self.empleado = []

    def agregar_empleado(self, empleado):
        self.empleado.append(empleado)
        empleado.departamento = self

    def __str__(self) -> str:
        return f" Departamento: {self.nombre} (Total empleados: {len(self.empleado)})"
    