from models import db
from datetime import datetime

class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    monto_total = db.Column(db.Float, nullable=False)
    puntos_generados = db.Column(db.Integer, nullable=False)

    cliente = db.relationship("Cliente", backref="compras", lazy=True)

    def __repr__(self):
        return f"<Compra Cliente={self.cliente_id} Monto={self.monto_total} Puntos={self.puntos_generados}>"
