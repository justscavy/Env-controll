from flask import Flask, render_template, request, jsonify
from shared_state import shared_state

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', state=shared_state)

@app.route('/update_vpd', methods=['POST'])
def update_vpd():
    data = request.json
    shared_state.min_vpd = float(data['min_vpd'])
    shared_state.max_vpd = float(data['max_vpd'])
    return jsonify(success=True)

@app.route('/get_states', methods=['GET'])
def get_states():
    states = {
        "min_vpd": shared_state.min_vpd,
        "max_vpd": shared_state.max_vpd,
    }
    return jsonify(states=states)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
