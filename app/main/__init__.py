from flask import Blueprint

from . import events

main = Blueprint('main', __name__, template_folder='../templates', static_folder='../static')

from . import routes
