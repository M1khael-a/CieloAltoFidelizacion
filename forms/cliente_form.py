from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from models.cliente import Cliente

class ClienteForm(FlaskForm):
    cedula = StringField("Cédula", validators=[DataRequired()])
    nombre = StringField("Nombre", validators=[DataRequired()])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    telefono = StringField("Teléfono")
    fecha_nacimiento = DateField(
        "Fecha de nacimiento (DD-MM-YYYY)", 
        format="%Y-%m-%d"
    )
    submit = SubmitField("Guardar")

    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id = cliente_id  # guardamos el id si es edición

    # Validación personalizada de correo único
    def validate_correo(self, correo):
        cliente = Cliente.query.filter_by(correo=correo.data).first()
        if cliente and cliente.id != self.cliente_id:
            raise ValidationError("El correo ya está registrado, usa otro.")
        
    # Validación personalizada de cédula única
    def validate_cedula(self, cedula):
        cliente = Cliente.query.filter_by(cedula=cedula.data).first()
        if cliente and cliente.id != self.cliente_id:
            raise ValidationError("La cédula ya está registrada, usa otra.")