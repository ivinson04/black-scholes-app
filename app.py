from flask import Flask, render_template, request, jsonify
from black_scholes import calculate_black_scholes  # Import the function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()

        # Extracting data from the frontend
        S = float(data['S'])
        K = float(data['K'])
        T = float(data['T'])  # Already converted to years in frontend
        r = float(data['r'])
        option_price = float(data['option_price'])
        option_type = data['option_type']

        # Perform Black-Scholes calculation
        results = calculate_black_scholes(S, K, T, r, option_price, option_type)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Keep it running on port 5001
