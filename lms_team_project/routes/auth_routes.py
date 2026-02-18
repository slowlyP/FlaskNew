from flask import Blueprint, render_template, request, redirect, session
from db.db_conn import get_connection

auth_bp = Blueprint("auth", __name__)


# 로그인 페이지
@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")


# 로그인 처리
@auth_bp.route("/login", methods=["POST"])
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

    if user:
        session.permanent = False
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["role"] = user["role"]
        session["uid"] = user["uid"]
        session["profile_image"] = user["profile_image"]

        return redirect("/")

    return "<script>alert('아이디나 비밀번호가 틀렸습니다.');history.back();</script>"


# 회원가입 페이지
@auth_bp.route("/signup")
def signup():

    if session.get("user_id"):
        return redirect("/")

    return render_template("auth/signup.html")


# 회원가입 처리
@auth_bp.route("/signup", methods=["POST"])
def signup_post():

    uid = request.form.get("uid")
    pw = request.form.get("password")
    pw2 = request.form.get("password2")
    name = request.form.get("name")

    if pw != pw2:
        return "<script>alert('비밀번호 불일치');history.back();</script>"

    conn = get_connection()

    with conn.cursor() as cursor:

        sql = "SELECT id FROM members WHERE uid=%s"
        cursor.execute(sql, (uid,))
        exist = cursor.fetchone()

        if exist:
            return "<script>alert('이미 존재');history.back();</script>"

        sql = """
        INSERT INTO members(uid,password,name)
        VALUES(%s,%s,%s)
        """
        cursor.execute(sql, (uid, pw, name))

    conn.commit()
    conn.close()

    return "<script>alert('회원가입 완료');location.href='/login';</script>"


# 로그아웃
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
