import werkzeug
from flask_restplus import reqparse, inputs

input_url = reqparse.RequestParser()
input_url.add_argument('url',
						type=str,
						required=True,
						location='url',
						help='URL')