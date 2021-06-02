from flask import Flask,request,send_file,send_from_directory
from flask_cors import CORS, cross_origin
from routes.auth import auth
from routes.detect import generate
from run_magenta import gen_melody
from werkzeug.utils import secure_filename

import bcrypt
import pymongo

# Project constants import
from constants import BASE_DIR
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/myapp")
db = client.get_database('total_records')
records = db.register
fileName = ""
out=""

@app.route("/")
@cross_origin()
def hello_world():
    return {'msg':'Hello, World!'}

app.register_blueprint(auth)
@app.route("/upload",methods=['POST'])
@cross_origin()
def upload():
    f = request.files['myFile']
    f.save(BASE_DIR+"routes/"+secure_filename(f.filename))
    fileName=secure_filename(f.filename)
    global out

    res = generate(fileName)
    out = res['fileName'].split('/')[-1]
    
    gen_melody(res['fileName'])
    print(out)
    return res
app.route("/gen")
@cross_origin()
def gen():
    generate(fileName)
    return {"msg":"done"}
@app.route("/getFile")
@cross_origin()
def getFile():
    print(out)
    return send_from_directory(BASE_DIR+'routes/',filename=out)
