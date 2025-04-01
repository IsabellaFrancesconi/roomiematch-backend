# Main Flask App placeholders 
import sqlite3
import flask
from flask import Flask, request, jsonify
import match

DATABASE_PATH = 'roomie_match.db'

app = Flask(__name__)

def get_db():
    db = getattr(flask, '_database', None)
    if db is None:
        db = flask._database = sqlite3.connect(DATABASE_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask, '_database', None)
    if db is not None:
        db.close()
        flask._database = None

@app.route('/')
def home():
    return """
    <marquee>RoomieMatch API is running</marquee.
    """

@app.route('/create_user', methods=['POST'])
def create_user():
    user_data = request.json #Input data coming from frontend 

    conn = get_db()
    cursor = conn.cursor()

    # TO DO Edit below 
    try:
        # setting userID to none will cause it to automatically be filled in by the database
        user_data['userID'] = None
        cursor.execute("""INSERT INTO roommate_profiles VALUES (
            :userID,
            :firstname, :lastname, :case_email, :gender, :gender_preference, :housing, :year, :major, :major_preference,
            :clean, :noise, :sleep, :greeklife, :guests, :language, :cook, :smoke, :against_smoker, :drink, :against_drinker,
            :pets, :against_pet, :politics, :politics_preference, :religion,
            :religion_preference, :bio, :top_1, :top_2, :top_3, :profile_pic
        )""", user_data)
        user_id = cursor.lastrowid

        # TODO insert user hobbies into the `user_hobbies` table

        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise e

    return jsonify({ "user": user_id })

# needs to call match_roommates function in match.py 
@app.route('/get_matches')
def get_matches():
    user_id = int(request.args.get("user"))

    cursor = get_db().cursor()
    matches = match.get_matches(cursor, user_id)

    return jsonify(matches)

@app.route('/user')
def user():
    user_id = int(request.args.get("user"))

    cursor = get_db().cursor()
    user_data = match.get_user(cursor, user_id)

    return jsonify(user_data)

@app.route('/accept')
def accept():
    user_id = int(request.args.get('user'))
    roommate_id = int(request.args.get('roommate'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_accepted VALUES(?, ?)", (user_id, roommate_id))
    conn.commit()

    return 'success', 200

@app.route('/reject')
def reject():
    user_id = int(request.args.get('user'))
    roommate_id = int(request.args.get('roommate'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_rejections VALUES(?, ?)", (user_id, roommate_id))
    conn.commit()

    return 'success', 200

if __name__ == '__main__':
    app.run(debug=True)

# Delete users method to be edited 
@app.route('/delete', methods=['DELETE'])
def delete():
    # Placeholder Logic 
    return jsonify({"message": "DELETE endpoint is ready, but not implemented yet."}), 200
