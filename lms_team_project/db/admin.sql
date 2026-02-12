DROP DATABASE IF EXISTS lms;
CREATE DATABASE lms;
USE lms;

CREATE USER 'song'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES
ON lms_team_project.*
TO 'song'@'localhost';
FLUSH PRIVILEGES;
SELECT user, host
FROM mysql.user;
SHOW GRANTS FOR 'song'@'localhost';