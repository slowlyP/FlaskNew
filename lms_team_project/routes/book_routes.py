from flask import Blueprint, render_template, session, redirect, request
from db.db_conn import get_connection

book_bp = Blueprint("book", __name__)

@book_bp.route("/list")
def book_list():
    conn = get_connection()
    with conn.cursor() as cursor:
        # 모든 교재 목록 조회
        sql = "SELECT * FROM books ORDER BY created_at DESC"
        cursor.execute(sql)
        books = cursor.fetchall()
    conn.close()

    return render_template("book/book_list.html", books=books)

@book_bp.route("/detail/<int:book_id>")
def book_detail(book_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        # 특정 id의 교재 정보 조회
        sql = "SELECT * FROM books WHERE id=%s"
        cursor.execute(sql, (book_id,))
        book = cursor.fetchone()
    conn.close()

    if not book:
        return "해당 교재를 찾을 수 없습니다"

    return render_template("book/book_datail.html", book=book)

# 장바구니

@book_bp.route("/cart/add/<int:book_id>", methods=["POST"])
def add_to_cart(book_id):
    if not session.get("id"):
        return "<script>alert('로그인이 필요합니다.'); location.href='/login';</script>"

    member_id = session.get("id")
    # 폼에서 넘겨받은 수량 가져오기 (기본값 1)
    request_quantity = int(request.form.get("quantity", 1))
    
    conn = get_connection()
    with conn.cursor() as cursor:
        # 이미 장바구니에 있는지 확인
        sql = "SELECT id, quantity FROM cart WHERE member_id=%s AND book_id=%s"
        cursor.execute(sql, (member_id, book_id))
        item = cursor.fetchone()

        if item:
            # 이미 있으면 기존 수량에 더하기
            sql = "UPDATE cart SET quantity = quantity + %s WHERE id=%s"
            cursor.execute(sql, (request_quantity, item['id']))
        else:
            # 없으면 선택한 수량만큼 새로 추가
            sql = "INSERT INTO cart (member_id, book_id, quantity) VALUES (%s, %s, %s)"
            cursor.execute(sql, (member_id, book_id, request_quantity))
            
    conn.commit()
    conn.close()
    
    return f"<script>alert('장바구니에 {request_quantity}개의 교재가 담겼습니다!'); location.href='/book/list';</script>"