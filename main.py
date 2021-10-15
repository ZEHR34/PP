from flask import Flask

app = Flask(__name__)


@app.route("/api/v1/hello-world-1")
def task():
    return "hello yura"

if __name__ == "__main__":
    app.run()
