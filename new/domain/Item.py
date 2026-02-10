class Item:
    # 카테고리 상수 및 라스트 정의
    CATEGORY_ETC = "잡화"
    CATEGORY_DRINK = "음료"
    CATEGORY_IT = "IT"
    CATEGORY_BOOK = "도서"


    CATEGORIES = [CATEGORY_ETC, CATEGORY_DRINK, CATEGORY_IT, CATEGORY_BOOK]

    def __init__(self, code, name, category, price, stock, id=None, created_at=None):
        self.id = id
        self.code = code
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.created_at = created_at

    def decrease_stock(self,qty=1):
        """재고 감소 로직"""
        if self.stock < qty:
            return False
        self.stock -= qty
        return True

    @classmethod
    def from_db(cls, row:dict):
        """DB 딕셔너리 데이터를 Item 객체로 변환"""
        if not row:
            return None
        return cls(
            id=row.get('id'),
            code=row.get('code'),
            name=row.get('name'),
            category=row.get('category'),
            price=int(row.get('price',0)),
            stock=int(row.get('stock',0)),
            created_at=row.get('created_at'),
        )

    def __str__(self):
        return f"[{self.category}] {self.name}({self.code}) | {self.price}원 | 재고:{self.stock}"
