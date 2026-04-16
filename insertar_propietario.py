import datetime
import pyodbc

# ============================================================
# Clase Propietarios
# ============================================================
class Propietarios:
    id:               int      = 0
    apartamento_id:   int      = 0
    cedula:           str      = ""
    nombre:           str      = ""
    telefono:         str      = ""
    email:            str      = ""
    fecha_registro:   datetime = datetime.datetime.now()


# ============================================================
# Conexión y operación INSERT
# ============================================================
strConnection: str = """
    Driver={MySQL ODBC 9.0 Unicode Driver};
    Server=localhost;
    Database=db_ph;
    PORT=3306;
    user=user_python;
    password=Csfg6283427834;"""


def insertar_propietario(entidad: Propietarios) -> bool:
    try:
        conexion = pyodbc.connect(strConnection)
        consulta: str = """
            INSERT INTO propietarios
                (apartamento_id, cedula, nombre, telefono, email, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?)"""
        cursor = conexion.cursor()
        cursor.execute(consulta, (
            entidad.apartamento_id,
            entidad.cedula,
            entidad.nombre,
            entidad.telefono,
            entidad.email,
            entidad.fecha_registro
        ))
        conexion.commit()
        cursor.close()
        conexion.close()
        print(f"Propietario '{entidad.nombre}' insertado correctamente.")
        return True
    except Exception as e:
        print("Error al insertar propietario: " + str(e))
        return False


# ============================================================
# Datos del nuevo propietario — edita estos valores
# ============================================================
nuevo = Propietarios()
nuevo.apartamento_id  = 2                           # ID del apartamento asignado
nuevo.cedula          = "5566778899"
nuevo.nombre          = "Jorge Herrera"
nuevo.telefono        = "3204445566"
nuevo.email           = "jorge.herrera@email.com"
nuevo.fecha_registro  = datetime.datetime.now()

insertar_propietario(nuevo)
