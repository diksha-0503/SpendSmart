# SpendSmart

A beginner-friendly personal expense tracker built with Python, Flask, MySQL, HTML, CSS, and a little JavaScript.

A personal expense tracker built with Python, Flask, MySQL, HTML, CSS, and JavaScript.

**[Live Demo](https://spendsmart-k0d6.onrender.com)** | **[Source Code](https://github.com/diksha-0503/SpendSmart)**

## Tech Stack
Python · Flask · MySQL · HTML · CSS · JavaScript

## Features

- Dashboard with this month's income, expenses, and remaining balance
- Add, edit, and delete income or expense transactions
- Filter transactions by type and category
- Category-wise expense summary
- Basic form validation and confirmation before deleting
- MySQL database storage

## Requirements

- Python 3.10 or newer
- MySQL Server
- VS Code (recommended, not required)

## 1. Create a virtual environment

Open a terminal in the `SpendSmart` project folder.

```powershell
python -m venv venv
venv\Scripts\activate
```

If PowerShell blocks activation, try this in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This change applies only to that PowerShell session.

## 2. Install Python packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Set up MySQL

1. Start your MySQL Server.
2. Open MySQL Workbench or the MySQL command-line client.
3. Open `database/schema.sql` and execute it.

The script creates the `spendsmart` database and `transactions` table. It also adds a few sample transactions. If you run the script again, the sample rows will be inserted again.

## 4. Configure database credentials

Copy `.env.example` to a new file named `.env` in the project root.

Update the values to match your local MySQL setup:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=spendsmart
SECRET_KEY=use-a-long-random-secret
```

Do not commit `.env` to GitHub. It is included in `.gitignore`.

## 5. Run the application

Make sure your virtual environment is active and MySQL is running. Then run:

```powershell
python app.py
```

Open the local URL shown in the terminal, usually:

http://127.0.0.1:5000

Press `Ctrl+C` in the terminal to stop the server.

## Project structure

```text
SpendSmart/
├── app.py
├── requirements.txt
├── .env.example
├── database/
│   └── schema.sql
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── transactions.html
│   ├── transaction_form.html
│   └── setup_error.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## How the app works

- `app.py` contains Flask routes and database queries.
- `templates/` contains HTML pages rendered by Flask.
- `static/css/style.css` styles the pages.
- `static/js/script.js` asks for confirmation before a transaction is deleted.
- `database/schema.sql` creates the database table and sample data.
- MySQL stores transaction data so it remains after the server restarts.

## Important notes

- This is a learning project, not a production-ready finance service.
- It currently has no login system, so it is intended for local/demo use.
- The Flask debug server is for development only. Do not deploy it publicly with debug mode enabled.
- Before a public deployment, add authentication, CSRF protection, stronger configuration, production hosting, and additional tests.
- The amount is validated in the app and stored as `DECIMAL` in MySQL. Database credentials belong in `.env`, not source code.
