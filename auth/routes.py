from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.login import Login
from models import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usuario = Login.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password):
            login_user(usuario)
            flash("Bienvenido!", "success")
            if usuario.rol == "admin":
                return redirect(url_for("cliente.listar_clientes"))
            else:
                return redirect(url_for("compras.registrar_compra"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))
