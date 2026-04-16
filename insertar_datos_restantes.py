import datetime
import pyodbc

strConnection: str = """
    Driver={MySQL ODBC 9.6 Unicode Driver};
    Server=localhost;
    Database=db_ph;
    PORT=3306;
    user=user_python;
    password=Csfg6283427834;"""


def ejecutar(cursor, tabla: str, consulta: str, filas: list) -> None:
    for fila in filas:
        cursor.execute(consulta, fila)
    print(f"  OK  {tabla} ({len(filas)} registros)")


conexion = pyodbc.connect(strConnection)
cursor   = conexion.cursor()

print("Insertando datos en las tablas restantes...\n")

# ============================================================
# 1. PAGOS  (cuota_id: 2 ya estaba pagada, registramos su pago)
# ============================================================
ejecutar(cursor, "pagos",
    "INSERT INTO pagos (cuota_id, valor_pagado, fecha_pago, metodo, comprobante) VALUES (?,?,?,?,?)",
    [
        (2, 350000.00, datetime.datetime(2026, 4, 10, 9, 30), 'transferencia', 'COMP-2026-001'),
        (1, 350000.00, datetime.datetime(2026, 4, 14, 11, 0), 'efectivo',      'COMP-2026-002'),
    ]
)

# ============================================================
# 2. AREAS COMUNES  (conjunto_id=1)
# ============================================================
ejecutar(cursor, "areas_comunes",
    "INSERT INTO areas_comunes (conjunto_id, nombre, descripcion, capacidad, activa) VALUES (?,?,?,?,?)",
    [
        (1, 'Salon Social',  'Salon para eventos y reuniones',        50, True),
        (1, 'Piscina',       'Piscina con carril de natacion',        30, True),
        (1, 'Gimnasio',      'Equipos de cardio y pesas',             15, True),
        (1, 'Parque Infantil','Zona de juegos para ninos',            20, True),
    ]
)

# ============================================================
# 3. RESERVAS  (area_id 1-4, propietario_id 1-3)
# ============================================================
ejecutar(cursor, "reservas",
    "INSERT INTO reservas (area_id, propietario_id, fecha, hora_inicio, hora_fin, estado) VALUES (?,?,?,?,?,?)",
    [
        (1, 1, datetime.date(2026, 4, 20), datetime.time(14, 0), datetime.time(18, 0), 'aprobada'),
        (2, 2, datetime.date(2026, 4, 21), datetime.time(10, 0), datetime.time(12, 0), 'pendiente'),
        (3, 3, datetime.date(2026, 4, 22), datetime.time(7,  0), datetime.time(8,  0), 'aprobada'),
        (1, 2, datetime.date(2026, 4, 25), datetime.time(18, 0), datetime.time(22, 0), 'pendiente'),
    ]
)

# ============================================================
# 4. ASAMBLEAS  (conjunto_id=1)
# ============================================================
ejecutar(cursor, "asambleas",
    "INSERT INTO asambleas (conjunto_id, fecha_hora, tipo, lugar, orden_del_dia) VALUES (?,?,?,?,?)",
    [
        (1, datetime.datetime(2026, 3, 15, 9, 0),  'ordinaria',
         'Salon Social Torre A',
         '1. Aprobacion de presupuesto 2026\n2. Informe de cartera\n3. Proposiciones y varios'),
        (1, datetime.datetime(2026, 4, 5, 18, 0), 'extraordinaria',
         'Salon Social Torre A',
         '1. Reparacion cubierta Torre B\n2. Contratacion empresa de aseo'),
    ]
)

# ============================================================
# 5. ASISTENCIAS  (asamblea_id 1-2, propietario_id 1-3)
# ============================================================
ejecutar(cursor, "asistencias",
    "INSERT INTO asistencias (asamblea_id, propietario_id, hora_llegada, voto_ejercido) VALUES (?,?,?,?)",
    [
        (1, 1, datetime.datetime(2026, 3, 15, 9,  5), True),
        (1, 2, datetime.datetime(2026, 3, 15, 9, 10), True),
        (1, 3, datetime.datetime(2026, 3, 15, 9, 20), False),
        (2, 1, datetime.datetime(2026, 4,  5, 18, 2), True),
        (2, 2, datetime.datetime(2026, 4,  5, 18, 8), True),
    ]
)

# ============================================================
# 6. EMPLEADOS  (conjunto_id=1)
# ============================================================
ejecutar(cursor, "empleados",
    "INSERT INTO empleados (conjunto_id, cedula, nombre, cargo, salario, fecha_ingreso, activo) VALUES (?,?,?,?,?,?,?)",
    [
        (1, '7788990011', 'Pedro Castillo',   'Portero',          1500000.00, datetime.date(2023, 1, 15), True),
        (1, '8899001122', 'Rosa Jimenez',     'Servicios Generales', 1300000.00, datetime.date(2022, 6, 1),  True),
        (1, '9900112233', 'Manuel Rios',      'Vigilante',        1600000.00, datetime.date(2024, 3, 10), True),
        (1, '1122334455', 'Gloria Vargas',    'Administradora',   2800000.00, datetime.date(2021, 8, 20), True),
    ]
)

# ============================================================
# 7. NOVEDADES  (empleado_id 1-4)
# ============================================================
ejecutar(cursor, "novedades",
    "INSERT INTO novedades (empleado_id, tipo, descripcion, fecha) VALUES (?,?,?,?)",
    [
        (1, 'Visitante',     'Ingreso de tecnico de mantenimiento ascensor', datetime.date(2026, 4, 10)),
        (3, 'Incidente',     'Motocicleta sin registro intentó ingresar al parqueadero', datetime.date(2026, 4, 11)),
        (2, 'Mantenimiento', 'Limpieza de zonas comunes completada', datetime.date(2026, 4, 13)),
        (1, 'Paquete',       'Recepcion de paquete para apartamento 201 Torre A', datetime.date(2026, 4, 14)),
    ]
)

# ============================================================
# 8. PROVEEDORES  (conjunto_id=1)
# ============================================================
ejecutar(cursor, "proveedores",
    "INSERT INTO proveedores (conjunto_id, nit, nombre, servicio, contacto, telefono) VALUES (?,?,?,?,?,?)",
    [
        (1, '800111222-1', 'Limpiezas S.A.',        'Aseo y limpieza',         'Juan Mora',    '6042223333'),
        (1, '800333444-2', 'Seguridad Total Ltda.',  'Vigilancia',             'Sandra Ruiz',  '6044445555'),
        (1, '900555666-3', 'TecnoAscensores S.A.S.', 'Mantenimiento ascensores','Andres Gil',  '3006667777'),
        (1, '800777888-4', 'JardinArte',             'Jardineria y zonas verdes','Paula Soto', '3118889999'),
    ]
)

# ============================================================
# 9. CONTRATOS  (proveedor_id 1-4)
# ============================================================
ejecutar(cursor, "contratos",
    "INSERT INTO contratos (proveedor_id, fecha_inicio, fecha_fin, valor_mensual, estado) VALUES (?,?,?,?,?)",
    [
        (1, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31), 1200000.00, 'activo'),
        (2, datetime.date(2026, 1, 1), datetime.date(2026, 12, 31), 2500000.00, 'activo'),
        (3, datetime.date(2025, 7, 1), datetime.date(2026, 6,  30), 800000.00,  'activo'),
        (4, datetime.date(2026, 3, 1), None,                         450000.00,  'activo'),
    ]
)

# ============================================================
# 10. VEHICULOS  (propietario_id 1-3)
# ============================================================
ejecutar(cursor, "vehiculos",
    "INSERT INTO vehiculos (propietario_id, placa, tipo, marca, modelo) VALUES (?,?,?,?,?)",
    [
        (1, 'ABC123', 'carro',  'Chevrolet', '2020'),
        (1, 'MTO456', 'moto',   'Honda',     '2022'),
        (2, 'DEF789', 'carro',  'Renault',   '2019'),
        (3, 'GHI012', 'carro',  'Mazda',     '2021'),
        (3, 'JKL345', 'moto',   'Yamaha',    '2023'),
    ]
)

conexion.commit()
cursor.close()
conexion.close()
print("\nTodos los datos insertados correctamente.")
