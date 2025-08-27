from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.login import Login

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
                return redirect(url_for("index"))
            else:
                return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("ingreso/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))
