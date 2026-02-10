from common import Session
from domain import Member
from domain import Order

class OrderService:

    @classmethod
    def add_order(cls, total_price):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # SQL: 누가, 얼마를 냈는지 저장(status = "PAID")
                sql = "INSERT INTO orders (member_id, total_price) VALUES (%s, %s)"
                cursor.execute(sql, (Session.login_member.id, total_price))
                conn.commit()

        finally:
            conn.close()
            