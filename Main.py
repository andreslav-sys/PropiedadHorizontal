import datetime;
import decimal;
import pyodbc;

# ============================================================
# Clase Propietarios
## ============================================================
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
## ============================================================
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
## ============================================================
class Conexion:

    # Para entrar a la base de datos
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
            print("Propietario insertado correctamente.");
            return True;

        except Exception as e:
            print("Error al insertar propietario: " + str(e));
            return False;

    # ----------------------------------------------------------
    # UPDATE - Actualizar propietario
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
            print("Propietario actualizado correctamente.");
            return True;

        except Exception as e:
            print("Error al actualizar propietario: " + str(e));
            return False;

    # ----------------------------------------------------------
    # DELETE - Eliminar propietario
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
            print("Propietario eliminado correctamente.");
            return True;

        except Exception as e:
            print("Error al eliminar propietario: " + str(e));
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

