from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_babel import Babel
from datetime import datetime

from database.db import initialize_db
# from database.token_store_redis import redis_store

from flask_restful import Api

from resources.errors import errors
from resources.token_expires_time import set_expires_time

from datetime import timedelta

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# app.config.from_envvar('ENV_JWT')

TOKEN_ACCESS_EXPIRES = timedelta(minutes=120)
TOKEN_REFRESH_EXPIRES = timedelta(days=1)

# Establecer tiempos de caducidad token (quiza seria mejor coger los tiempos del fichero config .env)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = TOKEN_ACCESS_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = TOKEN_REFRESH_EXPIRES
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/atopa'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# print(app.config)

set_expires_time(app.config['JWT_ACCESS_TOKEN_EXPIRES'], app.config['JWT_REFRESH_TOKEN_EXPIRES'])

app.config['BABEL_DEFAULT_LOCALE'] = 'es'

mail = Mail(app)

api = Api(app, errors=errors)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
babel = Babel(app)

initialize_db(app)
# initialize_redis_store()

# @jwt.token_in_blacklist_loader
# def check_if_token_is_revoked(decrypted_token):
#     jti = decrypted_token['jti']
#     entry = redis_store.get(jti)
#    if entry is None:
#        return True
#     return entry == 'true'
from resources.routes import initialize_routes
initialize_routes(api, jwt)

@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Origin, Accept, token, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    return response

def create_year():
    from database.db import db
    db.openSession()
    from database.models.colegio import Colegio
    colegios = Colegio.query.all()
    day = datetime.now().strftime("%d-%m")
    yearCurrent = datetime.now().strftime("%Y")
    for c in colegios:
        if c.fecha_inicio == day:
            from database.models.year import Year
            year = db.session.query(Year).filter(Year.current==1).one()
            newYear = yearCurrent + "/" + str(int(yearCurrent) + 1)
            year.current = 0
            newSchoolYear = Year(school_year=newYear, current=1, colegio=c.id)
            db.session.add(newSchoolYear)
            db.session.commit()
    db.session.close()

scheduler = BackgroundScheduler()
job = scheduler.add_job(create_year, 'cron', day_of_week="mon-sun", hour=0, minute=0)
scheduler.start()