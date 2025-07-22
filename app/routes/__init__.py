from flask import Blueprint

bp = Blueprint('exam', __name__)

@bp.route('/')
def index():
    return "Exam routes"