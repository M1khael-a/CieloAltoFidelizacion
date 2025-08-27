from models import db

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    puntos = db.Column(db.Integer, default=0)
    

        # Función para descontar puntos al redimir
    def redimir_premio(self, premio):
        if self.puntos >= premio.puntos_requeridos:
            self.puntos -= premio.puntos_requeridos
            return True
        return False

    def __repr__(self):
        return f"<Cliente {self.nombre} - Cédula: {self.cedula}>"
