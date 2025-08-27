# # 🟢 Ruta: Otra ruta para sumer puntos ?)
# @cliente_bp.route("/nueva_compra", methods=["GET", "POST"])
# def nueva_compra_general():
#     clientes = Cliente.query.all()

#     if request.method == "POST":
#         try:
#             cliente_id = int(request.form.get("cliente_id"))
#             monto = float(request.form.get("monto", 0))
#             cliente = Cliente.query.get_or_404(cliente_id)

#             if monto > 0:
#                 puntos = int(monto // 1000)  # regla de negocio: 1 punto por cada $1000
#                 cliente.puntos += puntos
#                 db.session.commit()
#                 flash(f"Compra registrada ✅. Se sumaron {puntos} puntos al cliente {cliente.nombre}", "success")
#                 return redirect(url_for("cliente.listar_clientes"))
#             else:
#                 flash("Debes ingresar un monto mayor a 0", "warning")
#         except ValueError:
#             flash("Datos inválidos en el formulario", "danger")

#     return render_template("compras/nueva_general.html", clientes=clientes)


# # 🟢 Ruta: Sumar puntos a un cliente
# @cliente_bp.route("/sumar_puntos/<int:cliente_id>", methods=["GET", "POST"])
# def sumar_puntos(cliente_id):
#     cliente = Cliente.query.get_or_404(cliente_id)

#     if request.method == "POST":
#         try:
#             puntos = int(request.form.get("puntos", 0))
#             if puntos > 0:
#                 cliente.puntos += puntos
#                 db.session.commit()
#                 flash(f"Se sumaron {puntos} puntos al cliente {cliente.nombre} ✅", "success")
#                 return redirect(url_for("cliente.listar_clientes"))
#             else:
#                 flash("Debes ingresar un número válido mayor a 0", "warning")
#         except ValueError:
#             flash("El valor de puntos no es válido", "danger")

#     return render_template("clientes/sumar_puntos.html", cliente=cliente)


# <--- HTML --->
# <a href="{{ url_for('cliente.nueva_compra_general', cliente_id=cliente.id) }}" class="btn btn-success btn-sm">🛒</a>





from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db
from models.cliente import Cliente
from models.premio import Premio
from datetime import datetime
from forms.cliente_form import ClienteForm


# Crear el Blueprint
cliente_bp = Blueprint("cliente", __name__, url_prefix="/clientes")

# 🟢 Ruta: Impresión de tirilla
@cliente_bp.route("/<int:cliente_id>/recibo_redencion/<int:premio_id>")
def recibo_redencion(cliente_id, premio_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    premio = Premio.query.get_or_404(premio_id)
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    return render_template("compras/recibo_redencion.html",
                           cliente=cliente,
                           premio=premio,
                           fecha_hora=fecha_hora)


# 🟢 Ruta desde index: buscar cliente por cédula para redención de RECOMPENSA
@cliente_bp.route("/redimir", methods=["GET", "POST"])
def redimir_buscar():
    if request.method == "POST":
        cedula = request.form.get("cedula")
        cliente = Cliente.query.filter_by(cedula=cedula).first()
        if cliente:
            return redirect(url_for("cliente.redimir", cliente_id=cliente.id))
        else:
            flash("Cliente no encontrado", "danger")
    return render_template("clientes/redimir.html")


# 🟢 Ruta para redimir puntos de un cliente específico dentro del boton del cliente
@cliente_bp.route("/<int:cliente_id>/redimir", methods=["GET", "POST"])
def redimir(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    premios = Premio.query.order_by(Premio.puntos_requeridos.asc()).all()

    if request.method == "POST":
        premio_id = request.form.get("premio_id")
        premio = Premio.query.get(premio_id)

        if premio and cliente.redimir_premio(premio):
            db.session.commit()
            flash(f"Premio '{premio.nombre}' redimido correctamente.", "success")
            return redirect(url_for("cliente.recibo_redencion", cliente_id=cliente.id, premio_id=premio.id)) ### RETORNAR A RECIBO DE REDENCIÓN
        else:
            flash("No tienes puntos suficientes para este premio.", "danger")

    return render_template("clientes/redimir.html", cliente=cliente, premios=premios)



# 🟢 Ruta: Muestra que cliente se le esta añadiendo la compra
@cliente_bp.route("/buscar/<cedula>")
def buscar_cliente(cedula):
    cliente = Cliente.query.filter_by(cedula=cedula).first()
    if cliente:
        return {
            "existe": True,
            "nombre": cliente.nombre,
            "correo": cliente.correo,
            "telefono": cliente.telefono
        }
    return {"existe": False}


# 🟢 Ruta: Listar todos los clientes con búsqueda por cédula
@cliente_bp.route("/", methods=["GET", "POST"])
def listar_clientes():
    cedula_busqueda = request.args.get("cedula", "").strip()

    if cedula_busqueda:
        clientes = Cliente.query.filter(Cliente.cedula.contains(cedula_busqueda)).all()
    else:
        clientes = Cliente.query.all()

    return render_template("clientes/listar.html", clientes=clientes, cedula_busqueda=cedula_busqueda)



# 🟢 Ruta: Crear un nuevo cliente
@cliente_bp.route("/crear", methods=["GET", "POST"])
def crear_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        nuevo_cliente = Cliente(
            cedula=form.cedula.data,
            nombre=form.nombre.data,
            correo=form.correo.data,
            telefono=form.telefono.data,
            fecha_nacimiento=form.fecha_nacimiento.data
        )
        db.session.add(nuevo_cliente)
        try:
            db.session.commit()
            flash("Cliente creado con éxito ✅", "success")
            return redirect(url_for("cliente.listar_clientes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear cliente: {str(e)}", "danger")
    return render_template("clientes/crear.html", form=form)


# 🟢 Ruta: Ver detalle de un cliente
@cliente_bp.route("/<int:cliente_id>")
def detalle_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template("clientes/detalle.html", cliente=cliente)


# 🟢 Ruta: Editar un cliente
@cliente_bp.route("/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(cliente_id=cliente.id, obj=cliente)

    if form.validate_on_submit():
        # Verificar si ya existe un correo igual en otro cliente
        existente = Cliente.query.filter_by(correo=form.correo.data).first()
        existente_cedula = Cliente.query.filter_by(cedula=form.cedula.data).first()
        if existente and existente.id != cliente.id:
            flash("El correo ya está registrado por otro cliente.", "danger")
        if existente_cedula and existente_cedula.id != cliente.id:
            flash("La cédula ya está registrada por otro cliente.", "danger")
        else:
            cliente.cedula = form.cedula.data
            cliente.nombre = form.nombre.data
            cliente.correo = form.correo.data
            cliente.telefono = form.telefono.data
            cliente.fecha_nacimiento = form.fecha_nacimiento.data

        try:
            db.session.commit()
            flash("Cliente actualizado con éxito ✏️", "success")
            return redirect(url_for("cliente.listar_clientes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar cliente: {str(e)}", "danger")

    return render_template("clientes/editar.html", form=form, cliente=cliente)


# 🟢 Ruta: Eliminar un cliente
@cliente_bp.route("/eliminar/<int:cliente_id>", methods=["POST"])
def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash("Cliente eliminado con éxito 🗑️", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar cliente: {str(e)}", "danger")
    return redirect(url_for("cliente.listar_clientes"))
