from ..db import db


class Year(db.Model):
    __tablename__ ='Year'
    id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(10), unique=True, nullable=False)
    current = db.Column(db.Integer, nullable=False)
    colegio = db.Column(db.Integer, db.ForeignKey('Colegio.id'),
                        nullable=False)
    # alumnos = db.relationship('Alumno', backref='year', lazy=True)
    # clases = db.relationship('Clase', backref='year', lazy=True)
    # tests = db.relationship('Test', backref='year', lazy=True)

    def __init__(self, school_year, current, colegio):
        self.school_year = school_year
        self.current = current
        self.colegio = colegio

    def __repr__(self):
        return '<Year %r>' % self.school_year

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'school_year': self.school_year,
            'current': self.current,
            'colegio': self.colegio
        }