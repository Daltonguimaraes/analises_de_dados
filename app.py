from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World! ' 'Esse é o primeiro commit'

if __name__ == '__main__':
    app.run(debug=True)
