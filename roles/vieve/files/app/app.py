from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Vieve is alive!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10992)
