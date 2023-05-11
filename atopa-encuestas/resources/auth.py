import binascii
import os
import random
import string
import sys

from flask import Response, request, render_template
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jti, decode_token, get_jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError, \
    InvalidTokenError
from sqlalchemy.exc import IntegrityError, NoResultFound

from database import db
from database.models.colegio import Colegio
from database.models.rol import Rol
from database.models.test import AlumnosTest
from database.models.user import User
from database.token_store_redis import redis_store
from flask_restful import Resource
from datetime import datetime, timedelta

from resources.decorators import superuser
from resources.errors import SchemaValidationError, UserAlreadyExistsError, UnauthorizedError, \
    UnauthorizedAppError, InternalServerError, UserNotExistsError
from resources.token_expires_time import ExpiresTimes


class SignupApi(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user = User(colegio=body['colegio'],
                        rol=body['rol'])
            user.hash_password()
            db.session.add(user)
            db.session.commit()
            id = user.id
            db.session.close()
            return {'id': str(id)}, 200
        except UnauthorizedAppError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UnauthorizedAppError
        except KeyError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class SignupColegioApi(Resource):
    def post(self):
        try:
            db.openSession()
            colegio = Colegio(nombre=get_random_string(12))
            db.session.add(colegio)
            db.session.commit()
            id = colegio.id
            db.session.close()
            return {'id': str(id), 'nombre': colegio.nombre}, 200
        except UnauthorizedAppError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UnauthorizedAppError
        except KeyError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class LoginApi(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            colegio = Colegio.query.filter_by(nombre=body.get('nombre')).one()
            if not colegio:
                raise UnauthorizedError

            # expires = timedelta(days=7)
            access_token = create_access_token(identity=str(colegio.id))  # ,expires_delta=expires)
            refresh_token = create_refresh_token(identity=str(colegio.id))

            # Almacenar tokens en redis con status no expirados, se pone un
            # tiempo mayor en redis (1.2) para que expiren de memoria también
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, 'false', ExpiresTimes.ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, 'false', ExpiresTimes.REFRESH_EXPIRES * 1.2)
            db.session.close()
            return {'token': access_token, 'refresh': refresh_token}, 200
        except (NoResultFound):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UnauthorizedError
        except (UnauthorizedError, AttributeError):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UnauthorizedError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class LoginApiAlumno(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user = db.session.query(AlumnosTest).filter_by(code=body.get('code')).one()
            if not user:
                raise UnauthorizedError

            # expires = timedelta(days=7)
            access_token = create_access_token(identity=str(user.id))  # ,expires_delta=expires)
            refresh_token = create_refresh_token(identity=str(user.id))

            # Almacenar tokens en redis con status no expirados, se pone un
            # tiempo mayor en redis (1.2) para que expiren de memoria también
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, 'false', ExpiresTimes.ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, 'false', ExpiresTimes.REFRESH_EXPIRES * 1.2)
            db.session.close()
            return {'token': access_token, 'refresh': refresh_token}, 200
        except (UnauthorizedError, AttributeError):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UnauthorizedError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class RefreshApi(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            user_id = get_jwt_identity()
            # expires = timedelta(days=7)
            new_access_token = create_access_token(identity=str(user_id), fresh=False)  # ,expires_delta=expires)
            access_jti = get_jti(encoded_token=new_access_token)
            redis_store.set(access_jti, 'false', ExpiresTimes.ACCESS_EXPIRES * 1.2)
            return {'token': new_access_token}, 200
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @jwt_required(refresh=True)
    def delete(self):
        try:
            jti = get_jwt()['jti']
            redis_store.set(jti, 'true', ExpiresTimes.REFRESH_EXPIRES * 1.2)
            return {"msg": "El token de refresco ha expirado"}, 200
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class LogoutApi(Resource):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()['jti']
            redis_store.set(jti, 'true', ExpiresTimes.ACCESS_EXPIRES * 1.2)
            return {"msg": "El token de acceso ha expirado"}, 200
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError