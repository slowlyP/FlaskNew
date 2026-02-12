use lms_team_project;



# members 테이블 생성
create table members(
id int auto_increment primary key,
uid varchar(50) unique not null,
password varchar(255) not null,
name varchar(50) not null,
role enum('user','admin','manager') default 'user',
active tinyint default 1,
created_at datetime default current_timestamp,
updated_at datetime default current_timestamp
on update current_timestamp
);


# lectures 테이블 생성
create table lectures(
id int auto_increment primary key,
title varchar(200),
teacher_name varchar(50),
description text,
capacity int,
start_date date,
end_date date,
active tinyint default 1,
created_at datetime default current_timestamp,
updated_at datetime default current_timestamp
on update current_timestamp
);

# boards 테이블 생성
create table boards(
id int auto_increment primary key,
member_id int not null,
title varchar(200) not null,
content text,
views int default 0,
active tinyint default 1,
created_at datetime default current_timestamp,
updated_at datetime default current_timestamp
on update current_timestamp,

foreign key(member_id)
references members(id)
);

# scores 테이블 생성
create table scores(
id int auto_increment primary key,
student_id int not null,
python int,
db int,
frontend int,
total int,
avg decimal(5,2),
grade varchar(5),
active tinyint default 1,
created_at datetime default current_timestamp,
updated_at datetime default current_timestamp
on update current_timestamp,
foreign key (student_id)
references members(id)
);


# 총점/ 평균 계산
UPDATE scores
SET
total = python + db + frontend,
avg = (python + db + frontend) / 3;


# 등급 자동 계산
UPDATE scores
SET grade =
CASE
    WHEN avg >= 90 THEN 'A'
    WHEN avg >= 80 THEN 'B'
    WHEN avg >= 70 THEN 'C'
    WHEN avg >= 60 THEN 'D'
    ELSE 'F'
END;

SELECT student_id, total, avg, grade
FROM scores
LIMIT 10;

# board_comments 테이블 생성

create table board_comments(
id int auto_increment primary key,
board_id int not null,
member_id int not null,
parent_id int null,
content text not null,
depth tinyint default 0,
active tinyint default 1,
created_at datetime default current_timestamp,
updated_at datetime default current_timestamp
on update current_timestamp,

foreign key(board_id)
references boards(id),

foreign key(member_id)
references members(id),

foreign key(parent_id)
references board_comments(id)
);


# enrollments 테이블 생성

create table enrollments(
id int auto_increment primary key,
lecture_id int not null,
member_id int not null,
status enum('applied','cancelled') default 'applied',
applied_at datetime default current_timestamp,

unique (lecture_id, member_id),

foreign key (lecture_id)
references lectures(id),

foreign key (member_id)
references members(id)
);


DROP TABLE board_comments;
DROP TABLE enrollments;

select * from members;
SELECT * FROM boards;
select * from scores;


# ========================================== 더미데이터 ==============

INSERT INTO members(uid,password,name,role)
VALUES
('admin','1234','관리자','admin'),
('user2','1234','회원2','user'),
('user3','1234','회원3','user'),
('user4','1234','회원4','user'),
('user5','1234','회원5','user'),
('user6','1234','회원6','user'),
('user7','1234','회원7','user'),
('user8','1234','회원8','user'),
('user9','1234','회원9','user'),
('user10','1234','회원10','user'),
('user11','1234','회원11','user'),
('user12','1234','회원12','user'),
('user13','1234','회원13','user'),
('user14','1234','회원14','user'),
('user15','1234','회원15','user'),
('user16','1234','회원16','user'),
('user17','1234','회원17','user'),
('user18','1234','회원18','user'),
('user19','1234','회원19','user'),
('user20','1234','회원20','user'),
('user21','1234','회원21','user'),
('user22','1234','회원22','user'),
('user23','1234','회원23','user'),
('user24','1234','회원24','user'),
('user25','1234','회원25','user'),
('user26','1234','회원26','user'),
('user27','1234','회원27','user'),
('user28','1234','회원28','user'),
('user29','1234','회원29','user'),
('user30','1234','회원30','user'),
('user31','1234','회원31','user'),
('user32','1234','회원32','user'),
('user33','1234','회원33','user'),
('user34','1234','회원34','user'),
('user35','1234','회원35','user'),
('user36','1234','회원36','user'),
('user37','1234','회원37','user'),
('user38','1234','회원38','user'),
('user39','1234','회원39','user'),
('user40','1234','회원40','user'),
('user41','1234','회원41','user'),
('user42','1234','회원42','user'),
('user43','1234','회원43','user'),
('user44','1234','회원44','user'),
('user45','1234','회원45','user'),
('user46','1234','회원46','user'),
('user47','1234','회원47','user'),
('user48','1234','회원48','user'),
('user49','1234','회원49','user'),
('user50','1234','회원50','user'); 

# lectures 더미데이터

INSERT INTO lectures(title,teacher_name,capacity)
VALUES
('Python 기초','이강사',30),
('Python 심화','이강사',25),
('DB 설계','박강사',20),
('DB 튜닝','박강사',20),
('Frontend 기초','최강사',30),
('Frontend 심화','최강사',25);


# boards 더미데이터 

INSERT INTO boards(member_id,title,content)
SELECT
FLOOR(1 + RAND()*50),
CONCAT('게시글 제목 ', id),
'테스트 게시글 내용'
FROM
(SELECT 1 id UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
 UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
 UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
 UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
 UNION SELECT 46 UNION SELECT 47 UNION SELECT 48 UNION SELECT 49 UNION SELECT 50
) t;


# score 더미데이터

INSERT INTO scores
(student_id,python,db,frontend,total,avg,grade)
SELECT
id,
FLOOR(60 + RAND()*40),
FLOOR(60 + RAND()*40),
FLOOR(60 + RAND()*40),
0,0,''
FROM members;

# enrollments 더미데이터

INSERT INTO enrollments(lecture_id,member_id)
SELECT
FLOOR(1 + RAND()*6),
id
FROM members;

#join 조회 테스트

SELECT b.id, b.title, m.name
FROM boards b
JOIN members m
ON b.member_id = m.id
LIMIT 10;


# 성적 학생 

SELECT m.name, s.python, s.db, s.frontend, s.avg
FROM scores s
JOIN members m
ON s.student_id = m.id
LIMIT 10;

# 인덱스 생성

CREATE INDEX idx_board_member
ON boards(member_id);

CREATE INDEX idx_score_student
ON scores(student_id);

INSERT INTO boards(member_id,title)
VALUES (999,'FK 테스트');