# ============================================================
# Sistema de Administración de Propiedad Horizontal
# Versión 2 - API REST
# ------------------------------------------------------------
# Mejoras sobre la versión 1 (rama main):
#   - Exposición de datos via API REST con Flask
#   - Autenticación segura con tokens JWT (HS512)
#   - Encriptación de credenciales en el token
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
#   GET    /api/token/generar
#   GET    /api/propietarios/<json>
#   GET    /api/propietarios/sp/<json>
#   POST   /api/propietarios/<json>
#   PUT    /api/propietarios/<json>
#   DELETE /api/propietarios/<json>
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
KEY_JWT: str = "976457hsdgfst8723643gsfhg";  # Clave secreta para firmar tokens JWT
PORT:    int = 4040;                           # Puerto del servidor
HOST:    str = "localhost";                    # Host del servidor

app = flask.Flask(__name__);


# ============================================================
# CLASE: Propietarios
# ------------------------------------------------------------
# Misma clase de la versión 1, pero ahora incluye ToDict()
# que convierte el objeto a diccionario para enviarlo como JSON
# a través de la API.
# ============================================================
class Propietarios:
    id:              int      = 0;
    apartamento_id:  int      = 0;
    cedula:          str      = "";
    nombre:          str      = "";
    telefono:        str      = "";
    email:           str      = "";
    fecha_registro:  datetime = datetime.datetime.now();

    # NUEVO en v2: convierte el objeto a diccionario JSON
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
# Igual que en la versión 1, maneja todo el acceso a la BD.
# En v2 los métodos retornan listas de objetos en lugar de
# imprimir directamente, para poder enviarlos por la API.
# ============================================================
class Conexion:

    strConnection: str = """
        Driver={MySQL ODBC 9.0 Unicode Driver};
        Server=localhost;
        Database=db_ph;
        PORT=3306;
        user=user_python;
        password=Csfg6283427834;""";

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
            cursor.execute("""
                INSERT INTO propietarios
                    (apartamento_id, cedula, nombre, telefono, email, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?)""",
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
            cursor.execute("""
                UPDATE propietarios
                SET apartamento_id=?, cedula=?, nombre=?, telefono=?, email=?
                WHERE id=?""",
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
# CLASE: Autenticacion  ← NUEVA en v2
# ------------------------------------------------------------
# Encapsula toda la lógica de seguridad JWT.
# jwt.encode() firma el payload con la clave KEY_JWT usando
# el algoritmo HS512 (HMAC-SHA512), generando un token
# encriptado que solo puede validarse con la misma clave.
# ============================================================
class Autenticacion:

    # Genera un token JWT firmado y encriptado con HS512
    def GenerarToken(self) -> str:
        payload = {
            "usuario": "api_ph",
            "sistema": "PropiedadHorizontal",
            "emitido": str(datetime.datetime.now()),
        };
        # jwt.encode firma el payload — nadie puede falsificarlo
        # sin conocer KEY_JWT
        token = jwt.encode(payload, KEY_JWT, algorithm="HS512");
        return token;

    # Valida que el token sea auténtico y no haya sido alterado.
    # Retorna True si es válido, False si fue modificado o es falso.
    def ValidarToken(self, token: str) -> bool:
        try:
            # jwt.decode verifica la firma — si alguien alteró
            # el token, esta línea lanza una excepción
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
# FUNCIÓN AUXILIAR: ValidarEntrada  ← NUEVA en v2
# ------------------------------------------------------------
# Parsea el JSON de entrada y valida el token en un solo lugar.
# Todos los endpoints la reutilizan — evita repetir código.
# ============================================================
def ValidarEntrada(entrada: str) -> tuple:
    respuesta: dict = {};
    try:
        data = json.loads(entrada);
    except:
        respuesta["Error"]     = "JSON invalido";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);

    if "Token" not in data:
        respuesta["Error"]     = "NoAuthentication";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);

    if not auth.ValidarToken(data["Token"]):
        respuesta["Error"]     = "TokenInvalido";
        respuesta["Respuesta"] = "ERROR";
        return None, flask.jsonify(respuesta);

    return data, None;


# ============================================================
# ENDPOINTS DE LA API  ← NUEVOS en v2
# ============================================================

# ----------------------------------------------------------
# GET /api/token/generar
# ----------------------------------------------------------
# Genera y devuelve un token JWT.
# No requiere autenticación — es el punto de entrada.
# Ejemplo: GET http://localhost:4040/api/token/generar
# ----------------------------------------------------------
@app.route("/api/token/<string:entrada>", methods=["GET"])
def ObtenerToken(entrada: str) -> str:
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
# GET /api/propietarios/<json>
# ----------------------------------------------------------
# Retorna todos los propietarios.
# Requiere Token válido en el JSON de entrada.
# Ejemplo: GET http://localhost:4040/api/propietarios/{"Token":"..."}
# ----------------------------------------------------------
@app.route("/api/propietarios/<string:entrada>", methods=["GET"])
def ObtenerPropietarios(entrada: str) -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada(entrada);
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
# GET /api/propietarios/sp/<json>
# ----------------------------------------------------------
# Igual pero usando el stored procedure de MySQL.
# ----------------------------------------------------------
@app.route("/api/propietarios/sp/<string:entrada>", methods=["GET"])
def ObtenerPropietariosSP(entrada: str) -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada(entrada);
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
# POST /api/propietarios/<json>
# ----------------------------------------------------------
# Inserta un nuevo propietario.
# Body esperado:
#   {"Token":"...","apartamento_id":1,"cedula":"123",
#    "nombre":"Juan","telefono":"300...","email":"j@mail.com"}
# ----------------------------------------------------------
@app.route("/api/propietarios/<string:entrada>", methods=["POST"])
def InsertarPropietario(entrada: str) -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada(entrada);
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
# PUT /api/propietarios/<json>
# ----------------------------------------------------------
# Actualiza un propietario existente.
# Body esperado:
#   {"Token":"...","id":1,"apartamento_id":1,"cedula":"123",
#    "nombre":"Nuevo Nombre","telefono":"300...","email":"..."}
# ----------------------------------------------------------
@app.route("/api/propietarios/<string:entrada>", methods=["PUT"])
def ActualizarPropietario(entrada: str) -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada(entrada);
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
# DELETE /api/propietarios/<json>
# ----------------------------------------------------------
# Elimina un propietario por id.
# Body esperado: {"Token":"...","id":5}
# ----------------------------------------------------------
@app.route("/api/propietarios/<string:entrada>", methods=["DELETE"])
def EliminarPropietario(entrada: str) -> str:
    respuesta: dict = {};
    try:
        data, error = ValidarEntrada(entrada);
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
