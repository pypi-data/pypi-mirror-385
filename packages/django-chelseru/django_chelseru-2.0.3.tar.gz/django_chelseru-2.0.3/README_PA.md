django-chelseru
یک بسته جنگویی برای گپ‌زنی همزمان، راستی‌آزمایی پیامکی و فرستادن پیامک با یاری‌دهنده‌های ایرانی.

نویسنده
Sobhan Bahman Rashnu

🚀 ویژگی‌ها
📱 راستی‌آزمایی پیامکی (رمز یک‌بارمصرف): راستی‌آزمایی امن کاربران با یاری‌گیری از رمزهای یک‌بارمصرف که از راه پیامک فرستاده می‌شوند.

💬 گپ‌زنی همزمان: کارکرد پیام‌رسانی همزمان بر پایه WebSocket.

✉️ سامانه‌های پیامکی: فرستادن پیامک از راه یاری‌دهنده‌های نامور پیامکی ایرانی.

⚙️ نصب
بسته را با یاری‌گیری از pip نصب کنید:

pip install django-chelseru

'drfchelseru' را به INSTALLED_APPS در پرونده settings.py خود بیفزایید:

INSTALLED_APPS = [
    ...
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'drfchelseru',
    ...
]

🛠️ پیکربندی
برای پیکربندی بسته، واژه‌نامه DJANGO_CHELSERU را به پرونده settings.py خود بیفزایید. این واژه‌نامه به شما پروانه می‌دهد تا چیدمان‌های راستی‌آزمایی و پیامک را خودساخته نمایید.

# settings.py

DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD'           : 'OTP',                        # روش‌های پشتیبانی شده: OTP, PASSWD
        'AUTH_SERVICE'          : 'rest_framework_simplejwt',   # سرویس‌های پشتیبانی شده: rest_framework_simplejwt
        'OPTIONS': {
            'OTP_LENGTH'            : 8,    # پیش‌فرض: 8
            'OTP_EXPIRE_PER_MINUTES': 4,    # پیش‌فرض: 4
            'OTP_SMS_TEMPLATE_ID'   : 1,    # شناسه قالب پیامکی برای رمز یک‌بارمصرف
        }
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',  # یاری‌دهنده‌های پشتیبانی شده: PARSIAN_WEBCO_IR, MELI_PAYAMAK_COM, KAVENEGAR_COM
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY'  : '',
            'MELI_PAYAMAK_COM_USERNAME' : '',
            'MELI_PAYAMAK_COM_PASSWORD' : '',
            'MELI_PAYAMAK_COM_FROM'     : '',
            'KAVENEGAR_COM_API_KEY'     : 'YOUR_KAVENEGAR_API_KEY',
            'KAVENEGAR_COM_FROM'        : 'YOUR_KAVENEGAR_FROM_NUMBER',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            ...
        }
    }
}

AUTH_METHOD: روش راستی‌آزمایی را روشن می‌سازد. برای راستی‌آزمایی پیامکی، از 'OTP' بهره بگیرید.

OTP_LENGTH: درازای رمز یک‌بارمصرف.

OTP_EXPIRE_PER_MINUTES: زمان پایان‌یافتن رمز یک‌بارمصرف بر پایه دقیقه.

OTP_SMS_TEMPLATE_ID: شناسه قالب پیامکی که برای فرستادن رمز یک‌بارمصرف بهره گرفته می‌شود.

SMS_SERVICE: یاری‌دهنده پیامکی دلخواه خود را برگزینید.

SETTINGS: آگاهی‌های نیاز برای یاری‌دهنده پیامکی برگزیده‌تان را فراهم آورید.

TEMPLATES: شناسه‌های قالب پیامکی خود را روشن سازید.

🔌 نقطه‌های پایانی
برای به کارگیری کارکردهای این بسته، URLهای زیر را به پرونده urls.py خود بیفزایید.

# urls.py

from django.urls import path, include

urlpatterns = [
    ...
    path('api/', include('drfchelseru.urls')),
    ...
]

این بسته نقطه‌های پایانی API زیر را فراهم می‌آورد:

نقطه‌ پایانی

شرح

روش

/api/otp/send/

یک رمز یک‌بارمصرف به شماره همراه گفته‌شده می‌فرستد.

POST

/api/authenticate/

کاربری را با رمز یک‌بارمصرف دریافت‌شده، راستی‌آزمایی می‌کند.

POST

/api/sessions/

نشست‌های فعال کاربر را فهرست کرده و درایوری می‌کند.

GET

/api/message/send/

یک پیامک با یاری‌دهنده پیکربندی‌شده می‌فرستد.

POST

به کارگیری نقطه‌های پایانی
1. فرستادن رمز یک‌بارمصرف (/api/otp/send/)
روش: POST شرح: یک رمز یک‌بارمصرف به شماره همراه کاربر می‌فرستد.

داده‌نماهای نیاز:

داده‌نما

گونه

شرح

نمونه

mobile_number

str

شماره همراه کاربر.

09121234567

پاسخ‌ها:

HTTP 200 OK: رمز یک‌بارمصرف با کامیابی فرستاده شد.

{"details": "The OTP code was sent correctly."}

HTTP 400 BAD REQUEST: ساختار نادرست mobile_number.

HTTP 409 CONFLICT: یک رمز یک‌بارمصرف پیش‌تر فرستاده شده و هنوز روایی دارد.

{"details": "An OTP code has already been sent. Please wait X seconds before trying again."}

HTTP 500 INTERNAL SERVER ERROR: یک دشواری در کارگذار پیش آمده است.

2. راستی‌آزمایی (/api/authenticate/)
روش: POST شرح: کاربر را با رمز یک‌بارمصرف فراهم شده، راستی‌آزمایی می‌کند. اگر با کامیابی انجام شود، توکن‌های JWT (access و refresh) را بازمی‌گرداند.

داده‌نماهای نیاز:

داده‌نما

گونه

شرح

نمونه

mobile_number

str

شماره همراه کاربر.

09121234567

code

str

رمز یک‌بارمصرف دریافت شده از راه پیامک.

12345678

group

int

اختیاری: یک شناسه دسته برای کاربر.

1

پاسخ‌ها:

HTTP 200 OK: راستی‌آزمایی با کامیابی انجام شد.

{
  "access": "...",
  "refresh": "..."
}

HTTP 401 UNAUTHORIZED: رمز یک‌بارمصرف ناروا یا پایان‌یافته.

{"error": "The code sent to this mobile number was not found."}

HTTP 400 BAD REQUEST: داده‌نماهای نیاز ناپیدا یا ساختار نادرست.

HTTP 500 INTERNAL SERVER ERROR: یک دشواری در کارگذار پیش آمده است.

3. فرستادن پیامک (/api/message/send/)
روش: POST شرح: یک پیامک خودساخته را با یاری‌دهنده پیکربندی‌شده می‌فرستد.

داده‌نماهای نیاز:

داده‌نما

گونه

شرح

نمونه

mobile_number

str

شماره همراه گیرنده.

09121234567

message_text

str

نوشتار پیام. (بیشینه ۲۹۰ نویسه)

Hello, World!

template_id

int

برای برخی یاری‌دهنده‌ها (برای نمونه پارسیان) نیاز است.

1

پاسخ‌ها:

HTTP 200 OK: پیام با کامیابی فرستاده شد.

{"details": "The Message was sent correctly."}

HTTP 400 BAD REQUEST: دشواری‌های درست‌سنجی برای داده‌نماها.

HTTP 401 UNAUTHORIZED: راستی‌آزمایی انجام نشد.

HTTP 500 INTERNAL SERVER ERROR: یک دشواری در کارگذار پیش آمده است.

HTTP 502 BAD GATEWAY: یاری‌دهنده پیامکی یک دشواری را بازگرداند.

4. فهرست نشست‌ها (/api/sessions/)
روش: GET شرح: همه نشست‌های فعال کاربران را فهرست می‌کند. نیاز به راستی‌آزمایی (IsAuthenticated) دارد.

سربرگ‌های نیاز:

سربرگ

ارزش

Authorization

Bearer <your_access_token>

💡 مدل‌ها
این بسته یک مدل Session برای درایوری نشست‌های فعال کاربران دارد. می‌توانید به این نشست‌ها از راه نقطه‌ پایانی /api/sessions/ دسترسی یافته و آنها را درایوری کنید.