from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields, reqparse
import requests
import os
from labtestocr import bloodtest, urinetest, stooltest


flask_app = Flask(__name__)
api = Api(app = flask_app, 
          version = "1.0", 
          title = "Labtest OCR", 
          description = "Receive image and return name/value/confidence of a test")

UPLOAD_FOLDER = 'upload/'
flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
flask_app.config['JSON_AS_ASCII'] = False

# name_space = api.namespace('Images', description='Retrive test values')

input_url = reqparse.RequestParser()
input_url.add_argument('url',
                        type=str,
                        required=True,
                        location='url',
                        help='URL')

@api.route('/upload')
class ocr_result(Resource):

    @api.expect(input_url)
    def post(self):
        url = request.args['url']
        file = requests.get(url)
        name = url.split('/')[-1]
        filename = '%s%s' % (flask_app.config['UPLOAD_FOLDER'], name)
        with open(filename, 'wb') as f:
            f.write(file.content)
        labtest = bloodtest(filename)
        return jsonify(labtest.result())

if __name__ == '__main__':
    flask_app.run(debug=True)

