from flask import Blueprint, render_template, session, redirect,request
from db.db_conn import get_connection

score_bp = Blueprint("score", __name__)

@score_bp.route("/my_score")
def my_score():
    if not session.get("user_id"):
        return redirect("/login")

    # 1. 대상 ID 결정
    # 관리자가 학생을 선택했으면 그 ID를, 아니면 세션 ID를 사용
    target_id = request.args.get("student_id") or session.get("user_id")
    
    # 2. 관리자 본인의 성적은 보지 않도록 설정
    # 대상이 본인인데 내 역할이 admin이면 score를 조회하지 않음
    is_admin_viewing_self = (str(target_id) == str(session.get("user_id"))) and (session.get("role") == "admin")

    conn = get_connection()
    members = []
    score = None
    history_avgs = []
    history_dates = []

    try:
        with conn.cursor() as cursor:
            # 관리자라면 학생 목록은 항상 가져옴 (선택해야 하니까)
            if session.get('role') == 'admin':
                cursor.execute("SELECT id, name, uid FROM members WHERE role='user'")
                members = cursor.fetchall()

            # 관리자가 본인을 보는 게 아닐 때만 성적 데이터를 조회
            if not is_admin_viewing_self:
                # 최신 성적 조회
                sql_latest = """
                    SELECT s.*, m.name FROM scores s 
                    JOIN members m ON s.student_id = m.id 
                    WHERE s.student_id = %s ORDER BY s.created_at DESC LIMIT 1
                """
                cursor.execute(sql_latest, (target_id,))
                score = cursor.fetchone()

                # 히스토리 조회
                sql_history = """
                    SELECT avg, created_at FROM scores 
                    WHERE student_id = %s ORDER BY created_at ASC LIMIT 5
                """
                cursor.execute(sql_history, (target_id,))
                history = cursor.fetchall()
                history_avgs = [row['avg'] for row in history]
                history_dates = [row['created_at'].strftime('%m-%d') for row in history]
    finally:
        conn.close()

    return render_template("score/my_score.html", 
                           score=score, 
                           members=members, 
                           history_avgs=history_avgs, 
                           history_dates=history_dates,
                           is_admin_self=is_admin_viewing_self) # 관리자 본인 여부 전달