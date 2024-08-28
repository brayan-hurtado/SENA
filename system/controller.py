from bd_connector import *
from werkzeug.security import check_password_hash
from flask_login import UserMixin

class Usuarios(UserMixin):
    def __init__(self, idUser, email, password, nombre='', apellido='', localidad='', telefono='', worker_role='', estado=False) -> None:
        self.idUser = idUser
        self.__email = email
        self.__password = password
        self.nombre = nombre
        self.apellido = apellido
        self.localidad = localidad
        self.telefono = telefono
        self.worker_role = worker_role
        self.estado = estado
    
    def get_id(self):
        return str(self.idUser) #El identificador único debe estar en cadena
    
    def get_email(self):
        return self.__email
    
    def get_password(self):
        return self.__password
    
    @classmethod
    def set_user_active(cls, email):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE users SET estado = %s WHERE email = %s"
                cursor.execute(sql, (1, email))  # 1 para True
                conexion.commit()
        finally:
            conexion.close()

    @classmethod
    def set_user_inactive(cls, email):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE users SET estado = %s WHERE email = %s"
                cursor.execute(sql, (0, email))  # 0 para False
                conexion.commit()
        finally:
            conexion.close()
    
   
    @classmethod
    def check_password(cls, hashed_password, __password):
        return check_password_hash(hashed_password, __password)
    
    
    @classmethod
    def register_user(cls, usuario):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:

                sql = "INSERT INTO users (email, password, nombre, apellido, localidad, telefono, worker_role, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (usuario.get_email(), usuario.get_password(), usuario.nombre, usuario.apellido, usuario.localidad, usuario.telefono, usuario.worker_role, 0)) # Por defecto, estado es False (0)
                usuario.idUser = cursor.lastrowid
                conexion.commit()
        finally:
            conexion.close()

class Asesor_SAC(Usuarios):
    def __init__(self, idUser, email, password, nombre, apellido, localidad, telefono, estado):
        super().__init__(idUser, email, password, nombre, apellido, localidad, telefono, estado, worker_role='Asesor')
        self.solicitudes = Solicitudes() #Relación de composición.

class BackOffice(Usuarios):
    def __init__(self, idUser, email, password, nombre, apellido, localidad, telefono, estado):
        super().__init__(idUser, email, password, nombre, apellido, localidad, telefono, estado, worker_role='Backoffice')

class UserManager:
    @classmethod
    def login_user(cls, usuario):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idUser, email, password, nombre, apellido, localidad, telefono, worker_role, estado FROM users WHERE email=%s"
                cursor.execute(sql, (usuario.get_email(),))
                row = cursor.fetchone()
                
                #Verificar si el usuario existe
                if row:
                    idUser, stored_email, stored_password, nombre, apellido, localidad, telefono, worker_role, estado = row
                    
                    if Usuarios.check_password(stored_password, usuario.get_password()):

                        return Usuarios(
                            idUser=idUser,
                            email=stored_email,
                            password=stored_password,
                            nombre=nombre,
                            apellido=apellido,
                            localidad=localidad,
                            telefono=telefono,
                            worker_role=worker_role,  # Almacena como WorkerRole
                            estado=estado
                        )
                    else:
                        return None
                else:
                    return None
        except Exception as ex:
            # Manejo de excepciones, podrías usar logging para registrar el error
            raise Exception(f"Error al intentar iniciar sesión: {ex}")
        finally:
            conexion.close()
    
    @staticmethod
    def get_user(idUser):
        conexion = obtener_conexion()
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT idUser, email, password, nombre, apellido, localidad, telefono, worker_role, estado
                FROM users
                WHERE idUser=%s
            """, (idUser,))
            row = cursor.fetchone()
        
        conexion.close()
        
        if row:
            return Usuarios(
                email=row['email'],
                password=row['password'],
                nombre=row['nombre'],
                apellido=row['apellido'],
                localidad=row['localidad'],
                telefono=row['telefono'],
                worker_role=row['worker_role'],
                idUser=row['idUser'],
                estado=row['estado']
            )
        return None

                
                
class Solicitudes:
    def __init__(self, servicio, logica, clientName, clientPlace, clientTel, rut, descripcion, 
                 deadline, dateAsign, IdOrden=None, status='Abierta'):
        self.IdOrden = IdOrden
        self.servicio = servicio
        self.logica = logica
        self.status = status
        self.clientName = clientName
        self.clientPlace = clientPlace
        self.clientTel = clientTel
        self.rut = rut
        self.descripcion = descripcion
        self.deadline = deadline
        self.dateAsign = dateAsign
        self.dateUpdated = None
    
    @staticmethod
    def mostrar_datos(IdOrden):
        conexion = obtener_conexion()
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
           sql = "SELECT IdOrden, servicio, logica, status, clientName, clientPlace, clientTel, rut, \
           descripcion, deadline, dateAsign, dateUpdated FROM solicitudes WHERE IdOrden = %s"
           cursor.execute(sql, (IdOrden,))
           consulta = cursor.fetchone()
        conexion.close()
        return consulta
    
    @staticmethod
    def listar_datos():
        conexion = obtener_conexion()
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT IdOrden, servicio, logica, status, clientName, clientPlace, clientTel, rut, \
                descripcion, deadline, dateAsign, dateUpdated FROM solicitudes"
            cursor.execute(sql)
            busqueda = cursor.fetchall()
            total = len(busqueda)
        conexion.close()
        return busqueda
    
    @classmethod
    def crear_solicitud(cls, solicitud):
        conexion = obtener_conexion()
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "INSERT INTO solicitudes(servicio, logica, clientName, clientPlace, clientTel, rut, \
            descripcion, deadline, dateAsign) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (solicitud.servicio, solicitud.logica, solicitud.clientName, solicitud.clientPlace, 
                                 solicitud.clientTel, solicitud.rut, solicitud.descripcion, solicitud.deadline, 
                                 solicitud.dateAsign))
            solicitud.IdOrden = cursor.lastrowid
            conexion.commit()
            new_rows = cursor.rowcount
        return new_rows
    
    @staticmethod
    def obtener_orden_id(IdOrden):
        conexion = obtener_conexion()
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT IdOrden, servicio, logica, clientName, clientPlace, clientTel, rut, \
            descripcion, deadline, dateAsign FROM solicitudes WHERE IdOrden=%s"
            cursor.execute(sql, (IdOrden,))
            solicitud = cursor.fetchone()
        conexion.close()
        return solicitud
    
    @classmethod
    def update_request(cls, solicitud):
        try:
            conexion = obtener_conexion()
            if not conexion:
                print("No se pudo establecer la conexión con la base de datos.")
                return

            # Verificar si el IdOrden existe antes de intentar actualizar
            if not cls.exists_id_orden(solicitud.IdOrden):
                print(f"El IdOrden {solicitud.IdOrden} no existe en la base de datos.")
                return

            with conexion.cursor() as cursor:
                sql = """
                    UPDATE solicitudes 
                    SET servicio=%s, logica=%s, clientName=%s, clientPlace=%s, clientTel=%s, rut=%s, 
                        descripcion=%s, deadline=%s, dateAsign=%s 
                    WHERE IdOrden=%s
                """
                values = (
                    solicitud.servicio, solicitud.logica, solicitud.clientName, solicitud.clientPlace, 
                    solicitud.clientTel, solicitud.rut, solicitud.descripcion, 
                    solicitud.deadline, solicitud.dateAsign, solicitud.IdOrden
                )
                print("Consulta SQL:", sql)
                print("Valores:", values)
            
                cursor.execute(sql, values)
                conexion.commit()
            
            # Verifica cuántas filas fueron afectadas
            if cursor.rowcount == 0:
                print("No se actualizó ninguna fila. Verifica que el IdOrden sea correcto.")
            else:
                print(f"Filas actualizadas: {cursor.rowcount}")

        except pymysql.MySQLError as e:
            print(f"Ocurrió un error en la base de datos: {e}")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
        finally:
            if conexion:
                conexion.close()
                
    @classmethod
    def exists_id_orden(cls, IdOrden):
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM solicitudes WHERE IdOrden = %s"
                cursor.execute(sql, (IdOrden,))
                result = cursor.fetchone()
                return result[0] > 0 if result else False
        except pymysql.MySQLError as e:
            print(f"Ocurrió un error en la base de datos: {e}")
            return False
        finally:
            if conexion:
                conexion.close()
    
    @classmethod
    def eliminar_orden(cls, IdOrden):
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM solicitudes WHERE IdOrden=%s"
            cursor.execute(sql, (IdOrden,))
            solicitud = cursor.rowcount
            conexion.commit()
        return solicitud

class Automatized_MG:
    def __init__(self):
        self.usuarios = []
        self.solicitudes = []