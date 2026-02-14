# api/chat_routes.py
from flask import Blueprint, request, jsonify
from core.conversation_manager import ConversationManager
from user.conversation_manag import ConversationManag
import traceback
from scraping.scheduler import run_sync_pipeline

chat_bp = Blueprint('chat', __name__)
manager = ConversationManager()
user=ConversationManag()
#start_scheduler()
# Route 1
@chat_bp.route('/message', methods=['POST'])
def handle_basic_message():

    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
    
    user_id = data.get("user_id", "default_user")
    user_message = data.get("message", "")

    try:
        response_text = manager.handle_message(user_id, user_message)

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "response": response_text
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# Route 2
@chat_bp.route('/user/message', methods=['POST'])
def handle_user_message():

    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
    
    user_id = data.get("user_id", "default_user")
    user_message = data.get("message", "")
    user_uuid = data.get("uuid", None)

    try:
        response_text = user.handle_message(user_id, user_message, user_uuid)

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "response": response_text,
            "uuid": user_uuid
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# Route 3 – Manual Model Sync
@chat_bp.route('/syncmodel', methods=['POST'])
def sync_model():

    try:
        run_sync_pipeline()

        return jsonify({
            "status": "success",
            "message": "Model sync completed successfully"
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
