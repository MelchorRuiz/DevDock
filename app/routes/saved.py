from flask import Blueprint, render_template

saved_bp = Blueprint('saved', __name__)

@saved_bp.route('/')
def index():
    return render_template('saved.html')
