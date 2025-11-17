# UCI Class Watcher

A web application that monitors UCI course availability and automatically notifies students via email when spots open up in their desired classes.

## Features
- Automatic email notifications when classes have open spots
- User authentication with ability to update watch preferences for registered users
- Statistics dashboard
- Supports all UCI departments

## Run Locally

### Prerequisites
- Python 3.8+
- PostgreSQL database

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/julianxchang/Class_Watcher.git
   cd Class_Watcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   DB_HOST=your_database_host
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   RESEND_API=your_resend_api_key
   APP_SECRET_KEY=your_secret_key
   ENV=prod
   ```

5. **Set up database**

   Run the SQL schema:
   ```bash
   psql -U your_user -d your_database -f file.sql
   ```

6. **Run the application**
   ```bash
   # Development server
   python run.py

   # Or with Gunicorn (production)
   gunicorn run:app
   ```

7. **Start the scheduler** (in a separate terminal)
   ```bash
   python scheduler.py
   ```

8. **Access the app**

   Open your browser and go to `http://localhost:8000`

## Tech Stack
- **Backend:** Flask, Python, PostgreSQL
- **Frontend:** HTML, CSS, JavaScript
- **APIs:** Resend API
- **Scraping:** BeautifulSoup4, Requests





