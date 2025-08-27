from models.cliente import db, Cliente

def crear_cliente(nombre, correo, telefono=None, fecha_nacimiento=None):
    nuevo_cliente = Cliente(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        fecha_nacimiento=fecha_nacimiento
    )
    db.session.add(nuevo_cliente)
    db.session.commit()
    return nuevo_cliente

def obtener_cliente_por_id(cliente_id):
    return Cliente.query.get(cliente_id)

def listar_clientes():
    return Cliente.query.all()

def agregar_puntos(cliente_id, puntos):
    cliente = Cliente.query.get(cliente_id)
    if cliente:
        cliente.puntos += puntos
        db.session.commit()
    return cliente
