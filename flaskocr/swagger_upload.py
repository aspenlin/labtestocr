from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields, reqparse
import parsers
import os
from labtestocr import bloodtest, urinetest, stooltest

flask_app = Flask(__name__)
api = Api(app = flask_app, 
          version = "1.0", 
          title = "Labtest OCR", 
          description = "Receive image and return name/value/confidence of a test")

# name_space = api.namespace('Images', description='Retrive test values')

UPLOAD_FOLDER = 'upload/'
flask_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@api.route('/upload')
class my_file_upload(Resource):

    @api.expect(parsers.file_upload)
    def post(self):
        args = parsers.file_upload.parse_args()
        if args['image_file'].mimetype == 'image/jpeg':
            destination = os.path.join(flask_app.config['UPLOAD_FOLDER'], 'medias/')
            filename = args['image_file'].filename
            if not os.path.exists(destination):
                os.makedirs(destination)

            img_file = '%s%s' % (destination, filename)
            args['image_file'].save(img_file)
        else:
            api.abort(404)
        return self.result(img_file)
        # return {'status': 'Done'}

    def result(self, img_file):
        labtest = bloodtest(img_file)
        return jsonify(labtest.result())



if __name__ == '__main__':
    flask_app.run(debug=True)
