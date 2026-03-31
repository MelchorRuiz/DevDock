from flask import Blueprint, render_template, request
from sqlalchemy.orm import selectinload

from app.models import Category, Tool

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # Get all categories for the sidebar
    categories = Category.query.all()
    
    # Get the active category (from parameter or the first one)
    active_category_id = request.args.get('category', type=int)
    
    if not active_category_id and categories:
        active_category_id = categories[0].id
    
    # Get tools for the active category
    active_category = None
    tools = []
    
    if active_category_id:
        active_category = Category.query.get(active_category_id)
        if active_category:
            tools = (
                Tool.query.options(selectinload(Tool.tags))
                .filter_by(category_id=active_category_id)
                .all()
            )
    
    return render_template('dashboard.html', 
                         categories=categories,
                         active_category=active_category,
                         tools=tools)
