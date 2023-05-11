import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.colegio import Colegio
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, ColegioNotExistsError, \
    ColegioAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class ColegiosApi(Resource):
    def get(self):
        try:
            db.openSession()
            colegios = Colegio.query.all()
            db.session.close()
            return jsonify(colegios=[i.serialize for i in colegios])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            colegio = Colegio(nombre=body['nombre'])
            db.session.add(colegio)
            db.session.commit()
            id = colegio.id
            db.session.commit()
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ColegioApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            colegio = db.session.query(Colegio).filter(Colegio.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(colegio, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Colegio).filter_by(id = id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            colegio = Colegio.query.get(id)
            db.session.close()
            return jsonify(colegio.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
