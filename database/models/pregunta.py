from flask_babel import gettext

from .picto import PictosPregunta
from .test import PreguntasTest, Respuesta
from ..db import db


class Pregunta(db.Model):
    __tablename__ = 'Pregunta'
    id = db.Column(db.Integer, primary_key=True)
    pregunta = db.Column(db.Text, nullable=False)
    tipo_estructura = db.Column(db.Integer, db.ForeignKey('TipoEstructura.id'),
                                nullable=False)
    tipo_pregunta = db.Column(db.Integer, db.ForeignKey('TipoPregunta.id'),
                              nullable=False)
    grupo_edad = db.Column(db.Integer, db.ForeignKey('GrupoEdad.id'),
                           nullable=False)
    # alumnos_test = db.relationship('AlumnosTest', secondary=Respuesta, backref='pregunta', lazy=True)
    pictos = db.relationship('Picto', secondary=PictosPregunta, backref='Pregunta', lazy=True)

    # tests = db.relationship('Test', secondary=PreguntasTest, backref='pregunta', lazy=True)

    def __init__(self, pregunta, tipo_estructura, tipo_pregunta, grupo_edad):
        self.pregunta = pregunta
        self.tipo_estructura = tipo_estructura
        self.tipo_pregunta = tipo_pregunta
        self.grupo_edad = grupo_edad

    def __repr__(self):
        return '<Pregunta %r>' % self.pregunta

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'pregunta': gettext(self.pregunta),
            'tipo_estructura': self.tipo_estructura,
            'tipo_pregunta': self.tipo_pregunta,
            'grupo_edad': self.grupo_edad
        }
