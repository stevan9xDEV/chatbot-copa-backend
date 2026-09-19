from collections.abc import MutableMapping
from uuid import UUID, uuid4

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from config.settings import settings
from services.groq_service import (
    GroqAuthenticationError,
    GroqConnectionError,
    GroqInvalidRequestError,
    GroqRateLimitError,
    GroqService,
    GroqServiceError,
    GroqUnavailableError,
)

chat_bp = Blueprint("chat", __name__, url_prefix="/api")
conversations: MutableMapping[str, list[dict[str, str]]] = {}


def error_response(message, status_code):
    return jsonify({"error": True, "message": message}), status_code


def validate_json_body():
    if not request.is_json:
        return None, error_response("O Content-Type deve ser application/json.", 400)

    try:
        data = request.get_json(silent=False)
    except BadRequest:
        return None, error_response("JSON inválido.", 400)

    if not isinstance(data, dict):
        return None, error_response("O corpo da requisição deve ser um objeto JSON.", 422)

    return data, None


def validate_conversation_id(value):
    if value is None:
        return None, None

    if not isinstance(value, str) or not value.strip():
        return None, error_response("conversation_id deve ser uma string não vazia.", 422)

    try:
        UUID(value)
    except ValueError:
        return None, error_response("conversation_id deve ser um UUID válido.", 422)

    return value, None


@chat_bp.post("/chat")
def chat():
    data, error = validate_json_body()
    if error:
        return error

    message = data.get("message")
    if message is None:
        return error_response("O campo 'message' é obrigatório.", 422)
    if not isinstance(message, str):
        return error_response("O campo 'message' deve ser uma string.", 422)

    message = message.strip().replace("\x00", "")
    if not message:
        return error_response("A mensagem não pode estar vazia.", 422)
    if len(message) > settings.MAX_MESSAGE_LENGTH:
        return error_response(
            f"A mensagem ultrapassa o limite máximo de {settings.MAX_MESSAGE_LENGTH} caracteres.",
            422,
        )

    conversation_id, error = validate_conversation_id(data.get("conversation_id"))
    if error:
        return error
    if conversation_id is None:
        conversation_id = str(uuid4())

    history = conversations.setdefault(conversation_id, [])
    history.append({"role": "user", "content": message})
    history[:] = history[-settings.MAX_HISTORY_MESSAGES:]

    try:
        response = GroqService().generate_response(history)
    except GroqAuthenticationError:
        history.pop()
        return error_response("A API de inteligência artificial não está autenticada.", 401)
    except GroqRateLimitError:
        history.pop()
        return error_response("Limite de requisições atingido. Tente novamente mais tarde.", 429)
    except GroqConnectionError:
        history.pop()
        return error_response("Não foi possível conectar ao serviço de inteligência artificial.", 503)
    except GroqUnavailableError:
        history.pop()
        return error_response("O serviço de inteligência artificial está temporariamente indisponível.", 503)
    except GroqInvalidRequestError:
        history.pop()
        return error_response("A solicitação foi rejeitada pelo serviço de inteligência artificial.", 400)
    except GroqServiceError:
        history.pop()
        return error_response("Não foi possível processar a solicitação.", 500)

    history.append({"role": "assistant", "content": response})
    history[:] = history[-settings.MAX_HISTORY_MESSAGES:]

    return jsonify({"response": response, "conversation_id": conversation_id})


@chat_bp.post("/chat/clear")
def clear_chat():
    data, error = validate_json_body()
    if error:
        return error

    conversation_id, error = validate_conversation_id(data.get("conversation_id"))
    if error:
        return error
    if conversation_id is None:
        return error_response("O campo 'conversation_id' é obrigatório.", 422)

    conversations.pop(conversation_id, None)
    return jsonify({"status": "ok", "message": "Histórico da conversa limpo."})
