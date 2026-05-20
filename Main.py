
#   PUT    /api/propietarios/sp
#   DELETE /api/propietarios/sp
#
# Autenticación:
#   Todos los endpoints (excepto /api/token) requieren
#   el header: Authorization: <token>
# ============================================================

import pyodbc;
import flask;
import json;
import sys;
import datetime;
import jwt;


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================
KEY_JWT: str = "976457hsdgfst8723643gsfhg";
PORT:    int = 4040;
HOST:    str = "localhost";

app = flask.Flask(__name__);


# ============================================================
# CLASE: Propietarios
# ============================================================
class Propietarios:
    id:              int      = 0;
    apartamento_id:  int      = 0;
    cedula:          str      = "";
    nombre:          str      = "";
    telefono:        str      = "";
    email:           str      = "";
    fecha_registro:  datetime = datetime.datetime.now();

    # Convierte el objeto a diccionario para enviarlo como JSON
    def ToDict(self) -> dict:
        return {
            "id":             self.id,
            "apartamento_id": self.apartamento_id,
            "cedula":         self.cedula,
            "nombre":         self.nombre,
            "telefono":       self.telefono,
            "email":          self.email,
            "fecha_registro": str(self.fecha_registro),
        };


# ============================================================
# CLASE: Cuotas
# ============================================================
class Cuotas:
    id:                int      = 0;
    apartamento_id:    int      = 0;
    propietario_id:    int      = 0;
    tipo:              str      = "ordinaria";
    valor:             float    = 0.0;
    fecha_vencimiento: datetime = datetime.datetime.now();
    pagada:            bool     = False;
    _propietario: Propietarios  = None;


# ============================================================
# CLASE: Conexion
# ------------------------------------------------------------
# Maneja todo el acceso a la base de datos.
# Tiene dos grupos de métodos:
#   - CRUD directo: SQL escrito en Python
#   - CRUD via SP:  llama stored procedures de MySQL
# ============================================================
class Conexion:

    strConnection: str = "Driver={MySQL ODBC 9.6 Unicode Driver};Server=localhost;Database=db_ph;PORT=3306;user=user_python;password=Csfg6283427834;";

    # ----------------------------------------------------------
    # CRUD DIRECTO
    # ----------------------------------------------------------

    def SelectLista(self) -> list:
        conexion = pyodbc.connect(self.strConnection);
        cursor   = conexion.cursor();
        cursor.execute("SELECT * FROM propietarios");
        lista: list = [];
        for elemento in cursor:
            entidad                = Propietarios();
            entidad.id             = elemento[0];
            entidad.apartamento_id = elemento[1];
            entidad.cedula         = elemento[2];
            entidad.nombre         = elemento[3];
            entidad.telefono       = elemento[4];
            entidad.email          = elemento[5];
            entidad.fecha_registro = elemento[6];
            lista.append(entidad);
        cursor.close();
        conexion.close();
        return lista;

    def Insert(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "INSERT INTO propietarios (apartamento_id, cedula, nombre, telefono, email, fecha_registro) VALUES (?, ?, ?, ?, ?, ?)",
                (entidad.apartamento_id, entidad.cedula, entidad.nombre,
                 entidad.telefono, entidad.email, entidad.fecha_registro));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    def Update(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "UPDATE propietarios SET apartamento_id=?, cedula=?, nombre=?, telefono=?, email=? WHERE id=?",
                (entidad.apartamento_id, entidad.cedula, entidad.nombre,
                 entidad.telefono, entidad.email, entidad.id));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    def Delete(self, id: int) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute("DELETE FROM propietarios WHERE id=?", (id,));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    # ----------------------------------------------------------
    # CRUD VIA STORED PROCEDURES
    # ----------------------------------------------------------

    # SELECT via stored procedure
    def SpSelectLista(self) -> list:
        conexion = pyodbc.connect(self.strConnection);
        cursor   = conexion.cursor();
        cursor.execute("{CALL proc_select_propietarios()}");
        lista: list = [];
        for elemento in cursor:
            entidad                = Propietarios();
            entidad.id             = elemento[0];
            entidad.apartamento_id = elemento[1];
            entidad.cedula         = elemento[2];
            entidad.nombre         = elemento[3];
            entidad.telefono       = elemento[4];
            entidad.email          = elemento[5];
            entidad.fecha_registro = elemento[6];
            lista.append(entidad);
        cursor.close();
        conexion.close();
        return lista;

    # INSERT via stored procedure
    def SpInsert(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "{CALL proc_insert_propietario(?, ?, ?, ?, ?)}",
                (entidad.apartamento_id, entidad.cedula, entidad.nombre,
                 entidad.telefono, entidad.email));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    # UPDATE via stored procedure
    def SpUpdate(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "{CALL proc_update_propietario(?, ?, ?, ?, ?, ?)}",
                (entidad.id, entidad.apartamento_id, entidad.cedula,
                 entidad.nombre, entidad.telefono, entidad.email));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    # DELETE via stored procedure
    def SpDelete(self, id: int) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute("{CALL proc_delete_propietario(?)}", (id,));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;


# ============================================================
# CLASE: Autenticacion
# ------------------------------------------------------------
# Maneja la generación y validación de tokens JWT.
# El token se firma con algoritmo HS512 (HMAC-SHA512).
# ============================================================
class Autenticacion:

    def GenerarToken(self) -> str:
        payload = {
            "usuario": "api_ph",
            "sistema": "PropiedadHorizontal",
            "emitido": str(datetime.datetime.now()),
        };
        token = jwt.encode(payload, KEY_JWT, algorithm="HS512");
        return token;

    def ValidarToken(self, token: str) -> bool:
        try:
            jwt.decode(token, KEY_JWT, algorithms=["HS512"]);
            return True;
        except:
            return False;


# ============================================================
# INSTANCIAS GLOBALES
# ============================================================
db:   Conexion      = Conexion();
auth: Autenticacion = Autenticacion();


# ============================================================
# FUNCIÓN AUXILIAR: ValidarEntrada
# ------------------------------------------------------------
# Lee el token desde el Header Authorization y lo valida.
# Retorna (data, error).
# ============================================================
def ValidarEntrada() -> tuple:
    respuesta: dict = {};
    token = flask.request.headers.get("Authorization");
    if not token:
        respuesta["Error"]     = "NoAuthentication";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);
    if not auth.ValidarToken(token):
        respuesta["Error"]     = "TokenInvalido";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);
    try:
        data = flask.request.get_json(silent=True) or {};
    except:
        data = {};
    return data, None;


# ============================================================
# ENDPOINTS — CRUD DIRECTO
# ============================================================

# GET /api/token
@app.route("/api/token", methods=["GET"])
def ObtenerToken() -> str:
    respuesta: dict = {};
    try:
        respuesta["Token"]     = auth.GenerarToken();
        respuesta["Respuesta"] = "OK";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# GET /api/propietarios
@app.route("/api/propietarios", methods=["GET"])
def ObtenerPropietarios() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        lista           = db.SelectLista();
        entidades: dict = {};
        for p in lista:
            entidades[str(p.id)] = p.ToDict();
        respuesta["Entidades"] = entidades;
        respuesta["Total"]     = len(lista);
        respuesta["Fuente"]    = "Directo";
        respuesta["Respuesta"] = "OK";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# POST /api/propietarios
# Body: {"apartamento_id":1,"cedula":"123","nombre":"Juan","telefono":"300...","email":"j@mail.com"}
@app.route("/api/propietarios", methods=["POST"])
def InsertarPropietario() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        entidad                = Propietarios();
        entidad.apartamento_id = data.get("apartamento_id", 1);
        entidad.cedula         = data.get("cedula", "");
        entidad.nombre         = data.get("nombre", "");
        entidad.telefono       = data.get("telefono", "");
        entidad.email          = data.get("email", "");
        entidad.fecha_registro = datetime.datetime.now();
        resultado = db.Insert(entidad);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "INSERT";
        respuesta["Fuente"]    = "Directo";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# PUT /api/propietarios
# Body: {"id":1,"apartamento_id":1,"cedula":"123","nombre":"Nuevo","telefono":"300...","email":"..."}
@app.route("/api/propietarios", methods=["PUT"])
def ActualizarPropietario() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        entidad                = Propietarios();
        entidad.id             = data.get("id", 0);
        entidad.apartamento_id = data.get("apartamento_id", 1);
        entidad.cedula         = data.get("cedula", "");
        entidad.nombre         = data.get("nombre", "");
        entidad.telefono       = data.get("telefono", "");
        entidad.email          = data.get("email", "");
        resultado = db.Update(entidad);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "UPDATE";
        respuesta["Fuente"]    = "Directo";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# DELETE /api/propietarios
# Body: {"id":5}
@app.route("/api/propietarios", methods=["DELETE"])
def EliminarPropietario() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        id_eliminar = data.get("id", 0);
        resultado   = db.Delete(id_eliminar);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "DELETE";
        respuesta["Fuente"]    = "Directo";
        respuesta["Id"]        = id_eliminar;
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);


# ============================================================
# ENDPOINTS — VIA STORED PROCEDURES
# ============================================================

# GET /api/propietarios/sp
@app.route("/api/propietarios/sp", methods=["GET"])
def ObtenerPropietariosSP() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        lista           = db.SpSelectLista();
        entidades: dict = {};
        for p in lista:
            entidades[str(p.id)] = p.ToDict();
        respuesta["Entidades"] = entidades;
        respuesta["Total"]     = len(lista);
        respuesta["Fuente"]    = "StoredProcedure";
        respuesta["Respuesta"] = "OK";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# POST /api/propietarios/sp
# Body: {"apartamento_id":1,"cedula":"123","nombre":"Juan","telefono":"300...","email":"j@mail.com"}
@app.route("/api/propietarios/sp", methods=["POST"])
def InsertarPropietarioSP() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        entidad                = Propietarios();
        entidad.apartamento_id = data.get("apartamento_id", 1);
        entidad.cedula         = data.get("cedula", "");
        entidad.nombre         = data.get("nombre", "");
        entidad.telefono       = data.get("telefono", "");
        entidad.email          = data.get("email", "");
        resultado = db.SpInsert(entidad);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "INSERT";
        respuesta["Fuente"]    = "StoredProcedure";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# PUT /api/propietarios/sp
# Body: {"id":1,"apartamento_id":1,"cedula":"123","nombre":"Nuevo","telefono":"300...","email":"..."}
@app.route("/api/propietarios/sp", methods=["PUT"])
def ActualizarPropietarioSP() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        entidad                = Propietarios();
        entidad.id             = data.get("id", 0);
        entidad.apartamento_id = data.get("apartamento_id", 1);
        entidad.cedula         = data.get("cedula", "");
        entidad.nombre         = data.get("nombre", "");
        entidad.telefono       = data.get("telefono", "");
        entidad.email          = data.get("email", "");
        resultado = db.SpUpdate(entidad);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "UPDATE";
        respuesta["Fuente"]    = "StoredProcedure";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);

# DELETE /api/propietarios/sp
# Body: {"id":5}
@app.route("/api/propietarios/sp", methods=["DELETE"])
def EliminarPropietarioSP() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;
        id_eliminar = data.get("id", 0);
        resultado   = db.SpDelete(id_eliminar);
        respuesta["Respuesta"] = "OK" if resultado else "ERROR";
        respuesta["Accion"]    = "DELETE";
        respuesta["Fuente"]    = "StoredProcedure";
        respuesta["Id"]        = id_eliminar;
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);


# ============================================================
# INICIO DEL SERVIDOR
# ============================================================
print("=" * 55);
print("  Sistema de Administración de Propiedad Horizontal");
print("  Versión 2 - API REST + JWT + Stored Procedures");
print("  GitHub: github.com/andreslav-sys/PropiedadHorizontal");
print("  Rama: v2-api");
print("=" * 55);
print(f"  Servidor en http://{HOST}:{PORT}");
print("  Endpoints CRUD directo: /api/propietarios");
print("  Endpoints via SP:       /api/propietarios/sp");
print("=" * 55);

app.run(HOST, PORT);
