CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    department VarChar(30) NOT NULL,
    course_number VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications_sent (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    department VARCHAR(30) NOT NULL,
    course_number VARCHAR(30) NOT NULL,
    class_codes TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_user_course ON users (email, course_number, department);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_sent(sent_at);