from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config.settings import settings
from routes.chat import chat_bp


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

    origins = [o.strip() for o in settings.CORS_ORIGIN.split(",") if o.strip()]
    if settings.FLASK_ENV == "production" and "*" in origins:
        raise ValueError("CORS_ORIGIN não pode ser * em produção.")

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(chat_bp)

    @app.get("/")
    def index():
        return jsonify({"status": "ok", "message": "Copa do Mundo AI API is running"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": True, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_internal_error(error):
        app.logger.exception("Erro interno: %s", type(error).__name__)
        return jsonify({"error": True, "message": "Ocorreu um erro interno no servidor."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=settings.FLASK_ENV == "development",
    )
