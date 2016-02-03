# In this example we are going to create a simple HTML
# page with 2 input fields (numbers), and a link.
# Using jQuery we are going to send the content of both
# fields to a route on our application, which will
# sum up both numbers and return the result.
# Again using jQuery we'l show the result on the page


# We'll render HTML templates and access data sent by GET
# using the request object from flask. jsonigy is required
# to send JSON as a response of a request
from flask import Flask, make_response, render_template, request, jsonify, redirect, url_for, send_from_directory
from functools import wraps, update_wrapper
from datetime import datetime
from werkzeug import secure_filename
import os
from time import sleep
import json
import random

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png'])
DATAFILE = 'vals.json'

# Initialize the Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/vals')
def vals():
    myvals = {"a": "100"}
    return json.dumps(myvals)

@app.route('/patient_info')
def patient_info():
    try:
        with open(DATAFILE, "r") as f:
            vals = f.read()
    except:
        import pdb; pdb.set_trace()

    return vals

@app.route('/')
@nocache
def index():
    return render_template('index.html')

@app.route('/room')
@nocache
def room():
    return render_template('server.html')

def update_code(auth_code):
    """
    modify datastore, return code
    """
    with open(DATAFILE, "r") as f:
        vals = json.loads(f.read())
    vals['values']['auth_code'] = auth_code
    with open(DATAFILE, "w") as f:
        f.write(json.dumps(vals))
    return auth_code

def read_code():
    with open(DATAFILE, "r") as f:
        vals = json.loads(f.read())
    return vals['values']['auth_code']

@app.route('/clear_code')
def clear_code():
    update_code(None)
    return "cleared"

@app.route('/request_code')
def request_code():
    """
    generate random code, modify datastore, return code
    """
    int_code = random.randint(0,99999)
    auth_code = str(int_code).zfill(5)
    return update_code(auth_code)

@app.route('/_update_server')
def update_server():
    name = request.args.get('name', 0, type=str)
    aboutme_001 = request.args.get('aboutme_001', 0, type=str)
    aboutme_002 = request.args.get('aboutme_002', 0, type=str)
    aboutme_003 = request.args.get('aboutme_003', 0, type=str)
    goals_001 = request.args.get('goals_001', 0, type=str)
    goals_002 = request.args.get('goals_002', 0, type=str)
    goals_003 = request.args.get('goals_003', 0, type=str)
    values = {'values':
                  {'name': name,
                   'aboutme_001': aboutme_001,
                   'aboutme_002': aboutme_002,
                   'aboutme_003': aboutme_003,
                   'goals_001': goals_001,
                   'goals_002': goals_002,
                   'goals_003': goals_003,
                   'auth_code': read_code(),
                   }}
    try:
        with open(DATAFILE, "w") as f:
            f.write(json.dumps(values))
    except:
        import pdb; pdb.set_trace()

    finally:
        return jsonify(result='success')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/_upload_photos', methods=['POST'])
def upload_photos():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

def upload(selected_filename):
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], selected_filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        # return redirect(url_for('uploaded_file', filename=selected_filename))
    return redirect(url_for('index'))

# Route that will process the file upload
@app.route('/upload_001', methods=['POST'])
def upload_001():
    selected_filename = 'file_001.png'
    return upload(selected_filename)

# Route that will process the file upload
@app.route('/upload_002', methods=['POST'])
def upload_002():
    selected_filename = 'file_002.png'
    return upload(selected_filename)

# Route that will process the file upload
@app.route('/upload_003', methods=['POST'])
def upload_003():
    selected_filename = 'file_003.png'
    return upload(selected_filename)

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
    )
