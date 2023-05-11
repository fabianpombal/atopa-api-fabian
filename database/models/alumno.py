from sqlalchemy import and_, UniqueConstraint

from .test import AlumnosTest
from .user import User
from ..db import db
from flask_babel import gettext

AlumnosClase = db.Table('AlumnosClase',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('alumno', db.Integer, db.ForeignKey('Alumno.id'),
                     nullable=False),
    db.Column('clase', db.Integer, db.ForeignKey('Clase.id'),
                     nullable=False),
    db.Column('alias', db.String(45), nullable=False),
    db.UniqueConstraint('alumno', 'clase', name="alumno_UNIQUE"),
    db.UniqueConstraint('alias', 'clase', name="alias_UNIQUE"))

class Alumno(db.Model):
    __tablename__='Alumno'
    id = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.String(1), nullable=False)
    alias = db.Column(db.String(45), nullable=True)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                        nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)
    # clases = db.relationship('Clase', secondary=AlumnosClase, backref='Alumno', lazy=True)
    # tests = db.relationship('Test', secondary=AlumnosTest, backref='alumno', lazy=True)

    def __init__(self, sexo, user, alias, activo=1):
        self.sexo = sexo
        self.user = user
        self.alias = alias
        self.activo = activo

    def __repr__(self):
        return '<Alumno %r>' % self.id

    def serialize(self, clase, code=None):
        """Return object data in easily serializable format"""
        if code:
            return {
                'id': self.id,
                'clase': clase,
                'alias': self.alias,
                'sexo': self.sexo,
                'user': self.user,
                'code': code,
                'activo': self.activo
            }
        else:
            return {
                'id': self.id,
                'clase': clase,
                'alias': self.alias,
                'sexo': self.sexo,
                'user': self.user,
                'activo': self.activo
            }
    @property
    def sexo_display(self):
        if self.sexo == 'H':
            return gettext('Hombre')
        elif self.sexo == 'M':
            return gettext('Mujer')
        else:
            return ''
    @property
    def nombre(self):
        return db.session.query(User).join(Alumno, and_(Alumno.user == User.id, Alumno.id == self.id)).one().nombre

    @property
    def apellidos(self):
        return db.session.query(User).join(Alumno, and_(Alumno.user == User.id, Alumno.id == self.id)).one().apellidos
