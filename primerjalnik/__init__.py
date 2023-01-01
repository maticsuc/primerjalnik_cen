import os, logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from primerjalnik.utils import LogHandler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ["DBUSER"],
    dbpass=os.environ["DBPASS"],
    dbhost=os.environ["DBHOST"],
    dbname=os.environ["DBNAME"]
)

app.config['SECRET_KEY'] = 'a7e4b0698e212cf43ef30030'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

h = LogHandler()
h.setFormatter(formatter)

logger = logging.getLogger('waitress')
logger.addHandler(h)


from primerjalnik import routes