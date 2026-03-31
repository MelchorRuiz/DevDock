import json

from flask import Blueprint, abort, jsonify, render_template, request, url_for
from sqlalchemy.orm import selectinload

from app.ai import cosine_similarity, get_query_embedding, rerank_tools
from app.models import Category, Tool

dashboard_bp = Blueprint('dashboard', __name__)

MIN_SIMILARITY_SCORE = 0.2
MAX_PREFILTERED_CANDIDATES = 25
MAX_RERANK_CANDIDATES = 12
MAX_RESULTS = 12


def _find_tools_by_query(query):
    if not query:
        return []

    query_embedding = get_query_embedding(query)
    if not query_embedding:
        return []

    candidates = (
        Tool.query.options(
            selectinload(Tool.tags),
            selectinload(Tool.category),
        )
        .filter(Tool.embedding.isnot(None))
        .all()
    )

    scored_tools = []
    for tool in candidates:
        try:
            tool_embedding = json.loads(tool.embedding)
            score = cosine_similarity(query_embedding, tool_embedding)
            scored_tools.append((score, tool))
        except (json.JSONDecodeError, TypeError):
            continue

    scored_tools.sort(key=lambda item: item[0], reverse=True)
    prefiltered = [
        tool for score, tool in scored_tools if score >= MIN_SIMILARITY_SCORE
    ][:MAX_PREFILTERED_CANDIDATES]

    if not prefiltered:
        prefiltered = [tool for _, tool in scored_tools[:MAX_RERANK_CANDIDATES]]

    if len(prefiltered) > 2:
        rerank_input = prefiltered[:MAX_RERANK_CANDIDATES]
        tools = rerank_tools(query, rerank_input)
    else:
        tools = prefiltered

    return tools[:MAX_RESULTS]


def _serialize_tool(tool, query=''):
    detail_params = {'tool_id': tool.id, 'q': query, '_external': False}
    detail_params['from'] = 'search'

    return {
        'id': tool.id,
        'name': tool.name,
        'description': tool.description,
        'url': tool.url,
        'favicon_url': tool.favicon_url,
        'tags': [tag.name for tag in tool.tags],
        'category_name': tool.category.name if tool.category else 'Herramienta',
        'detail_url': url_for('dashboard.tool_detail', **detail_params),
    }

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
    search_query = request.args.get('q', '').strip()

    return render_template(
        'tool_detail.html',
        categories=categories,
        active_category=active_category,
        tool=tool,
        origin=origin,
        search_query=search_query,
    )

@dashboard_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    categories = Category.query.all()

    return render_template('search.html',
                         query=query,
                         categories=categories,
                         active_category=None,
                         tools=[])


@dashboard_bp.route('/search/results')
def search_results():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'query': query, 'tools': []})

    try:
        tools = _find_tools_by_query(query)
        return jsonify({'query': query, 'tools': [_serialize_tool(tool, query=query) for tool in tools]})
    except Exception:
        return jsonify({'query': query, 'tools': []}), 500
