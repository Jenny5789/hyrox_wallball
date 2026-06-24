from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

@app.route('/')
def hello():
    return 'HYROX System Ready!'

if __name__ == '__main__':
    app.run(debug=True, port=5000)