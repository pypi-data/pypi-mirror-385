## دستیار

```markdown
# FipiranFunds

[![PyPI version](https://img.shields.io/pypi/v/fipiranfunds.svg)](https://pypi.org/project/fipiranfunds/)
[![Python Version](https://img.shields.io/pypi/pyversions/fipiranfunds.svg)](https://pypi.org/project/fipiranfunds/)
[![License](https://img.shields.io/pypi/l/fipiranfunds.svg)](https://pypi.org/project/fipiranfunds/)
[![GitHub Issues](https://img.shields.io/github/issues/Kimiaslhd/fipiranfunds.svg)](https://github.com/Kimiaslhd/fipiranfunds/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Kimiaslhd/fipiranfunds.svg)](https://github.com/Kimiaslhd/fipiranfunds/stargazers)

کتابخانه‌ی پایتون برای دریافت و ذخیره‌سازی داده‌های معاملات و بازدهی صندوق‌ها از API فپیران (Fipiran) و خروجی گرفتن به CSV. این README شامل توضیحات به فارسی برای کاربران ایرانی و نمونه‌های کدنویسی کاربردی به انگلیسی است.

A Python library for fetching and exporting Iranian fund data from the Fipiran API to CSV. This README includes Persian explanations for Iranian users and practical English code examples.

## پیش‌نیازها / Requirements

- **نسخه‌ی پایتون**: 3.6+ (توصیه‌شده: 3.8+ برای بهترین عملکرد و سازگاری).
- **الزامات اصلی** (به طور خودکار با نصب پکیج نصب می‌شوند):
  - requests >= 2.25.0
  - pandas >= 1.2.0
  - jdatetime >= 3.6.0
  - beautifulsoup4 (برای تجزیه HTML اگر نیاز باشد).

- **کتابخانه‌های اختیاری** (برای امکانات بیشتر):
  - pyodbc — برای اتصال و نوشتن در SQL Server (نیاز به نصب ODBC driver از مایکروسافت روی ویندوز، مانند “Microsoft ODBC Driver 17 for SQL Server”).
  - pytse-client — در صورتی که بخواهید از داده‌های TSETMC استفاده کنید.
  - tqdm — برای نوار پیشرفت (progress bar).
  - python-dateutil — کمک در پردازش تاریخ‌ها.

**نصب سریع (پیشنهادی برای تمام امکانات)**:
```
pip install fipiranfunds requests pandas jdatetime beautifulsoup4 pyodbc pytse-client tqdm python-dateutil
```

## نصب / Installation

برای استفاده ساده (فقط الزامات اصلی):
```
pip install fipiranfunds
```

برای توسعه یا نصب آخرین نسخه از گیت‌هاب:
```
pip install git+https://github.com/Kimiaslhd/fipiranfunds.git
```

## شروع سریع / Quick Start

این کتابخانه اجازه می‌دهد داده‌های صندوق‌های سرمایه‌گذاری ایرانی را از API فپیران دریافت کنید و به CSV خروجی بگیرید. مثال تعاملی زیر از شما تاریخ شمسی می‌پرسد و فایل CSV را روی Desktop ذخیره می‌کند.

```python
from fipiranfunds import export_fund_data

export_fund_data()
# برنامه از شما تاریخ شروع و پایان به فرمت شمسی YYYY/MM/DD را می‌پرسد.
# سپس فایل CSV خروجی روی Desktop ذخیره می‌شود (مثال: fipiranfunds_export_20240321_123456.csv).
```

## خلاصه‌ی قابلیت‌ها / Usage Overview

این پکیج API عمومی ساده‌ای در سطح بالا ارائه می‌دهد برای دسترسی آسان بدون نیاز به واردات زیرماژول‌ها. قابلیت‌های کلیدی:

- `export_fund_data()`: اجرای تعاملی برای دریافت داده‌ها در بازه تاریخی و ذخیره به CSV (روی Desktop).
- `FundDataFetcher`: کلاس برای استفاده برنامه‌نویسی (برگرداندن pandas.DataFrame).
- `jalali_to_gregorian(date_str)`: تبدیل تاریخ شمسی به میلادی (ISO format).
- توابع داخلی مانند `mapper.*` برای نگاشت فیلدهای API به نام‌های کاربرپسند در CSV.

برای جزئیات بیشتر، به بخش توابع و مثال‌ها مراجعه کنید.

## توابع و مثال‌ها / Functions & Examples

### export_fund_data()

تابع راحت و تعاملی: از کاربر تاریخ‌های شروع و پایان شمسی می‌پرسد، آن‌ها را به میلادی تبدیل کرده، داده‌ها را از API فراخوانی می‌کند و CSV را ذخیره می‌کند.

**رفتار کلیدی**:
- اعتبارسنجی تاریخ ورودی (Jalali format: YYYY/MM/DD).
- تلاش‌های مجدد (retries) در صورت بروز خطاهای موقتی شبکه.
- چاپ وضعیت پیشرفت و مسیر نهایی فایل CSV.

**مثال**:
```python
from fipiranfunds import export_fund_data

export_fund_data()

# نمونه ورودی:
# Enter start date (Jalali YYYY/MM/DD): 1403/01/01
# Enter end date (Jalali YYYY/MM/DD): 1403/01/05
# Data saved to: C:\Users\<YourUsername>\Desktop\fipiranfunds_export_20240321_140501.csv
```

### FundDataFetcher

کلاس برای کنترل برنامه‌نویسی پیشرفته، مانند استفاده در اسکریپت‌های ETL. خروجی: pandas.DataFrame.

**مثال**:
```python
from fipiranfunds import FundDataFetcher, jalali_to_gregorian

fetcher = FundDataFetcher()
start = jalali_to_gregorian("1403/01/01")  # خروجی: "2024-03-21"
end = jalali_to_gregorian("1403/01/31")
df = fetcher.fetch_fund_data(start, end)

print(df.head())
df.to_csv("funds_local.csv", index=False)
```

### jalali_to_gregorian(date_str)

تبدیل رشته تاریخ شمسی "YYYY/MM/DD" به رشته میلادی ISO "YYYY-MM-DD".

**مثال**:
```python
from fipiranfunds import jalali_to_gregorian

print(jalali_to_gregorian("1403/01/01"))  # خروجی: "2024-03-21"
```

## ساختار CSV خروجی / Output CSV Structure

**الگوی نام فایل**: fipiranfunds_export_<YYYYMMDD_HHMMSS>.csv

**ستون‌های نمونه** (ممکن است بسته به نسخه یا داده‌های API تغییر کنند):
- regNo
- fundTitle
- isCompleted
- calcDate
- licenseTitle
- fundSize
- fundType
- initiationDate
- dailyEfficiency
- weeklyEfficiency
- monthlyEfficiency
- quarterlyEfficiency
- sixMonthEfficiency
- annualEfficiency
- statisticalNav
- efficiency
- cancelNav
- issueNav
- dividendPeriodEfficiency
- netAsset
- unitBalance
- accountsNo
- articlesOfAssociationEfficiency

## اتصال به SQL Server (اختیاری) / SQL Server Connection (Optional)

اگر می‌خواهید داده‌ها را مستقیماً به دیتابیس SQL Server بنویسید (pyodbc را نصب کنید).

**مثال ساده**:
```python
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.1.131;DATABASE=LotusibBI;UID=user;PWD=pass"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# فرض کنید df داده‌های شما است
# روش سریع: ابتدا به CSV ذخیره کنید، سپس از BULK INSERT استفاده کنید
# یا از pandas.to_sql (با نصب SQLAlchemy) برای نوشتن مستقیم:
# df.to_sql("funds_table", conn, if_exists="append", index=False)
```

## نکات خطاها و راهنمایی‌ها / Troubleshooting & Tips

- **خطای تاریخ**: ورودی را بررسی کنید؛ فرمت باید YYYY/MM/DD باشد.
- **خطای API (مانند 500 یا IP-block)**: چند دقیقه صبر کنید و دوباره امتحان کنید — سایت ممکن است درخواست‌ها را موقتاً محدود کند.
- **تداخل نسخه‌ها**: اگر jdatetime با دیگر پکیج‌ها تداخل دارد، نسخه سازگار را پین کنید (مثلاً `pip install jdatetime==3.6.0`).
- **نکته عمومی**: برای تست، از محیط مجازی (virtualenv) استفاده کنید تا وابستگی‌ها ایزوله شوند.

## CLI (در صورت وجود) / CLI (If Available)

اگر پکیج CLI را پشتیبانی کند:
```
python -m fipiranfunds.cli
# یا اگر entry point تعریف شده باشد:
fipiranfunds
```

## توسعه و مشارکت / Contributing

خوشحال می‌شویم از کمک شما! 
- مسائل (issues) یا درخواست‌های pull را در [گیت‌هاب](https://github.com/Kimiaslhd/fipiranfunds) باز کنید.
- قبل از ارسال PR: تست‌های محلی را اجرا کنید، کد را با black فرمت کنید، و سبک PEP 8 را رعایت کنید.
- برای شروع: repo را fork کنید، تغییرات را اعمال کنید، و PR ارسال کنید.

## تغییرات / Changelog

- **0.1.14**: بهبود README، رفع مشکلات رندرینگ PyPI، و صادرات API در سطح بالا.
- **0.1.13**: نسخه اولیه با پشتیبانی پایه API و CSV.

برای تغییرات کامل، به [گیت‌هاب commits](https://github.com/Kimiaslhd/fipiranfunds/commits) مراجعه کنید.

## مجوز / License

MIT License. جزئیات در فایل LICENSE.

## نویسنده و تماس / Author & Contact

- **نام**: Kimia Salehi Delarestaghy
- **ایمیل**: kimiaslhd@gmail.com
- **لینکدین**: [https://www.linkedin.com/in/kimia-salehy-delarestaghy/](https://www.linkedin.com/in/kimia-salehy-delarestaghy/)
- **گیت‌هاب**: [https://github.com/Kimiaslhd/fipiranfunds](https://github.com/Kimiaslhd/fipiranfunds)
- **PyPI**: [https://pypi.org/project/fipiranfunds/](https://pypi.org/project/fipiranfunds/)

اگر سؤالی دارید، issue باز کنید یا ایمیل بزنید!
```

---
*Generated by: Grok 4*
