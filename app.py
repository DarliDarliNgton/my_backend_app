import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db
import logging
from datetime import timedelta
from sqlalchemy import text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Инициализация расширений
    db.init_app(app)
    jwt = JWTManager(app)
    Migrate(app, db)
    CORS(app, resources={r"/api/*": {
        "origins": "*",
        "allow_headers": ["Authorization", "Content-Type"],
        "supports_credentials": True
    }})

    # Регистрация blueprint
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.orders import orders_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')

    # Обработчики ошибок JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'The access token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        # Добавлено логирование для диагностики
        app.logger.error(f"Invalid token error: {str(error)}")
        return jsonify({
            'error': 'invalid_token',
            'message': 'Token verification failed'
        }), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'error': 'unauthorized',
            'message': 'Missing access token'
        }), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'fresh_token_required',
            'message': 'Fresh token required'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_revoked',
            'message': 'Token has been revoked'
        }), 401

    # Проверка подключения к БД при запуске
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            app.logger.info("✅ Database connection successful")
        except Exception as e:
            app.logger.error(f"❌ Database connection error: {str(e)}")

    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal Server Error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'}), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
