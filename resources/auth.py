import binascii
import os
import sys

from flask import Response, request, render_template
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jti, decode_token, get_jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError, \
    InvalidTokenError
from sqlalchemy.exc import IntegrityError, NoResultFound

from database import db
from database.models.colegio import Colegio
from database.models.preferencias import Preferencias
from database.models.profesor import Profesor
from database.models.rol import Rol
from database.models.test import AlumnosTest
from database.models.user import User
from database.models.year import Year
from database.token_store_redis import redis_store
from flask_restful import Resource
from datetime import datetime, timedelta

from resources.decorators import superuser
from resources.errors import SchemaValidationError, UserAlreadyExistsError, UnauthorizedError, \
    UnauthorizedAppError, InternalServerError, UserNotExistsError
from resources.mail import send_email
from resources.token_expires_time import ExpiresTimes


class SignupApi(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            date = datetime.now()
            year = Year.query.filter(Year.colegio == body['colegio'], Year.current == 1).one()
            user = User(nombre=body['nombre'], apellidos=body['apellidos'],
                        date_joined=date, DNI=body['DNI'], colegio=body['colegio'],
                        rol=body['rol'], validado=body['validado'], password=body['password'])
            user.hash_password()
            db.session.add(user)
            db.session.commit()
            id = user.id
            preferencias = Preferencias(user=id)
            db.session.add(preferencias)
            db.session.commit()
            profesor = Profesor(user=id, evaluacion=body['evaluacion'], email=body['email'], username=body['username'])
            db.session.add(profesor)
            db.session.commit()
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

class LoginApi(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            teacher = Profesor.query.filter_by(username=body.get('username')).one()
            user = User.query.get(teacher.user)
            authorized = user.check_password(body.get('password'))
            if not authorized:
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


class ForgotPassword(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            url = request.host_url + '/auth/reset/'  # cambiar url para la app de gestion
            user = User.query.filter_by(email=body['email']).one()
            expires = timedelta(hours=24)
            token = binascii.hexlify(os.urandom(3)).decode()
            redis_store.set(token, str(user.id), expires)
            db.session.close()
            return send_email('Cambie su contraseña',
                              sender='', #add email
                              recipients=[user.email],
                              text_body=render_template('email/reset_password.txt',
                                                        url=url + token),
                              html_body=render_template('email/reset_password.html',
                                                        url=url + token))
        except SchemaValidationError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResetPassword(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            reset_token = body.get('reset_token')
            password = body.get('password')

            if not reset_token or not password:
                raise SchemaValidationError

            user_id = redis_store.get(reset_token)

            user = db.session.query(User).filter(User.id == user_id).one()

            user.password = password
            user.hash_password()
            db.session.commit()
            db.session.close()
            return send_email('Cotraseña cambiada con éxito',
                              sender='', #add email
                              recipients=[user.email],
                              text_body='La contraseña se ha cambiado con éxito',
                              html_body='<p>La contraseña se ha cambiado con éxito</p>')

        except SchemaValidationError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except ExpiredSignatureError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ExpiredSignatureError
        except (DecodeError, InvalidTokenError):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InvalidTokenError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ChangePassword(Resource):
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            password = body.get('password')
            if 'user' in body:
                user_id = body.get('user')
                user = db.session.query(User).filter(User.id == user_id).one()
            elif 'username' in body:
                username = body.get('username')
                user = db.session.query(User).filter(User.username == username).one()

            if not password or (not user_id and not username):
                raise SchemaValidationError

            user.password = password
            user.hash_password()
            db.session.commit()
            db.session.close()
            return '', 200
        except SchemaValidationError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError