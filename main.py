rom flask import Flask, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from system.controller import *
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sup3r_s3cr3t_k3y'

msg = ''
tipo = ''
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    app.logger.debug(f"Loading user with ID: {user_id}")
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        app.logger.error(f"Invalid user_id format: {user_id}")
        return None

    usuario = UserManager.get_user(user_id)
    if usuario:
        return usuario
    return None

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            user = UserManager.login_user(Usuarios(0, email=email, password=password))
            if user:
                app.logger.debug(f"User found: {user.get_id()}")
                if check_password_hash(user.get_password(), password):
                    login_user(user)
                    app.logger.debug(f"User logged in: {user.get_id()}")
                    return redirect(url_for('home'))
                else:
                    flash("Contraseña inválida...")
            else:
                flash("Usuario no encontrado...")
        else:
            flash("Por favor, ingrese ambos campos de email y contraseña.")
        return redirect(url_for('login'))
    return render_template('auth/index.html')
    
    
@app.route('/registro_usuario', methods=['GET', 'POST'])
def formulario_registro_usuario():
    return render_template('auth/registro_usuario.html')

@app.route('/guardar_usuario', methods=['POST'])
def registrar_usuario():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        localidad = request.form['localidad']
        telefono = request.form['telefono']
        worker_role= request.form['worker_role']
        hashed_password = generate_password_hash(password)

        usuario = Usuarios(None, email, hashed_password, nombre, apellido, localidad, telefono, worker_role)
        Usuarios.register_user(usuario)
        flash("Usuario registrado exitosamente")
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        email = current_user.get_email()
        Usuarios.set_user_inactive(email)  # Establecer usuario como inactivo
    logout_user()
    return redirect(url_for('login'))

@app.route('/asesor/sala_gestion')
@login_required
def asesor_dashboard():
    solicitudes = Solicitudes.listar_datos()
    return render_template('asesor_sac.html', solicitudes = solicitudes)

@app.route('/backoffice/sala_gestion')
@login_required
def backoffice_dashboard():
    solicitudes = Solicitudes.listar_datos()
    return render_template('BackOffice.html', solicitudes = solicitudes)

@app.route('/management_room')
@login_required
def management_room():
    app.logger.debug(f"Current user: {current_user}")
    
    app.logger.debug(f"current_user: {current_user}")
    app.logger.debug(f"attributes: {dir(current_user)}")
    app.logger.debug(f"worker_role: {getattr(current_user, 'worker_role', 'No worker_role attribute')}")

    if not current_user.is_authenticated:
        app.logger.warning('Usuario no autenticado')
        return "Error: Usuario no autenticado", 403
    
    if not hasattr(current_user, 'worker_role'):
        app.logger.warning('Atributo worker_role no disponible para el usuario')
        return "Error: Atributo 'worker_role' no disponible", 403
    
    if current_user.worker_role == 'Asesor':
        return redirect(url_for('asesor_dashboard'))
    elif current_user.worker_role == 'Backoffice':
        return redirect(url_for('backoffice_dashboard'))
    else:
        app.logger.error(f"Rol no reconocido: {current_user.worker_role}")
        return "Rol no especificado", 403

@app.route('/Data_base', methods=['GET', 'POST'])
def home():
    solicitudes = Solicitudes.listar_datos()
    return render_template('Data_base.html', solicitudes = solicitudes)

@app.route('/registro_solicitud', methods=['GET', 'POST'])
def formulario_registro_solicitud():
    return render_template('registro_solicitud.html')

@app.route('/guardar_solicitud', methods=['POST'])
def guardar_solicitud():
    if request.method == 'POST':
        servicio = request.form['servicio']
        logica = request.form['logica']
        clientName = request.form['clientName']
        clientPlace = request.form['clientPlace']
        clientTel = request.form['clientTel']
        rut = request.form['rut']
        descripcion = request.form['descripcion']
        deadline = request.form['deadline']
        dateAsign = request.form['dateAsign']
        
        solicitud = Solicitudes(servicio, logica, clientName, clientPlace, clientTel, rut, descripcion, 
                                deadline, dateAsign)
        Solicitudes.crear_solicitud(solicitud)    
    return redirect(url_for('home'))

@app.route("/formulario_editar_solicitud/<int:IdOrden>", methods=['GET'])
def editar_solicitud(IdOrden):
    solicitud = Solicitudes.obtener_orden_id(IdOrden)
    return render_template('editar_registro.html', solicitud=solicitud)


@app.route("/actualizar_orden/<int:IdOrden>", methods=['POST'])
def actualizar_orden(IdOrden):
    if request.method == 'POST':
        servicio = request.form['servicio']
        logica = request.form['logica']
        clientName = request.form['clientName']
        clientPlace = request.form['clientPlace']
        clientTel = request.form['clientTel']
        rut = request.form['rut']
        descripcion = request.form['descripcion']
        deadline = request.form['deadline']
        dateAsign = request.form['dateAsign']
        
        solicitud = Solicitudes(servicio, logica, clientName, clientPlace, clientTel, rut, descripcion, deadline, 
                                dateAsign, IdOrden)
        Solicitudes.update_request(solicitud)
    return redirect('/Data_base')

@app.route("/eliminar_orden/<int:IdOrden>", methods=['POST'])
def eliminar_orden(IdOrden):
    IdOrden = request.form['IdOrden']
    Solicitudes.eliminar_orden(IdOrden)
    return redirect('/Data_base')

@app.route("/ver_detalles_solicitud/<int:IdOrden>", methods=['GET'])
def viewDetalles(IdOrden):
    if request.method == 'GET':
        solicitud = Solicitudes.mostrar_datos(IdOrden)
        if solicitud:
            return render_template('view.html', infoSolicitud = solicitud, msg='Detalles de la solicitud', tipo=1)
        else:
            return render_template('Data_base.html', msg = 'No existe la solicitud', tipo=1)
    return redirect(url_for('home'))

def status_403(error):
    return redirect(url_for('home'))

def status_401(error):
    return redirect(url_for('home'))

#Inicializar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
    csrf.init_app(app)
    app.register_error_handler(403, status_403)
    app.register_error_handler(401, status_401)
