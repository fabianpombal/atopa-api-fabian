from ..db import db


class Colegio(db.Model):
    __tablename__='Colegio'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('Rol.id'),
                    nullable=False)

    def __init__(self, nombre, rol):
        self.nombre = nombre
        self.rol = rol

    def __repr__(self):
        return '<Colegio %r>' % self.nombre

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rol': self.rol
        }
