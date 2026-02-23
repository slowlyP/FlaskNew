

drop database if exists lms_project;

create database lms_project
default character set utf8mb4
collate utf8mb4_general_ci;

select * from scores;

-- 직접 실행할 때는 숫자를 넣어주세요
SELECT * FROM scores WHERE student_id = 1 ORDER BY created_at DESC LIMIT 1;