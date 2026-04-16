from flask import Flask, render_template, request, redirect, Response, session
import requests

app = Flask(__name__)

app.secret_key = "six_seven" 

ADMIN_USER = "root"
ADMIN_PASS = "root123"

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


@app.route('/lb/delete/<id>', methods=['GET'])
def delete_lb(id):
    try:
        response = requests.delete(f"{API_URL}/config/lb/{id}")
        
        return redirect('/lb/list')
        
    except requests.exceptions.ConnectionError:
        return "Erreur de connexion à l'API."
    

@app.route('/lb/download/<id>')
def download_lb(id):
    response = requests.get(f"{API_URL}/config/lb/{id}")
    if response.status_code != 200:
        return "Erreur de récupération", 404
        
    lb = response.json()
    
    nginx_content = f"""# Configuration générée pour : {lb.get('name')}
http {{
    server_tokens off;

    server {{
        listen 80;
        server_name {lb.get('ip_bind')}; 

        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";

        location / {{
            proxy_pass {lb.get('pass')};

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }}
    }}
}}"""

    safe_filename = lb.get('name').lower().replace(' ', '-') + ".conf"

    return Response(
        nginx_content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={safe_filename}"}
    )


# ==========================================
# PARTIE REVERSE PROXY
# ==========================================

@app.route('/rp/list', methods=['GET'])
def list_rp():
    try:
        response = requests.get(f"{API_URL}/config/rp")
        data = response.json()
        return render_template('rp_list.html', reverseproxys=data)
    except requests.exceptions.ConnectionError:
        return "Erreur : Impossible de se connecter à l'API."
    
@app.route('/rp/<id>', methods=['GET'])
def detail_rp(id):
    try:
        response = requests.get(f"{API_URL}/config/rp/{id}")
        if response.status_code == 200:
            rp_data = response.json()
            return render_template('rp_detail.html', rp=rp_data)
        else:
            return "Erreur : Reverse Proxy introuvable", 404
    except requests.exceptions.ConnectionError:
        return "Erreur de connexion à l'API."


@app.route('/rp/create', methods=['GET', 'POST'])
def create_rp():
    if request.method == 'POST':
        servers_input = request.form.get('servers')
        servers_list = [s.strip() for s in servers_input.split(',')] if servers_input else []
        
        new_rp = {
            "name": request.form.get('name'),
            "servers": servers_list
        }
        
        response = requests.post(f"{API_URL}/config/rp", json=new_rp)
        
        if response.status_code == 201:
            return redirect('/rp/list')
        else:
            return "Erreur lors de la création côté API", 500

    return render_template('rp_create.html')


@app.route('/rp/delete/<id>', methods=['GET'])
def delete_rp(id):
    try:
        requests.delete(f"{API_URL}/config/rp/{id}")
        return redirect('/rp/list')
    except requests.exceptions.ConnectionError:
        return "Erreur de connexion à l'API."
    

# ==========================================
# PARTIE WEB SERVER
# ==========================================

@app.route('/ws/list')
def list_ws():
    response = requests.get(f"{API_URL}/config/ws").json()
    return render_template('ws_list.html', webservers=response)

@app.route('/ws/<id>')
def detail_ws(id):
    response = requests.get(f"{API_URL}/config/ws/{id}").json()
    return render_template('ws_detail.html', ws=response)

@app.route('/ws/create', methods=['GET', 'POST'])
def create_ws():
    if request.method == 'POST':
        new_ws = {
            "name": request.form.get('name'),
            "root": request.form.get('root'),
            "error_page": request.form.get('error_page'),
            "error_root": request.form.get('error_root')
        }
        requests.post(f"{API_URL}/config/ws", json=new_ws)
        return redirect('/ws/list')
    return render_template('ws_create.html')

@app.route('/ws/delete/<id>')
def delete_ws(id):
    requests.delete(f"{API_URL}/config/ws/{id}")
    return redirect('/ws/list')

# --- SYSTEME D'AUTHENTIFICATION ---

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    
    if request.endpoint not in allowed_routes and not session.get('logged_in'):
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['logged_in'] = True
            return redirect('/')
        else:
            error = "Identifiants incorrects. Veuillez réessayer."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=False, port=5000)