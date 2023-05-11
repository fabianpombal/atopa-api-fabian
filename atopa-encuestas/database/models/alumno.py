from sqlalchemy import and_, UniqueConstraint

from ..db import db
from flask_babel import gettext

class Alumno(db.Model):
    __tablename__='Alumno'
    id = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.String(1), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                        nullable=False)

    def __init__(self, sexo, user):
        self.sexo = sexo
        self.user = user

    def __repr__(self):
        return '<Alumno %r>' % self.id

    def serialize(self, code=None):
        """Return object data in easily serializable format"""
        if code:
            return {
                'id': self.id,
                'sexo': self.sexo,
                'user': self.user,
                'code': code,
            }
        else:
            return {
                'id': self.id,
                'sexo': self.sexo,
                'user': self.user,
            }
    @property
    def sexo_display(self):
        if self.sexo == 'H':
            return gettext('Hombre')
        elif self.sexo == 'M':
            return gettext('Mujer')
        else:
            return ''
