-- ============================================================
-- Sistema de Administración de Propiedad Horizontal
-- ============================================================

-- Usuario y base de datos
CREATE USER 'user_python'@'localhost' IDENTIFIED BY 'Csfg6283427834';
GRANT CREATE, INSERT, UPDATE, DELETE, SELECT, FILE, EXECUTE ON *.* TO 'user_python'@'localhost' WITH GRANT OPTION;

CREATE DATABASE db_ph;

-- ============================================================
-- 1. CONJUNTOS
--    Representa cada conjunto residencial administrado.
-- ============================================================
CREATE TABLE db_ph.conjuntos (
    id        INT NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(200) NOT NULL,
    nit       VARCHAR(20) NOT NULL UNIQUE,
    direccion VARCHAR(300) NOT NULL,
    ciudad    VARCHAR(100) NOT NULL,
    telefono  VARCHAR(20),
    PRIMARY KEY(id)
);

-- ============================================================
-- 2. TORRES
--    Cada conjunto puede tener una o varias torres.
-- ============================================================
CREATE TABLE db_ph.torres (
    id           INT NOT NULL AUTO_INCREMENT,
    conjunto_id  INT NOT NULL,
    nombre       VARCHAR(100) NOT NULL,
    total_pisos  INT NOT NULL DEFAULT 1,
    PRIMARY KEY(id),
    CONSTRAINT fk_torres__conjuntos FOREIGN KEY (conjunto_id) REFERENCES db_ph.conjuntos (id)
);

-- ============================================================
-- 3. APARTAMENTOS
--    Cada torre tiene varios apartamentos.
-- ============================================================
CREATE TABLE db_ph.apartamentos (
    id       INT NOT NULL AUTO_INCREMENT,
    torre_id INT NOT NULL,
    numero   VARCHAR(10) NOT NULL,
    piso     INT NOT NULL,
    area_m2  DECIMAL(10,2) NOT NULL,
    tipo     VARCHAR(50) NOT NULL DEFAULT 'residencial',
    activo   BIT NOT NULL DEFAULT 1,
    PRIMARY KEY(id),
    CONSTRAINT fk_aptos__torres FOREIGN KEY (torre_id) REFERENCES db_ph.torres (id)
);

-- ============================================================
-- 4. PROPIETARIOS
--    Cada apartamento tiene un propietario registrado.
-- ============================================================
CREATE TABLE db_ph.propietarios (
    id               INT NOT NULL AUTO_INCREMENT,
    apartamento_id   INT NOT NULL,
    cedula           VARCHAR(20) NOT NULL UNIQUE,
    nombre           VARCHAR(200) NOT NULL,
    telefono         VARCHAR(20),
    email            VARCHAR(150),
    fecha_registro   DATETIME NOT NULL DEFAULT NOW(),
    PRIMARY KEY(id),
    CONSTRAINT fk_prop__aptos FOREIGN KEY (apartamento_id) REFERENCES db_ph.apartamentos (id)
);

-- ============================================================
-- 5. CUOTAS
--    Cuotas de administración generadas por apartamento.
-- ============================================================
CREATE TABLE db_ph.cuotas (
    id                INT NOT NULL AUTO_INCREMENT,
    apartamento_id    INT NOT NULL,
    propietario_id    INT NOT NULL,
    tipo              VARCHAR(50) NOT NULL DEFAULT 'ordinaria',
    valor             DECIMAL(12,2) NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    pagada            BIT NOT NULL DEFAULT 0,
    PRIMARY KEY(id),
    CONSTRAINT fk_cuotas__aptos FOREIGN KEY (apartamento_id) REFERENCES db_ph.apartamentos (id),
    CONSTRAINT fk_cuotas__prop  FOREIGN KEY (propietario_id) REFERENCES db_ph.propietarios (id)
);

-- ============================================================
-- 6. PAGOS
--    Registro de cada pago realizado sobre una cuota.
-- ============================================================
CREATE TABLE db_ph.pagos (
    id           INT NOT NULL AUTO_INCREMENT,
    cuota_id     INT NOT NULL,
    valor_pagado DECIMAL(12,2) NOT NULL,
    fecha_pago   DATETIME NOT NULL DEFAULT NOW(),
    metodo       VARCHAR(50) NOT NULL DEFAULT 'transferencia',
    comprobante  VARCHAR(100),
    PRIMARY KEY(id),
    CONSTRAINT fk_pagos__cuotas FOREIGN KEY (cuota_id) REFERENCES db_ph.cuotas (id)
);

-- ============================================================
-- 7. AREAS_COMUNES
--    Zonas compartidas del conjunto (piscina, salon, etc.).
-- ============================================================
CREATE TABLE db_ph.areas_comunes (
    id          INT NOT NULL AUTO_INCREMENT,
    conjunto_id INT NOT NULL,
    nombre      VARCHAR(100) NOT NULL,
    descripcion VARCHAR(300),
    capacidad   INT NOT NULL DEFAULT 10,
    activa      BIT NOT NULL DEFAULT 1,
    PRIMARY KEY(id),
    CONSTRAINT fk_areas__conjuntos FOREIGN KEY (conjunto_id) REFERENCES db_ph.conjuntos (id)
);

-- ============================================================
-- 8. RESERVAS
--    Reservas de áreas comunes por parte de propietarios.
-- ============================================================
CREATE TABLE db_ph.reservas (
    id             INT NOT NULL AUTO_INCREMENT,
    area_id        INT NOT NULL,
    propietario_id INT NOT NULL,
    fecha          DATE NOT NULL,
    hora_inicio    TIME NOT NULL,
    hora_fin       TIME NOT NULL,
    estado         VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    PRIMARY KEY(id),
    CONSTRAINT fk_reservas__areas FOREIGN KEY (area_id)        REFERENCES db_ph.areas_comunes (id),
    CONSTRAINT fk_reservas__prop  FOREIGN KEY (propietario_id) REFERENCES db_ph.propietarios (id)
);

-- ============================================================
-- 9. ASAMBLEAS
--    Reuniones ordinarias y extraordinarias del conjunto.
-- ============================================================
CREATE TABLE db_ph.asambleas (
    id             INT NOT NULL AUTO_INCREMENT,
    conjunto_id    INT NOT NULL,
    fecha_hora     DATETIME NOT NULL,
    tipo           VARCHAR(50) NOT NULL DEFAULT 'ordinaria',
    lugar          VARCHAR(200) NOT NULL,
    orden_del_dia  TEXT,
    PRIMARY KEY(id),
    CONSTRAINT fk_asambleas__conjuntos FOREIGN KEY (conjunto_id) REFERENCES db_ph.conjuntos (id)
);

-- ============================================================
-- 10. ASISTENCIAS
--     Registro de asistencia de propietarios a asambleas.
-- ============================================================
CREATE TABLE db_ph.asistencias (
    id             INT NOT NULL AUTO_INCREMENT,
    asamblea_id    INT NOT NULL,
    propietario_id INT NOT NULL,
    hora_llegada   DATETIME NOT NULL DEFAULT NOW(),
    voto_ejercido  BIT NOT NULL DEFAULT 0,
    PRIMARY KEY(id),
    CONSTRAINT fk_asist__asambleas FOREIGN KEY (asamblea_id)    REFERENCES db_ph.asambleas (id),
    CONSTRAINT fk_asist__prop      FOREIGN KEY (propietario_id) REFERENCES db_ph.propietarios (id)
);

-- ============================================================
-- 11. EMPLEADOS
--     Personal del conjunto (porteros, vigilantes, aseo, etc.).
-- ============================================================
CREATE TABLE db_ph.empleados (
    id            INT NOT NULL AUTO_INCREMENT,
    conjunto_id   INT NOT NULL,
    cedula        VARCHAR(20) NOT NULL UNIQUE,
    nombre        VARCHAR(200) NOT NULL,
    cargo         VARCHAR(100) NOT NULL,
    salario       DECIMAL(12,2) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    activo        BIT NOT NULL DEFAULT 1,
    PRIMARY KEY(id),
    CONSTRAINT fk_emp__conjuntos FOREIGN KEY (conjunto_id) REFERENCES db_ph.conjuntos (id)
);

-- ============================================================
-- 12. NOVEDADES
--     Incidentes o novedades reportadas por empleados.
-- ============================================================
CREATE TABLE db_ph.novedades (
    id          INT NOT NULL AUTO_INCREMENT,
    empleado_id INT NOT NULL,
    tipo        VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha       DATE NOT NULL DEFAULT (CURDATE()),
    PRIMARY KEY(id),
    CONSTRAINT fk_nov__empleados FOREIGN KEY (empleado_id) REFERENCES db_ph.empleados (id)
);

-- ============================================================
-- 13. PROVEEDORES
--     Empresas que prestan servicios al conjunto.
-- ============================================================
CREATE TABLE db_ph.proveedores (
    id          INT NOT NULL AUTO_INCREMENT,
    conjunto_id INT NOT NULL,
    nit         VARCHAR(20) NOT NULL,
    nombre      VARCHAR(200) NOT NULL,
    servicio    VARCHAR(150) NOT NULL,
    contacto    VARCHAR(200),
    telefono    VARCHAR(20),
    PRIMARY KEY(id),
    CONSTRAINT fk_prov__conjuntos FOREIGN KEY (conjunto_id) REFERENCES db_ph.conjuntos (id)
);

-- ============================================================
-- 14. CONTRATOS
--     Contratos firmados con proveedores.
-- ============================================================
CREATE TABLE db_ph.contratos (
    id              INT NOT NULL AUTO_INCREMENT,
    proveedor_id    INT NOT NULL,
    fecha_inicio    DATE NOT NULL,
    fecha_fin       DATE,
    valor_mensual   DECIMAL(12,2) NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'activo',
    PRIMARY KEY(id),
    CONSTRAINT fk_contratos__prov FOREIGN KEY (proveedor_id) REFERENCES db_ph.proveedores (id)
);

-- ============================================================
-- 15. VEHICULOS
--     Vehículos registrados por propietario (parqueaderos).
-- ============================================================
CREATE TABLE db_ph.vehiculos (
    id             INT NOT NULL AUTO_INCREMENT,
    propietario_id INT NOT NULL,
    placa          VARCHAR(10) NOT NULL UNIQUE,
    tipo           VARCHAR(50) NOT NULL DEFAULT 'carro',
    marca          VARCHAR(100),
    modelo         VARCHAR(50),
    PRIMARY KEY(id),
    CONSTRAINT fk_veh__prop FOREIGN KEY (propietario_id) REFERENCES db_ph.propietarios (id)
);

-- ============================================================
-- STORED PROCEDURE: Seleccionar todos los propietarios
-- ============================================================
DELIMITER $$
CREATE PROCEDURE db_ph.proc_select_propietarios()
BEGIN
    SELECT * FROM db_ph.propietarios;
END$$
DELIMITER ;

-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================
INSERT INTO db_ph.conjuntos (nombre, nit, direccion, ciudad, telefono)
VALUES ('Conjunto Residencial Los Pinos', '900123456-1', 'Calle 45 # 23-10', 'Medellín', '6041234567');

INSERT INTO db_ph.torres (conjunto_id, nombre, total_pisos)
VALUES (1, 'Torre A', 10), (1, 'Torre B', 10);

INSERT INTO db_ph.apartamentos (torre_id, numero, piso, area_m2, tipo)
VALUES (1, '101', 1, 65.5, 'residencial'),
       (1, '201', 2, 65.5, 'residencial'),
       (2, '101', 1, 72.0, 'residencial');

INSERT INTO db_ph.propietarios (apartamento_id, cedula, nombre, telefono, email)
VALUES (1, '1020304050', 'Carlos Gómez',  '3001234567', 'carlos@email.com'),
       (2, '2030405060', 'Ana Martínez',  '3009876543', 'ana@email.com'),
       (3, '3040506070', 'Luis Rodríguez','3005551234', 'luis@email.com');

INSERT INTO db_ph.cuotas (apartamento_id, propietario_id, tipo, valor, fecha_vencimiento, pagada)
VALUES (1, 1, 'ordinaria', 350000.00, '2026-04-30', 0),
       (2, 2, 'ordinaria', 350000.00, '2026-04-30', 1),
       (3, 3, 'ordinaria', 380000.00, '2026-04-30', 0);