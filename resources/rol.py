import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.rol import Rol
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, RolNotExistsError, RolAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class RolesApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            roles = Rol.query.all()
            db.session.close()
            return jsonify(roles=[i.serialize for i in roles])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            rol = Rol(**body)
            db.session.add(rol)
            db.session.commit()
            id = rol.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise RolAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class RolApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            rol = db.session.query(Rol).filter(Rol.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(rol, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise RolNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise RolAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Rol).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise RolNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def get(self, id):
        try:
            db.openSession()
            rol = Rol.query.get(id)
            db.session.close()
            return jsonify(rol.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise RolNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError