class Member:
    def __init__(self, id, uid, pw, name, role="user", active=True):
        self.id = id
        self.uid = uid
        self.pw = pw
        self.name = name
        self.role = role
        self.active = active

    @classmethod
    def from_db(cls,row:dict):
        """
        DictCursor로부터 전달 받은 딕셔너리 데이터를 Member 객체로변환합니다.
        """
        if not row:
            return None

        return cls(
            id=row.get("id"),
            uid=row.get("uid"),
            pw=row.get("password"),
            name=row.get("name"),
            role=row.get("role"),
            active=bool(row.get("active"))
        )

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        return f"{self.name}({self.uid}:{self.pw})[{self.role}]"


    #========================주석 + 설명 ==============================
    #
    # class Member:
    #     """
    #     [Member 클래스의 역할]
    #
    #     1. 회원 1명의 정보를 객체로 표현한다.
    #     2. DB의 members 테이블 한 행(row)을 Member 객체로 변환한다.
    #     3. 사용자 권한(admin / manager / user)을 관리한다.
    #     4. 로그인 세션(Session)에 저장되는 사용자 객체의 형태를 정의한다.
    #
    #     즉, 이 클래스는
    #     '회원 도메인 객체(Domain Object)' 역할을 수행한다.
    #     """
    #
    #     def __init__(self, id, uid, name, role="user", active=True):
    #         """
    #         [Member 생성자]
    #
    #         - id      : DB의 기본키(PK)
    #         - uid     : 로그인 아이디 (사용자 식별용 문자열)
    #         - name    : 사용자 이름
    #         - role    : 사용자 권한 (user / manager / admin)
    #         - active  : 계정 활성 여부 (True / False)
    #
    #         DB에 저장된 회원 정보를 객체로 생성할 때 사용된다.
    #         """
    #         self.id = id  # 회원 고유 번호 (PK)
    #         self.uid = uid  # 로그인 아이디
    #         self.name = name  # 사용자 이름
    #         self.role = role  # 권한
    #         self.active = active  # 활성 상태
    #
    #     @classmethod
    #     def from_db(cls, row: dict):
    #         """
    #         [DB → Member 객체 변환 메서드]
    #
    #         - pymysql DictCursor로부터 전달받은
    #           딕셔너리(row)를 Member 객체로 변환한다.
    #         - DB 조회 결과가 없을 경우 None 반환
    #
    #         사용 예:
    #         member = Member.from_db(row)
    #         """
    #
    #         if not row:
    #             return None
    #
    #         return cls(
    #             id=row.get("id"),  # members.id
    #             uid=row.get("user_id"),  # members.user_id (로그인 아이디)
    #             name=row.get("name"),  # members.name
    #             role=row.get("role"),  # members.role
    #             active=bool(row.get("active"))  # members.active (0/1 → False/True)
    #         )
    #
    #     def is_admin(self):
    #         """
    #         [관리자 여부 확인]
    #
    #         - 사용자의 역할(role)이 'admin'인지 확인한다.
    #         - 관리자 전용 기능 접근 여부 판단에 사용된다.
    #         """
    #         return self.role == "admin"
    #
    #     def __str__(self):
    #         """
    #         [객체 출력용 문자열]
    #
    #         - print(member) 호출 시 사람이 읽기 좋은 형태로 출력
    #         - 디버깅 및 로그 출력용
    #         """
    #         return f"{self.name}({self.uid})[{self.role}]"
