from datetime import datetime

from ..db import db

Respuesta = db.Table('Respuesta',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('alumno', db.Integer, db.ForeignKey('AlumnosTest.id'),
                     nullable=False),
    db.Column('pregunta', db.Integer, db.ForeignKey('Pregunta.id'),
                     nullable=False),
    db.Column('respuesta', db.Text))

PreguntasTest = db.Table('PreguntasTest',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('test', db.Integer, db.ForeignKey('Test.id'),
                     nullable=False),
    db.Column('pregunta', db.Integer, db.ForeignKey('Pregunta.id'),
                     nullable=False))

AlumnosTest = db.Table('AlumnosTest',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('test', db.Integer, db.ForeignKey('Test.id'),
                     nullable=False),
    db.Column('alumno', db.Integer, db.ForeignKey('Alumno.id'),
                     nullable=False),
    db.Column('answer', db.Integer),
    db.Column('code', db.String),
    db.Column('activo', db.Integer, nullable=False, default=1),)
    # pregunta = db.relationship('Pregunta', secondary=Respuesta, backref='alumnosTest', lazy=True)


class Test(db.Model):
    __tablename__='Test'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    clase = db.Column(db.Integer, db.ForeignKey('Clase.id'),
                     nullable=False)
    estructura = db.Column(db.Integer, db.ForeignKey('TipoEstructura.id'),
                      nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    uploaded = db.Column(db.Integer)
    downloaded = db.Column(db.Integer)
    profesor = db.Column(db.Integer, db.ForeignKey('Profesor.id'),
                        nullable=False)
    closed = db.Column(db.Integer)
    year = db.Column(db.Integer, db.ForeignKey('Year.id'),
                     nullable=False)
    first = db.Column(db.Integer, db.ForeignKey('Test.id'),
                     nullable=False)
    # tests = db.relationship('Test', backref='test', lazy=True)
    followUp = db.Column(db.Integer)
    final = db.Column(db.Integer)
    survey1 = db.Column(db.Integer)
    survey2 = db.Column(db.Integer)
    preguntas = db.relationship('Pregunta', secondary=PreguntasTest, backref='Test', lazy=True)
    alumnos = db.relationship('Alumno', secondary=AlumnosTest, backref='Test', lazy=True)

    def __init__(self, nombre, clase, estructura, date_created, uploaded, downloaded, profesor, closed, year, followUp, final, survey1, survey2, first=None):
        self.nombre = nombre
        self.clase = clase
        self.estructura = estructura
        self.date_created = date_created
        self.uploaded = uploaded
        self.downloaded = downloaded
        self.profesor = profesor
        self.closed = closed
        self.year = year
        self.first = first
        self.followUp = followUp
        self.final = final
        self.survey1 = survey1
        self.survey2 = survey2

    def __repr__(self):
        return '<Test %r>' % self.nombre

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'clase': self.clase,
            'estructura': self.estructura,
            'date_created': datetime.strftime(self.date_created, "%d/%m/%Y %H:%M"),
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'profesor': self.profesor,
            'closed': self.closed,
            'year': self.year,
            'first': self.first,
            'followUp': self.followUp,
            'final': self.final,
            'survey1': self.survey1,
            'survey2': self.survey2
        }