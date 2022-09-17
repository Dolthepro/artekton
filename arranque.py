from types import NoneType
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL,MySQLdb
from flask_login import LoginManager, login_user, logout_user, login_required
from platformdirs import user_cache_path


app = Flask (__name__)


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Dolawmpr0'
app.config['MYSQL_DB']='dbadsi'
mysql =MySQL(app)

app.secret_key='mysecretkey'

@app.route('/')
def Index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        cedula=request.form['cedula']
        password=request.form['password']
        
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE cedula=%s",(cedula,))
        user=cur.fetchone()
        cur.close()

        if password=='':
            flash('Por favor, llene todos los campos')
            return render_template('login.html')

        elif user ==None:
            flash('Usuario no encontrado, verifique')
            return render_template('login.html') 

        elif len(user)>0:
            userstr=(str(user[2]))
            if userstr==password:
                session['user']=cedula
                session ['name']=user[4]
                session ['cargo']=user[3]
                session ['cedula']=user[1]
                session ['id_registro']=user[0]
                print(user[3])
                if session['cargo']=='Admin':
                    return redirect(url_for('Pusuarios'))
                elif session['cargo']=='Auxiliar':
                    return redirect(url_for('Auxiliar'))
                elif session['cargo']=='Jefe de Inventario':
                    return redirect(url_for('Pusuarios'))
            else:
                flash('Contraseña Inválida')
                return render_template('login.html') 
    else:
        return render_template('login.html')   

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/verificar', methods=['GET','POST'])
def Pusuarios():
    if 'cedula' in session:
        return render_template('P_usuarios.html')
    else:
        return render_template('login.html')

@app.route('/auxiliar', methods=['GET','POST'])
def Auxiliar():
    if session['cargo']=='Auxiliar':
        return render_template('auxiliar.html')
    else:
        return render_template('login.html')
        
    
@app.route('/buscar', methods=['GET','POST'])
def get_busqueda():
    if 'user' in session:
        nmaterial=request.form['buscar_material'] 
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventariog WHERE nombre_material LIKE %s',('%'+nmaterial+'%',))
        data=cur.fetchall()
        if nmaterial=='':
            flash('Por favor Instroduzca un nombre de material')
        elif data ==():
            flash('Material no encontrado')
        return render_template('mostrar-busqueda.html', registros = data)
    else:
        return render_template('login.html')

@app.route('/buscaraux', methods=['GET','POST'])
def get_busquedaAUX():
    if 'user' in session:
        nmaterial=request.form['buscar_material']
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventariog WHERE nombre_material LIKE %s',('%'+nmaterial+'%',))
        data=cur.fetchall()
        if nmaterial=='':
            flash('Por favor Instroduzca un nombre de material valido')
        elif data==():
            flash('Material no encontrado')
        return render_template('mostrar-busquedaAUX.html', registros = data)
    else:
        return render_template('login.html')


@app.route('/Inventario')
def Inventario():
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventariog order by n_referencia desc')
        data=cur.fetchall()
        return render_template('Inventario.html', registros=data)
    else:
        return render_template('login.html')

@app.route('/Inventarioauxiliar')
def Inventarioauxiliar():
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventariog order by n_referencia desc')
        data=cur.fetchall()
        return render_template('Inventarioauxiliar.html', registros=data)
    else:
        return render_template('login.html')

@app.route('/FAQ')
def FAQ():
    if 'user' in session:
        return render_template('FAQ.html')
    else:
        return render_template('login.html')

@app.route('/FAQAUX')
def FAQAUX():
    if 'user' in session:
        return render_template('FAQAUX.html')
    else:
        return render_template('login.html')

@app.route('/historial_inventario')
def historial_inventario():
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM historial_inventario order by fecha desc')
        data=cur.fetchall()
        return render_template('historial_inventario.html', registros=data)
    else:
        return render_template('login.html')

@app.route('/historial_inventarioAUX')
def historial_inventarioAUX():
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM historial_inventario order by fecha desc')
        data=cur.fetchall()
        return render_template('historial_inventarioAUX.html', registros=data)
    else:
        return render_template('login.html')

@app.route('/borrar/<string:n_referencia>')
def borrar(n_referencia):
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM inventariog WHERE n_referencia = {0}'.format(n_referencia))
    mysql.connection.commit()
    flash('Registro Eliminado Satisfactoriamente')
    return redirect(url_for('Inventario'))

@app.route('/editar/<n_referencia>')
def get_registro(n_referencia):
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventariog WHERE n_referencia = %s',(n_referencia))
        data=cur.fetchall()
        return render_template('editar-inventario.html', registro = data[0]) 
    else:
        return render_template('login.html')

@app.route('/actualizar/<n_referencia>', methods=['POST'])
def actualizar_inventario(n_referencia):
    if request.method=='POST':

        nombre_material=request.form['nombre_material']
        descripcion=request.form['descripcion']
        proveedor=request.form['proveedor'] 
        presentacion=request.form['presentacion']
        stock=request.form['stock']
        ubicacion=request.form['ubicacion']
        cur=mysql.connection.cursor()
        cur.execute("""UPDATE inventariog SET nombre_material=%s, descripcion=%s, proveedor=%s, presentacion=%s, stock=%s, ubicacion=%s WHERE n_referencia=%s """,(nombre_material,descripcion,proveedor,presentacion,stock,ubicacion,n_referencia))
        mysql.connection.commit()
        flash('Registro actualizado satisfactoriamente')
        return redirect(url_for('Inventario'))

@app.route('/agregar',methods=['GET','POST'])
def agregar():
    if request.method=='POST':
        nombre_material=request.form['nombre_material']
        descripcion=request.form['descripcion']
        proveedor=request.form['proveedor']
        presentacion=request.form['presentacion']
        stock=request.form['stock']
        ubicacion=request.form['ubicacion']
        id_registro=session ['id_registro']
        if nombre_material=='':
            flash('Por favor, llene el campo "Nombre de Material"')
            return redirect(url_for('Inventario'))
        if stock=='':
            flash('Por favor, llene el campo "Stock"')
            return redirect(url_for('Inventario'))
        else:
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO inventariog(id_registro,nombre_material,descripcion,proveedor,presentacion,stock,ubicacion)VALUES(%s,%s,%s,%s,%s,%s,%s)',
            (id_registro,nombre_material,descripcion,proveedor,presentacion,stock,ubicacion))
            mysql.connection.commit()
            flash('Registro Agregado Satisfactoriamente')
            return redirect(url_for('Inventario'))

@app.route('/admin')
def admin():
    if session['cargo']=='Admin':
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios order by id_registro desc')
        data=cur.fetchall()
        return render_template('Admin.html', registros=data)
    elif session['cargo']=='Jefe de Inventario':
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios order by id_registro desc')
        data=cur.fetchall()
        return render_template('Admin.html', registros=data)
    else:
        return render_template('Restringido.html')

@app.route('/agregar_usuario',methods=['GET','POST'])
def agregar_usuario():
    if request.method=='POST':
        cedula=request.form['cedula']
        passwordd=request.form['passwordd']
        cargo=request.form['cargo']
        id_nombre=request.form['id_nombre']
        if cedula=='':
            flash('Por favor, llene el campo "Cedula"')
            return redirect(url_for('admin'))
        elif passwordd=='':
            flash('Por favor, llene el campo "Contraseña"')
            return redirect(url_for('admin'))
        elif id_nombre=='':
            flash('Por favor, llene el campo "Nombre"')
            return redirect(url_for('admin'))
        else:
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO usuarios(cedula,passwordd,cargo,id_nombre)VALUES(%s,%s,%s,%s)',
            (cedula,passwordd,cargo,id_nombre))
            mysql.connection.commit()
            flash('Registro Agregado Satisfactoriamente')
            return redirect(url_for('admin'))

@app.route('/eliminar_u/<string:id_registro>')
def eliminar_u(id_registro):
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM usuarios WHERE id_registro= {0}'.format(id_registro))
    mysql.connection.commit()
    flash('Registro Eliminado Satisfactoriamente')
    return redirect(url_for('admin'))

@app.route('/editar_u/<id_registro>')
def editar_u(id_registro):
    if 'user' in session:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE id_registro = %s',(id_registro))
        data=cur.fetchall()
        return render_template('editar-usuario.html', registro = data[0])
    else:
        return render_template('login.html')

@app.route('/actualizar_u/<id_registro>', methods=['POST'])
def actualizar_u(id_registro):
    if request.method=='POST':
        cedula=request.form['cedula']
        passwordd=request.form['passwordd']
        cargo=request.form['cargo']
        id_nombre=request.form['id_nombre']
        cur=mysql.connection.cursor()
        cur.execute("""UPDATE usuarios SET cedula=%s, passwordd=%s, cargo=%s, id_nombre=%s WHERE id_registro=%s """,(cedula,passwordd,cargo,id_nombre,id_registro))
        mysql.connection.commit()
        flash('Registro actualizado satisfactoriamente')
        return redirect(url_for('admin'))

if __name__=='__main__':
    app.run(port=3000, debug=True)


