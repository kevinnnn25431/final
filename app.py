from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'super_secreto_clave_seguridad'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'reciclaje.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Voluntario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    actividad = db.Column(db.String(100), nullable=False)

@app.route('/')
def root():
    # Quite el redireccionamiento automatico para que siempre veas el login
    return render_template('login.html', mostrar_bienvenida=False)

@app.route('/iniciar', methods=['POST'])
def iniciar():
    user = request.form['usuario']
    pwd = request.form['password']
    usuario_db = Usuario.query.filter_by(nombre_usuario=user).first()
    
    if usuario_db and usuario_db.password == pwd:
        session['usuario'] = user
        return redirect(url_for('bienvenida')) 
    else:
        flash('Datos incorrectos', 'error')
        return redirect(url_for('root'))

@app.route('/registrarse', methods=['POST'])
def registrarse():
    user = request.form['usuario']
    pwd = request.form['password']
    
    if Usuario.query.filter_by(nombre_usuario=user).first():
        flash('El usuario ya existe', 'error')
        return redirect(url_for('root'))

    db.session.add(Usuario(nombre_usuario=user, password=pwd))
    db.session.commit()
    session['usuario'] = user
    return redirect(url_for('bienvenida'))

@app.route('/bienvenida')
def bienvenida():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('login.html', mostrar_bienvenida=True, nombre_usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('root'))

@app.route('/index')
def index():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('index.html')

@app.route('/introduccion')
def introduccion():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('introduccion.html')

@app.route('/como-funciona') 
def como_funciona():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('como funciona.html') 

@app.route('/tipos-del-reciclaje')
def tipos():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('tipos del reciclaje.html')

@app.route('/beneficios')
def beneficios():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('beneficios.html')

@app.route('/consejos')
def consejos():
    if 'usuario' not in session: return redirect(url_for('root'))
    return render_template('consejos.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar_voluntario():
    if 'usuario' not in session: return redirect(url_for('root'))

    if request.method == 'POST':
        db.session.add(Voluntario(
            nombre=request.form['nombre'], 
            edad=request.form['edad'], 
            actividad=request.form['actividad']
        ))
        db.session.commit()
        flash('¡Voluntario registrado con éxito!', 'success')
        return redirect(url_for('registrar_voluntario'))

    lista = Voluntario.query.all()
    return render_template('registrar.html', voluntarios=lista)

@app.route('/eliminar_voluntario/<int:id>')
def eliminar_voluntario(id):
    if 'usuario' not in session: return redirect(url_for('root'))
    
    voluntario_a_borrar = Voluntario.query.get_or_404(id)
    db.session.delete(voluntario_a_borrar)
    db.session.commit()
    
    flash('Voluntario eliminado correctamente', 'success')
    return redirect(url_for('registrar_voluntario'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("--- Sistema Listo ---")
    app.run(debug=True)