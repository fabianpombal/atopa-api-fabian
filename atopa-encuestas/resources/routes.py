from flask import request

from app import babel
from database.token_store_redis import redis_store
from resources.alumno import AlumnosApi, AlumnoApi, AlumnosApiSearch
from resources.auth import SignupApi, LoginApi, RefreshApi, LogoutApi, \
    LoginApiAlumno
from resources.colegio import ColegioApi, ColegiosApi
from resources.encuesta import EncuestasApi, EncuestaApi
from resources.grupoEdad import GrupoEdadesApi, GrupoEdadApi
from resources.pregunta import PreguntasApi, PreguntaApi, PreguntasApiSearch, PreguntasTestApiSearch
from resources.rol import RolesApi, RolApi
from resources.test import TestsApi, TestApi, TestForStudent, OpenTest, CodesPdf, FollowUpTest, TestsApiSearch, \
    CloseTest
from resources.tipo_estructura import TipoEstructurasApi, TipoEstructuraApi
from resources.tipo_pregunta import TipoPreguntasApi, TipoPreguntaApi
from resources.user import UsersApi, UserApi


def initialize_routes(api, jwt):
    @babel.localeselector
    def get_locale():
        body = request.get_json(silent=True)
        if body:
            if 'idioma' in body:
                lang = int(body['idioma'])
            else:
                lang = -1
        elif 'idioma' in request.args:
            lang = int(request.args.get('idioma'))
        else:
            lang = -1
        if lang == 0:
            return 'es'
        elif lang == 1:
            return 'gl'
        elif lang == 2:
            return 'en'
        else:
            return 'es'


    # metodo de alta de usuario POST
    api.add_resource(SignupApi, '/auth/signup')
    # metodo de login de usuario POST
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(LoginApiAlumno, '/auth/loginAlumno')
    # metodo refrescar token de usuario (POST)
    # metodo revocar refresh token (DELETE)
    api.add_resource(RefreshApi, '/auth/refresh')

    # metodo logout usuario (POST)
    api.add_resource(LogoutApi, '/auth/logout')

    # metodo de consulta de usuarios SOLO GET
    api.add_resource(UsersApi, '/users')
    # metodo de consulta un usuario GET / DELETE / PUT
    api.add_resource(UserApi, '/user/<id>')

    # metodo de consulta de roles GET y POST
    api.add_resource(RolesApi, '/roles')
    # metodo de consulta un rol GET / DELETE / PUT
    api.add_resource(RolApi, '/rol/<id>')

    # metodo de consulta de alumnos GET y POST
    api.add_resource(AlumnosApi, '/alumnos')
    # metodo de consulta un alumno GET / DELETE / PUT
    api.add_resource(AlumnoApi, '/alumno/<id>')
    api.add_resource(AlumnosApiSearch, '/alumnosSearch')


    # metodo de consulta de colegios GET y POST
    api.add_resource(ColegiosApi, '/colegios')
    # metodo de consulta un colegio GET / DELETE / PUT
    api.add_resource(ColegioApi, '/colegio/<id>')


    # metodo de consulta de grupoEdad GET y POST
    api.add_resource(GrupoEdadesApi, '/grupoEdades')
    # metodo de consulta un grupoEdad GET / DELETE / PUT
    api.add_resource(GrupoEdadApi, '/grupoEdad/<id>')


    # metodo de consulta de pregunta GET y POST
    api.add_resource(PreguntasApi, '/preguntas')
    # metodo de consulta una pregunta GET / DELETE / PUT
    api.add_resource(PreguntaApi, '/pregunta/<id>')
    api.add_resource(PreguntasApiSearch, '/preguntasSearch')
    api.add_resource(PreguntasTestApiSearch, '/preguntasTestSearch')


    # metodo de consulta de test GET y POST
    api.add_resource(TestsApi, '/tests')
    # metodo de consulta un test GET / DELETE / PUT
    api.add_resource(TestApi, '/test/<id>')
    api.add_resource(TestsApiSearch, '/testsSearch')
    # metodos para la aplicacion de alumnos
    api.add_resource(TestForStudent, '/testAlumno')
    # metodo para abrir un test
    api.add_resource(OpenTest, '/openTest')
    # metodo para cerrar un test
    api.add_resource(CloseTest, '/closeTest')
    # metodo para descargar el pdf de codigos de los alumnos de un test
    api.add_resource(CodesPdf, '/codesTest')
    # metodo que crea un test de seguimiento
    api.add_resource(FollowUpTest, '/followUpTest')

    # metodo de consulta de tipoEstructuras GET y POST
    api.add_resource(TipoEstructurasApi, '/tipoEstructuras')
    # metodo de consulta un tipoEstructura GET / DELETE / PUT
    api.add_resource(TipoEstructuraApi, '/tipoEstructura/<id>')

    # metodo de consulta de tipoPreguntas GET y POST
    api.add_resource(TipoPreguntasApi, '/tipoPreguntas')
    # metodo de consulta un tipoPregunta GET / DELETE / PUT
    api.add_resource(TipoPreguntaApi, '/tipoPregunta/<id>')


    # metodo de consulta de encuestas GET y POST
    api.add_resource(EncuestasApi, '/encuestas')
    # metodo de consulta encuesta GET / DELETE / PUT
    api.add_resource(EncuestaApi, '/encuesta/<id>')