from flask import Flask, render_template
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import desc
from datetime import date
from models.login import Login
from routes.versiculos import versiculos
import random
import pytz
from models import db
from flask_login import login_required
from auth.decorators import role_required
from routes.mail import mail  # 👈 Importamos mail pero sin circular import

# Importar los Blueprints
from routes.cliente import cliente_bp
from routes.auth import auth_bp
from routes.compra import compra_bp
from routes.usuarios import users_bp

# Inicialización de extensiones
app = Flask(__name__)
app.config.from_object(Config)

# Inicialización extensiones
mail.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

# Registrar los Blueprints
app.register_blueprint(cliente_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(compra_bp)
app.register_blueprint(users_bp, url_prefix="/users")

# 👇 Importar aquí los modelos para que Flask-Migrate los detecte
from models.cliente import Cliente
from models.compra import Compra
from models.premio import Premio
from auth.routes import auth_bp

# Página 403 personalizada
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@login_manager.user_loader
def load_user(user_id):
    return Login.query.get(int(user_id))

@app.route("/")
@role_required("admin", "general")
def index():
    # Top clientes
    top_clientes = Cliente.query.order_by(Cliente.puntos.desc()).limit(5).all()

    dia = date.today().toordinal()
    random.seed(dia)
    versiculo_del_dia = random.choice(versiculos)

    # Cumpleaños del día (solo mes y día)
    hoy = date.today()
    cumpleaneros = Cliente.query.filter(
        db.extract('day', Cliente.fecha_nacimiento) == hoy.day,
        db.extract('month', Cliente.fecha_nacimiento) == hoy.month
    ).all()

    return render_template(
        'dashboard.html',
        versiculo=versiculo_del_dia,
        top_clientes=top_clientes,
        cumpleaneros=cumpleaneros
    )

# 🔹 Filtro para hora en Bogotá
@app.template_filter("bogota_time")
def bogota_time(value, fmt="%d-%m-%Y %H:%M"):
    if value is None:
        return ""
    bogota = pytz.timezone("America/Bogota")
    return value.replace(tzinfo=pytz.utc).astimezone(bogota).strftime(fmt)


if __name__ == "__main__":
    app.run(debug=True)
