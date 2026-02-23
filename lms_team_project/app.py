from flask import Flask, render_template
from datetime import timedelta

# Blueprint import
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.lecture_routes import lecture_bp
from routes.mypage_routes import mypage_bp
from routes.board_routes import board_bp
from routes.score_routes import score_bp


app = Flask(__name__)
app.secret_key = "hello"

# 세션 유지 시간
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)


# 메인
@app.route("/")
def index():
    return render_template("index.html")


# Blueprint 등록 (app 생성 후!)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(lecture_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(board_bp)
app.register_blueprint(score_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5018, debug=True)
