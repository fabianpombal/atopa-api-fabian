import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.profesor import Profesor
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, ProfesorNotExistsError, \
    ProfesorAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class LoggedUserProfesor(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            profesor = Profesor.query.filter_by(user=user_id).one()
            user_json = user.serialize
            del user_json['id']
            profesor_json = profesor.serialize
            profesor_json['profesor'] = profesor_json['id']
            del profesor_json['id']
            db.session.close()
            return jsonify({**user_json, **profesor_json})
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class ProfesoresApi(Resource):
    @superuser
    def get(self):
        try:
            db.openSession()
            profesores = Profesor.query.all()
            db.session.close()
            return jsonify(profesores=[i.serialize for i in profesores])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            profesor = Profesor(**body)
            db.session.add(profesor)
            db.session.commit()
            id = profesor.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ProfesorAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ProfesorApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            profesor = db.session.query(Profesor).filter(Profesor.id == id).one()
            user = db.session.query(User).filter(User.id == profesor.user).one()
            body = request.get_json()
            for key, value in body.items():
                if key in ("username", "evaluacion", "email"):
                    setattr(profesor, key, value)
                if key in ("nombre", "apellidos", "DNI", "colegio", "password", "activo", "fecha_nacimiento", "rol"):
                    setattr(user, key, value)
                    if key == "password":
                        user.hash_password()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ProfesorNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ProfesorAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def delete(self, id):
        try:
            db.openSession()
            profesor = db.session.query(Profesor).filter_by(id=id)
            db.session.query(User).filter_by(id=profesor.user).delete()
            profesor.delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ProfesorNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            profesor = Profesor.query.get(id)
            db.session.close()
            return jsonify(profesor.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ProfesorNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError