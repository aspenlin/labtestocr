from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/home')
def hello_world():
    return 'Hello, World! How are you?'


@app.route('/about')
def about():
    return 'About Page'


if __name__ == '__main__':
	app.run()
