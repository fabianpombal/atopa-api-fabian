import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from database.models.user import User
from database.models.pregunta import Pregunta
from database.models.tipoPregunta import TipoPregunta

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, TipoPreguntaNotExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class TipoPreguntasApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            tipoPreguntas = TipoPregunta.query.all()
            db.session.close()
            return jsonify(tipoPreguntas=[i.serialize for i in tipoPreguntas])
        except AttributeError:
            raise TipoPreguntaNotExistsError
        except Exception:
            raise InternalServerError
    @superuser
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            tipoPregunta = TipoPregunta(**body)
            db.session.add(tipoPregunta)
            db.session.commit()
            id = tipoPregunta.id
            db.session.close()
            return {'id': str(id)}, 200
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class TipoPreguntaApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            tipoPregunta = db.session.query(TipoPregunta).filter(TipoPregunta.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(tipoPregunta, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        # except InvalidQueryError:
        #     raise SchemaValidationError
        except AttributeError as e:
            print(e)
            raise TipoPreguntaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(TipoPregunta).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            raise TipoPreguntaNotExistsError
        except Exception:
            raise InternalServerError
    @profesor
    def get(self, id):
        try:
            db.openSession()
            tipoPregunta = TipoPregunta.query.get(id)
            db.session.close()
            return jsonify(tipoPregunta.serialize)
        except AttributeError:
            raise TipoPreguntaNotExistsError
        except Exception:
            raise InternalServerError