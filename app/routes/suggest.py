import json
import re
import html as html_lib
import unicodedata
from urllib.parse import urlparse
from url_normalize import url_normalize
import validators
import requests
from flask import Blueprint, jsonify, render_template, request
from app import db
from app.ai import analyze_suggested_tool
from app.models import Category, Suggestion, Tag, Tool

suggest_bp = Blueprint('suggest', __name__)

SCRAPE_TEXT_LIMIT = 1200
SCRAPE_HTML_LIMIT = 200000
SCRAPE_TIMEOUT = 10


def _normalize_string(value):
    value = value or ""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def _match_category(categories, name):
    if not categories:
        return None

    normalized = _normalize_string(name)
    by_normalized = {_normalize_string(category.name): category for category in categories}

    if normalized in by_normalized:
        return by_normalized[normalized]

    if normalized:
        for key, category in by_normalized.items():
            if normalized in key or key in normalized:
                return category

    fallback = by_normalized.get(_normalize_string("Otras Herramientas"))
    return fallback or categories[0]


def _extract_first(pattern, html_text):
    match = re.search(pattern, html_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return html_lib.unescape(match.group(1)).strip()


def _extract_meta_description(html_text):
    patterns = [
        r'<meta[^>]+(?:name|property)=["\"](?:description|og:description)["\"][^>]*content=["\"](.*?)["\"]',
        r'<meta[^>]+content=["\"](.*?)["\"][^>]*(?:name|property)=["\"](?:description|og:description)["\"]',
    ]
    for pattern in patterns:
        content = _extract_first(pattern, html_text)
        if content:
            return content
    return ""


def _strip_html(html_text):
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html_text)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = html_lib.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _scrape_url(url):
    try:
        response = requests.get(
            url,
            timeout=SCRAPE_TIMEOUT,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            },
            allow_redirects=True,
        )
        response.raise_for_status()
        html_text = response.text or ""
    except Exception:
        return {
            "title": "",
            "description": "",
            "h1": "",
            "text": "",
        }

    if len(html_text) > SCRAPE_HTML_LIMIT:
        html_text = html_text[:SCRAPE_HTML_LIMIT]

    title = _extract_first(r"<title[^>]*>(.*?)</title>", html_text)
    description = _extract_meta_description(html_text)
    h1 = _extract_first(r"<h1[^>]*>(.*?)</h1>", html_text)
    text = _strip_html(html_text)
    if len(text) > SCRAPE_TEXT_LIMIT:
        text = text[:SCRAPE_TEXT_LIMIT]

    return {
        "title": title,
        "description": description,
        "h1": h1,
        "text": text,
    }


def _get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def _build_favicon_url(url):
    parsed = urlparse(url)
    if not parsed.netloc:
        return None
    return f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=64"


def _coerce_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "si")
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _build_tool_from_analysis(url, analysis, categories):
    is_tool = _coerce_bool(analysis.get("is_tool"))
    name = (analysis.get("name") or "").strip()
    description = (analysis.get("description") or "").strip()
    category_name = (analysis.get("category") or "").strip()
    tags_raw = analysis.get("tags") or []
    tags = [tag.strip() for tag in tags_raw if isinstance(tag, str) and tag.strip()]

    if not (is_tool and name and description):
        return None

    category = _match_category(categories, category_name)
    tool = Tool(
        name=name[:100],
        description=description,
        url=url,
        favicon_url=_build_favicon_url(url),
        category=category,
    )
    db.session.add(tool)

    for tag_name in tags:
        trimmed = tag_name[:50]
        existing = Tag.query.filter_by(name=trimmed).first()
        if not existing:
            existing = Tag(name=trimmed)
            db.session.add(existing)
        tool.tags.append(existing)

    tool.generate_embedding()
    return tool

@suggest_bp.route('/')
def index():
    return render_template('suggest.html')


@suggest_bp.route('/review', methods=['POST'])
def review():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or request.form.get("url") or "").strip()

    if not url:
        return jsonify({"error": "url_required"}), 400
    
    normalized = url_normalize(url, default_scheme="https")
    
    if not validators.url(normalized):
        return jsonify({"error": "invalid_url"}), 400

    if Tool.query.filter_by(url=normalized).first():
        return jsonify({"error": "tool_already_exists"}), 409

    previous_suggestion = Suggestion.query.filter_by(raw_url=normalized).order_by(Suggestion.created_at.desc()).first()
    if previous_suggestion:
        if previous_suggestion.status == "approved":
            try:
                analysis_payload = json.loads(previous_suggestion.ai_analysis or "{}")
            except json.JSONDecodeError:
                analysis_payload = {}
            return jsonify(
                {
                    "suggestion_id": previous_suggestion.id,
                    "status": "approved",
                    "analysis": analysis_payload.get("analysis") or {},
                }
            )
        else:
            return jsonify(
                {
                    "error": "url_already_validated",
                    "status": previous_suggestion.status,
                }
            ), 409

    try:
        suggestion = Suggestion(
            raw_url=normalized,
            suggested_by=_get_client_ip(),
            status="pending",
        )
        db.session.add(suggestion)
        db.session.commit()

        scraped = _scrape_url(normalized)
        categories = Category.query.order_by(Category.name).all()
        category_names = [category.name for category in categories]
        analysis = analyze_suggested_tool(normalized, scraped, category_names)
        analysis = analysis if isinstance(analysis, dict) else {}

        has_name = bool((analysis.get("name") or "").strip())
        has_description = bool((analysis.get("description") or "").strip())
        suggestion.status = "approved" if _coerce_bool(analysis.get("is_tool")) and has_name and has_description else "rejected"

        suggestion.ai_analysis = json.dumps(
            {"scraped": scraped, "analysis": analysis},
            ensure_ascii=False,
        )
        db.session.commit()

        response_payload = {
            "suggestion_id": suggestion.id,
            "status": suggestion.status,
            "analysis": analysis,
        }
        return jsonify(response_payload)
    except Exception:
        db.session.rollback()
        return jsonify({"error": "processing_failed"}), 500


@suggest_bp.route('/submit', methods=['POST'])
def submit():
    payload = request.get_json(silent=True) or {}
    suggestion_id = payload.get("suggestion_id") or request.form.get("suggestion_id")

    if not suggestion_id:
        return jsonify({"error": "suggestion_id_required"}), 400

    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return jsonify({"error": "suggestion_not_found"}), 404

    if suggestion.status != "approved":
        return jsonify({"error": "suggestion_not_approved"}), 400

    if Tool.query.filter_by(url=suggestion.raw_url).first():
        return jsonify({"error": "tool_already_exists"}), 409

    try:
        analysis_payload = json.loads(suggestion.ai_analysis or "{}")
        analysis = analysis_payload.get("analysis") or {}
        categories = Category.query.order_by(Category.name).all()
        tool = _build_tool_from_analysis(suggestion.raw_url, analysis, categories)
        if not tool:
            return jsonify({"error": "analysis_invalid"}), 400

        db.session.commit()
        return jsonify(
            {
                "suggestion_id": suggestion.id,
                "status": suggestion.status,
                "tool": {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "url": tool.url,
                    "favicon_url": tool.favicon_url,
                    "category_name": tool.category.name if tool.category else None,
                    "tags": [tag.name for tag in tool.tags],
                },
            }
        )
    except json.JSONDecodeError:
        return jsonify({"error": "analysis_invalid"}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"error": "submission_failed"}), 500