import json
import sys

from flask import Response, request, jsonify, make_response
from flask_babel import gettext
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, delete
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from database import db
from database.models.pregunta import Pregunta
from database.models.tipoPregunta import TipoPregunta
from database.models.user import User
from database.models.alumno import Alumno
from database.models.grupoEdad import GrupoEdad
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



class TestsApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            tests = db.session.query(Test, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad, GrupoEdad.id == Test.grupo_edad).join(User, and_(User.id == Test.user, User.colegio == user.colegio)).all()
            preguntas = {}
            for t in tests:
                preguntas[t[0]] = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == t[0].id, PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify(tests=[{**i[0].serialize, 'estructura_nombre': i[1], 'grupo_edad_nombre': i[2], 'preguntas': [p.serialize for p in preguntas[i[0]]]} for i in tests])
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
            body = request.get_json()
            body['user'] = user.id
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
            test = db.session.query(Test, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(
                TipoEstructura, and_(TipoEstructura.id == Test.estructura, Test.id == id)).join(GrupoEdad,
                                                                           GrupoEdad.id == Test.grupo_edad).one()
            preguntas = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == id,
                                                                                      PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify({**test[0].serialize, 'estructura_nombre': test[2],
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
    @superuser
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


class TestsApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            tests = db.session.query(Test, TipoEstructura.descripcion, GrupoEdad.grupo_edad).join(
                    TipoEstructura, TipoEstructura.id == Test.estructura).join(GrupoEdad,
                                                                               GrupoEdad.id == Test.grupo_edad).join(User, and_(User.id == Test.user,
                                                                 User.colegio == user.colegio))
            for attr, value in body.items():
                if attr != 'idioma':
                    tests = tests.filter(getattr(Test, attr.replace('Test.', "")).like("%%%s%%" % value))
            tests = tests.all()
            preguntas = {}
            for t in tests:
                preguntas[t[0]] = db.session.query(Pregunta).join(PreguntasTest, and_(PreguntasTest.c.test == t[0].id, PreguntasTest.c.pregunta == Pregunta.id)).all()
            db.session.close()
            return jsonify(tests=[{**i[0].serialize, 'estructura_nombre': i[1], 'grupo_edad_nombre': i[2],
                                   'preguntas': [p.serialize for p in preguntas[i[0]]]} for i in tests])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise TestNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError