-- db/01_esquema.sql (Versionado en Git, repetible e independiente)

CREATE TABLE IF NOT EXISTS departamento (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS empleado (
    rut             TEXT PRIMARY KEY,               -- Texto para preservar DV y ceros
    nombre          TEXT NOT NULL,
    fecha_ingreso   DATE NOT NULL,               -- Formato fecha para ordenar
    sueldo_base     INTEGER NOT NULL,            -- En pesos chilenos
    departamento_id INTEGER,
    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);