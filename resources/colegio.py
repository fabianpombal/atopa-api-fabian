import sys

from flask import Response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from database import db
from database.models.colegio import Colegio
from database.models.user import User

from flask_restful import Resource

from database.models.year import Year
from resources.errors import SchemaValidationError, InternalServerError, ColegioNotExistsError, \
    ColegioAlreadyExistsError
from datetime import datetime
from resources.decorators import profesor, alumno, superuser
import requests

class ColegiosApi(Resource):
    def get(self):
        try:
            db.openSession()
            colegios = Colegio.query.all()
            db.session.close()
            return jsonify(colegios=[i.serialize for i in colegios])
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            # print(f"Cuerpo: {body}\n\n")
            
            colegio = Colegio(**body)
            cuerpo = colegio.to_json()
            # print(colegio.to_json())
            db.session.add(colegio)
            db.session.commit()
            id = colegio.id
            colegio = Colegio.query.get(id)
            print(colegio)
            # date = datetime.strptime(colegio.fecha_inicio, "%d-%m")
            # currentDate = datetime.now()
            # yearCurrent = datetime.now().strftime("%Y")
            # if date >= currentDate:
            #     school_year = str(int(yearCurrent) - 1) + "/" + yearCurrent
            # else:
            #     school_year = yearCurrent + "/" + str(int(yearCurrent) + 1)
            # print(f"\n\nDate={date}\nCDate={currentDate}\nCYear={yearCurrent}\nSchool={school_year}\n\n")
            # year = Year(school_year=school_year, current=1, colegio=id)

            # db.session.add(year)
            # db.session.commit()
            db.session.close()
            

            api_url = "http://localhost:6001/colegios"
            
            response = requests.post(api_url, json=cuerpo)  
            # print(f"\nResponse: {response}\n\n")
            return {'id': str(id)}, 200
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioAlreadyExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ColegioApi(Resource):
    
    def put(self, id):
        try:
            db.openSession()
            colegio = db.session.query(Colegio).filter(Colegio.id == id).one()
           
            hash_antiguo = colegio.hash
            body = request.get_json()
            for key, value in body.items():
                setattr(colegio, key, value)
            colegio.calculate_hash()
            cuerpo = colegio.to_json()
            db.session.commit()
            db.session.close()
           
            
            api_url = f"http://localhost:6001/colegio/{hash_antiguo}"
            
            
            print(cuerpo)
           
            response = requests.put(api_url, json=cuerpo)
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except IntegrityError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioAlreadyExistsError
        except Exception:
            print('que le pasa?')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            # print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

   
    def delete(self, id):
        try:
            db.openSession()
            db.session.query(Colegio).filter_by(id = id).delete()
            db.session.commit()
            db.session.close()
            return '', 200
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

   
    def get(self, id):
        try:
            db.openSession()
            colegio = Colegio.query.get(id)
            db.session.close()
            return jsonify(colegio.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class ColegioUser(Resource):
    
    def get(self):
        try:
            db.openSession()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            colegio = Colegio.query.get(user.colegio)
            db.session.close()
            return jsonify(colegio.serialize)
        except AttributeError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise ColegioNotExistsError
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('que le pasa?')
            # print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError
