from flask import Flask, request, jsonify
from jwt_utils import build_token
from flask_cors import CORS
from werkzeug.exceptions import Unauthorized
import hashlib
from services.question_service import create_question, get_question_by_id_from_db, get_question_by_position,delete_question_by_position,delete_question_by_id,delete_all_questions,update_question_by_id,delete_all_participations,get_quiz_info_handler,create_participation_handler,get_all_questions
from models.question_model import Question, question_to_json
from services.rebuild_service import rebuild_database
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def hello_world():
	x = 'world'
	return f"Hello, {x}"

@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
    try:
        data = get_quiz_info_handler()
        return jsonify(data), 200
    except Exception as e:
        print(f"Error in /quiz-info: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/login", methods=["POST"])
def login():
    payload = request.get_json()

    if not payload or 'password' not in payload:
        return jsonify({"error": "Password required"}), 400

    tried_password = payload['password'].encode('utf-8')
    hashed = hashlib.md5(tried_password).digest()
    
    EXPECTED_HASH=b'\xd2x\x07{\xbf\xe7(Z\x14MK[\x11\xad\xb9\xcf'
    if hashed == EXPECTED_HASH:
        token = build_token()
        return jsonify({"token": token})
    else:
        raise Unauthorized("Incorrect password")

@app.route('/questions', methods=['POST'])
@require_auth
def post_question():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON"}), 400

    try:
        new_question_id = create_question(data)
        return jsonify({"message": "Question created", "id": new_question_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions', methods=['GET'])
def get_questions():
    try:
        position = request.args.get('position', type=int)
        
        if position is not None:
            question = get_question_by_position(position)
            if not question:
                return jsonify({"error": "Question not found"}), 404
            return jsonify(question_to_json(question)), 200
        else:
            questions = get_all_questions()
            return jsonify([question_to_json(q) for q in questions]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions/<int:questionId>', methods=['GET'])
def get_question_by_id(questionId):
    try:
        question = get_question_by_id_from_db(questionId) 
        if not question:
            return jsonify({"error": "Question not found"}), 404

        return jsonify(question_to_json(question)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions', methods=['GET'])
def get_question():
    try:
        position = request.args.get('position', type=int)
        if position is None:
            return jsonify({"error": "Missing or invalid 'position' parameter"}), 400

        question = get_question_by_position(position)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        return jsonify(question_to_json(question)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    
@app.route('/questions/<int:question_id>', methods=['PUT'])
@require_auth
def update_question(question_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON"}), 400

    try:
        updated = update_question_by_id(question_id, data)
        if not updated:
            return jsonify({"error": "Question not found"}), 404
        return jsonify({"message": "Question updated"}), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions/position', methods=['DELETE'])
@require_auth
def handle_delete_by_position():
    try:
        position = request.args.get('position', type=int)
        if position is None:
            return jsonify({"error": "Missing or invalid 'position' parameter"}), 400

        success = delete_question_by_position(position)
        if not success:
            return jsonify({"error": "Question not found"}), 404

        return '', 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions/<int:question_id>', methods=['DELETE'])
@require_auth
def handle_delete_by_id(question_id):
    try:
        success = delete_question_by_id(question_id)
        if not success:
            return jsonify({"error": "Question not found"}), 404

        return '', 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/questions/all', methods=['DELETE'])
@require_auth
def handle_delete_all():
    try:
        delete_all_questions()
        return '', 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/participations/all', methods=['DELETE'])
@require_auth
def handle_delete_all_participations():
    try:
        delete_all_participations()
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/participations', methods=['POST'])
def create_participation():
    try:
        json_data = request.get_json()

        if not json_data or 'playerName' not in json_data or 'answers' not in json_data:
            return jsonify({"error": "Missing playerName or answers"}), 400

        player_name = json_data['playerName']
        submitted_answers = json_data['answers']

        result= create_participation_handler(player_name, submitted_answers)
        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        print(f"Error in POST /participations: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/rebuild-db', methods=['POST'])
@require_auth
def rebuild_db_endpoint():
    try:
        rebuild_database()
        return "Ok", 200
    except Exception as e:
        print("Error rebuilding DB:", e)
        return jsonify({"error": "Failed to rebuild database"}), 500

if __name__ == "__main__":
    app.run()

