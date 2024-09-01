import pymysql
import pymysql.cursors

def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='admin', # Contraseña de la base de datos.
        database='db_automationsys'
    )
