from flask import Flask, render_template, request, jsonify
from black_scholes import calculate_black_scholes, required_stock_price  # Import the new function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging

        # Extracting data from the frontend
        S = float(data['S'])
        K = float(data['K'])
        T = float(data['T'])  # Already converted to years in frontend
        r = float(data['r'])
        option_price = float(data['option_price'])
        option_type = data['option_type']
        days_later = float(data.get('days_later', 0))  # New input, default to 0 if not provided

        # Perform Black-Scholes calculation
        results = calculate_black_scholes(S, K, T, r, option_price, option_type)
        print("Calculation results:", results)  # Debugging

        # Calculate required stock price if days_later is provided and valid
        if days_later > 0 and days_later < T * 365:  # Ensure days_later is reasonable
            stock_price_results = required_stock_price(
                S, K, T, r, option_price, results['sigma'], option_type, days_later
            )
            results.update(stock_price_results)  # Merge the results

        return jsonify(results)

    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)