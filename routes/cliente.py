from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, session
from models import db
from models.cliente import Cliente
from models.login import Login
from models.premio import Premio
from forms.cliente_form import ClienteForm
from datetime import datetime
import io
from datetime import datetime
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from auth.decorators import role_required
from flask_mail import Message
from routes.mail import mail
from datetime import date

# ------

# Crear el Blueprint
cliente_bp = Blueprint("cliente", __name__, url_prefix="/clientes")


# 🟢 Ruta : Enviar correo de felicitaciones GENERAL/GLOBAL
@cliente_bp.route("/enviar_cumpleanos")
@role_required("admin")
def enviar_cumpleanos():
    hoy = date.today()
    cumpleaneros = Cliente.query.filter(
        db.extract('day', Cliente.fecha_nacimiento) == hoy.day,
        db.extract('month', Cliente.fecha_nacimiento) == hoy.month
    ).all()

    if not cumpleaneros:
        flash("No hay cumpleaños hoy.", "info")
        return redirect(url_for("index"))

    for cliente in cumpleaneros:
        msg = Message(
            subject=f"🎂 ¡Feliz cumpleaños {cliente.nombre}, te desea Cielo Alto! 🎉!",
            recipients=[cliente.correo],
            body=f"Hola {cliente.nombre}, desde Cielo Alto te deseamos un feliz cumpleaños 🎉"
        )
        mail.send(msg)

    flash(f"Se enviaron {len(cumpleaneros)} correos de cumpleaños 🎉", "success")
    return redirect(url_for("index"))




# 🟢 Ruta : Enviar correo de felicitaciones a cumpleañero individualmente
@cliente_bp.route("/felicitacion/<int:cliente_id>")
@role_required("admin")
def enviar_felicitacion(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    # Crear el correo
    msg = Message(
        subject=f"🎂 ¡Feliz cumpleaños {cliente.nombre}, te desea Cielo Alto! 🎉",
        recipients=[cliente.correo],  # asegúrate que Cliente tenga el campo email
        body=f"Hola {cliente.nombre},\n\n"
             "En Cielo Alto queremos desearte un muy feliz cumpleaños 🎂🎉.\n"
             "Te esperamos para celebrar con un detalle especial de nuestra parte.\n\n"
             "¡Que sea un año lleno de bendiciones!\n\n"
             "Con cariño,\nEl equipo de Cielo Alto"
    )

    try:
        mail.send(msg)
        flash(f"Felicitación enviada a {cliente.nombre}", "success")
    except Exception as e:
        flash(f"Error al enviar correo: {e}", "danger")

    return redirect(url_for("index"))  # vuelve al dashboard


# 🟢 Ruta : Impresión de tickete de redención de puntos
@cliente_bp.route("/<int:cliente_id>/ticket/<int:premio_id>")
@role_required("admin", "general")
def imprimir_ticket(cliente_id, premio_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    premio = Premio.query.get_or_404(premio_id)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5
    xc = width / 2

    # --- LOGO ---
    y_top = height - 60
    logo_path = "static/img/imp.png"
    try:
        logo = ImageReader(logo_path)
        iw, ih = logo.getSize()
        target_w = 180
        target_h = target_w * (ih / iw)
        x_logo = (width - target_w) / 2
        y_logo = y_top - target_h
        c.drawImage(logo, x_logo, y_logo, width=target_w, height=target_h, mask='auto')
        y_cursor = y_logo - 50
    except Exception:
        y_cursor = y_top - 50

    # --- TEXTO ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(xc, y_cursor, f"{datetime.now().strftime('%d/%m/%Y')}")
    y_cursor -= 40

    c.setFont("Helvetica", 13)
    c.drawCentredString(xc, y_cursor, f"{cliente.nombre}")
    y_cursor -= 30
    c.drawCentredString(xc, y_cursor, f"{cliente.cedula}")
    y_cursor -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(xc, y_cursor, f"Premio redimido")
    y_cursor -= 30
    c.drawCentredString(xc, y_cursor, f"{premio.nombre} ({premio.puntos_requeridos} pts)")
    y_cursor -= 40

    c.setFont("Helvetica", 13)
    c.drawCentredString(xc, y_cursor, f"Puntos restantes: {cliente.puntos} pts")
    y_cursor -= 60

    # --- FOOTER ---
    c.setFont("Helvetica-Oblique", 12)
    c.setFillGray(0.35)
    c.drawCentredString(xc, 40, "Gracias por confiar en nosotros")
    c.setFillGray(0)

    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=False,
                     download_name="ticket_redencion.pdf",
                     mimetype="application/pdf")

# 🟢 Ruta desde index: buscar cliente por cédula para redención de RECOMPENSA
@cliente_bp.route("/redimir", methods=["GET", "POST"])
@role_required("admin", "general")
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
@role_required("admin", "general")
def redimir(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    premios = Premio.query.order_by(Premio.puntos_requeridos.asc()).all()
    premio_redimido = None

    if request.method == "POST":
        premio_id = request.form.get("premio_id")
        premio = Premio.query.get(premio_id)

        if premio and cliente.redimir_premio(premio):
            db.session.commit()
            flash(f"Premio '{premio.nombre}' redimido correctamente.", "success")
            return redirect(url_for("cliente.redimir", cliente_id=cliente_id, premio_id=premio.id))
        else:
            flash("No tienes puntos suficientes para este premio.", "danger")

    premio_id_qs = request.args.get("premio_id")
    if premio_id_qs:
        premio_redimido = Premio.query.get(premio_id_qs)

    return render_template("clientes/redimir.html", cliente=cliente, premios=premios, premio_redimido=premio_redimido)



# 🟢 Ruta: Muestra que cliente se le esta añadiendo la compra
@cliente_bp.route("/buscar/<cedula>")
@role_required("admin", "general")
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
@role_required("admin", "general")
def listar_clientes():
    cedula_busqueda = request.args.get("cedula", "").strip()

    if cedula_busqueda:
        clientes = Cliente.query.filter(Cliente.cedula.contains(cedula_busqueda)).all()
    else:
        clientes = Cliente.query.all()

    return render_template("clientes/listar.html", clientes=clientes, cedula_busqueda=cedula_busqueda)



# 🟢 Ruta: Crear un nuevo cliente
@cliente_bp.route("/crear", methods=["GET", "POST"])
@role_required("admin", "general")
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
@role_required("admin", "general")
def detalle_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template("clientes/detalle.html", cliente=cliente)


# 🟢 Ruta: Editar un cliente
@cliente_bp.route("/editar/<int:cliente_id>", methods=["GET", "POST"])
@role_required("admin")
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
@role_required("admin")
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
