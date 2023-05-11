from datetime import datetime

from ..db import db

Respuesta = db.Table('Respuesta',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('alumno', db.Integer, db.ForeignKey('AlumnosTest.id'),
                     nullable=False),
    db.Column('pregunta', db.Integer, db.ForeignKey('Pregunta.id'),
                     nullable=False),
    db.Column('respuesta', db.Text))

PreguntasTest = db.Table('PreguntasTest',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('test', db.Integer, db.ForeignKey('Test.id'),
                     nullable=False),
    db.Column('pregunta', db.Integer, db.ForeignKey('Pregunta.id'),
                     nullable=False))

AlumnosTest = db.Table('AlumnosTest',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('test', db.Integer, db.ForeignKey('Test.id'),
                     nullable=False),
    db.Column('alumno', db.Integer, db.ForeignKey('Alumno.id'),
                     nullable=False),
    db.Column('answer', db.Integer),
    db.Column('code', db.String),)


class Test(db.Model):
    __tablename__='Test'
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer, db.ForeignKey('Test.id'),
                     nullable=False)
    grupo_edad = db.Column(db.Integer, db.ForeignKey('GrupoEdad.id'),
                           nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                     nullable=False)

    def __init__(self, grupo_edad, user, first=None):
        self.grupo_edad = grupo_edad
        self.first = first
        self.user = user

    def __repr__(self):
        return '<Test %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'first': self.first,
            'grupo_edad': self.grupo_edad,
            'user': self.user
        }