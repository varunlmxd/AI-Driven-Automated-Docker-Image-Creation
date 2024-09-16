from flask import Flask, jsonify, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Hello(Resource):
    def get(self):
        return jsonify({'message': "Hello World"})

    def post(self):
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Bad request', 'message': 'No message field provided'}), 400
        return jsonify({"message": data["message"]})

class Square(Resource):
    def get(self, num):
        try:
            return jsonify({'square': num ** 2})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

class Cube(Resource):
    def get(self, num):
        try:
            return jsonify({'cube': num ** 3})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

api.add_resource(Hello, '/')
api.add_resource(Square, '/square/<int:num>')
api.add_resource(Cube, '/cube/<int:num>')

if __name__ == '__main__':
    app.run(debug=True)
