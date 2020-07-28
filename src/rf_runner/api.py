import json
import logging
from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from rf_runner.publisher_factory import PublisherFactory
from rf_runner.fetcher_factory import FetcherFactory
from rf_runner.config import Config
from rf_runner.runner import Runner

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig()
# logger = logging.getLogger("fetcher")
# logger.setLevel(logging.DEBUG)

app = Flask(__name__)
CORS(app)
config = Config()
runner = Runner(config)


@app.route('/api/publishers', methods=['GET'])
def publishers():
    return jsonify(PublisherFactory.get_meta())


@app.route('/api/publishers_conf', methods=['GET', 'POST'])
def publishers_conf():
    if request.method == 'POST':
        config.load_publisher(request.json)
        return {'success': True}, 200
    if request.method == 'GET':
        return jsonify(config.get_publisher())


@app.route('/api/fetchers', methods=['GET'])
def fetchers():
    return jsonify(FetcherFactory.get_meta())


@app.route('/api/fetchers_conf', methods=['GET', 'POST'])
def fetchers_conf():
    if request.method == 'POST':
        config.load_fetcher(request.json)
        return {'success': True}, 200
    if request.method == 'GET':
        return jsonify(config.get_fetcher())


@app.route('/api/tests', methods=['GET'])
def tests():
    return jsonify(runner.discover_tests())


@app.route('/api/run', methods=['POST'])
def run():
    runner.run()
    return {'success': True}, 200


if __name__ == "__main__":
    app.run()
