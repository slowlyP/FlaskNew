from flask import Flask, render_template,session,request,redirect
import pymysql
import os
from werkzeug.utils import secure_filename
import uuid

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
        session["profile_image"] = user["profile_image"]

        return redirect("/")

    # 로그인 실패
    return "<script>alert('아이디나 비밀번호가 틀렸습니다.');history.back();</script>"



# 회원가입 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/signup")
def signup():

# 로그인 상태 차단
    if session.get("user_id"):
        return redirect("/")

    return render_template("auth/signup.html")






@app.route("/signup", methods=["POST"])
def signup_post():
    
    if session.get("user_id"):
        return redirect("/")

    uid = request.form.get("uid")
    pw = request.form.get("password")
    pw2 = request.form.get("password2")
    name = request.form.get("name")


        # 비밀번호 확인
    if pw != pw2:
        return """
        <script>
        alert('비밀번호가 일치하지 않습니다.');
        history.back();
        </script>
        """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql = "SELECT id FROM members WHERE uid=%s"
            cursor.execute(sql, (uid,))
            exist = cursor.fetchone()

            if exist:
                return"""
                <script>alert('이미 존재하는 아이디입니다.');history.back();</script>
                """
            #회원 가입 INSERT   
            sql = """
            INSERT INTO members
            (uid, password, name)
            VALUES (%s, %s, %s)
            """

            cursor.execute(sql, (uid, pw, name))

        conn.commit()

    finally:
        conn.close()

    return"""
    <script>alert('회원가입 완료');location.href='/login';</script>
    """




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
                SELECT uid,name,profile_image
                FROM members
                WHERE id=%s
            """
            cursor.execute(sql,(user_id,))
            user=cursor.fetchone()

        return render_template("edit_profile.html",user=user)


    # ---------------- POST ----------------
    name=request.form.get("name")
    password=request.form.get("password")
    file=request.files.get("profile")

    filename=None

    # 파일 처리
    if file and allowed_file(file.filename):

        import uuid

        ext = file.filename.rsplit(".",1)[1]
        filename = f"{uuid.uuid4()}.{ext}"

        filepath = os.path.join(
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

        if filename:
            session["profile_image"] = filename

        return redirect("/mypage")

        #====== 관리자 ========

@app.route("/admin/members")
def admin_members():

    # 관리자 인지 체크
    if session.get("role") != "admin":
        return """
        <script>alert('관리자만 접근 가능합니다.');history.back();</script>
        """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            sql =  """
                SELECT id, uid, name, role, active, created_at
                FROM members
                ORDER BY id DESC
            """
            
            cursor.execute(sql)
            members = cursor.fetchall()

    finally:
        conn.close()

    return render_template(
        "admin/member_list.html",
        members=members
    )

    # 회원 비활성화 / 활성화

@app.route("/admin/member/toggle/<int:member_id>")
def toggle_member(member_id):

    # 관리자 체크
    if session.get("role") != "admin":
        return """
        <script>alert('관리자만 가능합니다.');history.back();</script>
        """

    if member_id == session.get("user_id"):
        return"""
        <script>alert('자기 계정은 비활성화할 수 없습니다.');history.back();</script>
        """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            # 현재 active 조회
            sql = """
            SELECT active
            FROM members
            WHERE id=%s
            """
            cursor.execute(sql, (member_id,))
            member = cursor.fetchone()

            new_active = 0 if member["active"] == 1 else 1

            sql = """
            UPDATE members
            SET active=%s
            WHERE id=%s
            """
            cursor.execute(sql, (new_active, member_id))
        conn.commit()
    finally:
        conn.close()
    
    return redirect("/admin/members")


# 회원 삭제

@app.route("/admin/member/delete/<int:member_id>")
def delete_member(member_id):
    # 관리자인지 체크
    if session.get("role") != "admin":
        return """
        <script>alert('관리자만 가능합니다.');history.back();</script>
        """
    # 자기 자신 삭제 방지
    if member_id ==session.get("user_id"):
        return"""
        <script>alert('자기 계정은 삭제할 수 없습니다.');history.back();</script>"""


    conn = get_connection()
    

    try:
        with conn.cursor() as cursor:

            sql = """
            DELETE FROM members
            WHERE id=%s
            """
            cursor.execute(sql, (member_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect("/admin/members")


    # 회원 탈퇴( 본인 )

@app.route("/member/delete")
def member_delete():

    #로그인 체크
    if not session.get("user_id"):
        return redirect("/login")

    user_id = session.get("user_id")
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            DELETE FROM members
            WHERE id=%s
            """
            cursor.execute(sql, (user_id,))
        conn.commit()
    finally:
        conn.close()
    
    session.clear()

    return"""
    <script>alert('회원 탈퇴가 완료되었습니다.');location.href='/';</script>
    """


    #======================================강의 목록

@app.route("/lecture")
def lecture_list():

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT id, title, teacher_name, capacity, start_date, end_date
            FROM lectures
            WHERE active=1
            ORDER BY id DESC
            """

            cursor.execute(sql)
            lectures = cursor.fetchall()

    finally:
        conn.close()

    return render_template(
        "lecture/lecture_list.html",
        lectures=lectures
    )


# =======================================강의 상세 페이지 

@app.route("/lecture/<int:lecture_id>")
def lecture_detail(lecture_id):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT * 
            FROM lectures
            WHERE id=%s
            """

            cursor.execute(sql, (lecture_id,))
            lecture = cursor.fetchone()
    finally:
        conn.close()


    return render_template(
        "lecture/lecture_detail.html",
        lecture=lecture
    )




# ===================== 수강신청
@app.route("/enroll/<int:lecture_id>")
def enroll_lecture(lecture_id):

    # 1️⃣ 로그인 체크
    if not session.get("user_id"):
        return redirect("/login")

    member_id = session.get("user_id")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            # 2️⃣ 중복 신청 체크
            sql = """
                SELECT id
                FROM enrollments
                WHERE lecture_id=%s
                AND member_id=%s
            """
            cursor.execute(sql, (lecture_id, member_id))
            exist = cursor.fetchone()

            if exist:
                return """
                <script>
                alert('이미 신청한 강의입니다.');
                history.back();
                </script>
                """

            # 3️⃣ 정원 조회
            sql = """
                SELECT capacity
                FROM lectures
                WHERE id=%s
            """
            cursor.execute(sql, (lecture_id,))
            lecture = cursor.fetchone()

            if lecture["capacity"] <= 0:
                return """
                <script>
                alert('정원이 마감되었습니다.');
                history.back();
                </script>
                """

            # 4️⃣ 수강신청 INSERT
            sql = """
                INSERT INTO enrollments
                (lecture_id, member_id)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (lecture_id, member_id))

            # 5️⃣ 정원 감소
            sql = """
                UPDATE lectures
                SET capacity = capacity - 1
                WHERE id=%s
            """
            cursor.execute(sql, (lecture_id,))

        conn.commit()

    finally:
        conn.close()

    return """
    <script>
    alert('수강신청 완료!');
    location.href='/lecture';
    </script>
    """




# ============================= 수강 목록
@app.route('/my_lectures')
def my_lectures():

    # 1️⃣ 로그인 체크
    if 'user_id' not in session:
        return """
        <script>
        alert('로그인이 필요합니다.');
        location.href='/login';
        </script>
        """

    member_id = session['user_id']

    # 2️⃣ DB 연결
    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            sql = """
                SELECT
                    l.id,
                    l.title,
                    l.teacher_name,
                    l.capacity,
                    l.start_date,
                    l.end_date
                FROM enrollments e
                JOIN lectures l
                    ON e.lecture_id = l.id
                WHERE e.member_id = %s
                ORDER BY l.start_date DESC
            """

            cursor.execute(sql, (member_id,))
            lectures = cursor.fetchall()

    finally:
        conn.close()

    # 3️⃣ 템플릿 전달
    return render_template(
        "lecture/my_lectures.html",
        lectures=lectures
    )


# ===========================수강 취소 + 정원 복구

@app.route("/cancel_enroll/<int:lecture_id>")
def cancel_enroll(lecture_id):
    
    # 로그인 체크
    if not session.get("user_id"):
        return redirect("/login")

    member_id = session.get("user_id")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT id
            FROM enrollments
            WHERE lecture_id=%s
            AND member_id=%s
            """
            cursor.execute(sql, (lecture_id, member_id))
            exist = cursor.fetchone()

            if not exist:
                return """
                <script>
                alert('신청 내역이 없습니다.');
                history.back();
                </script>
                """
            
            sql = """
            DELETE FROM enrollments
            WHERE lecture_id=%s
            AND member_id=%s
            """

            cursor.execute(sql, (lecture_id,member_id))

            sql = """
            UPDATE lectures
            SET capacity = capacity +1
            WHERE id=%s
            """

            cursor.execute(sql, (lecture_id,))
        conn.commit()

    finally:
        conn.close()

    return """
    <script>alert('수강취소 완료');location.href='/my_lectures';</script>"""






# 서버 실행 (맨 아래 1번만)
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5018, debug=True)
