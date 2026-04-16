import datetime;
import decimal;
import pyodbc;

# ============================================================
# Clase Propietarios
# ------------------------------------------------------------
# Molde que representa a un propietario dentro del sistema.
# Cada campo corresponde a una columna de la tabla propietarios.
# ============================================================
class Propietarios:
    id:               int      = 0;
    apartamento_id:   int      = 0;
    cedula:           str      = "";
    nombre:           str      = "";
    telefono:         str      = "";
    email:            str      = "";
    fecha_registro:   datetime = datetime.datetime.now();


# ============================================================
# Clase Cuotas
# ------------------------------------------------------------
# Molde que representa una cuota de administración.
# Cada cuota pertenece a un apartamento y a un propietario.
# ============================================================
class Cuotas:
    id:                int      = 0;
    apartamento_id:    int      = 0;
    propietario_id:    int      = 0;
    tipo:              str      = "ordinaria";
    valor:             decimal  = 0.0;
    fecha_vencimiento: datetime = datetime.datetime.now();
    pagada:            bool     = False;

    # Podemos guardar el objeto completo del propietario relacionado
    _propietario: Propietarios = None;


# ============================================================
# Clase Conexion
# ------------------------------------------------------------
# Encargada de toda la comunicación con la base de datos.
# Contiene métodos para cada operación: SELECT, INSERT,
# UPDATE y DELETE sobre la tabla de propietarios.
# ============================================================
class Conexion:

    # "Pasaporte" para entrar a la base de datos
    strConnection: str = """
        Driver={MySQL ODBC 9.0 Unicode Driver};
        Server=localhost;
        Database=db_ph;
        PORT=3306;
        user=user_python;
        password=Csfg6283427834;""";

    # ----------------------------------------------------------
    # SELECT - Basica
    # ----------------------------------------------------------
    # Consulta todos los propietarios y los muestra en pantalla
    # tal cual como vienen de la base de datos (filas crudas).
    # ----------------------------------------------------------
    def SelectBasico(self) -> None:
        conexion = pyodbc.connect(self.strConnection);

        consulta: str = "SELECT * FROM propietarios";
        cursor = conexion.cursor();
        cursor.execute(consulta);

        print("\n--- Propietarios (filas crudas) ---");
        for elemento in cursor:
            print(elemento);

        cursor.close();
        conexion.close();

    # ----------------------------------------------------------
    # SELECT - Lista de objetos
    # ----------------------------------------------------------
    # Consulta todos los propietarios y los convierte en una
    # lista de objetos Propietarios para usar en el programa.
    # Es más útil que SelectBasico() porque permite acceder
    # a cada campo por su nombre (ej: p.nombre, p.email).
    # ----------------------------------------------------------
    def SelectLista(self) -> list:
        conexion = pyodbc.connect(self.strConnection);

        consulta: str = "SELECT * FROM propietarios";
        cursor = conexion.cursor();
        cursor.execute(consulta);

        lista: list = [];
        for elemento in cursor:
            # Creamos una ficha vacía y la llenamos campo por campo
            entidad                  = Propietarios();
            entidad.id               = elemento[0];
            entidad.apartamento_id   = elemento[1];
            entidad.cedula           = elemento[2];
            entidad.nombre           = elemento[3];
            entidad.telefono         = elemento[4];
            entidad.email            = elemento[5];
            entidad.fecha_registro   = elemento[6];
            lista.append(entidad);  # Agregamos a la lista

        cursor.close();
        conexion.close();
        return lista;

    # ----------------------------------------------------------
    # SELECT - Via stored procedure
    # ----------------------------------------------------------
    # Llama al procedimiento almacenado que ya está guardado
    # en MySQL. Hace lo mismo que SelectBasico() pero usando
    # una función definida directamente en la base de datos.
    # ----------------------------------------------------------
    def SelectProcedimiento(self) -> None:
        conexion = pyodbc.connect(self.strConnection);

        consulta: str = "{CALL proc_select_propietarios();}";
        cursor = conexion.cursor();
        cursor.execute(consulta);

        print("\n--- Propietarios (via stored procedure) ---");
        for elemento in cursor:
            print(elemento);

        cursor.close();
        conexion.close();

    # ----------------------------------------------------------
    # INSERT - Agregar propietario
    # ----------------------------------------------------------
    # Recibe un objeto Propietarios con todos sus datos y lo
    # guarda como un nuevo registro en la base de datos.
    # Los "?" evitan que alguien pueda inyectar código SQL
    # malicioso (buena práctica de seguridad).
    # Retorna True si todo salió bien, False si hubo error.
    # ----------------------------------------------------------
    def Insert(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);

            consulta: str = """
                INSERT INTO propietarios
                    (apartamento_id, cedula, nombre, telefono, email, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?)""";
            cursor = conexion.cursor();
            cursor.execute(consulta, (
                entidad.apartamento_id,
                entidad.cedula,
                entidad.nombre,
                entidad.telefono,
                entidad.email,
                entidad.fecha_registro
            ));

            # commit() confirma los cambios en la BD.
            # Sin esto el INSERT no queda guardado.
            conexion.commit();

            cursor.close();
            conexion.close();
            print("✔ Propietario insertado correctamente.");
            return True;

        except Exception as e:
            print("✘ Error al insertar propietario: " + str(e));
            return False;

    # ----------------------------------------------------------
    # UPDATE - Actualizar propietario
    # ----------------------------------------------------------
    # Recibe un objeto Propietarios con los datos ya modificados
    # y actualiza el registro en la BD buscándolo por su id.
    # Solo se cambian los campos que se envían en el objeto.
    # El "WHERE id=?" garantiza que solo se modifique ESE registro.
    # ----------------------------------------------------------
    def Update(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);

            consulta: str = """
                UPDATE propietarios
                SET apartamento_id=?,
                    cedula=?,
                    nombre=?,
                    telefono=?,
                    email=?
                WHERE id=?""";
            cursor = conexion.cursor();
            cursor.execute(consulta, (
                entidad.apartamento_id,
                entidad.cedula,
                entidad.nombre,
                entidad.telefono,
                entidad.email,
                entidad.id       # El id va al final porque es el del WHERE
            ));
            conexion.commit();

            cursor.close();
            conexion.close();
            print("✔ Propietario actualizado correctamente.");
            return True;

        except Exception as e:
            print("✘ Error al actualizar propietario: " + str(e));
            return False;

    # ----------------------------------------------------------
    # DELETE - Eliminar propietario
    # ----------------------------------------------------------
    # Recibe el id del propietario que se quiere eliminar.
    # El "WHERE id=?" protege de borrar toda la tabla.
    # La coma en (id,) es requerida por Python para que lo
    # interprete como una tupla y no como un número simple.
    # ----------------------------------------------------------
    def Delete(self, id: int) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);

            consulta: str = "DELETE FROM propietarios WHERE id=?";
            cursor = conexion.cursor();
            cursor.execute(consulta, (id,));
            conexion.commit();

            cursor.close();
            conexion.close();
            print("✔ Propietario eliminado correctamente.");
            return True;

        except Exception as e:
            print("✘ Error al eliminar propietario: " + str(e));
            return False;


# ============================================================
# PROGRAMA PRINCIPAL
# ------------------------------------------------------------
# Aquí probamos cada una de las 4 operaciones del CRUD.
# ============================================================
print("Sistema de Administración de Propiedad Horizontal");
print("=" * 52);

# Creamos el objeto de conexión (nuestro asistente para la BD)
conexion: Conexion = Conexion();


# ============================================================
# 1. INSERT - Agregar un nuevo propietario
# ============================================================
print("\n[1] INSERT - Agregando nuevo propietario...");

nuevo: Propietarios         = Propietarios();
nuevo.apartamento_id        = 1;
nuevo.cedula                = "9988776655";
nuevo.nombre                = "María Fernanda López";
nuevo.telefono              = "3112223344";
nuevo.email                 = "mfernanda@email.com";
nuevo.fecha_registro        = datetime.datetime.now();

conexion.Insert(nuevo);


# ============================================================
# 2. SELECT - Ver todos los propietarios
# ============================================================
print("\n[2] SELECT - Lista de propietarios:");
lista = conexion.SelectLista();
for p in lista:
    # Accedemos a cada campo del objeto por su nombre
    print("  " + str(p.id) + " | " + p.cedula + " | " + p.nombre + " | " + p.email);


# ============================================================
# 3. UPDATE - Modificar datos de un propietario
# ============================================================
print("\n[3] UPDATE - Actualizando propietario con id=1...");

# Primero buscamos el propietario que queremos cambiar
modificar: Propietarios = Propietarios();
modificar.id               = 1;             # <-- El que queremos cambiar
modificar.apartamento_id   = 1;
modificar.cedula           = "1020304050";
modificar.nombre           = "Carlos Gómez Actualizado";
modificar.telefono         = "3001111111";
modificar.email            = "carlos.nuevo@email.com";

conexion.Update(modificar);


# ============================================================
# 4. SELECT - Ver propietarios después del UPDATE
# ============================================================
print("\n[4] SELECT - Lista actualizada:");
lista = conexion.SelectLista();
for p in lista:
    print("  " + str(p.id) + " | " + p.cedula + " | " + p.nombre + " | " + p.email);


# ============================================================
# 5. DELETE - Eliminar el propietario que insertamos
# ============================================================
print("\n[5] DELETE - Eliminando el propietario recién insertado...");

# Buscamos el id del propietario que acabamos de crear
# (buscamos por cédula para obtener su id real)
lista_actual = conexion.SelectLista();
for p in lista_actual:
    if p.cedula == "9988776655":
        conexion.Delete(p.id);
        break;


# ============================================================
# 6. SELECT FINAL - Verificar estado final de la tabla
# ============================================================
print("\n[6] SELECT FINAL - Estado de la tabla:");
conexion.SelectBasico();

print("\n[7] SELECT via Stored Procedure:");
conexion.SelectProcedimiento();

print("\n" + "=" * 52);
print("Fin del programa.");


"""
-- REFERENCIA RAPIDA --

-- Tablas del sistema (15 en total):
    1.  conjuntos       - Conjuntos residenciales
    2.  torres          - Torres de cada conjunto
    3.  apartamentos    - Apartamentos por torre
    4.  propietarios    - Dueños de cada apartamento
    5.  cuotas          - Cuotas de administración
    6.  pagos           - Pagos de cuotas
    7.  areas_comunes   - Zonas comunes (piscina, salon...)
    8.  reservas        - Reservas de áreas comunes
    9.  asambleas       - Reuniones de copropietarios
    10. asistencias     - Asistencia a asambleas
    11. empleados       - Personal del conjunto
    12. novedades       - Incidentes reportados
    13. proveedores     - Empresas contratadas
    14. contratos       - Contratos con proveedores
    15. vehiculos       - Vehículos registrados

-- Comandos:
    py main.py

-- Instalar paquete:
    py -m pip install pyodbc
"""