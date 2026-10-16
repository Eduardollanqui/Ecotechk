class Persona:
    def __init__(self, rut: str, nombre: str):
        self.rut = rut # RUT como texto para conservar el DV y ceros iniciales
        self.nombre = nombre
