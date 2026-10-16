from dominio.empleado import Empleado
from dominio.departamento import Departamento
from dominio.registro_tiempo import RegistroTiempo

def main():
    # crear departamento
    dep = Departamento("Operaciones")

    #crear empleado (RUT como string, sueldo_base)
    nelson = Empleado("15000321-9", "Nelson Llanquileo", "2024-03-01", 950_000)

    #asosiar un objeto segun el diagrama
    dep.agregar_empleado(nelson)

    #registrar horas trabajadas
    reg1 = RegistroTiempo("R01", "2024-04-01", 8.0, "Desarrollo de modulo")
    reg2 = RegistroTiempo("R02", "2024-04-02", 7.5, "Reunion de avance")
    nelson.registrar_hora(reg1)
    nelson.registrar_hora(reg2)

    #imprimir informacion de pueba
    print(dep)
    print(nelson)
    print(f"Horas registradas para {nelson.nombre}: {nelson.total_horas()} hrs")

if __name__ == "__main__":
    main()
    