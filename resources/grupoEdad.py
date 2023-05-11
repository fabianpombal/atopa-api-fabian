import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.grupoEdad import GrupoEdad
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, GrupoEdadNotExistsError, \
    GrupoEdadAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class GrupoEdadesApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            grupoEdades = GrupoEdad.query.all()
            db.session.close()
            return jsonify(grupoEdades=[i.serialize for i in grupoEdades])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            grupoEdad = GrupoEdad(**body)
            db.session.add(grupoEdad)
            db.session.commit()
            id = grupoEdad.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise GrupoEdadAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class GrupoEdadApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            grupoEdad = db.session.query(GrupoEdad).filter(GrupoEdad.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(grupoEdad, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise GrupoEdadNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise GrupoEdadAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(GrupoEdad).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise GrupoEdadNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @jwt_required()
    def get(self, id):
        try:
            db.openSession()
            grupoEdad = GrupoEdad.query.get(id)
            db.session.close()
            return jsonify(grupoEdad.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise GrupoEdadNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError