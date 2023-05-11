import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from database import db
from database.models.picto import Picto
from database.models.pregunta import Pregunta
from database.models.user import User
from database.models.grupoEdad import GrupoEdad
from database.models.tipoPregunta import TipoPregunta
from database.models.tipoEstructura import TipoEstructura

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, PreguntaNotExistsError, \
    PreguntaAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class PreguntasApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            preguntas = Pregunta.query.all()
            db.session.close()
            return jsonify(preguntas=[i.serialize for i in preguntas])
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            pregunta = Pregunta(**body)
            if 'name' and 'link' in body:
                picto = Picto.query.filter_by(name=body['name']).one()
                if not picto:
                    picto = Picto(link=body['link'], name=body['name'])
                if not pregunta.pictos:
                    pregunta.pictos = []
                pregunta.pictos.append(picto)
            db.session.add(pregunta)
            db.session.commit()
            id = pregunta.id
            db.session.close()
            return {'id': str(id)}, 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class PreguntaApi(Resource):
    @superuser
    def put(self, id):
        try:
            db.openSession()
            pregunta = db.session.query(Pregunta).filter(Pregunta.id == id).one()
            body = request.get_json()
            for key, value in body.items():
                if key not in ('name', 'link'):
                    setattr(pregunta, key, value)
            if 'name' and 'link' in body:
                picto = Picto.query.filter_by(name=body['name']).one()
                if not picto:
                    picto = Picto(link=body['link'], name=body['name'])
                if not pregunta.pictos:
                    pregunta.pictos = []
                pregunta.pictos.append(picto)
            db.session.commit()
            db.session.close()
            return '', 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @superuser
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Pregunta).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def get(self, id):
        try:
            db.openSession()
            pregunta = Pregunta.query.get(id)
            db.session.close()
            return jsonify(pregunta.serialize)
        except BadRequest:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise SchemaValidationError
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class PreguntasApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            preguntas = db.session.query(Pregunta, GrupoEdad.grupo_edad, TipoPregunta.descripcion, TipoEstructura.descripcion).join(GrupoEdad,
                                        GrupoEdad.id == Pregunta.grupo_edad).join(TipoPregunta, TipoPregunta.id == Pregunta.tipo_pregunta).join(TipoEstructura, TipoEstructura.id == Pregunta.tipo_estructura)
            for attr, value in body.items():
                if attr != 'idioma':
                    preguntas = preguntas.filter(getattr(Pregunta, attr.replace('Pregunta.', "")).like("%%%s%%" % value))
            preguntas = preguntas.all()
            db.session.close()
            return jsonify(preguntas=[{**i[0].serialize, 'grupo_edad_nombre': i[1], 'tipo_pregunta_nombre': i[2], 'tipo_estructura_nombre': i[3]} for i in preguntas])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class PreguntasTestApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            preguntas1 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==1, Pregunta.tipo_estructura==body['tipo_estructura'], Pregunta.grupo_edad==body['grupo_edad']).all()
            preguntas2 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==2, Pregunta.tipo_estructura==body['tipo_estructura'],
                                                           Pregunta.grupo_edad==body['grupo_edad']).all()
            preguntas3 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==3, Pregunta.tipo_estructura==body['tipo_estructura'],
                                                           Pregunta.grupo_edad==body['grupo_edad']).all()
            preguntas4 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==4, Pregunta.tipo_estructura==body['tipo_estructura'],
                                                           Pregunta.grupo_edad==body['grupo_edad']).all()
            preguntas5 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==5, Pregunta.tipo_estructura==body['tipo_estructura'],
                                                           Pregunta.grupo_edad==body['grupo_edad']).all()
            preguntas6 = db.session.query(Pregunta).filter(Pregunta.tipo_pregunta==6, Pregunta.tipo_estructura==body['tipo_estructura'],
                                                           Pregunta.grupo_edad==body['grupo_edad']).all()
            db.session.close()
            return jsonify(preguntas1=[i.serialize for i in preguntas1], preguntas2=[i.serialize for i in preguntas2], preguntas3=[i.serialize for i in preguntas3], preguntas4=[i.serialize for i in preguntas4], preguntas5=[i.serialize for i in preguntas5], preguntas6=[i.serialize for i in preguntas6])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise PreguntaNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError