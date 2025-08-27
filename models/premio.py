from models import db

class Premio(db.Model):
    __tablename__ = "premios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    puntos_requeridos = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Premio {self.nombre} - {self.puntos_requeridos} pts>"
