-- db/01_esquema_oracle.sql (Versionado en Git, repetible e independiente)

-- Tabla: departamento
CREATE TABLE departamento (
id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
nombre      VARCHAR2(100) NOT NULL CONSTRAINT uk_departamento_nombre UNIQUE
);

-- Tabla: empleado
CREATE TABLE empleado (
rut             VARCHAR2(12) PRIMARY KEY,                  -- Texto para preservar DV y ceros
nombre          VARCHAR2(150) NOT NULL,
fecha_ingreso   DATE NOT NULL,                            -- Formato fecha para ordenar
sueldo_base     NUMBER(10) NOT NULL,                      -- En pesos chilenos
departamento_id NUMBER,
CONSTRAINT fk_empleado_departamento
FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);