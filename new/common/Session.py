import pymysql
class Session:
    login_member = None

    @staticmethod
    def get_connection():
        print("get_connection()메서드 호출 - mysql에 접속됩니다.")

        return pymysql.connect(
            host='localhost',
            user='mbc',
            password='1234',
            db='lms',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @classmethod
    def login(cls,member):
        cls.login_member = member

    @classmethod
    def logout(cls):
        cls.login_member = None

    @classmethod
    def is_login(cls):
        return cls.login_member is not None

    @classmethod
    def is_admin(cls):
        return cls.is_login() and cls.login_member.role == "admin"

    @classmethod
    def is_manager(cls):
        return cls.is_login() and cls.login_member.role in ("manager", "admin")

    # import pymysql
    #
    # class Session:
    #     """
    #     [Session 클래스의 역할]
    #
    #     1. 현재 로그인한 사용자 정보를 전역적으로 관리한다.
    #     2. MySQL 데이터베이스 연결을 생성한다.
    #     3. 로그인 여부 및 권한(admin / manager)을 판단한다.
    #
    #     → BoardService, ScoreService 등 모든 서비스 클래스가
    #       이 Session 클래스를 통해 로그인 상태와 DB에 접근한다.
    #     """
    #
    #     # 현재 로그인한 사용자(Member 객체)를 저장하는 클래스 변수
    #     # 로그아웃 시 None으로 초기화됨
    #     login_member = None
    #
    #     @staticmethod
    #     def get_connection():
    #         """
    #         [DB 연결 생성 메서드]
    #
    #         - MySQL 데이터베이스와의 연결(Connection)을 생성한다.
    #         - pymysql을 사용하며, DictCursor를 통해
    #           SQL 결과를 dict 형태로 반환한다.
    #
    #         이 메서드는:
    #         - 게시판
    #         - 성적 관리
    #         - 회원 관리
    #         등 모든 DB 작업의 시작점이 된다.
    #         """
    #         print("get_connection()메서드 호출 - mysql에 접속됩니다.")
    #
    #         return pymysql.connect(
    #             host='localhost',  # DB 서버 주소
    #             user='mbc',  # DB 접속 계정
    #             password='1234',  # DB 비밀번호
    #             db='lms',  # 사용할 데이터베이스 이름
    #             charset='utf8mb4',  # 한글 및 특수문자 처리
    #             cursorclass=pymysql.cursors.DictCursor  # 결과를 dict로 반환
    #         )
    #
    #     @classmethod
    #     def login(cls, member):
    #         """
    #         [로그인 처리 메서드]
    #
    #         - 로그인에 성공한 Member 객체를 세션에 저장한다.
    #         - 이후 모든 서비스에서 Session.login_member를 통해
    #           현재 로그인 사용자를 참조할 수 있다.
    #
    #         예:
    #         Session.login(member)
    #         """
    #         cls.login_member = member
    #
    #     @classmethod
    #     def logout(cls):
    #         """
    #         [로그아웃 처리 메서드]
    #
    #         - 세션에 저장된 로그인 정보를 제거한다.
    #         - 로그인 상태가 해제되며,
    #           이후 기능 접근 시 로그인 여부 체크에 걸리게 된다.
    #         """
    #         cls.login_member = None
    #
    #     @classmethod
    #     def is_login(cls):
    #         """
    #         [로그인 상태 확인]
    #
    #         - 현재 로그인한 사용자가 있는지 확인한다.
    #         - 로그인 상태면 True, 아니면 False 반환
    #
    #         이 메서드는:
    #         - 메뉴 접근 제한
    #         - 기능 실행 여부 판단
    #         에 사용된다.
    #         """
    #         return cls.login_member is not None
    #
    #     @classmethod
    #     def is_admin(cls):
    #         """
    #         [관리자 권한 확인]
    #
    #         - 현재 로그인 상태이면서
    #         - 사용자 역할(role)이 'admin'인 경우 True 반환
    #
    #         사용 예:
    #         - 관리자 전용 메뉴
    #         - 전체 데이터 조회
    #         - 삭제/수정 권한 판단
    #         """
    #         return cls.is_login() and cls.login_member.role == "admin"
    #
    #     @classmethod
    #     def is_manager(cls):
    #         """
    #         [매니저 권한 확인]
    #
    #         - 로그인 상태이면서
    #         - 역할(role)이 'manager' 또는 'admin'인 경우 True
    #
    #         사용 예:
    #         - 성적 입력
    #         - 제한된 관리 기능
    #         """
    #         return cls.is_login() and cls.login_member.role in ("manager", "admin")

