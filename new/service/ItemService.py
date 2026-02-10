import re
from common import Session
from domain.Item import Item
from Service.OrderService import OrderService

class ItemService:

    @classmethod
    def load(cls):
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as cnt FROM items")
                count = cursor.fetchone()['cnt']
        finally:
            conn.close()


            # 상품 관리 admin,manager 전용

    @classmethod
    def add_item(cls):
        if not Session.is_login() or Session.login_member.role != "manager":
            print("manager 권한이 필요합니다.")
            return

        code = input("아이템 코드 : ").strip()
        name = input("아이템 이름 : ").strip()
        price = int(input("가격 : "))
        stock = int(input("재고수량  : "))

        print("\n카테고리 선택")
        for idx, cat in enumerate(Item.CATEGORIES, start=1):
            print(f"{idx}. {cat}")

        sel = int(input("번호 선택:"))
        category = Item.CATEGORIES[sel - 1]

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO items (code, name, category, price, stock) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (code, name, category, price, stock))
                conn.commit()
                print("아이템 등록 완료")
        except Exception as e:
            print(f"등록 실패 : {e}")
        finally:
            conn.close()

    @classmethod
    def modify_item(cls):
        print("\n---상품 정보 수정---")
        code = input("수정할 상품의 코드(CODE) 입력 : ")
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM items WHERE code = %s", (code,))
                item = cursor.fetchone()
                if not item:
                    print("해당 코드를 가진 상품이 없습니다.")
                    return
                print(f"현재 정보 : {item['name']} | {item['price']}원 | {item['category']}")

                new_name = input(" 새 상품명 (엔터 시 유지): ") or item['name']
                new_price = input(" 새 가격 (엔터 시 유지): ")
                new_price = int(new_price) if new_price else item['price']

                print("\n카테고리: 1.잡화 2.음료 3.IT 4.도서")
                new_cat_idx = input(" 새 카테고리 번호 (엔터 시 유지):")
                new_cat = Item.CATEGORIES[int(new_cat_idx) - 1] if new_cat_idx else item['category']

                sql = "UPDATE items SET name=%s, price=%s, category=%s WHERE code=%s"
                cursor.execute(sql, (new_name, new_price, new_cat, code))
                conn.commit()
                print(f"[{code}] 상품 정보 수정 완료")
        except Exception as e:
            print(f"수정 실패 : {e}")
        finally:
            conn.close()
    
    @classmethod
    def delete_item(cls):
        """상품 삭제"""
        print("\n---상품 삭제---")
        code = input("삭제할 상품의 코드(CODE) 입력 : ")

        confirm = input(f"정말 [{code}] 상품을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("삭제 취소되었습니다.")
            return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM items WHERE code = %s"
                cursor.execute(sql, (code,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"[{code}] 상품이 DB에서 삭제되었습니다.")
                else:
                    print("삭제 실패: 존재하지 않는 코드입니다.")

        except Exception as e:
            print(f"삭제 실패 : 주문 내역이 있는 상품은 삭제할 수 없습니다. .(에러 : {e})")
        finally:
            conn.close()


    @classmethod
    def list_item(cls):
        print("\n[아이템 목록]")
        conn = Session.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM items")
                rows = cursor.fetchall()
                if not rows:
                    print("등록된 아이템이 없습니다.")
                    return
                
                for row in rows:
                    item = Item.from_db(row)
                    print(item)
                
                if not Session.is_login():
                    print("\n로그인 후 이용 가능합니다.")
                    return
                
                code = input("\n장바구니에 담을 상품 코드(엔터:취소: )")
                if not code:return

                qty = int(input("수량 : "))

                target_item = Item.from_db(next((r for r in rows if r['code'] ==code),None))
                if target_item:
                    for cart in Session.cart:
                        if cart["item"].code ==code:
                            cart["qty"] += qty
                            print("장바구니 수량 증가")
                            return
                    Session.cart.append({"item": target_item, "qty": qty})
                    print("장바구니에 추가됨")

                else:
                    print("상품을 찾을 수 없습니다.")
        finally:
            conn.close()

    @classmethod
    def view_cart(cls):
        if not Session.cart:
            print("장바구니가 비어있습니다.")
            return

        print("\n[장바구니]")
        total = 0
        for cart in Session.cart:
            item = cart["item"]
            qty = cart["qty"]
            price = item.price * qty
            total += price
            print(f"[{item.code}] {item.name} | 단가:{item.price}원 | 수량:{qty} | 합계:{price}원")
        print(f"총 금액: {total}원")
#==========================================================================================================
    #구매 확정 (DB 재고 차감)
#==========================================================================================================
    @classmethod
    def purchase(cls):
        if not Session.is_login(): return
        if not Session.cart:
            print("장바구니가 비어있습니다.")
            return
        
        while True:
            cls.view_cart()
            print("\n1. 수량 변경 2. 구매 확정 0. 취소")
            sel = input("선택 : ")
            if sel == "1":
                cls.modify_cart()
            elif sel == "2":
                break
            elif sel == "0":
                return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 재고 체크

                for cart in Session.cart:
                    item = cart["item"]
                    cursor.execute("SELECT stock FROM items WHERE code = %s", (item.code,))
                    current_stock = cursor.fetchone()['stock']
                    if current_stock < cart["qty"]:
                        print(f"{item.name}의 재고가 부족합니다.")
                        return

                # 2. 재고 차감 및 주문 등록

                total = 0
                for cart in Session.cart:
                    item = cart["item"]
                    qty = cart["qty"]
                    
                #   DB 재고 차감

                    cursor.execute("UPDATE items SET stock = stock - %s WHERE code = %s", (qty, item.code))
                    # 주문 내역 추가 (OrderService 호충 또는 직접 sql)
                    # OrderService.add_order_db(item, qty, Session.login_member.id)
                    total += item.price * qty

                conn.commit()
                Session.cart.clear()
                print(f"\n구매 완료! 총 {total}원 결제되었습니다.")
        finally:
            conn.close()


    @classmethod
    def admin_menu(cls):
        if not Session.is_manager():
            print("\n[경고] 관리자 권한이 필요합니다.")
            return

        cls.print_items_all()
        while True:
            print("""
            !!!!!!!!!!!!!!!!!!!!!!!!!
               상품 관리자 전용 메뉴
            !!!!!!!!!!!!!!!!!!!!!!!!!
            1. 상품 리스트
            2. 새 상품 등록
            3. 상품 정보 수정 (이름/가격/카테고리)
            4. 재고 수량 관리 (입고/조정)
            5. 상품 삭제
            6. 전체 판매 내역 보기 (orders)
            7. 환불 요청 승인 처리
            0. 뒤로가기
            """)

            sel = input(">>>")
            if sel == "1":
                cls.print_items_all()
            elif sel == "2":
                cls.add_item()
            elif sel == "3":
                cls.modify_item()
            elif sel == "4":
                cls.print_items_all()
                cls.update_stock()
            elif sel == "5":
                cls.delete_item()
            elif sel == "6":
                OrderService.all_orders()
            elif sel == "7":
                OrderService.approve_refund()
            elif sel == "0":
                break
            else:
                print("잘못된 접근입니다.")

    @classmethod
    def print_items_all(cls):
        """관리자용 : 품절된 상품까지 모두 출력"""
        print("\n[전체 상품 목록 (관리자)]")
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM items")
                rows = cursor.fetchall()
                for row in rows:
                    print(Item.from_db(row))

        finally:
            conn.close()

    @classmethod
    def update_stock(cls):
        """재고 수량만 수정"""
        code = input("수량 수정항 상품 코드(code): ")
        new_stock = int(input("변경할 재고 수량: "))

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE items SET stock=%s WHERE code=%s"
                cursor.execute(sql, (new_stock, code))
                conn.commit()
                if cursor.rowcount > 0:
                    print("재고 수량이 업데이트 되었습니다.")
                else:
                    print("상품을 찾을 수 없습니다.")
        finally:
            conn.close()

    @classmethod
    def delete_item(cls):
        """상품 삭제"""
        code = input("삭제할 상품 코드(code): ")
        confirm = input(f"정말 '{code}' 상품을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':return

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM items WHERE code=%s"
                cursor.execute(sql, (code,))
                conn.commit()
                if cursor.rowcount > 0:
                    print("상품이 삭제 되었습니다.")
                else:
                    print("상품을 찾을 수 없습니다.")
        finally:
            conn.close()


    @classmethod
    def purchase(cls):
        if not Session.is_login() or not Session.cart:
            print("장바구니가 비어 있습니다.")
            return
        total_price = sum,(c['item'].price * c['qty'] for c in Session.cart)
        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. orders 테이블에 마스터 레코드 ㅐㅇ성 (누가, 총 얼마)
                sql_order = "INSERT INTO orders (member_id total_price) VALUES (%s, %s)"
                cursor.execute(sql_order, (Session.login_member.id, total_price))

                #방금 생성된 주문 번호(orders.id) 가져오기
                order_id = cursor.lastrowid

                # 2. 장바구니 상품들을 order_items 에 하나씩 저장
                for cart in Session.cart:
                    item = cart["item"]
                    qty = cart["qty"]

                    sql_item = """
                                INSERT INTO order_items (order_id, item_id, qty, price)
                                VALUES (%s, %s, %s, %s) \
                                    """
                    cursor.execute(sql_item, (order_id, item.id, qty, item.price))

                    # DB 재고 차감
                    cursor.execute("UPDATE items SET stock = stock - %s WHERE id = %s", (qty, item.id))

                conn.commit()
                Session.cart.clear()
                print(f"\n[결제 완료] 주문번호: {order_id} / 총액: {total_price}원")
        except Exception as e:
            conn.rollback()
            print(f"결제 중 오류 발생: {e}")
        finally:
            conn.close()
    
    @classmethod
    def run(cls):

        while True:
            print("""
            =====상품 관리 시스템=====
            1. 상품 목록 및 장바구니
            2. 장바구니 보기
            3. 결제하기
            4. 구매 내역 및 취소/환불
            """)

            if Session.is_login() and Session.login_member.role == "manager":
                print("9. 상품 관리(관리자)")
            print("0. 뒤로가기")

            sel = input(">>>")
            if sel == "1":
                cls.list_items()
            elif sel == "2":
                cls.view_cart()
            elif sel == "3":
                cls.purchase()
            elif sel == "4":
                cls.order_menu() # 주문 관련 서브 메뉴로 이동
            elif sel == "9":
                cls.admin_menu()
            elif sel == "0":
                break

    @classmethod
    def order_menu(cls):
        """구매 내역 조회 및 취소/환불을 위한 서브 메뉴"""
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return
        
        while True:
            print("""
            ====[구매 관리]====
            1. 내 구매 내역 보기
            2. 주문 취소 (재고 복구)
            3. 환불 요청 하기
            0. 뒤로가기
            """)

            sel = input(">>>")
            if sel == "1":
                OrderService.my_orders()
            elif sel == "2":
                OrderService.cancel_order()
            elif sel == "3":
                OrderService.my_orders()
                OrderService.request_refund()
            elif sel == "0":
                break