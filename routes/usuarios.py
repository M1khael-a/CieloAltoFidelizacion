from flask import Blueprint, render_template, request, flash
from models import db
from models.cliente import Cliente
from models.premio import Premio

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if request.method == 'POST':
        documento = request.form.get('documento')

        # Buscar cliente en la base de datos
        cliente = Cliente.query.filter_by(cedula=documento).first()


        if cliente:
            premios = Premio.query.all()  # Ahora vienen de la BD
            return render_template(
                'usuarios/resultados.html',
                nombre_cliente=cliente.nombre,
                puntos=cliente.puntos,
                porcentaje=(cliente.puntos / 500 * 100) if cliente.puntos else 0,
                premios=premios
            )
        
        else:
            flash("No encontramos un cliente con ese documento", "warning")
    return render_template('usuarios/consulta.html')


# # =========================
# # Redimir premio
# # =========================
# @users_bp.route("/<int:cliente_id>/redimir", methods=["GET", "POST"])
# def redimir(cliente_id):
#     cliente = Cliente.query.get_or_404(cliente_id)
#     premios = Premio.query.order_by(Premio.puntos_requeridos.asc()).all()
#     premio_redimido = None

#     if request.method == "POST":
#         premio_id = request.form.get("premio_id")
#         premio = Premio.query.get(premio_id)

#         if premio and cliente.redimir_premio(premio):
#             db.session.commit()
#             flash(f"Premio '{premio.nombre}' redimido correctamente.", "success")
#             return redirect(url_for("users.redimir", cliente_id=cliente_id, premio_id=premio.id))
#         else:
#             flash("No tienes puntos suficientes para este premio.", "danger")

#     premio_id_qs = request.args.get("premio_id")
#     if premio_id_qs:
#         premio_redimido = Premio.query.get(premio_id_qs)

#     return render_template("clientes/redimir.html", cliente=cliente, premios=premios, premio_redimido=premio_redimido)

# # =========================
# # Imprimir ticket
# # =========================
# @users_bp.route("/<int:cliente_id>/ticket/<int:premio_id>")
# def imprimir_ticket(cliente_id, premio_id):
#     cliente = Cliente.query.get_or_404(cliente_id)
#     premio = Premio.query.get_or_404(premio_id)

#     buffer = io.BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A5)
#     width, height = A5
#     xc = width / 2

#     # --- LOGO ---
#     y_top = height - 60
#     logo_path = "static/img/imp.png"
#     try:
#         logo = ImageReader(logo_path)
#         iw, ih = logo.getSize()
#         target_w = 180
#         target_h = target_w * (ih / iw)
#         x_logo = (width - target_w) / 2
#         y_logo = y_top - target_h
#         c.drawImage(logo, x_logo, y_logo, width=target_w, height=target_h, mask='auto')
#         y_cursor = y_logo - 50
#     except Exception:
#         y_cursor = y_top - 50

#     # --- TEXTO ---
#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(xc, y_cursor, f"{datetime.now().strftime('%d/%m/%Y')}")
#     y_cursor -= 40

#     c.setFont("Helvetica", 13)
#     c.drawCentredString(xc, y_cursor, f"{cliente.nombre}")
#     y_cursor -= 30
#     c.drawCentredString(xc, y_cursor, f"{cliente.cedula}")
#     y_cursor -= 40

#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(xc, y_cursor, f"Premio redimido")
#     y_cursor -= 30
#     c.drawCentredString(xc, y_cursor, f"{premio.nombre} ({premio.puntos_requeridos} pts)")
#     y_cursor -= 40

#     c.setFont("Helvetica", 13)
#     c.drawCentredString(xc, y_cursor, f"Puntos restantes: {cliente.puntos} pts")
#     y_cursor -= 60

#     # --- FOOTER ---
#     c.setFont("Helvetica-Oblique", 12)
#     c.setFillGray(0.35)
#     c.drawCentredString(xc, 40, "Gracias por confiar en nosotros")
#     c.setFillGray(0)

#     c.showPage()
#     c.save()
#     buffer.seek(0)
#     return send_file(buffer, as_attachment=False,
#                      download_name="ticket_redencion.pdf",
#                      mimetype="application/pdf")
