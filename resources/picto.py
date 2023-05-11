import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.picto import Picto
from database.models.user import User

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, PictoNotExistsError, PictoAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class PictosApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            pictos = Picto.query.all()
            db.session.close()
            return jsonify(pictos=[i.serialize for i in pictos])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @superuser
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            picto = Picto(**body)
            db.session.add(picto)
            db.session.commit()
            id = picto.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PictoAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class PictoApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            picto = db.session.query(Picto).filter(Picto.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(picto, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PictoNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PictoAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Picto).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PictoNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            picto = Picto.query.get(id)
            db.session.close()
            return jsonify(picto.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PictoNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError