from flask import Blueprint, render_template, session, redirect
from db.db_conn import get_connection

lecture_bp = Blueprint("lecture", __name__)


# 강의목록
@lecture_bp.route("/lecture")
def lecture_list():

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        SELECT id,title,teacher_name,capacity,start_date,end_date
        FROM lectures
        WHERE active=1
        """
        cursor.execute(sql)
        lectures = cursor.fetchall()

    conn.close()

    return render_template(
        "lecture/lecture_list.html",
        lectures=lectures
    )


# 상세
@lecture_bp.route("/lecture/<int:lecture_id>")
def lecture_detail(lecture_id):

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = "SELECT * FROM lectures WHERE id=%s"
        cursor.execute(sql,(lecture_id,))
        lecture = cursor.fetchone()

    conn.close()

    return render_template(
        "lecture/lecture_detail.html",
        lecture=lecture
    )


# 수강신청
@lecture_bp.route("/enroll/<int:lecture_id>")
def enroll_lecture(lecture_id):

    if not session.get("user_id"):
        return redirect("/login")

    if session.get("role") == "admin":
        return redirect("/lecture")

    member_id = session.get("user_id")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            # 중복 체크
            sql = """
                SELECT id
                FROM enrollments
                WHERE lecture_id=%s
                AND member_id=%s
            """
            cursor.execute(sql,(lecture_id,member_id))
            exist = cursor.fetchone()

            if exist:
                return """
                <script>
                alert('이미 신청한 강의입니다.');
                history.back();
                </script>
                """

            # 정원 체크
            sql = """
                SELECT capacity
                FROM lectures
                WHERE id=%s
            """
            cursor.execute(sql,(lecture_id,))
            lecture = cursor.fetchone()

            if lecture["capacity"] <= 0:
                return """
                <script>
                alert('정원이 마감되었습니다.');
                history.back();
                </script>
                """

            # 수강신청
            sql = """
                INSERT INTO enrollments
                (lecture_id, member_id)
                VALUES (%s,%s)
            """
            cursor.execute(sql,(lecture_id,member_id))

            # 정원 감소
            sql = """
                UPDATE lectures
                SET capacity = capacity - 1
                WHERE id=%s
            """
            cursor.execute(sql,(lecture_id,))

        conn.commit()

    except Exception as e:
        conn.rollback()

        return """
        <script>
        alert('이미 신청한 강의입니다.');
        history.back();
        </script>
        """

    finally:
        conn.close()

    return """
    <script>
    alert('수강신청 완료!');
    location.href='/lecture';
    </script>
    """



# 내 수강목록
@lecture_bp.route("/my_lectures")
def my_lectures():

    conn = get_connection()

    with conn.cursor() as cursor:
        sql = """
        SELECT l.*
        FROM enrollments e
        JOIN lectures l
        ON e.lecture_id=l.id
        WHERE e.member_id=%s
        """
        cursor.execute(sql,(session["user_id"],))
        lectures = cursor.fetchall()

    conn.close()

    return render_template(
        "lecture/my_lectures.html",
        lectures=lectures
    )


# 수강취소
@lecture_bp.route("/cancel_enroll/<int:lecture_id>")
def cancel_enroll(lecture_id):

    conn = get_connection()

    with conn.cursor() as cursor:

        sql = """
        DELETE FROM enrollments
        WHERE lecture_id=%s
        AND member_id=%s
        """
        cursor.execute(sql,(lecture_id,session["user_id"]))

        sql = """
        UPDATE lectures
        SET capacity=capacity+1
        WHERE id=%s
        """
        cursor.execute(sql,(lecture_id,))

    conn.commit()
    conn.close()

    return redirect("/my_lectures")
