from flask import Flask, jsonify, request, make_response
import json
import os
from datetime import datetime
import random

app = Flask(__name__)

HISTORY_FILE = 'history.json'

# Manual CORS handling
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.route('/play', methods=['POST', 'OPTIONS'])
def play_game():
    if request.method == 'OPTIONS':
        return make_response()
    
    data = request.get_json()
    user_choice = data.get('choice')
    choices = ['rock', 'paper', 'scissors']
    
    if user_choice not in choices:
        return jsonify({'error': 'Invalid choice'}), 400
    
    computer_choice = random.choice(choices)
    
    # Determine winner
    if user_choice == computer_choice:
        result = 'tie'
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'scissors' and computer_choice == 'paper') or \
         (user_choice == 'paper' and computer_choice == 'rock'):
        result = 'win'
    else:
        result = 'lose'
    
    # Save to history
    match = {
        'timestamp': datetime.now().isoformat(),
        'user_choice': user_choice,
        'computer_choice': computer_choice,
        'result': result
    }
    
    history = load_history()
    history.append(match)
    save_history(history)
    
    return jsonify({
        'computer_choice': computer_choice,
        'result': result
    })

@app.route('/history', methods=['GET', 'OPTIONS'])
def get_history():
    if request.method == 'OPTIONS':
        return make_response()
    
    history = load_history()
    return jsonify(history)

@app.route('/reset', methods=['POST', 'OPTIONS'])
def reset_history():
    if request.method == 'OPTIONS':
        return make_response()

    save_history([])  # Clears the history file
    return jsonify({'message': 'History reset successfully'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
