from flask import Flask, request, jsonify, url_for, redirect
from werkzeug.utils import secure_filename
from labtestocr import bloodtest, stooltest, urinetest
import os

app = Flask(__name__)
# need to make a upload folder in the current directory
# for saving pictures coming from POST
UPLOAD_FOLDER = 'upload'
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

@app.route('/result/<filename>', methods=['GET'])
def get_result(filename):
	# fetch the file
	file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
	labtest = urinetest(file)
	# return the result
	return jsonify(labtest.result())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



if __name__ == '__main__':
	app.run(debug=True)