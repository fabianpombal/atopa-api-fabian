from ..db import db

PictosPregunta = db.Table('PictosPregunta',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('pregunta', db.Integer, db.ForeignKey('Pregunta.id'),
                     nullable=False),
    db.Column('picto', db.Integer, db.ForeignKey('Picto.id'),
                     nullable=False),
    db.Column('order', db.Integer, nullable=False, default=1))

class Picto(db.Model):
    __tablename__='Picto'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # preguntas = db.relationship('Pregunta', secondary=PictosPregunta, backref='picto', lazy=True)

    def __init__(self, link, name):
        self.link = link
        self.name = name

    def __repr__(self):
        return '<Picto %r>' % self.name

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'link': self.link,
            'name': self.name
        }