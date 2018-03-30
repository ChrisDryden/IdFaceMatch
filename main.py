from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
import os
import sys
import math
import numpy as np
import tensorflow as tf
import json
import pickle
from scipy.spatial import distance
 
app = Flask(__name__)

working_dir = os.getcwd() 
UPLOAD_FOLDER = working_dir + '/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

 
#Error handlers can be passed to seperate file
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')


@app.route('/')
def home():
    response = ''
    if not session.get('logged_in'):
        return render_template('login.html', response=response)
    else:
        return redirect(url_for('homepage'))

@app.route('/homepage')
def homepage():
	return render_template('homepage.html')

@app.route('/register', methods=['POST'])
def register():
    if not session.get('logged_in'):
        return render_template('register.html')
    else:
        return "Hello Boss!"


@app.route('/complete_registration', methods=['POST'])
def complete_registration():
    if not session.get('logged_in'):
        if request.form['password'] != '' and request.form['username'] != '':
            if request.form['password'] == request.form['confirm_password']:
                flash('Registration Successful')
                return register()
        flash('Wrong Password!')
        return register()
    else:
        return "Hello Boss!"
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    print("Processing file: " + file.filename)
    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(f)
    img_features = {}

    # Creates graph from saved graph_def.pb.
    graph_file = working_dir + '/inception/classify_image_graph_def.pb'
    with tf.gfile.FastGFile(graph_file, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      _ = tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
    #  Runs the network with the inputs of the picture.
    # 'pool_3:0': Next to last layer before neural network
    #  float description of the features of the image in vector form
      last_layer = sess.graph.get_tensor_by_name('pool_3:0')
      img_path = working_dir + '\\upload\\' + file.filename
      image_data = tf.gfile.FastGFile(img_path, 'rb').read()
      # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
      #   encoding of the image.
      features = sess.run(last_layer, {'DecodeJpeg/contents:0': image_data})
      img_features[file.filename] = list([float(x) for x in features[0][0][0]])
      print("Image completed: " + file.filename)

    print(img_features[file.filename])
    '''with open("Dict.txt", "rb") as my2File:
        data = pickle.load(my2File)
    chris = img_features[file.filename]
    closestname = ''
    closestvalue = 99999
    for item in data:
        a = chris
        b = data[item]
        dst = distance.euclidean(a,b)
        if dst < closestvalue:
            closestname = item
            closestvalue = dst
    print(closestname)  
    '''

    #imag = url_for('upload', filename = closestname)
    return render_template('register.html', complete=True)


# Serve static files
@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file
  return app.send_static_file(path)



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
#    app.run(debug=True, host='127.0.0.1', port=5000)
    app.run(debug=True, host='0.0.0.0', port=80)