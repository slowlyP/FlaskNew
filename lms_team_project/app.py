from flask import Flask, render_template,session,request,redirect
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hello'

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

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
                    SELECT id, uid, name, role, created_at, profile_image
                    FROM members
                    WHERE id=%s
                """

            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
    finally:
        conn.close()

    return render_template("mypage.html", user=user)


    # 정보수정




@app.route("/edit_profile", methods=["GET","POST"])
def edit_profile():

    if not session.get("user_id"):
        return redirect("/login")

    user_id=session.get("user_id")

    conn=get_connection()

    # ---------------- GET ----------------
    if request.method=="GET":

        with conn.cursor() as cursor:
            sql="""
                SELECT uid,name
                FROM members
                WHERE id=%s
            """
            cursor.execute(sql,(user_id,))
            user=cursor.fetchone()

        return render_template("edit_profile.html",user=user)

    # ---------------- POST ----------------
    # ---------------- POST ----------------
    name=request.form.get("name")
    password=request.form.get("password")
    file=request.files.get("profile")

    filename=None

    # 파일 처리
    if file and allowed_file(file.filename):

        filename=secure_filename(file.filename)

        filepath=os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

    with conn.cursor() as cursor:

        if password and filename:
            sql="""
                UPDATE members
                SET name=%s,
                    password=%s,
                    profile_image=%s
                WHERE id=%s
            """
            cursor.execute(sql,
                (name,password,filename,user_id))

        elif filename:
            sql="""
                UPDATE members
                SET name=%s,
                    profile_image=%s
                WHERE id=%s
            """
            cursor.execute(sql,
                (name,filename,user_id))

        elif password:
            sql="""
                UPDATE members
                SET name=%s,
                    password=%s
                WHERE id=%s
            """
            cursor.execute(sql,
                (name,password,user_id))

        else:
            sql="""
                UPDATE members
                SET name=%s
                WHERE id=%s
            """
            cursor.execute(sql,
                (name,user_id))

        conn.commit()
        conn.close()

        # 세션 이름 갱신
        session["user_name"]=name

        return redirect("/mypage")





# 서버 실행 (맨 아래 1번만)
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5018, debug=True)
