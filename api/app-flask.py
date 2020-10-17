from flask import Flask
from .endpoints.prediction import prediction_api 

app = Flask(__name__)
app.register_blueprint(prediction_api)  

if __name__ == '__main__':

	# Run server
	app.run(debug=True, host='0.0.0.0', port=5000)
