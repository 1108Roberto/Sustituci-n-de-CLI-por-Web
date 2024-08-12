from flask import Flask, request, redirect, url_for, render_template, flash
import redis
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurar la conexión a Redis
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/')
def index():
    keys = client.keys('receta:*')
    recetas = []
    for key in keys:
        receta_str = client.get(key)
        receta = json.loads(receta_str)
        recetas.append({'id': key.split(':')[1], 'nombre': receta['nombre']})
    return render_template('index.html', recetas=recetas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        ingredientes = request.form['ingredientes'].strip()
        pasos = request.form['pasos'].strip()

        if not nombre or not ingredientes or not pasos:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for('agregar'))

        id = client.incr('receta_id')
        receta = {
            'nombre': nombre,
            'ingredientes': ingredientes,
            'pasos': pasos
        }
        client.set(f'receta:{id}', json.dumps(receta))
        flash(f"Receta agregada exitosamente con ID {id}.")
        return redirect(url_for('index'))

    return render_template('agregar.html')

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    receta_str = client.get(f'receta:{id}')
    if not receta_str:
        flash("Receta no encontrada.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        ingredientes = request.form['ingredientes'].strip()
        pasos = request.form['pasos'].strip()

        receta = json.loads(receta_str)
        receta['nombre'] = nombre if nombre else receta['nombre']
        receta['ingredientes'] = ingredientes if ingredientes else receta['ingredientes']
        receta['pasos'] = pasos if pasos else receta['pasos']

        client.set(f'receta:{id}', json.dumps(receta))
        flash("Receta actualizada exitosamente.")
        return redirect(url_for('index'))

    receta = json.loads(receta_str)
    return render_template('actualizar.html', receta=receta, id=id)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    result = client.delete(f'receta:{id}')
    if result:
        flash("Receta eliminada exitosamente.")
    else:
        flash("Receta no encontrada.")
    return redirect(url_for('index'))

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        id = request.form['id'].strip()
        if not id.isdigit():
            flash("ID inválido.")
            return redirect(url_for('buscar'))

        receta_str = client.get(f'receta:{id}')
        if receta_str:
            receta = json.loads(receta_str)
            return render_template('buscar.html', receta=receta)
        else:
            flash("Receta no encontrada.")
            return redirect(url_for('buscar'))

    return render_template('buscar.html', receta=None)

if __name__ == "__main__":
    app.run(debug=True)
