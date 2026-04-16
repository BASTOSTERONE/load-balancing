from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, API!"


@app.route('/config/lb', methods=['GET'])
def get_loadbalancers():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'loadbalancer.json')
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Fichier loadbalancer.json introuvable"}), 404

@app.route('/config/lb/<id>', methods=['GET'])
def get_loadbalancer(id):
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'loadbalancer.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for lb in data:
                if str(lb.get('id')) == str(id):
                    return jsonify(lb)
            
            return jsonify({"error": "Load-balancer non trouvé"}), 404
            
    except FileNotFoundError:
        return jsonify({"error": "Fichier loadbalancer.json introuvable"}), 404


@app.route('/config/lb', methods=['POST'])
def create_loadbalancer():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'loadbalancer.json')
    try:
        new_data = request.json
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        if len(data) > 0:
            new_id = max([lb.get('id', 0) for lb in data]) + 1
        else:
            new_id = 1
            
        new_data['id'] = new_id
        
        data.append(new_data)
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            
        return jsonify({"message": "Création réussie", "id": new_id}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)