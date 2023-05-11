from ..db import db


class TipoEstructura(db.Model):
    __tablename__ = "TipoEstructura"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(45), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    # preguntas = db.relationship('Pregunta', backref='tipoEstructura', lazy=True)
    # tests = db.relationship('Test', backref='tipoEstructura', lazy=True)

    def __init__(self, tipo, descripcion):
        self.tipo = tipo
        self.descripcion = descripcion

    def __repr__(self):
        return '<Tipo Estructura %r>' % self.tipo

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'descripcion': self.descripcion
        }