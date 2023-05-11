from ..db import db

class Rol(db.Model):
  __tablename__ ='Rol'
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(255), unique=True, nullable=False)
  admin = db.Column(db.Integer, nullable=False)
  # users = db.relationship('User', backref='rol', lazy=True)

  def __init__(self, nombre, admin):
    self.nombre = nombre
    self.admin = admin

  def __repr__(self):
    return '<Rol %r>' % self.nombre

  @property
  def serialize(self):
    """Return object data in easily serializable format"""
    return {
      'id': self.id,
      'nombre': self.nombre,
      'admin': self.admin
    }