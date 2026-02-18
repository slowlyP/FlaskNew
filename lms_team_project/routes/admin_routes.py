
from flask import Blueprint, render_template, request, session, redirect
from db.db_conn import get_connection
import os
from werkzeug.utils import secure_filename



admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ⭐ 여기 추가
UPLOAD_FOLDER = "static/uploads"



# 회원목록
@admin_bp.route("/members")
def admin_members():

    if session.get("role") != "admin":
        return "관리자만 접근"

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        SELECT id, uid, name, role, active, created_at
        FROM members
        ORDER BY id DESC
        """
        cursor.execute(sql)
        members = cursor.fetchall()

    conn.close()

    return render_template(
        "admin/member_list.html",
        members=members
    )


# 활성/비활성
@admin_bp.route("/member/toggle/<int:member_id>")
def toggle_member(member_id):

    conn = get_connection()

    with conn.cursor() as cursor:

        sql = "SELECT active FROM members WHERE id=%s"
        cursor.execute(sql,(member_id,))
        m = cursor.fetchone()

        new_active = 0 if m["active"] == 1 else 1

        sql = "UPDATE members SET active=%s WHERE id=%s"
        cursor.execute(sql,(new_active,member_id))

    conn.commit()
    conn.close()

    return redirect("/admin/members")


# 삭제
@admin_bp.route("/member/delete/<int:member_id>")
def delete_member(member_id):

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "DELETE FROM members WHERE id=%s"
        cursor.execute(sql,(member_id,))

    conn.commit()
    conn.close()

    return redirect("/admin/members")


# 강의등록 페이지

@admin_bp.route("/lecture/add", methods=["GET","POST"])
def lecture_add():

    # 관리자 체크
    if session.get("role") !="admin":
        return redirect("/lecture")


    # get 페이지 열기
    if request.method == "GET":
        return render_template("admin/lecture_add.html")

    # post 등록 처리
    title = request.form.get("title")
    teacher = request.form.get("teacher")
    capacity = request.form.get("capacity")

    #파일 업로드
    file = request.files.get("teacher_image")

    filename = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)

        save_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(save_path)

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        INSERT INTO lectures
        (title, teacher_name, teacher_image, capacity)
        VALUES(%s,%s,%s,%s)
        """
        cursor.execute(sql, (title, teacher, filename, capacity))

    conn.commit()
    conn.close()

    return redirect("/lecture")

    


@admin_bp.route("/lecture/edit/<int:lecture_id>", methods=["GET","POST"])
def lecture_edit(lecture_id):

    # 관리자 체크
    if session.get("role") != "admin":
        return redirect("/lecture")

    conn = get_connection()

    # 1️⃣ GET → 수정페이지 열기
    if request.method == "GET":

        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM lectures
            WHERE id=%s
            """
            cursor.execute(sql,(lecture_id,))
            lecture = cursor.fetchone()

        conn.close()

        return render_template(
            "admin/lecture_edit.html",
            lecture=lecture
        )

    # 2️⃣ POST → 수정 처리
    title = request.form.get("title")
    teacher = request.form.get("teacher")
    capacity = request.form.get("capacity")

    file = request.files.get("teacher_image")

    filename = None

    # 이미지 새로 업로드 했을 때만
    if file and file.filename != "":

        filename = secure_filename(file.filename)

        save_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(save_path)

        sql = """
        UPDATE lectures
        SET title=%s,
            teacher_name=%s,
            capacity=%s,
            teacher_image=%s
        WHERE id=%s
        """

        params = (title, teacher, capacity, filename, lecture_id)

    else:
        sql = """
        UPDATE lectures
        SET title=%s,
            teacher_name=%s,
            capacity=%s
        WHERE id=%s
        """

        params = (title, teacher, capacity, lecture_id)

    with conn.cursor() as cursor:
        cursor.execute(sql, params)

    conn.commit()
    conn.close()

    return redirect(f"/lecture/{lecture_id}")


# 강의 삭제
@admin_bp.route("/lecture/delete/<int:lecture_id>")
def lecture_delete(lecture_id):

    if session.get("role") != "admin":
        return redirect("/lecture")

    conn = get_connection()

    with conn.cursor() as cursor:

        # 수강신청 삭제
        sql = """
        DELETE FROM enrollments
        WHERE lecture_id=%s
        """
        cursor.execute(sql,(lecture_id,))

        # 강의 삭제
        sql = """
        DELETE FROM lectures
        WHERE id=%s
        """
        cursor.execute(sql,(lecture_id,))

    conn.commit()
    conn.close()

    return redirect("/lecture")


