import os
import math
import json
from google import genai

# Usar API key desde variable de entorno
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please set it with your Gemini API key: export GOOGLE_API_KEY='your-key-here'"
    )

client = genai.Client(api_key=api_key)

_QUERY_EMBEDDING_CACHE = {}
_RERANK_CACHE = {}

def _extract_json_object(text):
    if not text:
        return {}

    raw = text.strip()
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}

    try:
        parsed = json.loads(raw[start : end + 1])
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}

def generate_embeddings(text):
    result  = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    
    return result.embeddings[0].values


def get_query_embedding(query):
    normalized_query = (query or "").strip().lower()
    if not normalized_query:
        return []

    cached = _QUERY_EMBEDDING_CACHE.get(normalized_query)
    if cached is not None:
        return cached

    embedding = generate_embeddings(normalized_query)
    _QUERY_EMBEDDING_CACHE[normalized_query] = embedding
    return embedding


def cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def _extract_json_array(text):
    if not text:
        return []

    raw = text.strip()
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        pass

    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []

    try:
        parsed = json.loads(raw[start : end + 1])
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def rerank_tools(query, tools):
    if not query or not tools:
        return tools

    candidates = []
    candidate_ids = []
    for tool in tools:
        candidate_ids.append(tool.id)
        candidates.append(
            {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.name if tool.category else "",
                "tags": [tag.name for tag in tool.tags],
            }
        )

    normalized_query = (query or "").strip().lower()
    cache_key = (normalized_query, tuple(candidate_ids))
    cached_ids = _RERANK_CACHE.get(cache_key)
    if cached_ids is not None:
        tools_by_id = {tool.id: tool for tool in tools}
        return [tools_by_id[tool_id] for tool_id in cached_ids if tool_id in tools_by_id]

    prompt = (
        "Eres un sistema de reranking para un buscador de herramientas tecnicas. "
        "Recibiras una consulta y una lista de candidatos. "
        "Debes ordenar los candidatos por relevancia semantica para la consulta "
        "y eliminar los candidatos que no sean relevantes.\n\n"
        f"Consulta: {query}\n\n"
        f"Candidatos (JSON): {json.dumps(candidates, ensure_ascii=False)}\n\n"
        "Responde SOLO con un arreglo JSON de IDs RELEVANTES y ordenados por relevancia, "
        "por ejemplo: [3, 10, 7]. "
        "Si ningun candidato es relevante, responde []. "
        "No agregues explicaciones ni texto extra."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        ordered_ids = _extract_json_array(getattr(response, "text", ""))
        ordered_ids = [int(tool_id) for tool_id in ordered_ids if str(tool_id).isdigit()]
    except Exception:
        return tools

    if not ordered_ids:
        return []

    tools_by_id = {tool.id: tool for tool in tools}
    reranked = [tools_by_id[tool_id] for tool_id in ordered_ids if tool_id in tools_by_id]
    _RERANK_CACHE[cache_key] = [tool.id for tool in reranked]

    return reranked


def analyze_suggested_tool(url, scraped_data, categories):
    prompt = (
        "Eres un sistema de revision para sugerencias de herramientas de programacion. "
        "Debes decidir si el enlace corresponde a una herramienta util para programadores. "
        "Usa la informacion de scraping disponible.\n\n"
        f"Categorias disponibles: {json.dumps(categories, ensure_ascii=False)}\n\n"
        f"URL: {url}\n"
        f"Titulo: {scraped_data.get('title', '')}\n"
        f"Descripcion: {scraped_data.get('description', '')}\n"
        f"H1: {scraped_data.get('h1', '')}\n"
        f"Texto: {scraped_data.get('text', '')}\n\n"
        "Responde SOLO con JSON valido y sin texto adicional. "
        "El formato debe ser: "
        '{"is_tool": true, "name": "...", "description": "...", "category": "...", "tags": ["..."]}. '
        "Si no es una herramienta, usa is_tool=false y deja name/description/category vacios o tags=[] "
        "pero incluye siempre todas las claves."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        print(f"🔍 Analysis response for {url}: {getattr(response, 'text', '')}")  # Debug log
        return _extract_json_object(getattr(response, "text", ""))
    except Exception:
        return {}
    
 