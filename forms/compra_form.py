from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CompraForm(FlaskForm):
    cedula = StringField("Cédula del cliente", validators=[DataRequired()])
    monto = DecimalField("Monto de la compra", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Registrar compra")
