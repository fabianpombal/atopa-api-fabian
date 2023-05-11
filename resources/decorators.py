from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from flask_jwt_extended.view_decorators import _decode_jwt_from_request, verify_jwt_in_request

from database import db
from database.models.alumno import Alumno
from database.models.rol import Rol
from database.models.test import AlumnosTest
from database.models.user import User
from resources.errors import UnauthorizedAppError


def superuser(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        db.openSession()
        verify_jwt_in_request()
        user_id = get_jwt()['sub']
        user = User.query.get(user_id)
        superuser = False
        r = Rol.query.get(user.rol)
        db.session.close()
        if r.admin == 1:
            superuser = True
        if superuser:
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise UnauthorizedAppError

        return view_function(*args, **kwargs)

    return wrapper


def alumno(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        db.openSession()
        verify_jwt_in_request()
        user_id = get_jwt()['sub']
        alumno = db.session.query(AlumnosTest).filter_by(id=user_id).one()
        alumnoobj = Alumno.query.get(alumno.alumno)
        user = User.query.get(alumnoobj.user)
        cliente = False
        r = Rol.query.get(user.rol)
        db.session.close()
        if r.nombre == "alumno":
            cliente = True
        if cliente:
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise UnauthorizedAppError

        return view_function(*args, **kwargs)

    return wrapper


def profesor(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        db.openSession()
        verify_jwt_in_request()
        user_id = get_jwt()['sub']
        user = User.query.get(user_id)
        edit = False
        r = Rol.query.get(user.rol)
        db.session.close()
        if r.nombre == "profesor" or r.admin == 1:
            edit = True
        if edit:
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise UnauthorizedAppError

        return view_function(*args, **kwargs)

    return wrapper
