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


@app.route('/config/lb/<id>', methods=['DELETE'])
def delete_loadbalancer(id):
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'loadbalancer.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        new_data = [lb for lb in data if str(lb.get('id')) != str(id)]
        
        if len(data) == len(new_data):
            return jsonify({"error": "Load Balancer non trouvé"}), 404
            
        with open(file_path, 'w') as file:
            json.dump(new_data, file, indent=4)
            
        return jsonify({"message": "Suppression réussie"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# PARTIE REVERSE PROXY
# ==========================================

@app.route('/config/rp', methods=['GET'])
def get_reverseproxys():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'reverseproxy.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify([])
    


@app.route('/config/rp/<id>', methods=['GET'])
def get_reverseproxy(id):
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'reverseproxy.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for rp in data:
                if str(rp.get('id')) == str(id):
                    return jsonify(rp)
            return jsonify({"error": "Reverse Proxy non trouvé"}), 404
    except FileNotFoundError:
        return jsonify({"error": "Fichier reverseproxy.json introuvable"}), 404
    

@app.route('/config/rp', methods=['POST'])
def create_reverseproxy():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'reverseproxy.json')
    try:
        new_data = request.json
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        new_id = max([rp.get('id', 0) for rp in data]) + 1 if len(data) > 0 else 1
        new_data['id'] = new_id
        
        data.append(new_data)
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            
        return jsonify({"message": "Création réussie", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config/rp/<id>', methods=['DELETE'])
def delete_reverseproxy(id):
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'reverseproxy.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        new_data = [rp for rp in data if str(rp.get('id')) != str(id)]
        
        if len(data) == len(new_data):
            return jsonify({"error": "Reverse Proxy non trouvé"}), 404
            
        with open(file_path, 'w') as file:
            json.dump(new_data, file, indent=4)
            
        return jsonify({"message": "Suppression réussie"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ==========================================
# PARTIE WEB SERVER
# ==========================================

@app.route('/config/ws', methods=['GET', 'POST'])
def handle_webservers():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'webserver.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        if request.method == 'GET':
            return jsonify(data)
            
        elif request.method == 'POST':
            new_data = request.json
            new_id = max([ws.get('id', 0) for ws in data]) + 1 if len(data) > 0 else 1
            new_data['id'] = new_id
            data.append(new_data)
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return jsonify({"message": "Création réussie", "id": new_id}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/ws/<id>', methods=['GET', 'DELETE'])
def handle_single_webserver(id):
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'webserver.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
        if request.method == 'GET':
            for ws in data:
                if str(ws.get('id')) == str(id):
                    return jsonify(ws)
            return jsonify({"error": "Web Server non trouvé"}), 404
            
        elif request.method == 'DELETE':
            new_data = [ws for ws in data if str(ws.get('id')) != str(id)]
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=4)
            return jsonify({"message": "Suppression réussie"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


    
if __name__ == '__main__':
    app.run(debug=False, port=5001)