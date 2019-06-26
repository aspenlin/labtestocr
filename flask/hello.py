from flask import Flask, request, jsonify, url_for, redirect
from werkzeug.utils import secure_filename
# from tess import result
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/Users/jingjinglin/Machine_Learning/Siuvo2019SummerIntern/Tesseract-OCR/flask/static/upload'
app.config['JSON_AS_ASCII'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# the file coming from post
		file = request.files['file']
		filename = secure_filename(file.filename)
		# save the file
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# return tessocr result
		return redirect(url_for('get_result', filename=filename))

	return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/<filename>', methods=['GET'])
def get_result(filename):
	# fetch the file
	file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	# return the result
	return str(file)



if __name__ == '__main__':
	app.run()