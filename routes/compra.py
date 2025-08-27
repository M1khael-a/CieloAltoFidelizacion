from flask import Blueprint, render_template, redirect, url_for, flash
from models import db
from models.compra import Compra
from models.cliente import Cliente
from forms.compra_form import CompraForm
from datetime import datetime
from auth.decorators import role_required

compra_bp = Blueprint("compra", __name__, url_prefix="/compras")

# 🟢 Ruta: Nueva compra (general)
@compra_bp.route("/nueva_compra", methods=["GET", "POST"])
@role_required("admin", "general")
def nueva_compra():
    form = CompraForm()
    if form.validate_on_submit():
        cliente = Cliente.query.filter_by(cedula=form.cedula.data).first()
        if not cliente:
            flash("No existe un cliente con esa cédula ❌", "danger")
            return render_template("compras/nueva.html", form=form)

        # Calcular puntos (ejemplo: 1 punto por cada $1000)
        puntos = int(form.monto.data // 1000)

        # Registrar la compra
        nueva_compra = Compra(
            cliente_id=cliente.id,
            monto_total=form.monto.data,
            puntos_generados=puntos,
            fecha=datetime.utcnow()
        )
        db.session.add(nueva_compra)

        # Actualizar puntos del cliente
        cliente.puntos += puntos

        try:
            db.session.commit()
            flash(f"Compra registrada ✅. Se sumaron {puntos} puntos.", "success")
            return redirect(url_for("cliente.listar_clientes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar compra: {str(e)}", "danger")

    return render_template("compras/nueva.html", form=form)

# 🟢 Ruta: Historias de compra por usuario
@compra_bp.route("/historico/<int:cliente_id>")
@role_required("admin", "general")
def historico_compras(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    compras = Compra.query.filter_by(cliente_id=cliente.id).order_by(Compra.fecha.desc()).all()
    return render_template("compras/historico.html", cliente=cliente, compras=compras)