from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    print("Received a request from UptimeRobot or browser")  # ログを追加
    return "I'm alive!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)