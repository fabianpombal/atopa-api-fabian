from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

db: SQLAlchemy
session: None
engine : None
def initialize_db(app):
    global db
    db = SQLAlchemy(app)
    global engine
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], poolclass=NullPool) #,pool_size=10, max_overflow=0

def openSession():
    global session
    session = scoped_session(sessionmaker(bind=engine))