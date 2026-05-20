# ============================================================
# Sistema de Administración de Propiedad Horizontal
# Versión 2 - API REST
# ------------------------------------------------------------
# Mejoras sobre la versión 1 (rama main):
#   - Exposición de datos via API REST con Flask
#   - Autenticación segura con tokens JWT (HS512)
#   - Token enviado en el Header Authorization
#   - Endpoints para las 4 operaciones CRUD
#   - Endpoint adicional via Stored Procedure
#   - Clase Autenticacion separada
#   - Método ToDict() para serialización JSON
#   - Validación centralizada de entrada y token
#
# GitHub: https://github.com/andreslav-sys/PropiedadHorizontal
# Rama:   v2-api
#
# Paquetes requeridos:
#   py -m pip install pyodbc
#   py -m pip install Flask
#   py -m pip install PyJWT
#
# Ejecutar:
#   py main.py
#
# Endpoints:
#   GET    /api/token
#   GET    /api/propietarios
#   GET    /api/propietarios/sp
#   POST   /api/propietarios
#   PUT    /api/propietarios
#   DELETE /api/propietarios
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
# ============================================================
class Conexion:

    strConnection: str = "Driver={MySQL ODBC 9.6 Unicode Driver};Server=localhost;Database=db_ph;PORT=3306;user=user_python;password=Csfg6283427834;";

    # ----------------------------------------------------------
    # SELECT - Retorna lista de objetos Propietarios
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

    # ----------------------------------------------------------
    # SELECT - Via stored procedure
    # ----------------------------------------------------------
    def SelectProcedimiento(self) -> list:
        conexion = pyodbc.connect(self.strConnection);
        cursor   = conexion.cursor();
        cursor.execute("{CALL proc_select_propietarios();}");

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

    # ----------------------------------------------------------
    # INSERT
    # ----------------------------------------------------------
    def Insert(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "INSERT INTO propietarios (apartamento_id, cedula, nombre, telefono, email, fecha_registro) VALUES (?, ?, ?, ?, ?, ?)",
                (entidad.apartamento_id,
                 entidad.cedula,
                 entidad.nombre,
                 entidad.telefono,
                 entidad.email,
                 entidad.fecha_registro));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    # ----------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------
    def Update(self, entidad: Propietarios) -> bool:
        try:
            conexion = pyodbc.connect(self.strConnection);
            cursor   = conexion.cursor();
            cursor.execute(
                "UPDATE propietarios SET apartamento_id=?, cedula=?, nombre=?, telefono=?, email=? WHERE id=?",
                (entidad.apartamento_id,
                 entidad.cedula,
                 entidad.nombre,
                 entidad.telefono,
                 entidad.email,
                 entidad.id));
            conexion.commit();
            cursor.close();
            conexion.close();
            return True;
        except:
            return False;

    # ----------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------
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
# Lee el token desde el Header "Authorization" y lo valida.
# Retorna (data, error) — si hay error, data es None.
# ============================================================
def ValidarEntrada() -> tuple:
    respuesta: dict = {};

    # Leemos el token del header Authorization
    token = flask.request.headers.get("Authorization");

    if not token:
        respuesta["Error"]     = "NoAuthentication";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);

    if not auth.ValidarToken(token):
        respuesta["Error"]     = "TokenInvalido";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);

    # Leemos el body JSON si existe
    try:
        data = flask.request.get_json(silent=True) or {};
    except:
        data = {};

    return data, None;


# ============================================================
# ENDPOINTS DE LA API
# ============================================================

# ----------------------------------------------------------
# GET /api/token
# ----------------------------------------------------------
# Genera y devuelve un token JWT.
# No requiere autenticación.
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# GET /api/propietarios
# ----------------------------------------------------------
# Retorna todos los propietarios.
# Header requerido: Authorization: <token>
# ----------------------------------------------------------
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
        respuesta["Respuesta"] = "OK";
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);


# ----------------------------------------------------------
# GET /api/propietarios/sp
# ----------------------------------------------------------
# Retorna propietarios via stored procedure.
# Header requerido: Authorization: <token>
# ----------------------------------------------------------
@app.route("/api/propietarios/sp", methods=["GET"])
def ObtenerPropietariosSP() -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada();
        if error:
            return error;

        lista           = db.SelectProcedimiento();
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


# ----------------------------------------------------------
# POST /api/propietarios
# ----------------------------------------------------------
# Inserta un nuevo propietario.
# Header requerido: Authorization: <token>
# Body JSON:
#   {
#     "apartamento_id": 1,
#     "cedula": "123456",
#     "nombre": "Juan Perez",
#     "telefono": "3001234567",
#     "email": "juan@email.com"
#   }
# ----------------------------------------------------------
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
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);


# ----------------------------------------------------------
# PUT /api/propietarios
# ----------------------------------------------------------
# Actualiza un propietario existente.
# Header requerido: Authorization: <token>
# Body JSON:
#   {
#     "id": 1,
#     "apartamento_id": 1,
#     "cedula": "123456",
#     "nombre": "Nuevo Nombre",
#     "telefono": "3009999999",
#     "email": "nuevo@email.com"
#   }
# ----------------------------------------------------------
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
        respuesta["Fecha"]     = str(datetime.datetime.now());
        return flask.jsonify(respuesta);
    except:
        respuesta["Respuesta"] = "ERROR";
        respuesta["Mensaje"]   = str(sys.exc_info());
        return flask.jsonify(respuesta);


# ----------------------------------------------------------
# DELETE /api/propietarios
# ----------------------------------------------------------
# Elimina un propietario por id.
# Header requerido: Authorization: <token>
# Body JSON:
#   {
#     "id": 5
#   }
# ----------------------------------------------------------
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
print("  Versión 2 - API REST + JWT");
print("  GitHub: github.com/andreslav-sys/PropiedadHorizontal");
print("  Rama: v2-api");
print("=" * 55);
print(f"  Servidor en http://{HOST}:{PORT}");
print("=" * 55);

app.run(HOST, PORT);