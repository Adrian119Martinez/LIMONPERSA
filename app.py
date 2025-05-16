import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

import bleach
import jwt
from flask import Flask, request, jsonify, session
from pymongo import MongoClient

# Importar la configuración de la conexión
from config import MONGO_URI

# Inicializar la conexión a MongoDB usando el URI del archivo de configuración
client = MongoClient(MONGO_URI)
db = client['LimonPersa-Proyect']
usuarios = db['usuarios']

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Para manejo de sesiones (opcional)
JWT_SECRET_KEY = secrets.token_hex(32)   # Clave para firmar los JWT

# Decorador para proteger endpoints con JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # El token debe venir en la cabecera Authorization con el formato: "Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({'success': False, 'message': 'Token no proporcionado'}), 401

        try:
            # Decodificar y validar el token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            # Verificar que el usuario existe en la base de datos
            current_user = usuarios.find_one({"email": data["email"]})
            if not current_user:
                raise Exception("Usuario no encontrado")
        except Exception as e:
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)
    return decorated

# Endpoint de login (sin protección, ya que se utiliza para obtener el token)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'contrasena' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    # Sanitizar las entradas del usuario
    email = bleach.clean(data['email'])
    contrasena = bleach.clean(data['contrasena'])

    # Buscar el usuario en la base de datos
    user = usuarios.find_one({'email': email})

    if user and user.get('contrasena') == contrasena:
        # Generar un token JWT con expiración de 1 hora
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        # Guardar el email en la sesión (opcional)
        session['username'] = email
        
        # Retornamos también el nombre y apellidos del usuario
        return jsonify({
            'success': True,
            'token': token,
            'nombre': user.get('nombre'),
            'apellido_pat': user.get('apellido_pat'),
            'apellido_mat': user.get('apellido_mat'),
            'message': 'Inicio de sesión exitoso'
        })
    else:
        return jsonify({'success': False, 'message': 'Usuario o contraseña inválidos'}), 401
    
# Endpoint para registrar un nuevo usuario (sin protección)
@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    if not data or 'nombre' not in data or 'apellido_pat' not in data or 'apellido_mat' not in data or 'direccion' not in data or 'email' not in data or 'contrasena' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    if usuarios.find_one({'email': data['email']}):
        return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400

    nuevo_usuario = {
        'nombre': bleach.clean(data['nombre']),
        'apellido_pat': bleach.clean(data['apellido_pat']),
        'apellido_mat': bleach.clean(data['apellido_mat']),
        'direccion': bleach.clean(data['direccion']),
        'email': bleach.clean(data['email']),
        'contrasena': bleach.clean(data['contrasena']),
        'fecha_registro': datetime.utcnow(),
        'gestion_cuenta': {
            'tipo': 'estandar',
            'estado': 'activo',
            'fecha_ultima_modificacion': datetime.utcnow()
        }
    }
    result = usuarios.insert_one(nuevo_usuario)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint raíz (protegido)
@app.route('/', methods=['GET'])
@token_required
def home():
    return jsonify({'success': True, 'message': 'Usuario autenticado'})

# Endpoint para listar usuarios (protegido)
@app.route('/usuarios', methods=['GET'])
@token_required
def listar_usuarios():
    all_users = usuarios.find()
    users_list = [
        {
            'nombre': user.get('nombre'),
            'apellido_pat': user.get('apellido_pat'),
            'apellido_mat': user.get('apellido_mat'),
            'email': user.get('email')
        } for user in all_users
    ]
    return jsonify({'success': True, 'usuarios': users_list})

# Endpoint para cerrar sesión (protegido)
@app.route('/logout', methods=['GET'])
@token_required
def logout():
    session.pop('username', None)
    return jsonify({'success': True, 'message': 'Sesión cerrada correctamente'})

if __name__ == '__main__':
    app.run(debug=True)

# Endpoint para listar tratamientos (protegido)
@app.route('/tratamientos', methods=['GET'])
@token_required
def listar_tratamientos():
    all_tratamientos = db['tratamientos'].find()
    tratamientos_list = [
        {
            'id': str(tratamiento['_id']),
            'id_enfermedad': str(tratamiento['id_enfermedad']),
            'nombre': tratamiento['nombre'],
            'descripcion': tratamiento['descripcion'],
            'instrucciones': tratamiento['instrucciones']
        } for tratamiento in all_tratamientos
    ]
    return jsonify({'success': True, 'tratamientos': tratamientos_list})

# Endpoint para agregar un nuevo tratamiento (protegido)
@app.route('/tratamientos', methods=['POST'])
@token_required
def agregar_tratamiento():
    data = request.get_json()
    if not data or 'id_enfermedad' not in data or 'nombre' not in data or 'descripcion' not in data or 'instrucciones' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nuevo_tratamiento = {
        'id_enfermedad': data['id_enfermedad'],
        'nombre': bleach.clean(data['nombre']),
        'descripcion': bleach.clean(data['descripcion']),
        'instrucciones': bleach.clean(data['instrucciones'])
    }
    result = db['tratamientos'].insert_one(nuevo_tratamiento)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201

# Endpoint para listar categorías de enfermedades (protegido)
@app.route('/categorias_enfermedades', methods=['GET'])
@token_required
def listar_categorias_enfermedades():
    all_categorias = db['categorias_de_enfermedades'].find()
    categorias_list = [
        {
            'id': str(categoria['_id']),
            'id_enfermedad': str(categoria['id_enfermedad']),
            'nombre': categoria['nombre'],
            'descripcion': categoria['descripcion']
        } for categoria in all_categorias
    ]
    return jsonify({'success': True, 'categorias': categorias_list})

# Endpoint para agregar una nueva categoría de enfermedad (protegido)
@app.route('/categorias_enfermedades', methods=['POST'])
@token_required
def agregar_categoria_enfermedad():
    data = request.get_json()
    if not data or 'id_enfermedad' not in data or 'nombre' not in data or 'descripcion' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    nueva_categoria = {
        'id_enfermedad': data['id_enfermedad'],
        'nombre': bleach.clean(data['nombre']),
        'descripcion': bleach.clean(data['descripcion'])
    }
    result = db['categorias_de_enfermedades'].insert_one(nueva_categoria)
    return jsonify({'success': True, 'id': str(result.inserted_id)}), 201