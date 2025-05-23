# Main Flask App  
# Run in local testing mode: flask --app app --debug run
import os
import sys
import sqlite3
import flask
from flask import Flask, request, jsonify
import match
from flask_cors import CORS

DATABASE_PATH = 'roomie_match.db' if os.getenv('FLASK_DEBUG') else '/home/site/wwwroot/roomie_match.db'

# create the database if it doesn't exist
# (this is important for production deployment on azure)
if not os.path.exists(DATABASE_PATH):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    with open("CreateDB.SQL") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()

app = Flask(__name__)

# Allow requests from frontend URL 
# CORS(app, origins="https://roomiehopie.vercel.app") 
CORS(app, origins="*")

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
        # allow this to be automatic too
        cursor.execute("""INSERT INTO roommate_profiles(
                userID,
                firstname, lastname, case_email, gender, gender_preference, housing, year, major, major_preference,
                clean, noise, sleep, greeklife, guests, language, cook, smoke, against_smoker, drink, against_drinker,
                pets, against_pet, politics, politics_preference, religion,
                religion_preference, bio, top_1, top_2, top_3, profile_pic
            ) VALUES (
            :userID,
            :firstname, :lastname, :case_email, :gender, :gender_preference, :housing, :year, :major, :major_preference,
            :clean, :noise, :sleep, :greeklife, :guests, :language, :cook, :smoke, :against_smoker, :drink, :against_drinker,
            :pets, :against_pet, :politics, :politics_preference, :religion,
            :religion_preference, :bio, :top_1, :top_2, :top_3, :profile_pic
        )""", user_data)
        user_id = cursor.lastrowid
        # Insert hobbies into user_hobbies table
        if 'hobbies' in user_data:
            for hobby in user_data['hobbies']:
                # Get the hobbyID from the hobbies table
                cursor.execute("SELECT hobbyID FROM hobbies WHERE hobby = ?", (hobby,))
                hobby_id = cursor.fetchone()
                if hobby_id:
                    # Insert the user-hobby pair into the user_hobbies table
                    cursor.execute("INSERT INTO user_hobbies (userID, hobbyID) VALUES (?, ?)", (user_id, hobby_id[0]))

        conn.commit() # Commit changes to db 

    except sqlite3.IntegrityError as e:
        conn.rollback() # Rollback if there's an error 
        raise e

    return jsonify({ "user": user_id })

# needs to call match_roommates function in match.py 
@app.route('/get_matches', methods=['GET'])
def get_matches():
    user_id = int(request.args.get("user"))

    cursor = get_db().cursor()
    matches = match.get_matches(cursor, user_id)

    return jsonify(matches)

@app.route('/user', methods=['GET'])
def user():
    # Check if the userID parameter is provided in the request
    user_id = int(request.args.get("user"))
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    try:
        user_id = int(user_id) # Convert to integer 
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    
    # Create cursor and fetch the user data
    cursor = get_db().cursor()
    try:
        user_data = match.get_user(cursor, user_id) # Fetch user data from db 
        # Fetch user hobbies (pass user_id as argument)
        hobbies = match.get_user_hobbies(cursor, user_id) # Pass cursor and user_id
        user_data['hobbies'] = list(hobbies)
        return jsonify(user_data)
    
    except Exception as e:
        return jsonify({"error": f"Error fetching user data: {str(e)}"}), 500

@app.route('/accept', methods=['POST'])
def accept():
    user_id = int(request.args.get('user'))
    roommate_id = int(request.args.get('roommate'))

    conn = get_db()
    cursor = conn.cursor()
    # Make sure both users exist in db 
    cursor.execute("SELECT userID FROM roommate_profiles WHERE userID = ? OR userID = ?", (user_id, roommate_id))
    result = cursor.fetchall()
    if len(result) != 2:
        return jsonify({"error": "One or both user IDs do not exist in roommate_profiles."}), 400

    try:
        cursor.execute("INSERT INTO user_accepted VALUES(?, ?)", (user_id, roommate_id))
        conn.commit()
        return jsonify({"message": "Roommie Match accepted!"}), 200
    except Exception as e:
        app.logger.error(f"Error while accepting match: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/reject', methods=['POST'])
def reject():
    user_id = int(request.args.get('user'))
    roommate_id = int(request.args.get('roommate'))

    conn = get_db()
    cursor = conn.cursor()
    # Insert user into rejections table
    cursor.execute("INSERT INTO user_rejections VALUES(?, ?)", (user_id, roommate_id))
    conn.commit()
    return jsonify({"message": "Match rejected. "}), 200

# Delete a user from any table (handles cascading deletes) 
@app.route('/delete', methods=['DELETE'])
def delete():
    user_id = int(request.args.get('user'))
    conn = get_db()
    cursor = conn.cursor()

    # Delete from roommate_profiles, user_accepted, user_rejections, user_hobbies, etc.
    cursor.execute("DELETE FROM user_accepted WHERE userID = ? OR acceptedUserID = ?", (user_id, user_id))
    cursor.execute("DELETE FROM user_rejections WHERE userID = ? OR rejectedUserID = ?", (user_id, user_id))
    cursor.execute("DELETE FROM user_hobbies WHERE userID = ?", (user_id,))
    cursor.execute("DELETE FROM roommate_profiles WHERE userID = ?", (user_id,))
    conn.commit()

    return jsonify({"message": "User deleted successfully."}), 200

@app.route('/get_mutuals', methods=['GET'])
def get_mutuals():
    user_id = int(request.args.get("user"))
    cursor = get_db().cursor()

    query = """SELECT u2.userID
               FROM user_accepted r1
               INNER JOIN user_accepted r2 ON r1.acceptedUserID = r2.userID
               INNER JOIN roommate_profiles u2 ON r2.userID = u2.userID
               WHERE r1.userID = ? AND r2.acceptedUserID = ?"""

    cursor.execute(query, (user_id, user_id))
    results = [row[0] for row in cursor.fetchall()]

    return jsonify(results)

if __name__ == '__main__':
    app.run()