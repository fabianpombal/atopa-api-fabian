from sqlalchemy import UniqueConstraint

from ..db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ ='User'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellidos = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False)
    DNI = db.Column(db.String(9), nullable=True)
    colegio = db.Column(db.Integer, db.ForeignKey('Colegio.id'),
                        nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('Rol.id'),
                    nullable=False)
    validado = db.Column(db.Integer)
    password = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Integer, nullable=False, default=1)
    fecha_nacimiento = db.Column(db.String(10), nullable=True)
    __table_args__ = (UniqueConstraint('DNI', 'colegio', name="DNI_UNIQUE"),
                      UniqueConstraint('nombre', 'apellidos', 'fecha_nacimiento','rol', name="student_UNIQUE"))


    def __init__(self, nombre, apellidos, date_joined, colegio, rol, activo=1, validado=None, password=None, DNI=None, fecha_nacimiento=None):
        self.nombre = nombre
        self.apellidos = apellidos
        self.date_joined = date_joined
        self.DNI = DNI
        self.colegio = colegio
        self.rol = rol
        self.validado = validado
        self.password = password
        self.activo = activo
        self.fecha_nacimiento = fecha_nacimiento

    def __repr__(self):
        return '<User %r>' % self.nombre

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'date_joined': self.date_joined.strftime('%d/%m/%Y %H:%M'),
            'DNI': self.DNI,
            'colegio': self.colegio,
            'rol': self.rol,
            'validado': self.validado,
            'activo': self.activo,
            'fecha_nacimiento': self.fecha_nacimiento
        }