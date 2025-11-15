# UCI Class Watcher 🎓

A web application that monitors UCI course availability and automatically notifies students via email when a spot opens up in their desired classes.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features ✨

- **Email Notifications** - Instant alerts via email when spots open up
- **Multiple Departments** - Supports multiple UCI departments
- **Statistics Dashboard** - Track total notifications sent, current watchers, and trending courses
- **Responsive Design** - Mobile-friendly interface with hamburger navigation
- **PostgreSQL Database** - Reliable data persistence for watchers and notification history

## Tech Stack 🛠️

- **Backend**: Flask (Python 3.13)
- **Database**: PostgreSQL with psycopg2
- **Email Service**: Resend API
- **Web Scraping**: BeautifulSoup4 (bs4)
- **Deployment**: Docker, Gunicorn
- **Frontend**: HTML, CSS

## Prerequisites 📋

- Python 3.13+
- PostgreSQL
- Resend API key
- Docker (optional, for containerized deployment)

## Installation 🚀

### 1. Clone the repository

```bash
git clone https://github.com/julianxchang/Class_Watcher.git
cd Class_Watcher
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory:

```env
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
RESEND_API=your_resend_api_key
```

### 4. Initialize the database

Run the SQL migration files:

```bash
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f file.sql
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f stats_migration.sql
```

### 5. Run the application

```bash
python run.py
```

The application will be available at `http://localhost:8000`

### 6. Start the course monitoring scheduler (in a separate terminal)

```bash
python scheduler.py
```

## Docker Deployment 🐳

```bash
docker build -t uci-class-watcher .
docker run -p 8000:8000 --env-file .env uci-class-watcher
```

## Usage 💡

1. **Watch a Course**: Navigate to the homepage and enter your email, department, and course number
2. **Receive Notifications**: Get instant email alerts when a spot opens up
3. **View Statistics**: Check `/stats` to see real-time analytics
4. **Contact Support**: Use the contact form to request new departments or report issues

## Project Structure 📁

```
Class_Watcher/
├── app/
│   ├── __init__.py          # Flask app initialization & routes
│   ├── db.py                # Database connection
│   ├── utils.py             # Email & scraping utilities
│   ├── static/
│   │   └── styles/
│   │       └── style.css    # Custom CSS
│   └── Templates/
│       ├── base.html        # Base template with navigation
│       ├── index.html       # Homepage
│       ├── stats.html       # Statistics page
│       ├── changelog.html   # Version history
│       └── ...              # Other templates
├── worker.py                # Course availability checker
├── scheduler.py             # Cron-like scheduler
├── run.py                   # Application entry point
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
└── README.md
```

## Database Schema 🗄️

### `users` table

- `id`: Primary key
- `email`: Student email
- `department`: Course department
- `course_number`: Course number

### `notifications_sent` table

- `id`: Primary key
- `email`: Recipient email
- `department`: Course department
- `course_number`: Course number
- `class_codes`: Comma-separated class codes
- `sent_at`: Timestamp (default: CURRENT_TIMESTAMP)

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog 📝

### v2.1 (2025-11-13)

- Added support for more departments
- Improved styling and responsive design

### v2 (2025-11-11)

- Refactored code to scale efficiently
- Replaced Huey with cron job scheduler
- Migrated from SMTP to Resend API
- Enhanced form error handling

### v1.0 (2024-01-05)

- Initial release

## License 📄

This project is licensed under the MIT License.

## Contact 📧

Julian Chang - [GitHub](https://github.com/julianxchang)

Project Link: [https://github.com/julianxchang/Class_Watcher](https://github.com/julianxchang/Class_Watcher)

## Acknowledgments 🙏

- UCI WebSOC for course data
- Resend for email delivery
- Flask community for excellent documentation
