import requests
import yfinance as yf
from bs4 import BeautifulSoup
from django.core.cache import cache
import time
# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

WATCHLIST_BASE_HEADERS = [
    "S.No.", "", "Name", "CMP", "P/E", "CMP/BV", "PEG", "M.cap/Sales",
    "Sales Growth", "Profit Growth", "ROE", "ROCE", "Asset Turnover", "OPM",
    "NPM", "Debt/Equ", "Int Coverage", "Inventory Turnover", "Current Ratio"
]

WATCHLIST_FULL_HEADERS = WATCHLIST_BASE_HEADERS + ["Score", "Analysis", "Suggestion", "Rating"]


# ---------------------------
# Normalize Symbol
# ---------------------------
def normalize_symbol(symbol):
    return symbol.replace("&", "").strip()


# ---------------------------
# Stock Summary (Key Metrics)
# ---------------------------
def scrape_stock_summary(symbol):
    cache_key = f"summary_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f"https://www.screener.in/company/{symbol}/"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        summary = {}

        # NEW METHOD: Screener now uses div with class "company-ratios"
        ratio_section = soup.find("div", class_="company-ratios")

        if ratio_section:
            items = ratio_section.find_all("li")
            for item in items:
                name = item.find("span", class_="name")
                value = item.find("span", class_="number")
                if name and value:
                    summary[name.get_text(strip=True)] = value.get_text(strip=True)

        cache.set(cache_key, summary, 86400)
        return summary

    except Exception as e:
        print("Summary Error:", e)
        return {}


# ---------------------------
# Financial Tables
# ---------------------------
def scrape_table(symbol, table_type):
    cache_key = f"{table_type}_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return [], []

        soup = BeautifulSoup(response.text, "html.parser")

        section_map = {
            "pnl": "profit-loss",
            "bs": "balance-sheet",
            "cf": "cash-flow",
            "ratios": "ratios",
            "shareholding": "shareholding"
        }

        section_id = section_map.get(table_type)
        if not section_id:
            return [], []

        section = soup.find("section", id=section_id)
        if not section:
            return [], []

        table = section.find("table")
        if not table:
            return [], []

        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        rows = []
        for tr in table.find_all("tr")[1:]:
            cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if any(cols):
                rows.append(cols)

        cache.set(cache_key, (headers, rows), 86400)
        return headers, rows

    except Exception as e:
        print(f"{table_type} Error:", e)
        return [], []


# ---------------------------
# Peer Comparison (Selenium Only)
# ---------------------------
def scrape_peers(symbol):
    cache_key = f"peers_{symbol}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = f"https://www.screener.in/company/{symbol}/consolidated/"

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(text(),'Peer')]")
            )
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        sections = soup.find_all("section")

        for section in sections:
            heading = section.find("h2")
            if heading and "peer" in heading.text.lower():

                table = section.find("table")
                if not table:
                    continue

                headers = [th.get_text(strip=True) for th in table.find_all("th")]

                rows = []
                for tr in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                    if any(cols):
                        rows.append(cols)

                cache.set(cache_key, (headers, rows), 86400)
                return headers, rows

        return [], []

    except Exception as e:
        print("Peer Selenium Error:", e)
        return [], []


# ---------------------------
# Candlestick Data (Supports period)
# ---------------------------
def get_candlestick_data(symbol, period="1y"):
    try:
        ticker = yf.Ticker(symbol + ".NS")
        hist = ticker.history(period=period)

        if hist.empty:
            return []

        candles = []

        for index, row in hist.iterrows():
            open_price = round(float(row["Open"]), 2)
            high_price = round(float(row["High"]), 2)
            low_price = round(float(row["Low"]), 2)
            close_price = round(float(row["Close"]), 2)

            candles.append({
                "x": index.strftime("%Y-%m-%d"),
                "y": [open_price, high_price, low_price, close_price]
            })

        return candles

    except Exception as e:
        print("Chart Error:", e)
        return []


# ---------------------------
# Watchlist Scraper
# ---------------------------
def scrape_watchlist_with_selenium(email, password, watchlist_url):

    if not email or not password:
        raise ValueError("Email or Password is missing!")

    # Chrome Setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Step 1: Open Login Page
        driver.get("https://www.screener.in/login/")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Step 2: Enter Credentials
        driver.find_element(By.NAME, "username").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        # Step 3: Confirm Login (wait for account menu)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "account"))
        )

        # Step 4: Open Watchlist
        driver.get(watchlist_url)

        # Step 5: Wait for stock table rows
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table tbody tr"))
        )

        time.sleep(2)  # Extra safety buffer

        # Step 6: Parse HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # IMPORTANT: Target correct stock table
        table = soup.find("table", class_="data-table")

        if not table:
            print("Stock table not found!")
            return [], []

        headers = []
        rows = []

        # Extract Headers
        thead = table.find("thead")
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all("th")]

        # Remove S.No column if present
        remove_first_column = False
        if headers and headers[0].lower().startswith("s"):
            remove_first_column = True
            headers = headers[1:]

        # Extract Rows
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if not tds:
                    continue

                row = [td.get_text(strip=True) for td in tds]

                if remove_first_column:
                    row = row[1:]

                rows.append(row)

        print("Headers:", headers)
        print("Rows Found:", len(rows))

        return headers, rows

    finally:
        driver.quit()


# ---------------------------
# Floating value helpers
# ---------------------------
def safe_float(value):
    try:
        if value == "" or value is None:
            return 0.0

        cleaned = str(value).strip()
        cleaned = cleaned.replace(",", "")
        cleaned = cleaned.replace("%", "")
        cleaned = cleaned.replace("₹", "")
        cleaned = cleaned.replace("x", "")

        if cleaned in {"", "-", "--", "NA", "N/A"}:
            return 0.0

        return float(cleaned)
    except Exception:
        return 0.0


def evaluate_watchlist_row(row):
    padded_row = list(row[:19]) + [""] * max(0, 19 - len(row))

    pe = safe_float(padded_row[4])
    cmpbv = safe_float(padded_row[5])
    peg = safe_float(padded_row[6])
    mcapsales = safe_float(padded_row[7])
    sales = safe_float(padded_row[8])
    profit = safe_float(padded_row[9])
    roe = safe_float(padded_row[10])
    roce = safe_float(padded_row[11])
    asset = safe_float(padded_row[12])
    opm = safe_float(padded_row[13])
    npm = safe_float(padded_row[14])
    debt = safe_float(padded_row[15])
    interest = safe_float(padded_row[16])
    invent = safe_float(padded_row[17])
    current = safe_float(padded_row[18])

    checks = [
        pe < 30,
        cmpbv < 3,
        peg < 1,
        mcapsales < 3,
        sales > 10,
        profit > 15,
        roe > 15,
        roce > 15,
        asset > 1,
        opm > 15,
        npm > 10,
        debt <= 0.2,
        interest >= 20,
        invent > 4,
        1.5 <= current <= 2,
    ]

    score = round((sum(checks) / 15) * 100)
    analysis = "GREEN" if score >= 60 else "RED"
    suggestion = "BUY" if score >= 60 else "AVOID"

    rating = "⭐"
    if score >= 80:
        rating = "⭐⭐⭐⭐⭐"
    elif score >= 60:
        rating = "⭐⭐⭐⭐"
    elif score >= 50:
        rating = "⭐⭐⭐"
    elif score >= 40:
        rating = "⭐⭐"

    return {
        "score": f"{score}%",
        "analysis": analysis,
        "suggestion": suggestion,
        "rating": rating,
    }


def build_watchlist_report_rows(rows):
    enriched_rows = []

    for row in rows or []:
        base_row = list(row[:19]) + [""] * max(0, 19 - len(row))
        evaluation = evaluate_watchlist_row(base_row)
        enriched_rows.append(base_row + [
            evaluation["score"],
            evaluation["analysis"],
            evaluation["suggestion"],
            evaluation["rating"],
        ])

    return enriched_rows
