from flask import Blueprint, render_template

suggest_bp = Blueprint('suggest', __name__)

@suggest_bp.route('/')
def index():
    return render_template('suggest.html')