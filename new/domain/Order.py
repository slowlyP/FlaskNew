class Order:
    def __init__(self, member_id, total_price, id=None, status="PAID", created_at=None, member_name=None):
        self.id = id
        self.member_id = member_id
        self.total_price = total_price
        self.status = status # PAID, REFUND_REQ, REFUNDED, CANCELED
        self.created_at = created_at

        #JOIN으로 가져올 회원 이름 (조회용)
        self.member_name = member_name


    @classmethod
    def from_db(cls, row: dict):
        """DB 딕셔너리 데이터를 Order 객체로 변환"""
        if not row:
            return None 
        return cls(
            id=row.get("id"),
            member_id=row.get('member_id'),
            total_price=row.get('total_price'),
            status=row.get('status'),
            created_at=row.get('created_at'),
            #JOIN 쿼리 시 members 테이블의 name 컬럼
            member_name=row.get('name'),
        )

    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else "날짜없음"
        name_str = f"[{self.member_name}]" if self.member_name else ""

        return f"주문번호: {self.id:<4} | {date_str} | {name_str:<10} | 총액: {self.total_price:>7}원 | 상태:{self.status}"
          