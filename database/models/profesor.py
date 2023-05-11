from ..db import db


class Profesor(db.Model):
    __tablename__ = 'Profesor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                        nullable=False)
    evaluacion = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True, nullable=False)
    # clases = db.relationship('Clase', backref='profesor', lazy=True)
    # tests = db.relationship('Test', backref='profesor', lazy=True)

    def __init__(self, user, evaluacion, email, username):
        self.user = user
        self.evaluacion = evaluacion
        self.email = email
        self.username = username

    def __repr__(self):
        return '<Profesor %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'user': self.user,
            'evaluacion': self.evaluacion,
            'email': self.email,
            'username': self.username
        }