# Main Flask App placeholders 
from flask import Flask, request, jsonify
from match import calculate_match

app = Flask(__name__)

@app.route('/')
def home():
    return "RoomieMatch API is running"

@app.route('/get_matches', methods=['POST'])
def get_matches():
    user_data = request.json.get("user_data")
    all_users = request.json.get("all_users")

    matches = calculate_match(user_data, all_users)
    return jsonify(matches)

if __name__ == '__main__':
    app.run(debug=True)
