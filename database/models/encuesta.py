from ..db import db

class Encuesta(db.Model):
    __tablename__='Encuesta'
    id = db.Column(db.Integer, primary_key=True)
    respuesta = db.Column(db.Text, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                        nullable=False)
    test = db.Column(db.Integer, db.ForeignKey('Test.id'),
                     nullable=True)
    # preguntas = db.relationship('Pregunta', secondary=PictosPregunta, backref='picto', lazy=True)

    def __init__(self, respuesta, user, test):
        self.respuesta = respuesta
        self.user = user
        self.test = test

    def __repr__(self):
        return '<Encuesta %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'respuesta': self.respuesta,
            'user': self.user,
            'test': self.test
        }