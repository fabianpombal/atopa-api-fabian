import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.user import User
from database.models.pregunta import Pregunta
from database.models.preferencias import Preferencias

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, PreferenciasNotExistsError, \
    PreferenciasAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class PreferenciasApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            preferencias = Preferencias.query.all()
            db.session.close()
            return jsonify(preferencias=[i.serialize for i in preferencias])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def post(self):
        try:
            body = request.get_json()
            preferencias = Preferencias(**body)
            db.openSession()
            db.session.add(preferencias)
            db.session.commit()
            db.session.close()
            id = preferencias.id
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class PreferenciaApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            preferencias = db.session.query(Preferencias).filter(Preferencias.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(preferencias, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Preferencias).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def get(self, id):
        try:
            db.openSession()
            tipoEstructura = Preferencias.query.get(id)
            db.session.close()
            return jsonify(tipoEstructura.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class PreferenciasUser(Resource):
    @profesor
    def get(self, id):
        try:
            db.openSession()
            tipoEstructura = Preferencias.query.filter(Preferencias.user == id).one()
            db.session.close()
            return jsonify(tipoEstructura.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreferenciasNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError