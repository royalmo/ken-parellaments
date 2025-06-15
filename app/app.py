from flask import Flask, render_template, request
from pairings import store_request_to_json, JSON_FILE_PATH

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('pairings.html')

@app.route("/data.json")
def data():
    with open(JSON_FILE_PATH) as f:
        return f.read()
    
@app.route("/make-pairings", methods=["POST"])
def make_pairings():
    new_json = store_request_to_json(request.form)
    return 'DONE!'

if __name__=="__main__":
    app.run(debug=True, port=5000)
