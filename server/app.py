#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):

    def get(self):
        response_dict = {
            "message": "Welcome to the Newsletter RESTful API",
        }
        return make_response(jsonify(response_dict), 200)

api.add_resource(Home, '/')

class Newsletters(Resource):

    def get(self):
        response_dict_list = [n.to_dict() for n in Newsletter.query.all()]
        return make_response(jsonify(response_dict_list), 200)

    def post(self):
        try:
            data = request.get_json()  # Expecting JSON input
            
            new_record = Newsletter(
                title=data['title'],
                body=data['body'],
            )

            db.session.add(new_record)
            db.session.commit()

            return make_response(jsonify(new_record.to_dict()), 201)

        except Exception as e:
            return make_response({"error": str(e)}, 400)

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):

    def get(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if not record:
            return make_response(jsonify({"message": "Newsletter not found"}), 404)
        
        return make_response(jsonify(record.to_dict()), 200)
    
    def patch(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if not record:
            return make_response(jsonify({"message": "Newsletter not found"}), 404)

        try:
            data = request.get_json()  # Expecting JSON input
            
            for attr in data:
                setattr(record, attr, data[attr])
            
            db.session.add(record)
            db.session.commit()
            
            return make_response(jsonify(record.to_dict()), 200)

        except Exception as e:
            return make_response({"error": str(e)}, 400)
    
    def delete(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        if not record:
            return make_response(jsonify({"message": "Newsletter not found"}), 404)

        db.session.delete(record)
        db.session.commit()

        return make_response(jsonify({"message": f"Newsletter with id {id} deleted successfully"}), 200)

api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
