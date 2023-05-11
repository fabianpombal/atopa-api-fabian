import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, delete
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.clase import Clase
from database.models.user import User
from database.models.alumno import Alumno, AlumnosClase
from database.models.grupoEdad import GrupoEdad
from database.models.profesor import Profesor
from database.models.year import Year

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, ClaseNotExistsError, ClaseAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser

class ClasesApi(Resource):
    @profesor
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user.rol == 3:
                clases = db.session.query(Clase).join(Profesor, Profesor.id == Clase.teacher).join(User, and_(User.id == Profesor.user, User.colegio == user.colegio)).all()
            else:
                profesor = Profesor.query.filter_by(user=user_id).one()
                clases = Clase.query.filter(Clase.teacher == profesor.id).all()
            jsonObj = []
            for i in clases:
                alumnos = db.session.query(Alumno, User, Clase).join(User, User.id == Alumno.user).join(AlumnosClase, and_(AlumnosClase.c.clase == i.id, AlumnosClase.c.alumno == Alumno.id)).all()
                jsonObj.append({**i.serialize, 'alumnos': [{**(j[0]).serialize(j[2].id), **j[1].serialize, 'id': j[0].id} for j in alumnos]})
            db.session.close()
            return jsonify(clases=jsonObj)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    @profesor
    def post(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            body = request.get_json()
            user = User.query.get(user_id)
            teacher = Profesor.query.filter_by(user=user.id).one()
            clase = Clase(nombre=body['nombre'],grupo_edad=body['grupo_edad'],year=body['year'],modify=body['modify'], teacher=teacher.id)
            db.session.add(clase)
            db.session.commit()
            id = clase.id
            errors = []
            if 'alumnos' in body:
                for a in body['alumnos']:
                    try:
                        alumno = db.session.query(Alumno, User).join(User, Alumno.user == User.id).filter(Alumno.id == a['id']).one()
                        insert_stmnt = AlumnosClase.insert().values(clase=id, alumno=alumno[0].id, alias=alumno[0].alias)
                        db.session.execute(insert_stmnt)
                        db.session.commit()
                    except IntegrityError as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
                        if 'alias_UNIQUE' in str(e):
                            errors.append("No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[1].apellidos + " ALIAS YA EXISTE EN ESTA CLASE (" + alumno[0].alias + ")" + '\n')
                        if 'alumno_UNIQUE' in str(e):
                            errors.append("No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[1].apellidos + " ALUMNO YA EXISTE EN ESTA CLASE" + '\n')
                        else:
                            errors.append("No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[1].apellidos + " (" +
                                          str(e) + ")" + '\n')
            db.session.close()
            if len(errors) == 0:
                return {'id': str(id)}, 200
            else:
                er = ''
                for e in errors:
                    er += e + "\n"
                return {'message': er, 'status': 400}, 400
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ClaseApi(Resource):
    @profesor
    def put(self, id):
        try:
            db.openSession()
            clase = db.session.query(Clase).filter(Clase.id == id).one()
            body = request.get_json()
            print(body)
            for key, value in body.items():
                if key != 'alumnos':
                    setattr(clase, key, value)
            errors = []
            if 'alumnos' in body:
                delete_stmt = delete(AlumnosClase).where(AlumnosClase.c.clase == id)
                db.session.execute(delete_stmt)
                db.session.commit()
                for a in body['alumnos']:
                    try:
                        alumno = db.session.query(Alumno, User).join(User, Alumno.user == User.id).filter(
                            Alumno.id == a['id']).one()
                        insert_stmnt = AlumnosClase.insert().values(clase=id, alumno=alumno[0].id,
                                                                    alias=alumno[0].alias)
                        try:
                            db.session.execute(insert_stmnt)
                            db.session.commit()
                        except:
                            db.session.rollback()
                            raise
                    except IntegrityError as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
                        if 'alias_UNIQUE' in str(e):
                            errors.append("No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[
                                1].apellidos + " ALIAS YA EXISTE EN ESTA CLASE (" + alumno[0].alias + ")" + '\n')
                        if 'alumno_UNIQUE' in str(e):
                            errors.append("No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[
                                1].apellidos + " ALUMNO YA EXISTE EN ESTA CLASE" + '\n')
                        else:
                            errors.append(
                                "No se puede añadir el alumno: " + alumno[1].nombre + " " + alumno[1].apellidos + " (" +
                                str(e) + ")" + '\n')
            db.session.close()
            if len(errors) == 0:
                return {'id': str(id)}, 200
            else:
                er = ''
                for e in errors:
                    er += e + "\n"
                return {'message': er, 'status': 400}, 400
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Clase).filter_by(id=id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
    @profesor
    def get(self, id):
        try:
            db.openSession()
            clase = Clase.query.get(id)
            db.session.close()
            return jsonify(clase.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class ClasesApiSearch(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            test = body['test']
            del body['test']
            if user.rol == 3:
                clases = db.session.query(Clase).join(Profesor, Profesor.id == Clase.teacher).join(User, and_(
                    User.id == Profesor.user, User.colegio == user.colegio))
            else:
                profesor = Profesor.query.filter_by(user=user_id).one()
                clases = db.session.query(Clase).filter(Clase.teacher == profesor.id)
            for attr, value in body.items():
                clases = clases.filter(getattr(Clase, attr.replace('Clase.', "")).like("%%%s%%" % value))
            clases = clases.all()
            jsonObj = []
            for i in clases:
                alumnos = db.session.query(Alumno, User, AlumnosClase.c.clase).join(AlumnosClase, and_(AlumnosClase.c.clase == i.id, AlumnosClase.c.alumno == Alumno.id)).join(User, User.id == Alumno.user)
                if alumnos.count() < 3 and test:
                    continue
                jsonObj.append({**i.serialize,
                                'alumnos': [{**(j[0]).serialize(j[2]), **j[1].serialize, 'id': j[0].id} for j in alumnos.all()]})
            db.session.close()
            return jsonify(clases=jsonObj)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ClaseNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
