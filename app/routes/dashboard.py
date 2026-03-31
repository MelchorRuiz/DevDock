from flask import Blueprint, abort, render_template, request
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


@dashboard_bp.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    categories = Category.query.all()
    tool = (
        Tool.query.options(
            selectinload(Tool.tags),
            selectinload(Tool.category),
        )
        .filter_by(id=tool_id)
        .first()
    )

    if not tool:
        abort(404)

    active_category = tool.category
    origin = request.args.get('from', 'dashboard')

    return render_template(
        'tool_detail.html',
        categories=categories,
        active_category=active_category,
        tool=tool,
        origin=origin,
    )

@dashboard_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    categories = Category.query.all()
    tools = []

    if query:
        tools = (
            Tool.query.options(selectinload(Tool.tags))
            .filter(
                (Tool.name.ilike(f'%{query}%')) |
                (Tool.description.ilike(f'%{query}%'))
            )
            .all()
        )

    return render_template('search.html',
                         query=query,
                         categories=categories,
                         active_category=None,
                         tools=tools)
