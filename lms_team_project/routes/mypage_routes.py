from flask import Blueprint, render_template, session, request, redirect
from db.db_conn import get_connection
import os, uuid

mypage_bp = Blueprint("mypage", __name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


# 마이페이지
@mypage_bp.route("/mypage")
def mypage():

    if not session.get("user_id"):
        return redirect("/login")

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        SELECT id, uid, name, role, created_at, profile_image
        FROM members
        WHERE id=%s
        """
        cursor.execute(sql, (session["user_id"],))
        user = cursor.fetchone()

    conn.close()

    return render_template("mypage.html", user=user)


# 정보수정
@mypage_bp.route("/edit_profile", methods=["GET","POST"])
def edit_profile():

    if not session.get("user_id"):
        return redirect("/login")

    conn = get_connection()

    if request.method == "GET":

        with conn.cursor() as cursor:
            sql = """
            SELECT uid,name,profile_image
            FROM members
            WHERE id=%s
            """
            cursor.execute(sql, (session["user_id"],))
            user = cursor.fetchone()

        return render_template("edit_profile.html", user=user)

    name = request.form.get("name")
    password = request.form.get("password")
    file = request.files.get("profile")

    filename = None

    if file and allowed_file(file.filename):

        ext = file.filename.rsplit(".",1)[1]
        filename = f"{uuid.uuid4()}.{ext}"

        file.save(os.path.join(UPLOAD_FOLDER, filename))

    with conn.cursor() as cursor:

        if password and filename:
            sql = """
            UPDATE members
            SET name=%s,password=%s,profile_image=%s
            WHERE id=%s
            """
            cursor.execute(sql,(name,password,filename,session["user_id"]))

        elif filename:
            sql = """
            UPDATE members
            SET name=%s,profile_image=%s
            WHERE id=%s
            """
            cursor.execute(sql,(name,filename,session["user_id"]))

        elif password:
            sql = """
            UPDATE members
            SET name=%s,password=%s
            WHERE id=%s
            """
            cursor.execute(sql,(name,password,session["user_id"]))

        else:
            sql = """
            UPDATE members
            SET name=%s
            WHERE id=%s
            """
            cursor.execute(sql,(name,session["user_id"]))

    conn.commit()
    conn.close()

    session["user_name"] = name
    if filename:
        session["profile_image"] = filename

    return redirect("/mypage")


# 회원탈퇴
@mypage_bp.route("/member/delete")
def member_delete():

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "DELETE FROM members WHERE id=%s"
        cursor.execute(sql,(session["user_id"],))

    conn.commit()
    conn.close()

    session.clear()

    return "<script>alert('탈퇴완료');location.href='/'</script>"
