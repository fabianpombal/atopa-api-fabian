from ..db import db

from hashlib import sha1

class Colegio(db.Model):
    __tablename__='Colegio'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    fecha_inicio = db.Column(db.String(5), nullable=False, default='01-09')
    localidad = db.Column(db.String(255), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    # users = db.relationship('User', backref='colegio', lazy=True)

    

    def __init__(self, nombre, email, fecha_inicio, localidad):
        self.nombre = nombre
        self.email = email
        self.fecha_inicio = fecha_inicio
        self.localidad = localidad
        self.calculate_hash()


    def __repr__(self):
        return '<Colegio %r>' % self.nombre

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'fecha_inicio': self.fecha_inicio,
            'localidad': self.localidad,
            'hash': self.hash
        }

   
    def to_json(self):
        """Return an object to post into other api"""
        obj = {
            'nombre': self.nombre,
            'hash': self.hash
        }
        return obj
    
    def calculate_hash(self):
        cadena = f"{self.nombre}{self.email}{self.fecha_inicio}{self.localidad}"
        self.hash = sha1(cadena.encode("utf-8")).hexdigest()
        
    
    
    
