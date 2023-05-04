from distutils import config
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

# Configuración de la conexión a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '130201'
app.config['MYSQL_DB'] = 'Clinica'

mysql = MySQL(app)

# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

# Ruta para la página de inicio de sesión
@app.route('/')

def home():
    return render_template('/index.html')
@app.route('/templates/index.html')

def services():
    return render_template('/services.html')
@app.route('/templates/services.html')

def user():
    return render_template('/user.html')
@app.route('/templates/user.html')

@app.route('/registro2')
def registro2():
    return render_template('registro2.html')

# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

@app.route('/login.html', methods= ['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = '¡Ingresaste exitosamente!'
            return render_template('user.html', mesage = mesage)
        else:
            mesage = 'Por favor, introduce los datos correctamente'
    return render_template('login.html', mesage = mesage)
    
# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('home'))

# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

@app.route('/templates/register.html', methods = ['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Usuario ya registrado'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Correo inválido'
        elif not userName or not password or not email:
            mesage = 'Por favor, rellena todos los campos'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = '¡Te has registrado exitosamente!'
    elif request.method == 'POST':
        mesage = 'Por favor, rellena todos los campos'
    return render_template('register.html', mesage = mesage)

# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------- CONEXIÓN AL CRUD Y SUS FUNCIONES ------------------------------------------------#

@app.route('/templates/crud.html')
def crud():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT  * FROM paciente")
    data = cursor.fetchall()
    cursor.close()
    return render_template('/crud.html', paciente=data)

@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        f_last_name = request.form['f_last_name']
        s_last_name = request.form['s_last_name']
        age = request.form['age']
        sex = request.form['sex']
        blood_type = request.form['blood_type']
        height = request.form['height']
        weight = request.form['weight']
        doctor = request.form['doctor']
        cell_phone = request.form['cell_phone']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        # Verificar si los datos ya existen
        cursor.execute("SELECT * FROM paciente WHERE nombre = %s AND apPaterno = %s AND apMaterno = %s", (name, f_last_name, s_last_name))
        result = cursor.fetchone()
        if result:
            flash("ERROR. El paciente ya está registrado en la base de datos. No fue posible agregarlo.")
            return redirect(url_for('crud'))
        else:
            cursor.execute("INSERT INTO paciente (nombre, apPaterno, apMaterno, edad, sexo, tipoSangre, estatura, peso, medico, telMovil, correo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, f_last_name, s_last_name, age, sex, blood_type, height, weight, doctor, cell_phone, email))
            mysql.connection.commit()
            flash("¡Los datos han sido ingresados exitosamente!")
            return redirect(url_for('crud'))

@app.route('/update', methods=['POST','GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        f_last_name = request.form['f_last_name']
        s_last_name = request.form['s_last_name']
        sex = request.form['sex']
        age = request.form['age']
        cell_phone = request.form['cell_phone']
        email = request.form['email']
        doctor = request.form['doctor']
        blood_type = request.form['blood_type']
        height = request.form['height']
        weight = request.form['weight']
        cursor = mysql.connection.cursor()
        # Validar que no exista un paciente con los mismos datos
        cursor.execute("""
            SELECT COUNT(*)
            FROM paciente
            WHERE nombre=%s AND apPaterno=%s AND apMaterno=%s AND pacienteid != %s
        """, (name, f_last_name, s_last_name, id_data))
        result = cursor.fetchone()
        if result[0] > 0:
            flash("ERROR: Ya existe un paciente con los mismos datos. No fue posible actualizar el registro.")
            return redirect(url_for('crud'))
        # Actualizar los datos del paciente
        cursor.execute("""
            UPDATE paciente
            SET nombre=%s, apPaterno=%s, apMaterno=%s, sexo=%s, edad=%s,  telMovil=%s,  correo=%s, medico=%s, tipoSangre=%s, estatura=%s, peso=%s   
            WHERE pacienteid=%s
        """, (name, f_last_name, s_last_name, sex, age, cell_phone, email, doctor, blood_type, height, weight, id_data))
        flash("Los datos se han actualizado correctamente.")
        mysql.connection.commit()
        return redirect(url_for('crud'))
    
@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("El registro ha sido eliminado exitosamente.")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM paciente WHERE pacienteid=%s", (id_data, ))
    mysql.connection.commit()
    return redirect(url_for('crud'))

# -------------------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------HACER LAS CITAS-------------------------------------------------------------------------------------#

@app.route('/templates/citar.html')
def citar():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT  * FROM citas")
    data = cursor.fetchall()
    cursor.close()
    return render_template('/citar.html', paciente=data)

@app.route('/insertC', methods = ['POST'])
def insertC():
    if request.method == "POST":
        nombrePaciente = request.form['nombrePaciente']
        telMovil = request.form['telMovil']
        correo = request.form['correo']
        sintomas = request.form['sintomas']
        fecha = request.form['fecha']
        departamento = request.form['departamento']
        genero = request.form['genero']
        hora = request.form['hora']
        cursor = mysql.connection.cursor()
        # Verificar si los datos ya existen
        cursor.execute("SELECT * FROM citas WHERE nombrePaciente = %s AND telMovil = %s AND correo = %s", (nombrePaciente, telMovil, correo))
        result = cursor.fetchone()
        if result:
            flash("ERROR. El paciente ya está registrado en la base de datos. No fue posible agregarlo.")
            return redirect(url_for('citar'))
        else:
            cursor.execute("INSERT INTO citas (nombrePaciente, telMovil, correo, sintomas, fecha, departamento, genero, hora) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (nombrePaciente, telMovil, correo, sintomas, fecha, departamento, genero, hora))
            mysql.connection.commit()
            flash("¡Los datos han sido ingresados exitosamente!")
            return redirect(url_for('citar'))

@app.route('/updateC', methods=['POST','GET'])
def updateC():
    if request.method == 'POST':
        id_dataC = request.form['id']
        nombrePaciente = request.form['nombrePaciente']
        telMovil = request.form['telMovil']
        correo = request.form['correo']
        sintomas = request.form['sintomas']
        fecha = request.form['fecha']
        departamento = request.form['departamento']
        genero = request.form['genero']
        hora = request.form['hora']
        cursor = mysql.connection.cursor()
        # Validar que no exista una cita con los mismos datos
        #cursor.execute("""
        #    SELECT COUNT(*)
        #    FROM citas
        #    WHERE nombrePaciente=%s AND correo=%s AND id != %s
        # """, (nombrePaciente, correo, id))
        #result = cursor.fetchone()
        #if result[0] > 0:
            #flash("ERROR: Ya existe una cita con los mismos datos. No fue posible actualizar la cita.")
            #return redirect(url_for('citar'))
        # Actualizar los datos del paciente
        cursor.execute("""
            UPDATE citas
            SET nombrePaciente=%s, telMovil=%s, correo=%s, sintomas=%s, fecha=%s,  departamento=%s,  genero=%s, hora=%s   
            WHERE id=%s
        """, (nombrePaciente, telMovil, correo, sintomas, fecha, departamento, genero, hora, id_dataC))
        flash("La cita se ha actualizado correctamente.")
        mysql.connection.commit()
        return redirect(url_for('citar'))


@app.route('/deleteC/<string:id_dataC>', methods = ['GET'])
def deleteC(id_dataC):
    flash("La cita ha sido eliminado exitosamente.")
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM citas WHERE id=%s", (id_dataC, ))
    mysql.connection.commit()
    return redirect(url_for('citar'))


# -------------------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
	app. run(port=4000, host="0.0.0.0")
