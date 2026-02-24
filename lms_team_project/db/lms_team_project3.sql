

drop database if exists lms_project;

create database lms_project
default character set utf8mb4
collate utf8mb4_general_ci;

select * from scores;

-- 직접 실행할 때는 숫자를 넣어주세요
SELECT * FROM scores WHERE student_id = 1 ORDER BY created_at DESC LIMIT 1;

# 교재의 제목 가격 설명 이미지

create table books (
	id int auto_increment primary key,
    title varchar(255) not null, -- 교재의 제목
    author varchar(100), 	     -- 저자
    price int default 0,         -- 가격
    description text,			 -- 교재 설명
    book_image varchar(255),	 -- 교재 표지 이미지 파일명
    stock int default 0,		 -- 재고
    created_at timestamp default current_timestamp
);

# 장바구니 
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,           -- 누가 담았는지
    book_id INT NOT NULL,             -- 어떤 책을 담았는지
    quantity INT DEFAULT 1,           -- 수량 (기본 1개)
    created_at DATETIME DEFAULT NOW(),
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
    
# 교재 더미데이터

INSERT INTO books (title, author, price, description, book_image) VALUES
('Python 마스터 가이드', '김파이', 25000, '기초부터 실무 프로젝트까지 한 권으로 끝내는 파이썬 가이드북입니다.', NULL),
('SQL 데이터베이스 입문', '이디비', 22000, '비전공자도 쉽게 이해할 수 있는 SQL 기초와 데이터 설계 원리입니다.', NULL),
('React로 만드는 현대적 웹', '박리액', 28000, '최신 React Hooks와 상태 관리 라이브러리를 활용한 웹 개발 실습서입니다.', NULL),
('자료구조와 알고리즘', '최알고', 30000, '코딩 테스트 합격을 위한 필수 알고리즘 핵심 요약집입니다.', NULL),
('Node.js 서버 프로그래밍', '정노드', 27000, 'Express 프레임워크를 활용한 고성능 서버 구축 및 배포 가이드입니다.', NULL),
('자바스크립트 완벽 가이드', '강스크', 32000, 'ES6+ 문법부터 비동기 프로그래밍까지 자바스크립트의 모든 것을 담았습니다.', NULL),
('인공지능 입문: 머신러닝', '홍인공', 35000, '수학적 지식이 부족해도 시작할 수 있는 파이썬 머신러닝 입문서입니다.', NULL),
('클라우드 인프라 설계', '오클라', 33000, 'AWS와 Docker를 활용한 클라우드 아키텍처 설계의 기초입니다.', NULL);
		