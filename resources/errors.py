from werkzeug.exceptions import HTTPException


class InternalServerError(HTTPException):
    pass
class SchemaValidationError(HTTPException):
    pass

#USUARIO
class UserAlreadyExistsError(HTTPException):
    pass
class ClientAppAlreadyExistsError(HTTPException):
    pass
class UserNotExistsError(HTTPException):
  pass
class UpdatingUserError(HTTPException):
    pass
class DeletingUserError(HTTPException):
  pass
class UnauthorizedError(HTTPException):
    pass
class UnauthorizedAppError(HTTPException):
    pass

#ROL
class RolAlreadyExistsError(HTTPException):
    pass
class RolNotExistsError(HTTPException):
  pass
class UpdatingRolError(HTTPException):
    pass
class DeletingRolError(HTTPException):
  pass

#ALUMNO
class AlumnoAlreadyExistsError(HTTPException):
    pass
class AlumnoNotExistsError(HTTPException):
  pass
class UpdatingAlumnoError(HTTPException):
    pass
class DeletingAlumnoError(HTTPException):
  pass

#CLASE
class ClaseAlreadyExistsError(HTTPException):
    pass
class ClaseNotExistsError(HTTPException):
  pass
class UpdatingClaseError(HTTPException):
    pass
class DeletingClaseError(HTTPException):
  pass

#COLEGIO
class ColegioAlreadyExistsError(HTTPException):
    pass
class ColegioNotExistsError(HTTPException):
  pass
class UpdatingColegioError(HTTPException):
    pass
class DeletingColegioError(HTTPException):
  pass

#GRUPOEDAD
class GrupoEdadAlreadyExistsError(HTTPException):
    pass
class GrupoEdadNotExistsError(HTTPException):
  pass
class UpdatingGrupoEdadError(HTTPException):
    pass
class DeletingGrupoEdadError(HTTPException):
  pass

#PICTO
class PictoAlreadyExistsError(HTTPException):
    pass
class PictoNotExistsError(HTTPException):
  pass
class UpdatingPictoError(HTTPException):
    pass
class DeletingPictoError(HTTPException):
  pass

#PREGUNTA
class PreguntaAlreadyExistsError(HTTPException):
    pass
class PreguntaNotExistsError(HTTPException):
  pass
class UpdatingPreguntaError(HTTPException):
    pass
class PreguntaColegioError(HTTPException):
  pass

#PROFESOR
class ProfesorAlreadyExistsError(HTTPException):
    pass
class ProfesorNotExistsError(HTTPException):
  pass
class UpdatingProfesorError(HTTPException):
    pass
class DeletingProfesorError(HTTPException):
  pass

#TEST
class TestAlreadyExistsError(HTTPException):
    pass
class TestNotExistsError(HTTPException):
  pass
class UpdatingTestError(HTTPException):
    pass
class DeletingTestError(HTTPException):
  pass
class NotResults(HTTPException):
    pass

#TIPOESTRUCTURA
class TipoEstructuraAlreadyExistsError(HTTPException):
    pass
class TipoEstructuraNotExistsError(HTTPException):
  pass
class UpdatingTipoEstructuraError(HTTPException):
    pass
class DeletingTipoEstructuraError(HTTPException):
  pass

#TIPOPREGUNTA
class TipoPreguntaAlreadyExistsError(HTTPException):
    pass
class TipoPreguntaNotExistsError(HTTPException):
  pass
class UpdatingTipoPreguntaError(HTTPException):
    pass
class DeletingTipoPreguntaError(HTTPException):
  pass

#YEAR
class YearAlreadyExistsError(HTTPException):
    pass
class YearNotExistsError(HTTPException):
  pass
class UpdatingYearError(HTTPException):
    pass
class DeletingYearError(HTTPException):
  pass

#PREFERENCIAS
class PreferenciasAlreadyExistsError(HTTPException):
    pass
class PreferenciasNotExistsError(HTTPException):
  pass
class UpdatingPreferenciasError(HTTPException):
    pass
class DeletingPreferenciasError(HTTPException):
  pass

#ENCUESTA
class EncuestaAlreadyExistsError(HTTPException):
    pass
class EncuestaNotExistsError(HTTPException):
  pass
class UpdatingEncuestaError(HTTPException):
    pass
class DeletingEncuestaError(HTTPException):
  pass

errors = {
    "NotResults": {
        "message": "Todavía no hay respuestas",
        "status": 400
    },
    "InternalServerError": {
        "message": "Error de servidor. Algo ha ido mal.",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "La petición no tiene el formato correcto.",
        "status": 400
    },
    "UserAlreadyExistsError": {
        "message": "Ya existe un usuario con ese username o email",
        "status": 400
    },
    "UpdatingUserError": {
        "message": "El id del usuario no existe.",
        "status": 403
    },
    "DeletingUserError": {
        "message": "El usuario no se puede eliminar.",
        "status": 403
    },
    "UserNotExistsError": {
        "message": "No existe un usuario con los datos proporcionados",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "El usuario y/o la contraseña no son correctos.",
        "status": 401
    },
    "UnauthorizedAppError": {
        "message": "Clave API incorrecta.",
        "status": 401
    },
    "UpdatingRolError": {
        "message": "El id del rol no existe.",
        "status": 403
    },
    "DeletingRolError": {
        "message": "El rol no se puede eliminar.",
        "status": 403
    },
    "RolNotExistsError": {
        "message": "No existe un rol con el id o nombre proporcionado",
        "status": 400
    },
    "RolAlreadyExistsError": {
        "message": "Ya existe un rol con el mismo nombre.",
        "status": 400
    },
    "UpdatingAlumnoError": {
        "message": "El id del alumno no existe.",
        "status": 403
    },
    "DeletingAlumnoError": {
        "message": "El alumno no se puede eliminar.",
        "status": 403
    },
    "AlumnoNotExistsError": {
        "message": "No existe un alumno con el id o nombre proporcionado",
        "status": 400
    },
    "AlumnoAlreadyExistsError": {
        "message": "Ya existe un alumno con el mismo DNI o alias.",
        "status": 400
    },
    "UpdatingClaseError": {
        "message": "El id de la clase no existe.",
        "status": 403
    },
    "DeletingClaseError": {
        "message": "La clase no se puede eliminar.",
        "status": 403
    },
    "ClaseNotExistsError": {
        "message": "No existe una clase con el id o nombre proporcionado",
        "status": 400
    },
    "ClaseAlreadyExistsError": {
        "message": "Ya existe una clase con el mismo nombre.",
        "status": 400
    },
    "UpdatingColegioError": {
        "message": "El id del colegio no existe.",
        "status": 403
    },
    "DeletingColegioError": {
        "message": "El colegio no se puede eliminar.",
        "status": 403
    },
    "ColegioNotExistsError": {
        "message": "No existe un colegio con el id o nombre proporcionado",
        "status": 400
    },
    "ColegioAlreadyExistsError": {
        "message": "Ya existe un colegio con el mismo nombre.",
        "status": 400
    },
    "UpdatingGrupoEdadError": {
        "message": "El id del grupo de edad no existe.",
        "status": 403
    },
    "DeletingGrupoEdadError": {
        "message": "El grupo de edad no se puede eliminar.",
        "status": 403
    },
    "GrupoEdadNotExistsError": {
        "message": "No existe un grupo de edad con el id o nombre proporcionado",
        "status": 400
    },
    "GrupoEdadAlreadyExistsError": {
        "message": "Ya existe un grupo de edad con el mismo nombre.",
        "status": 400
    },
    "UpdatingPictoError": {
        "message": "El id del picto no existe.",
        "status": 403
    },
    "DeletingPictoError": {
        "message": "El picto no se puede eliminar.",
        "status": 403
    },
    "PictoNotExistsError": {
        "message": "No existe un picto con el id o nombre proporcionado",
        "status": 400
    },
    "PictoAlreadyExistsError": {
        "message": "Ya existe un picto con el mismo nombre.",
        "status": 400
    },
    "UpdatingPreguntaError": {
        "message": "El id de la pregunta no existe.",
        "status": 403
    },
    "DeletingPreguntaError": {
        "message": "La pregunta no se puede eliminar.",
        "status": 403
    },
    "PreguntaNotExistsError": {
        "message": "No existe una pregunta con el id o nombre proporcionado",
        "status": 400
    },
    "PreguntaAlreadyExistsError": {
        "message": "Ya existe una pregunta con el mismo nombre.",
        "status": 400
    },
    "UpdatingProfesorError": {
        "message": "El id del profesor no existe.",
        "status": 403
    },
    "DeletingProfesorError": {
        "message": "El profesor no se puede eliminar.",
        "status": 403
    },
    "ProfesorNotExistsError": {
        "message": "No existe un profesor con el id o nombre proporcionado",
        "status": 400
    },
    "ProfesorAlreadyExistsError": {
        "message": "Ya existe un profesor con el mismo username.",
        "status": 400
    },
    "UpdatingTestError": {
        "message": "El id del test no existe.",
        "status": 403
    },
    "DeletingTestError": {
        "message": "El test no se puede eliminar.",
        "status": 403
    },
    "TestNotExistsError": {
        "message": "No existe un test con el id o nombre proporcionado",
        "status": 400
    },
    "TestAlreadyExistsError": {
        "message": "Ya existe un test con el mismo nombre.",
        "status": 400
    },
    "UpdatingTipoEstructuraError": {
        "message": "El id del tipo de estructura no existe.",
        "status": 403
    },
    "DeletingTipoEstructuraError": {
        "message": "El tipo de estructura no se puede eliminar.",
        "status": 403
    },
    "TipoEstructuraNotExistsError": {
        "message": "No existe un tipo de estructura con el id o nombre proporcionado",
        "status": 400
    },
    "TipoEstructuraAlreadyExistsError": {
        "message": "Ya existe un tipo de estructura con el mismo nombre.",
        "status": 400
    },
    "UpdatingTipoPreguntaError": {
        "message": "El id del tipo de pregunta no existe.",
        "status": 403
    },
    "DeletingTipoPreguntaError": {
        "message": "El tipo de pregunta no se puede eliminar.",
        "status": 403
    },
    "TipoPreguntaNotExistsError": {
        "message": "No existe un tipo de pregunta con el id o nombre proporcionado",
        "status": 400
    },
    "TipoPreguntaAlreadyExistsError": {
        "message": "Ya existe un tipo de pregunta con el mismo nombre.",
        "status": 400
    },
    "YearColegioError": {
        "message": "El id del año académico no existe.",
        "status": 403
    },
    "DeletingYearError": {
        "message": "El año académico no se puede eliminar.",
        "status": 403
    },
    "YearNotExistsError": {
        "message": "No existe un año académico con el id o nombre proporcionado",
        "status": 400
    },
    "YearAlreadyExistsError": {
        "message": "Ya existe un año académico con el mismo nombre.",
        "status": 400
    },
    "UpdatingPreferenciasError": {
        "message": "El id de las preferencias no existe.",
        "status": 403
    },
    "DeletingPreferenciasError": {
        "message": "Las preferencias no se pueden eliminar.",
        "status": 403
    },
    "PreferenciasNotExistsError": {
        "message": "No existen preferencias con el id o usuario proporcionado",
        "status": 400
    },
    "PreferenciasAlreadyExistsError": {
        "message": "Ya existen preferencias con el mismo usuario.",
        "status": 400
    },
    "UpdatingEncuestaError": {
        "message": "El id de la encuesta no existe.",
        "status": 403
    },
    "DeletingEncuestaError": {
        "message": "La encuesta no se puede eliminar.",
        "status": 403
    },
    "EncuestaNotExistsError": {
        "message": "No existe una encuesta con el id o usuario proporcionado",
        "status": 400
    },
    "EncuestaAlreadyExistsError": {
        "message": "Ya existe una encuesta como esa.",
        "status": 400
    },
}