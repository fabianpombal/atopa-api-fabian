import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.clase import Clase
from database.models.user import User
from database.models.alumno import Alumno
from database.models.year import Year
from database.models.test import Test

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, YearNotExistsError, YearAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class YearsApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            years = Year.query.filter(Year.colegio == user.colegio).all()
            db.session.close()
            return jsonify(years=[i.serialize for i in years])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            year = Year(**body)
            db.session.add(year)
            db.session.commit()
            id = year.id
            db.session.close()
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise YearAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class YearApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            year = db.session.query(Year).filter(Year.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                setattr(year, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise YearNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise YearAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Year).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise YearNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            year = Year.query.get(id)
            db.session.close()
            return jsonify(year.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise YearNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError