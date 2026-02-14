# app.py
from flask import Flask
from api.chat_routes import chat_bp
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/chat/*": {"origins": "*"}})
    app.register_blueprint(chat_bp, url_prefix='/chat')

    @app.route('/')
    def health_check():
        return "Chatbot API is running!", 200

    return app

if __name__ == '__main__':
    app = create_app()
    
   
    app.run(host='0.0.0.0', port=5000, debug=True)