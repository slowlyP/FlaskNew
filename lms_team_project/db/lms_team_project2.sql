DELETE FROM enrollments;
use lms_team_project;

TRUNCATE TABLE enrollments;


UPDATE lectures SET capacity=30 WHERE id=1;
UPDATE lectures SET capacity=25 WHERE id=2;

select * from members;

alter table lectures
add teacher_image varchar(255);

SELECT id, title, teacher_image
FROM lectures;

UPDATE lectures
SET teacher_image = NULL
WHERE teacher_image = 'no-profile.png';

ALTER TABLE enrollments
DROP FOREIGN KEY enrollments_ibfk_1;

ALTER TABLE enrollments
ADD CONSTRAINT enrollments_ibfk_1
FOREIGN KEY (lecture_id)
REFERENCES lectures(id)
ON DELETE CASCADE;