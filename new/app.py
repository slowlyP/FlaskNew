
# ==========================================
# Flask 기본 모듈 import
# ==========================================


from flask import Flask, render_template, request, redirect, session

# ==========================================
# MemberService import
# ==========================================
# 로그인 DB 조회용

from service.MemberService import MemberService



# ==========================================
# Flask 앱 생성
# ==========================================
app = Flask(__name__)
# ==========================================
# 세션 암호키 설정
# ==========================================
# session 사용 시 필수
# 아무 문자열 가능 (보안용)
app.secret_key = "mysecretkey"




# ===============================
#      메인페이지
# ===============================

@app.route("/")
def home():
    return render_template("index.html")



# ===============================
#       로그인
# ===============================
@app.route("/login", methods=["GET","POST"])
def login():
    """
    [로그인 처리 라우트]

    GET  → 로그인 화면 출력
    POST → 로그인 처리
    """

    # --------------------------------------
    # 1️⃣ GET 요청 처리
    # --------------------------------------
    # 로그인 페이지 접속 시 실행
    if request.method =="GET":
        return render_template("auth/login.html")



    # --------------------------------------
    # 2️⃣ POST 요청 처리
    # --------------------------------------
    # 로그인 form 제출 시 실행

    # form 데이터 가져오기
    uid = request.form.get("uid")
    pw = request.form.get("password")

    # --------------------------------------
    # 3️⃣ DB 로그인 조회
    # --------------------------------------
    user = MemberService.login(uid,pw)

    # --------------------------------------
    # 4️⃣ 로그인 성공
    # --------------------------------------
    if user:

        # 세션 저장
        # 브라우저 유저 로그인
        session["uid"] = user["uid"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        # 메인 페이지 이동
        return redirect("/")

    # --------------------------------------
    # 5️⃣ 로그인 실패
    # --------------------------------------
    else:
        return "아이디 또는 비밀번호 오류"









# ===============================
#       회원가입
# ===============================
@app.route("/signup")
def signup():
    return render_template("auth/signup.html")




# ===============================
# 마이페이지
# ===============================
@app.route("/mypage")
def mypage():
    return render_template("member/mypage.html")



# ===============================
# 게시판 목록
# ===============================
@app.route("/board")
def board_list():
    return render_template("board/list.html")





# ===============================
# 게시글 작성
# ===============================
@app.route("/board/write")
def board_write():
    return render_template("board/write.html")


# ===============================
# 서버 실행
# ===============================
if __name__ == "__main__":
    
    # flask 개발 서버 실행
    app.run(debug=True)