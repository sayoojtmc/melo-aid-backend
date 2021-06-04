from flask import Flask,request,send_file,send_from_directory
from flask_cors import CORS, cross_origin
from routes.auth import auth
from routes.detect import generate
from run_magenta import gen_melody
from werkzeug.utils import secure_filename
import bcrypt
from moviepy.editor import *
import pymongo
import os
import glob
# Project constants import
from constants import BASE_DIR
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/myapp")
db = client.get_database('total_records')
records = db.register
filePath = ""
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
    if(fileName[-3:] == "mp4"):
        video = VideoFileClip(BASE_DIR+"routes/"+fileName).subclip(0,20)
        audio = video.audio
        audio.write_audiofile(BASE_DIR+"routes/"+"audio-trimmed.mp3")
    else:
        audio = AudioFileClip(BASE_DIR+"routes/"+fileName).subclip(0,20)
        audio.write_audiofile(BASE_DIR+"routes/"+"audio-trimmed.mp3")
    global out
    fileName="audio-trimmed.mp3"

    res = generate(fileName)
    out = res['fileName'].split('/')[-1]
    
    global filePath
    filePath=res['fileName']
    print(out)
    return res
@app.route("/getFile")
@cross_origin()
def getFile():
    print(out)
    return send_from_directory(BASE_DIR+'routes/',filename=out)
@app.route("/genMelody")
@cross_origin()
def genMelody():
    global filePath
    gen_melody(filePath)
    list_of_files = glob.glob(BASE_DIR+"magenta/generated/*")
    files = sorted(list_of_files,key=os.path.getctime)[-3:]
    for i,j in enumerate(files):
        files[i] = j.split('/')[-1]
    return {"files":files} 
