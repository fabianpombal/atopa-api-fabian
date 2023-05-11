from sqlalchemy import UniqueConstraint

from ..db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ ='User'
    id = db.Column(db.Integer, primary_key=True)
    colegio = db.Column(db.Integer, db.ForeignKey('Colegio.id'),
                        nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('Rol.id'),
                    nullable=False)


    def __init__(self, colegio, rol):
        self.colegio = colegio
        self.rol = rol

    def __repr__(self):
        return '<User %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'colegio': self.colegio,
            'rol': self.rol
        }