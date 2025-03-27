# Main Flask App placeholders 
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "RoomieMatch API is running"

@app.route('/create_user', methods=['POST'])
def create_user():
    user_data = request.json

    print("CREATING USER", user_data)

    user_id = 420

    return jsonify({ "user": user_id })

@app.route('/get_matches')
def get_matches():
    user_id = request.args.get("user")

    # TODO compute matches with user``
    matches = [
        { "user_id": 320, "score": 0.5 },
        { "user_id": 20, "score": 0.7 },
    ]

    return jsonify(matches)

@app.route('/user')
def user():
    user_id = request.args.get("user")

    # TODO retrieve user data from db
    user_data = { "field1": 0, "field2": 1 }

    return jsonify(user_data)

if __name__ == '__main__':


    app.run(debug=True)
