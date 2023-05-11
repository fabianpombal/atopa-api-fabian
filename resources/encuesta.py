import json
import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.encuesta import Encuesta
from database.models.test import Test
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, EncuestaNotExistsError, EncuestaAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class EncuestasApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            encuestas = Encuesta.query.all()
            db.session.close()
            return jsonify(encuestas=[i.serialize for i in encuestas])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def post(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            body = request.get_json()
            # user = User.query.get(user_id)
            if 'test' in body:
                test = body['test']
                testObj = db.session.query(Test).filter(Test.id == test).one()
                if testObj.first:
                    setattr(testObj, 'survey2', 1)
                else:
                    setattr(testObj, 'survey1', 1)
                db.session.commit()
            else:
                test = None
            encuesta = Encuesta(user=user_id,test=test, respuesta=json.dumps(body['respuesta']))
            db.session.add(encuesta)
            db.session.commit()
            id = encuesta.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise EncuestaAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class EncuestaApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            encuesta = db.session.query(Encuesta).filter(Encuesta.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(encuesta, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise EncuestaNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise EncuestaAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Encuesta).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise EncuestaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            encuesta = Encuesta.query.get(id)
            db.session.close()
            return jsonify(encuesta.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise EncuestaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError