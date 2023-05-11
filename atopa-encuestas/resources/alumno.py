import csv
import io
import sys


from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from database import db
from database.models.rol import Rol
from database.models.test import AlumnosTest, Test
from database.models.user import User
from database.models.pregunta import Pregunta
from database.models.alumno import Alumno

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, AlumnoNotExistsError, AlumnoAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class AlumnosApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            alumnos = db.session.query(Alumno, User).join(User, and_(User.id == Alumno.user,
                        User.colegio == user.colegio)).all()
            db.session.close()
            return jsonify(alumnos=[{**(i[0]).serialize(None), **i[1].serialize, 'id': i[0].id} for i in alumnos])
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user_id = get_jwt_identity()
            user_log = User.query.get(user_id)
            rol = Rol.query.filter_by(nombre="alumno").one().id
            if 'alumnos' in body:
                for al in body['alumnos']:
                    if 'colegio' not in al:
                        al['colegio'] = user_log.colegio
                    elif not al['colegio']:
                        al['colegio'] = user_log.colegio
                    user = User(colegio=al['colegio'], rol=rol)
                    db.session.add(user)
                    db.session.commit()
                    alumno = Alumno(sexo=al['sexo'],user=user.id)
                    db.session.add(alumno)
                    db.session.commit()

            else:
                if 'colegio' not in body:
                    body['colegio'] = user_log.colegio
                elif not body['colegio']:
                    body['colegio'] = user_log.colegio
                user = User(colegio=body['colegio'], rol=rol)
                db.session.add(user)
                db.session.commit()
                alumno = Alumno(sexo=body['sexo'], user=user.id)
                db.session.add(alumno)
                db.session.commit()
            db.session.close()
            return '', 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class AlumnoApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            alumno = db.session.query(Alumno).filter(Alumno.id == id).one()
            user = db.session.query(User).filter(User.id == alumno.user).one()
            body = request.get_json()
            for key, value in body.items():
                if key == "sexo":
                    setattr(alumno, key, value)
                if key == "colegio":
                    setattr(user, key, value)
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def delete(self, id):
        try:
            db.openSession()
            alumno = db.session.query(Alumno).filter_by(id = id).one()
            db.session.query(User).filter(User.id == alumno.user).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            alumno = db.session.query(Alumno, User).join(User,and_(User.id == Alumno.user, Alumno.id == id)).one()
            db.session.close()
            return jsonify({**(alumno[0]).serialize(None), **alumno[1].serialize})
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class AlumnosApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            alumnos = db.session.query(Alumno, User).join(User, and_(User.id == Alumno.user, User.colegio == user.colegio))
            for attr, value in body.items():
                if attr.startswith('Alumno.'):
                    if value:
                        alumnos = alumnos.filter(getattr(Alumno, attr.replace('Alumno.', "")).like("%%%s%%" % value))
                    else:
                        alumnos = alumnos.filter(getattr(Alumno, attr.replace('Alumno.', "")).is_(value))
                else:
                    alumnos = alumnos.filter(getattr(User, attr.replace('User.', "")).like("%%%s%%" % value))
            alumnos = alumnos.all()
            db.session.close()
            jsonObj = []
            for i in alumnos:
                jsonObj.append({**(i[0]).serialize(), **i[1].serialize, 'id': i[0].id})
            return jsonify(alumnos=jsonObj)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise AlumnoNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError