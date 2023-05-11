from sqlalchemy import UniqueConstraint

from .alumno import AlumnosClase
from ..db import db


class Clase(db.Model):
    __tablename__ = 'Clase'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    grupo_edad = db.Column(db.Integer, db.ForeignKey('GrupoEdad.id'),
                        nullable=False)
    modify = db.Column(db.Integer)
    teacher = db.Column(db.Integer, db.ForeignKey('Profesor.id'),
                           nullable=False)
    year = db.Column(db.Integer, db.ForeignKey('Year.id'),
                           nullable=False)
    # alumnos = db.relationship('Alumno', secondary=AlumnosClase, backref='Clase', lazy=True)
    __table_args__ = (UniqueConstraint('nombre', 'teacher', 'year', name="nombre_unique"),
                      )
    # tests = db.relationship('Test', backref='clase', lazy=True)

    def __init__(self, nombre, grupo_edad, modify, teacher, year):
        self.nombre = nombre
        self.grupo_edad = grupo_edad
        self.modify = modify
        self.teacher = teacher
        self.year = year

    def __repr__(self):
        return '<Clase %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'grupo_edad': self.grupo_edad,
            'modify': self.modify,
            'teacher': self.teacher,
            'year': self.year
        }