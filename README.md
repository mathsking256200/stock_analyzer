# Stock Analyzer

A Django-based stock analysis web application that lets users browse stocks by sector, open a detailed stock page, view key financial tables, fetch candlestick chart data, inspect peer comparison data, access a Screener watchlist dashboard, and export watchlist analysis to Excel.

## Main Features

- Sector-wise stock listing on the home page
- Individual stock detail page using a slug-based route
- Stock summary scraping from Screener
- Financial tables for:
  - Profit & Loss
  - Balance Sheet
  - Cash Flow
  - Ratios
  - Shareholding
- Peer comparison scraping using Selenium
- Candlestick chart data using Yahoo Finance (`yfinance`)
- User registration and login system
- Password reset through email and token flow
- Razorpay payment step during registration
- Watchlist dashboard scraping from Screener
- Excel export of watchlist data with conditional formatting

## Project Structure

```text
stock_analyzer/
├── manage.py
├── analyzer/
│   ├── migrations/
│   ├── static/
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   ├── style.css
│   │   └── documents/
│   ├── templates/
│   │   ├── about.html
│   │   ├── footer.html
│   │   ├── forgot.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── payment.html
│   │   ├── privacy.html
│   │   ├── register.html
│   │   ├── reset.html
│   │   ├── stock_detail.html
│   │   ├── table_template.html
│   │   └── welcome.html
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
└── stock_analyzer/
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## Tech Stack

- Python
- Django
- MySQL
- BeautifulSoup4
- Requests
- Selenium
- webdriver-manager
- yfinance
- OpenPyXL
- Razorpay

## Database Models

### Stock
Stores stock master data.

Fields:
- `name`
- `symbol`
- `slug`
- `sector`

### User
Stores custom registered user details.

Fields:
- `first_name`
- `last_name`
- `email`
- `phone`
- `password`
- `dob`
- `gender`
- `address`
- `created_at`
- `reset_token`
- `token_created_at`

### Payment
Stores Razorpay transaction references.

Fields:
- `user`
- `razorpay_order_id`
- `razorpay_payment_id`
- `amount`
- `created_at`

## URL Routes

- `/` - Home page
- `/analyze/` - Redirects selected stock to detail page
- `/stock/<slug:slug>/` - Stock detail page
- `/register/` - User registration
- `/payment-success/` - Payment success callback
- `/login/` - Login page
- `/reset-password/` - Reset password page
- `/forgot-password/` - Forgot password flow
- `/reset/<token>/` - Email token reset page
- `/welcome/` - User dashboard / watchlist page
- `/logout/` - Logout
- `/export-excel/` - Download analyzed watchlist in Excel
- `/about/` - About page
- `/privacy/` - Privacy page

## How It Works

### 1. Home Page
The application loads available sectors and stocks from the `Stock` table. Users can filter stocks by sector and choose a stock to analyze.

### 2. Stock Detail Page
When a user opens a stock page, the application:
- normalizes the stock symbol,
- scrapes summary metrics from Screener,
- scrapes major financial tables,
- scrapes peer comparison data,
- fetches candlestick data from Yahoo Finance,
- renders all results in a single dashboard page.

### 3. User Registration and Payment
The registration form stores user data in session first. A Razorpay order is then created, and after payment success the user and payment records are saved.

### 4. Watchlist Dashboard
After login, the system uses Selenium to open a Screener watchlist, scrape the table data, and display it on the dashboard.

### 5. Excel Export
The latest watchlist rows are exported to Excel using OpenPyXL. Several numeric columns are highlighted in green or red according to predefined screening rules.

## Installation

### 1. Clone the repository

```bash
git clone <https://github.com/mathsking256200/stock_analyzer.git>
cd stock_analyzer
```

### 2. Create and activate a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create MySQL database

Create a database named:

```sql
CREATE DATABASE stocks_db;
```

### 5. Update configuration

Before running the project, update database, email, Razorpay, and Screener-related credentials.

At minimum, review:
- `stock_analyzer/settings.py`
- `analyzer/views.py`

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create stock records

Add stock rows in the database through python shell. File is stored in analyzer/static/documents/stock.txt.

```bash
python manage.py shell
```
Kindly paste whole code in shell, so all 205 stocks will be added in database.

To exit the shell:

```bash
exit()
```


### 8. Run the server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Requirements for Selenium

This project uses Selenium for peer comparison scraping and watchlist scraping.

You need:
- Google Chrome or Chromium installed
- a compatible Chrome driver
- or let `webdriver-manager` manage the driver automatically

## Security Notes Before Uploading to GitHub

This project currently contains hardcoded secrets and credentials in source code. Do **not** publish them as-is.

Sensitive values found in the code include:
- Django secret key
- MySQL username and password
- SMTP email username and password
- Razorpay test keys
- Screener login credentials inside `views.py`

### Recommended actions before making the repository public

1. Remove all hardcoded credentials from the code.
2. Move secrets to environment variables or a `.env` file.
3. Rotate all exposed credentials immediately.
4. Replace MD5 password hashing with Django's built-in authentication system.
5. Add proper Razorpay signature verification in the payment callback.
6. Set `DEBUG = False` in production.
7. Configure `ALLOWED_HOSTS` before deployment.

## Known Limitations

- Uses a custom `User` model instead of Django authentication
- Passwords are hashed with MD5, which is not secure
- Payment callback currently does not verify Razorpay signature
- Heavy dependence on third-party website structure for scraping
- Watchlist scraping depends on valid external login credentials
- Dashboard export only works after watchlist data has been loaded in the current process

## Suggested Improvements

- Switch to Django's built-in auth system
- Store secrets in environment variables
- Add robust exception handling and logging
- Add admin panel data management for stocks
- Add search and pagination
- Add tests for scraping and view logic
- Add deployment configuration for production

## License

This project is intended for academic and learning purposes.
