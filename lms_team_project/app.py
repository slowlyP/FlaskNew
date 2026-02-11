from flask import Flask, render_template,session,request,redirect

app = Flask(__name__)
app.secret_key = 'hello'


# 메인
@app.route("/")
def index():
    return render_template("index.html")   # 또는 home.html


# 로그인 페이지
@app.route("/login")
def login():
    return render_template("auth/login.html")





@app.route("/signup")
def signup():
    return render_template("auth/signup.html")

@app.route("/signup", methods=["POST"])
def signup_post():

    uid = request.form.get("uid")
    pw = request.form.get("password")
    name = request.form.get("name")

    print(uid, pw, name)

    return redirect("/login")




@app.route("/mypage")
def mypage():
    return render_template("mypage.html")





# 서버 실행 (맨 아래 1번만)
if __name__ == "__main__":
    app.run(debug=True)
