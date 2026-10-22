class DominioException(Exception):
    """Excepcion base para el dominio."""
    pass

class EmpleadoYaExisteException(DominioException):
    """Se lanza cuando se intenta registrar un empleado o una persona que ya existe en la BD"""
    pass
    
class ErrorBaseDeDatosException(DominioException):
    """Excepcion generica para errores no esperados en la capa de persistencia/base de datos"""
    pass
