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

# ======================================================================================score ==========================================================

# 성적 입력 페이지 이동 및 저장

@admin_bp.route("/score/add", methods=["GET", "POST"])
def score_add():
    # 관리자 체크
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_connection()

    # GET : 성적 입력페이지
    if request.method =="GET":
        with conn.cursor() as cursor:
            sql = "SELECT id, name FROM members WHERE role = 'user'"
            cursor.execute(sql)
            members= cursor.fetchall()
        conn.close()
        return render_template("admin/score_add.html", members=members)

    # POST : 성적 데이터 insert
    student_id = request.form.get("student_id")
    python = int(request.form.get("python", 0))
    db_score = int(request.form.get("db", 0))
    frontend = int(request.form.get("frontend", 0))

    # 계산 로직
    total = python + db_score + frontend
    avg = round(total /3,2)

    if avg >=90:grade = 'A'
    elif avg >=80:grade = 'B'
    elif avg >=70:grade = 'C'
    else: grade = 'F'

    with conn.cursor() as cursor:
        # update가 아닌 insert를 사용하여 성적 이력 쌓음
        sql = """
            INSERT INTO scores(student_id, python, db, frontend, total, avg, grade)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql,(student_id, python,db_score,frontend,total,avg,grade))

    conn.commit()
    conn.close()

    return redirect(f"/my_score?student_id={student_id}")

        

@admin_bp.route("/book/add", methods=["GET", "POST"])
def book_add():
    if session.get("role") != "admin":
        return redirect("/book/list") # 경로 통일
    
    if request.method == "GET":
        return render_template("admin/book_add.html")

    title = request.form.get("title")
    author = request.form.get("author") # 저자 추가
    price = request.form.get("price")
    description = request.form.get("description")
    file = request.files.get("book_image")

    filename = None
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_connection()
    with conn.cursor() as cursor:
        # SQL문에 author 추가
        sql = "INSERT INTO books (title, author, price, description, book_image) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (title, author, price, description, filename))
    conn.commit()
    conn.close()

    return redirect("/book/list") # 경로 통일

    # 교재 수정 페이지 및 처리
@admin_bp.route("/book/edit/<int:book_id>", methods=["GET", "POST"])
def admin_book_edit(book_id):
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_connection()

    # 1. GET: 기존 데이터 불러오기
    if request.method == "GET":
        with conn.cursor() as cursor:
            sql = "SELECT * FROM books WHERE id = %s"
            cursor.execute(sql, (book_id,))
            book = cursor.fetchone()
        conn.close()
        
        if not book:
            return "존재하지 않는 교재입니다.", 404
            
        return render_template("admin/book_edit.html", book=book)

    # 2. POST: 데이터 업데이트 처리
    title = request.form.get("title")
    author = request.form.get("author")  # 저자 추가
    price = request.form.get("price")
    description = request.form.get("description")
    file = request.files.get("book_image")

    filename = None
    with conn.cursor() as cursor:
        if file and file.filename != "":
            # 새 이미지를 업로드한 경우
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            sql = """
                UPDATE books 
                SET title=%s, author=%s, price=%s, description=%s, book_image=%s 
                WHERE id=%s
            """
            params = (title, author, price, description, filename, book_id)
        else:
            # 이미지는 그대로 둘 경우
            sql = """
                UPDATE books 
                SET title=%s, author=%s, price=%s, description=%s 
                WHERE id=%s
            """
            params = (title, author, price, description, book_id)
        
        cursor.execute(sql, params)

    conn.commit()
    conn.close()
    return redirect("/book/list")  # 목록 페이지로 이동


# 교재 삭제 (선택 사항)
@admin_bp.route("/book/delete/<int:book_id>")
def admin_book_delete(book_id):
    if session.get("role") != "admin":
        return redirect("/")

    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "DELETE FROM books WHERE id = %s"
        cursor.execute(sql, (book_id,))
    
    conn.commit()
    conn.close()
    return redirect("/book/list")