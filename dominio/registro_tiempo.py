class RegistroTiempo:
    def __init__(self, id_registro: str, fecha: str, horas_trabajadas: float, descripcion: str):
        self.id_registro = id_registro
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion = descripcion