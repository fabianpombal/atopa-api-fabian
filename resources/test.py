import json
import sys

from flask import Response, request, jsonify, make_response
from flask_babel import gettext
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, delete
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from database import db
from database.models.clase import Clase
from database.models.picto import Picto, PictosPregunta
from database.models.pregunta import Pregunta
from database.models.tipoPregunta import TipoPregunta
from database.models.user import User
from database.models.alumno import Alumno, AlumnosClase
from database.models.grupoEdad import GrupoEdad
from database.models.profesor import Profesor
from database.models.year import Year
from database.models.tipoEstructura import TipoEstructura
from database.models.test import Test, AlumnosTest, Respuesta, PreguntasTest

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, TestNotExistsError, TestAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, portrait, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, ListFlowable, ListItem, PageBreak, \
    Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from resources.footerCanvas import FooterCanvas


class TestsApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user.rol == 3:
                tests = db.session.query(Test, Clase, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(Clase,
                                                                                              Clase.id == Test.clase).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad, GrupoEdad.id == Clase.grupo_edad).join(Profesor,
                    Profesor.id == Test.profesor).join(User, and_(User.id == Profesor.user, User.colegio == user.colegio)).all()
            else:
                profesor = Profesor.query.filter_by(user=user_id).one()
                tests = db.session.query(Test, Clase, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(Clase,
                                                                                                             and_(Clase.id == Test.clase, Clase.teacher == profesor.id)).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad,
                                                                               GrupoEdad.id == Clase.grupo_edad).all()
            preguntas = {}
            for t in tests:
                preguntas[t[0]] = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == t[0].id, PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify(tests=[{**i[0].serialize, 'clase_nombre': i[1].nombre, 'estructura_nombre': i[2], 'grupo_edad': i[1].grupo_edad, 'grupo_edad_nombre': i[3], 'preguntas': [p.serialize for p in preguntas[i[0]]]} for i in tests])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def post(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            teacher = Profesor.query.filter_by(user=user.id).one()
            body = request.get_json()
            body['date_created'] = datetime.now()
            body['profesor'] = teacher.id
            del body['id']
            preguntas = body['preguntas']
            del body['preguntas']
            test = Test(**body)
            db.session.add(test)
            db.session.commit()
            for p in preguntas:
                insert_stmnt = PreguntasTest.insert().values(test=test.id, pregunta=p)
                db.session.execute(insert_stmnt)
            db.session.commit()
            id = test.id
            db.session.close()
            return {'id': str(id)}, 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class TestApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            test = db.session.query(Test).filter(Test.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                if key != 'preguntas':
                    setattr(test, key, value)
            if 'preguntas' in body:
                delete_stmt = delete(PreguntasTest).where(PreguntasTest.c.test == id)
                db.session.execute(delete_stmt)
                db.session.commit()
                for p in body['preguntas']:
                    insert_stmnt = PreguntasTest.insert().values(test=test.id, pregunta=p)
                    db.session.execute(insert_stmnt)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def delete(self, id):
        try:
            db.openSession()
            test = db.session.query(Test).filter_by(id=id)
            if test.one().first:
                testFirst = db.session.query(Test).filter(Test.id == test.one().first).one()
                testFirst.followUp = 0
                testFirst.final = 0
            test.delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            test = db.session.query(Test, Clase, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(Clase,
                                                                                                         and_(
                                                                                                             Clase.id == Test.clase, Test.id == id)).join(
                TipoEstructura, and_(TipoEstructura.id == Test.estructura, Test.id == id)).join(GrupoEdad,
                                                                           GrupoEdad.id == Clase.grupo_edad).one()
            preguntas = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == id,
                                                                                      PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify({**test[0].serialize, 'clase_nombre': test[1].nombre, 'estructura_nombre': test[2],
                                   'grupo_edad': test[1].grupo_edad, 'grupo_edad_nombre': test[3],
                                   'preguntas': [p.serialize for p in preguntas]})
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class TestForStudent(Resource):
    @alumno
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            alumno_current = db.session.query(AlumnosTest).filter_by(id=user_id).one()
            alumnoobj = Alumno.query.get(alumno_current.alumno)
            test = Test.query.get(alumno_current.test)
            preguntas = test.preguntas
            alumnos = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest, and_(test.id == AlumnosTest.c.test, AlumnosTest.c.alumno == Alumno.id,)).join(User, User.id == Alumno.user).filter(Alumno.id != alumnoobj.id).all()
            # por = Picto.query.filter_by(name="por qué").one()
            pictos = {}
            for p in preguntas:
                # pregunta = Pregunta.query.get(p.id)
                aux = {}
                pictosPregunta = db.session.query(PictosPregunta).filter_by(pregunta=p.id).all()
                for pi in pictosPregunta:
                    picto = Picto.query.get(pi.picto)
                    aux[pi.order] = picto.name
                pictos[p.tipo_pregunta] = aux
            db.session.close()
            return jsonify(test=test.serialize, alumnos=[{**(i[0]).serialize(code=i[1], clase=test.clase), 'nombre': i[2], 'apellidos': i[3]} for i in alumnos], preguntas=[i.serialize for i in preguntas], pictos=pictos,
                           alumno={**alumnoobj.serialize(alumno_current.code), 'nombre': alumnoobj.nombre, 'apellidos': alumnoobj.apellidos}) # , por=["por qué", por.link]
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @alumno
    def post(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            alumno_current = db.session.query(AlumnosTest).filter_by(id=user_id).one()
            test = Test.query.get(alumno_current.test)
            preguntas = test.preguntas
            body = request.get_json()
            respuestas = body['respuestas']
            stmt = AlumnosTest.update().where(AlumnosTest.c.id == user_id).values(answer=1)
            db.session.execute(stmt)
            for pregunta in preguntas:
                resp_json = {}
                for num, answer in enumerate(respuestas[str(pregunta.tipo_pregunta)]):
                    resp_json[str(num+1)] = answer
                if str(pregunta.tipo_pregunta) + "text" in respuestas:
                    for num_text, r in enumerate(respuestas[str(pregunta.tipo_pregunta) + "text"]):
                        resp_json[str(num_text+1) + 'text'] = r
                insert_stmnt = Respuesta.insert().values(alumno=alumno_current.id,
                                 pregunta=pregunta.id,
                                 respuesta=json.dumps(resp_json))
                db.session.execute(insert_stmnt)
                db.session.commit()
            db.session.close()
            return 'Respuestas guardadas', 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class OpenTest(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            test = db.session.query(Test).filter(Test.id == body['test']).one()
            clase = db.session.query(Clase).filter(Clase.id == test.clase).one()
            alumnos = db.session.query(Alumno).join(AlumnosClase, and_(AlumnosClase.c.clase == clase.id, AlumnosClase.c.alumno == Alumno.id)).all()
            test.alumnos = []
            for al in alumnos:
                insert_stmnt = AlumnosTest.insert().values(test=test.id, alumno=al.id, answer=0, code=str(test.id) + str(al.id))
                db.session.execute(insert_stmnt)
            test.uploaded = 1
            clase.modify = 0
            db.session.commit()
            db.session.close()
            return 'Test abierto', 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class CloseTest(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            test = db.session.query(Test).filter(Test.id == body['test']).one()
            clase = db.session.query(Clase).filter(Clase.id == test.clase).one()
            alumnos = db.session.query(Alumno).join(AlumnosClase, and_(AlumnosClase.c.clase == clase.id, AlumnosClase.c.alumno == Alumno.id)).all()
            for al in alumnos:
                update_stmnt = AlumnosTest.update().where(AlumnosTest.c.alumno==al.id, AlumnosTest.c.test == test.id).values(activo=0)
                db.session.execute(update_stmnt)
                db.session.commit()
            test.closed = 1
            clase.modify = 1
            if test.first:
                testFirst = db.session.query(Test).filter(Test.id == test.first).one()
                testFirst.final = 0
            db.session.commit()
            db.session.close()
            return 'Test abierto', 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class FollowUpTest(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            quiz = db.session.query(Test).filter(Test.id==body['test']).one()
            quiz.followUp = 1
            quiz.final = 1
            test = Test(nombre=quiz.nombre + " - " + gettext("seguimiento"),clase=quiz.clase, estructura=quiz.estructura,
                        date_created=datetime.now(), year=quiz.year, first=quiz.id, followUp=1 ,profesor=quiz.profesor,
                        uploaded=0, downloaded=0, closed=0, final=0, survey1=0, survey2=0)
            db.session.add(test)
            db.session.commit()
            preguntas = db.session.query(PreguntasTest).filter_by(test=quiz.id)
            for p in preguntas:
                insert_stmnt = PreguntasTest.insert().values(test=test.id, pregunta=p.pregunta)
                db.session.execute(insert_stmnt)
            db.session.commit()
            id = test.id
            db.session.close()
            return {'id': str(id)}, 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class CodesPdf(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            cuestionario = Test.query.get(body['test'])

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=100, bottomMargin=50)
            doc.pagesize = portrait(A4)
            elements = []

            data = [
                [gettext("Nombre"), gettext("Apellidos"), gettext("Alias"), gettext("DNI"), gettext("Fecha de nacimiento"),
                 gettext("Sexo"), gettext("Código")],
            ]

            alumnos = db.session.query(AlumnosTest).filter_by(test=cuestionario.id).all()
            for al in alumnos:
                student = db.session.query(Alumno, User, AlumnosClase.c.alias).join(User, and_(User.id == Alumno.user, Alumno.id == al.alumno)).join(AlumnosClase, and_(AlumnosClase.c.alumno == Alumno.id, AlumnosClase.c.clase == cuestionario.clase)).one()
                if student[2]:
                    alias = student[2]
                else:
                    alias = ''
                if student[1].DNI:
                    dni = student[1].DNI
                else:
                    dni = ''
                data.append(
                    [student[1].nombre, student[1].apellidos, alias, dni, student[1].fecha_nacimiento,
                     student[0].sexo, str(al.code)])
            style = TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-BoldOblique'),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('LINEABOVE', (0, 0), (-1, 0), 1, colors.white)
            ])

            # Configure style and word wrap
            s = getSampleStyleSheet()
            s = s['BodyText']
            s.wordWrap = 'CJK'
            s.fontName = 'Helvetica-Bold'
            data2 = []
            for r, row in enumerate(data):
                aux = []
                for c, cell in enumerate(row):
                    if c == 0 and (1 <= r <= len(data) - 1):
                        s.fontName = 'Helvetica-Oblique'
                    elif (0 <= c <= len(row) - 1) and r == 0:
                        s.fontName = 'Helvetica-Bold'
                    else:
                        s.fontName = 'Helvetica'
                    s.fontSize = 9
                    aux.append(Paragraph(cell, s))
                data2.append(aux)
            t = Table(data2)
            t.setStyle(style)

            # Send the data and build the file
            elements.append(t)
            doc.multiBuild(elements, canvasmaker=FooterCanvas)
            pdf = buffer.getvalue()
            buffer.close()
            response = make_response(pdf)
            response.headers.set('Content-Disposition', 'attachment',
                                 filename="codigos-cuestionario-{0}.pdf".format(cuestionario.nombre))
            response.headers.set('Content-Type', 'application/pdf')
            db.session.close()
            return response
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class TestsApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user.rol == 3:
                tests = db.session.query(Test, Clase, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(Clase,
                                                                                                             Clase.id == Test.clase).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad,
                                                                               GrupoEdad.id == Clase.grupo_edad).join(
                    Profesor,
                    Profesor.id == Test.profesor).join(User, and_(User.id == Profesor.user,
                                                                 User.colegio == user.colegio))
            else:
                profesor = Profesor.query.filter_by(user=user_id).one()
                tests = db.session.query(Test, Clase, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(Clase,
                                                                                                             and_(
                                                                                                                 Clase.id == Test.clase,
                                                                                                                 Clase.teacher == profesor.id)).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad,
                                                                               GrupoEdad.id == Clase.grupo_edad)
            for attr, value in body.items():
                if attr != 'idioma':
                    tests = tests.filter(getattr(Test, attr.replace('Test.', "")).like("%%%s%%" % value))
            tests = tests.all()
            preguntas = {}
            for t in tests:
                preguntas[t[0]] = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == t[0].id, PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify(tests=[{**i[0].serialize, 'clase_nombre': i[1].nombre, 'estructura_nombre': i[2],
                                   'grupo_edad': i[1].grupo_edad, 'grupo_edad_nombre': i[3],
                                   'preguntas': [p.serialize for p in preguntas[i[0]]]} for i in tests])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError