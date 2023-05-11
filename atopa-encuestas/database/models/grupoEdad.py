from ..db import db


class GrupoEdad(db.Model):
    __tablename__ = "GrupoEdad"
    id = db.Column(db.Integer, primary_key=True)
    grupo_edad = db.Column(db.String(45), unique=True, nullable=False)
    franja_edad = db.Column(db.String(45), nullable=False)

    def __init__(self, grupo_edad, franja_edad):
        self.grupo_edad = grupo_edad
        self.franja_edad = franja_edad

    def __repr__(self):
        return '<Grupo Edad %r>' % self.grupo_edad

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'grupo_edad': self.grupo_edad,
            'franja_edad': self.franja_edad
        }