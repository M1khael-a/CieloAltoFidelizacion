
## --- NUEVO USUARIO ---

# from app import app
# from models import db
# from models.login import Login

# with app.app_context():
#     if not Login.query.filter_by(username="admin").first():
#         admin = Login(username="admin", rol="admin")
#         admin.set_password("admin123")
#         db.session.add(admin)

#     if not Login.query.filter_by(username="usuario").first():
#         general = Login(username="usuario", rol="general")
#         general.set_password("usuario123")
#         db.session.add(general)

#     db.session.commit()
#     print("Usuarios iniciales creados con éxito ✅")


## -- ✨ CAMBIAR CONTRASEÑA ---

from app import app
from models import db
from models.login import Login

with app.app_context():
    user = Login.query.filter_by(username="usuario").first()
    if user:
        user.set_password("123")  # 👈 esto genera el hash
        db.session.commit()
        print("Contraseña cambiada con éxito 🚀")
