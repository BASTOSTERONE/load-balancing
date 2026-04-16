from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5001"

@app.route("/")
def start(): 
    return render_template('start.html')
    

@app.route('/lb/list', methods=['GET'])
def list_lb():
    try:
        response = requests.get(f"{API_URL}/config/lb")
        
        data = response.json()
        
        return render_template('lb_list.html', loadbalancers=data)
    
    except requests.exceptions.ConnectionError:
        return "Erreur : Impossible de se connecter à l'API."
    
@app.route('/lb/<id>', methods=['GET'])
def detail_lb(id):
    try:
        response = requests.get(f"{API_URL}/config/lb/{id}")
        
        if response.status_code == 200:
            lb_data = response.json()
            return render_template('lb_detail.html', lb=lb_data)
        else:
            return "Erreur : Load-balancer introuvable", 404
            
    except requests.exceptions.ConnectionError:
        return "Erreur de connexion à l'API."


@app.route('/lb/create', methods=['GET', 'POST'])
def create_lb():

    if request.method == 'POST':
        new_lb = {
            "name": request.form.get('name'),
            "ip_bind": request.form.get('ip_bind'),
            "pass": request.form.get('pass')
        }
        
        response = requests.post(f"{API_URL}/config/lb", json=new_lb)
        
        if response.status_code == 201:
            return redirect('/lb/list')
        else:
            return "Erreur lors de la création côté API", 500

    return render_template('lb_create.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)