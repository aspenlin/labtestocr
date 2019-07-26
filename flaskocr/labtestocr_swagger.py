# 2019-07 Jingjing Lin, joejoeustc@gmail.com
# python version 3.5.2, flask version 1.1.0, flask_restplus version 0.12.1
# requests version 2.22.0
# usage: using flask_restplus to setup swagger interface
import os
import requests
from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, reqparse
# labtestocr is the class written by JJLin to parse result from a labtest report
from labtestocr import bloodTest, urineTest, stoolTest, psa

# setup flask and the interface
flask_app = Flask(__name__)
api = Api(app = flask_app, 
          version = "1.0", 
          title = "Labtest OCR", 
          description = "Receive image and return name/value/confidence of a test")

# upload floder
UPLOAD_FOLDER = 'upload/'
flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# so that can show Chinese properly
flask_app.config['JSON_AS_ASCII'] = False

# user input
user_input = reqparse.RequestParser()
user_input.add_argument('url',
                        type=str,
                        required=True,
                        location='url',
                        help='URL')
user_input.add_argument('test type',
                        type=str,
                        required=True,
                        location='string',
                        help='bloodTest, urineTest, stoolTest, psa')

# process user input and output results
@api.route('/upload')
class ocr_result(Resource):
    @api.expect(user_input)
    def post(self):
        url = request.args['url']
        test_type = request.args['test type']
        # download the image
        file = requests.get(url)
        # get the image name
        name = url.split('/')[-1]
        # the image path for save
        filename = '%s%s' % (flask_app.config['UPLOAD_FOLDER'], name)
        # save the image to the above path
        with open(filename, 'wb') as f:
            f.write(file.content)
        # convert string to class, be careful, 
        # eval() is dangerous, for converting string to class, for tmp use here
        labtest = eval(test_type)(filename)
        return jsonify(labtest.result())

if __name__ == '__main__':
    flask_app.run(debug=False, host='0.0.0.0')

