from flask import Flask, jsonify, request
from app.handlers.farmers_markets_handler import FarmersMarketHandler
from app.handlers.market_info_handler import MarketInfoHandler

app = Flask(__name__)
market_handler = FarmersMarketHandler()
market_info_handler = MarketInfoHandler(market_handler)

@app.route('/api/get_filters', methods=['GET'])
def get_filters():
    filters = market_handler.get_filters()
    return jsonify(filters)

@app.route('/api/find_markets_from_radius', methods=['GET'])
def find_markets_from_radius():
    data = request.json
    results = market_handler.find_markets_from_radius(data)
    return jsonify(results)

@app.route('/api/post_market', methods=['POST'])
def post_market():
    data = request.json
    market_info = market_info_handler.get_market_info(data['listing_id'])
    return jsonify(market_info)

@app.route('/api/get_random_markets', methods=['GET'])
def get_random_markets():
    random_markets = market_info_handler.get_random_markets()
    return jsonify(random_markets)

@app.route('/api/query_results', methods=['POST'])
def query_results():
    data = request.json
    results = market_handler.query_results(data)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
