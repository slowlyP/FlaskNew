

UPDATE lectures
SET description =
'Python 기초 문법과 실습을 배우는 과정입니다.'
WHERE id = 1;

UPDATE lectures
SET start_date = '2026-03-01',
    end_date   = '2026-04-30'
WHERE id = 1;

UPDATE lectures
SET description = 'Frontend UI 설계 과정',
    start_date  = '2026-05-01',
    end_date    = '2026-06-30'
WHERE title = 'Frontend 심화';

SELECT title, description,
       start_date, end_date
FROM lectures;

-- Python 심화
UPDATE lectures
SET description = 'Python 심화 문법과 프로젝트 실습 과정입니다.',
    start_date  = '2026-04-01',
    end_date    = '2026-05-30'
WHERE title = 'Python 심화';


-- DB 설계
UPDATE lectures
SET description = '데이터베이스 모델링과 ERD 설계 과정입니다.',
    start_date  = '2026-03-15',
    end_date    = '2026-05-15'
WHERE title = 'DB 설계';


-- DB 튜닝
UPDATE lectures
SET description = 'SQL 성능 최적화와 인덱스 튜닝 과정입니다.',
    start_date  = '2026-04-10',
    end_date    = '2026-06-10'
WHERE title = 'DB 튜닝';


-- Frontend 기초
UPDATE lectures
SET description = 'HTML, CSS, JavaScript 기초 과정입니다.',
    start_date  = '2026-03-01',
    end_date    = '2026-04-30'
WHERE title = 'Frontend 기초';
