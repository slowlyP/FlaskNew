from flask import Flask, render_template,session,request,redirect
import pymysql

app = Flask(__name__)
app.secret_key = 'hello'


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="song",
        password="1234",
        database="lms_team_project",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


# 메인
@app.route("/")
def index():
    return render_template("index.html")   # 또는 home.html


# 로그인 페이지
@app.route("/login")
def login():
    return render_template("auth/login.html")



@app.route("/login", methods=["POST"])
def login_post():

    uid = request.form.get("uid")
    pw = request.form.get("password")

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
            SELECT *
            FROM members
            WHERE uid=%s
            AND password=%s
            AND active=1
        """

    cursor.execute(sql, (uid, pw))
    user = cursor.fetchone()

    # 로그인 성공
    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["role"] = user["role"]
        session["uid"] = user["uid"]

        return redirect("/")

    # 로그인 실패
    return "<script>alert('아이디나 비밀번호가 틀렸습니다.');history.back();</script>"




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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route("/mypage")
def mypage():

    # 로그인 체크 
    if not session.get("user_id"):
        return"""
        <script>
        alert('로그인후 이용가능합니다.');location.href='/login';
        </script>
        """
    user_id = session.get("user_id")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql = """
                    SELECT id, uid, name, role, created_at
                    FROM members
                    WHERE id=%s
                """

            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
    finally:
        conn.close()

    return render_template("mypage.html", user=user)





# 서버 실행 (맨 아래 1번만)
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5018, debug=True)
