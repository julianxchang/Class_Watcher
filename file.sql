CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    course_number VARCHAR(30) NOT NULL
);