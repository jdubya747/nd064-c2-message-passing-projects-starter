import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaProducer
from flask import Flask, jsonify, g
db = SQLAlchemy()

def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="UdaConnect API", version="0.1.0")

    CORS(app)  # Set CORS for development

    register_routes(api, app)
    db.init_app(app)

    @app.before_request
    def before_request():
        # Set up a Kafka producer
        KAFKA_SERVER = 'kafka:9092'
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        # Setting Kafka to g enables us to use this
        # in other parts of our application
        g.kafka_producer = producer

    @app.route("/health")
    def health():
        return jsonify("healthy")
  
    return app
