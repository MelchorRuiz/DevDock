from flask import Blueprint, request, jsonify
import json
from app.routes.dashboard import _find_tools_by_query, _serialize_tool

mcp_bp = Blueprint('mcp', __name__)

initialize_response = {
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "tools": {}
    },
    "serverInfo": {
        "name": "devtools-mcp",
        "version": "1.0.0"
    }
}

tools = [{
    "name": "recommend_dev_tools",
    "description": "Recomienda herramientas para desarrolladores según una necesidad descrita en lenguaje natural.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Necesidad del desarrollador"
            }
        },
        "required": ["query"]
    }
}]

@mcp_bp.route('/', methods=['POST'])
def index():
    payload = request.get_json()
    
    rpc_id = payload.get("id")
    method = payload.get('method')
    
     # helper JSON-RPC response
    def rpc_result(result):
        return jsonify({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": result
        })

    def rpc_error(code, message):
        return jsonify({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {
                "code": code,
                "message": message
            }
        })
    
    if method == "initialize":
        return rpc_result(initialize_response)
    
    if method == "tools/list":
        return rpc_result({"tools": tools})
    
    if method == "tools/call":
        params = payload.get("params", {})
        name = params.get("name")
        if name != "recommend_dev_tools":
            return rpc_error(-32601, "Method not found")
        
        args = params.get("arguments", {})
        query = args.get("query", "")
    

        finded_tools = _find_tools_by_query(query)
        result = [_serialize_tool(tool) for tool in finded_tools]

        return rpc_result({
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"tools": result}, ensure_ascii=False)
                }
            ]
        })
    
    return rpc_error(-32601, "Method not found")