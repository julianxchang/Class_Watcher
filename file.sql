CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    department VarChar(30) NOT NULL,
    course_number VARCHAR(30) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_user_course
ON users (email, course_number, department);