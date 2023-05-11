import os
import sys

from flask import Response, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.colegio import Colegio
from database.models.rol import Rol
from database.models.user import User
from flask_restful import Resource
from resources.errors import UserNotExistsError, InternalServerError, SchemaValidationError, UpdatingUserError, \
    DeletingUserError, UnauthorizedAppError, UserAlreadyExistsError
from resources.decorators import superuser, profesor


class UsersApi(Resource):
    @superuser
    def get(self):
        try:
            db.openSession()
            users = User.query.all()
            db.session.close()
            return jsonify(users=[i.serialize for i in users])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class UserApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            user = db.session.query(User).filter(User.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(user, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def delete(self, id):
        try:
            db.openSession()
            db.session(User).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def get(self, id):
        try:
            db.openSession()
            user = User.query.get(id)
            db.session.close()
            return jsonify(user.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise UserNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
