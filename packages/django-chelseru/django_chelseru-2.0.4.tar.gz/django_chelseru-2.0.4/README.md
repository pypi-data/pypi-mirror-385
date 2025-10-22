# django-chelseru Django Package

## Overview

django-chelseru is a Django package developed by Sobhan Bahman Rashnu for real-time chatting via WebSocket, OTP-based SMS verification, and SMS sending with Iranian providers. It also supports payment integrations.

Useful for building applications requiring secure authentication, messaging, real-time chat, and online payments.

## Features

- **Authentication**: OTP and PASSWD methods using rest_framework_simplejwt.
- **SMS Services**: PARSIAN_WEBCO_IR, MELI_PAYAMAK_COM, KAVENEGAR_COM.
- **Payment Gateways**: PAYPING_IR, ZARINPAL_COM.
- **Real-time Chat**: WebSocket/Channels for messaging.
- Session management and API endpoints for OTP, authentication, SMS, payments, and chat.

## Requirements

- Python 3.8+
- Django 4.x
- django-rest-framework
- djangorestframework-simplejwt
- django-channels
- user-agents
- requests
- Other dependencies: See `requirements.txt`

## Installation

1. Install the package:

   ```bash
   pip install django-chelseru
   ```
2. Add to `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...
       'rest_framework',
       'rest_framework_simplejwt',
       'channels',
       'drfchelseru',
   ]
   ```
3. Configure middleware and ASGI in `settings.py`.
4. Apply migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the server (use ASGI for WebSocket):

   ```bash
   daphne -b 0.0.0.0 -p 8000 project.asgi:application
   ```

## Project Structure

- **models.py**: Defines models for users, OTP codes, sessions, SMS messages, organizations, chat rooms, chat permissions, messages, wallets, and payments.
- **views.py**: Handles API endpoints for OTP authentication, SMS, payments, and chat.
- **urls.py**: Maps URL patterns to views for API routes.
- **consumers.py**: Implements WebSocket consumer for real-time chat.
- **middlewares.py**: Includes `TakeUserSessionMiddlaware` for session management and `JWTAuthMiddleware` for WebSocket authentication.

## Models

- **User**: Extends Django's User model with mobile number and group.
- **OTPCode**: Stores OTP codes for authentication with expiration logic.
- **Session**: Tracks user sessions with IP, device, and browser info.
- **MessageSMS**: Logs SMS messages sent to users.
- **Organization**: Represents organizations owned by users.
- **ChatRoomPermissions**: Defines access levels for chat room actions.
- **ChatRoom**: Manages chat rooms with users, status, and permissions.
- **MessageChat**: Stores chat messages with sender and timestamp.
- **Wallet**: Tracks user wallet balances for payments.
- **Payment**: Manages payment transactions with gateway integration.

## Configuration

Update your Django `settings.py`:

```python
MIDDLEWARE = [
    ...
    'drfchelseru.middlewares.TakeUserSessionMiddlaware',
]

ASGI_APPLICATION = 'yourproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD': 'OTP',
        'AUTH_SERVICE': 'rest_framework_simplejwt',
        'OPTIONS': {
            'OTP_LENGTH': 8,
            'OTP_EXPIRE_PER_MINUTES': 4,
            'OTP_SMS_TEMPLATE_ID': 5,
        }
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY': '',
            'MELI_PAYAMAK_COM_USERNAME': '',
            'MELI_PAYAMAK_COM_PASSWORD': '',
            'MELI_PAYAMAK_COM_FROM': '',
            'KAVENEGAR_COM_API_KEY': '',
            'KAVENEGAR_COM_FROM': '',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            'T3': 3,
        }
    },
    'BANK': {
        'GATEWAY': 'PAYPING_IR',
        'SETTINGS': {
            'MERCHANT_ID': '',
            'CALLBACK_URL': '',
            'CURRENCY': 'IRT'
        }
    }
}
```

## API Endpoints

- **POST /drfchelseru/message/send/**: Send SMS.

  - Request: `{ "mobile_number": "09211892425", "message_text": "Hello", "template_id": 1 }`
  - Response: `{ "details": "The Message was sent correctly." }` (200 OK)

- **POST /drfchelseru/otp/send/**: Request OTP code.

  - Request: `{ "mobile_number": "09211892425" }`
  - Response: `{ "details": "The OTP code was sent correctly." }` (200 OK)

- **POST /drfchelseru/authenticate/**: Authenticate with OTP.

  - Request: `{ "mobile_number": "09211892425", "code": "652479", "group": 0 }`
  - Response: `{ "access": "<access_token>", "refresh": "<refresh_token>" }` (200 OK)

- **GET /drfchelseru/sessions/**: List user sessions (authenticated users only).

  - Headers: `Authorization: Bearer <access_token>`
  - Response: List of sessions (200 OK)

- **POST /drfchelseru/payment/create/**: Initiate payment.

  - Request: `{ "order_id": "123", "amount": 1000.0, "description": "Test payment", "callback_url": "http://example.com/callback", "mobile": "09211892425", "email": "user@example.com", "currency": "IRT" }`
  - Response: `{ "details": { "gateway_url": "<url>", ... } }` (200 OK)

- **GET/POST /drfchelseru/payment/verify/**: Verify payment.

  - GET Query: `?Authority=<authority>&Status=OK`
  - POST Body: `{ "paymentCode": "<code>", "paymentRefId": "<refid>", ... }`
  - Response: `{ "details": { "is_pay": 1, ... } }` (200 OK)

- **/drfchelseru/chat/chatrooms/**: CRUD for chat rooms (authenticated users only).

  - POST Request: `{ "user": 2 }` (to create room with user ID 2)
  - Headers: `Authorization: Bearer <access_token>`
  - Response: Chat room details (201 Created)

- **/drfchelseru/chat/messages/**: CRUD for chat messages (authenticated users only).

  - POST Request: `{ "chat_room": 1, "text": "Hello" }`
  - GET Query: `?chat_room=1`
  - Headers: `Authorization: Bearer <access_token>`
  - Response: Message details or list (200 OK / 201 Created)

## WebSocket Usage

- Connect to a chat room for real-time messaging:

  ```bash
  wscat -c wss://<your-domain>/drfchelseru/chat/<chat_room_id>/?token=<jwt_token>
  ```
  - Example token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMDE5NTY3LCJpYXQiOjE3NTU4MzU1NjcsImp0aSI6IjhhYTY1Y2I3ZDhmMjRmMzliYjFmNDFkZmJiYjcyYmVmIiwidXNlcl9pZCI6Mzl9.mHmIjbTl3X1cd3Ky5HFCD6gy4kGxMVcActo9JXtT9JQ`
  - Replace `<chat_room_id>` (e.g., 17) with the desired room ID and provide a valid JWT token.

## Middleware

- **TakeUserSessionMiddlaware**: Logs user session data (IP, user agent, device, browser) for HTTP requests.
- **JWTAuthMiddleware**: Authenticates WebSocket connections using JWT tokens.

## Usage

- Access the API at `http://<your-domain>/drfchelseru/`.
- Connect to WebSocket at `ws://<your-domain>/drfchelseru/chat/<chat_room_id>/?token=<jwt_token>`.
- Admin panel: Create a superuser with `python manage.py createsuperuser`.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

MIT License



_______________________________________________________________________________________________________________________


# django-chelseru پکیج جنگو

## بررسی اجمالی

django-chelseru یک پکیج جنگو است که توسط سبحان بهمن رشنو توسعه یافته برای گفتگوهای همزمان از راه وب‌سوکت، تایید پیامکی بر پایه OTP، و فرستادن پیامک با فراهم‌کنندگان ایرانی. همچنین از یکپارچگی پرداخت پشتیبانی می‌کند.

کاربردی برای ساخت برنامه‌هایی که نیاز به تایید امن، پیام‌رسانی، گفتگو همزمان، و پرداخت برخط دارند.

## ویژگی‌ها

- **تایید**: روش‌های OTP و PASSWD با بهره‌گیری از rest_framework_simplejwt.
- **خدمات پیامک**: PARSIAN_WEBCO_IR، MELI_PAYAMAK_COM، KAVENEGAR_COM.
- **درگاه‌های پرداخت**: PAYPING_IR، ZARINPAL_COM.
- **گفتگو همزمان**: وب‌سوکت/کانال‌ها برای پیام‌رسانی.
- مدیریت نشست و نقاط پایانی API برای OTP، تایید، پیامک، پرداخت‌ها، و گفتگو.

## نیازمندی‌ها

- Python 3.8+
- Django 4.x
- django-rest-framework
- djangorestframework-simplejwt
- django-channels
- user-agents
- requests
- دیگر وابستگی‌ها: ببینید `requirements.txt`

## نصب

1. پکیج را نصب کنید:

   ```bash
   pip install django-chelseru
   ```
2. به `INSTALLED_APPS` در `settings.py` بیفزایید:

   ```python
   INSTALLED_APPS = [
       ...
       'rest_framework',
       'rest_framework_simplejwt',
       'channels',
       'drfchelseru',
   ]
   ```
3. میان‌گیر و ASGI را در `settings.py` پیکربندی کنید.
4. مهاجرت‌ها را اعمال کنید:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. کارساز را اجرا کنید (برای وب‌سوکت از ASGI بهره ببرید):

   ```bash
   daphne -b 0.0.0.0 -p 8000 project.asgi:application
   ```

## ساختار پروژه

- **models.py**: مدل‌ها را برای کاربران، کدهای OTP، نشست‌ها، پیامک‌ها، سازمان‌ها، اتاق‌های گفتگو، دسترسی‌های اتاق گفتگو، پیام‌ها، کیف‌پول‌ها، و پرداخت‌ها تعریف می‌کند.
- **views.py**: نقاط پایانی API برای تایید OTP، پیامک، پرداخت‌ها، و گفتگو را مدیریت می‌کند.
- **urls.py**: الگوهای URL را به نما‌ها برای مسیرهای API نگاشت می‌کند.
- **consumers.py**: مصرف‌کننده وب‌سوکت را برای گفتگو همزمان پیاده‌سازی می‌کند.
- **middlewares.py**: شامل `TakeUserSessionMiddlaware` برای مدیریت نشست و `JWTAuthMiddleware` برای تایید وب‌سوکت.

## مدل‌ها

- **User**: مدل کاربر جنگو را با شماره همراه و گروه گسترش می‌دهد.
- **OTPCode**: کدهای OTP را برای تایید با منطق انقضا ذخیره می‌کند.
- **Session**: نشست‌های کاربر را با IP، دستگاه، و داده‌های مرورگر پیگیری می‌کند.
- **MessageSMS**: پیامک‌های فرستاده‌شده به کاربران را ثبت می‌کند.
- **Organization**: سازمان‌هایی را که مالک کاربران هستند نشان می‌دهد.
- **ChatRoomPermissions**: سطوح دسترسی برای کارهای اتاق گفتگو را تعریف می‌کند.
- **ChatRoom**: اتاق‌های گفتگو را با کاربران، وضعیت، و دسترسی‌ها مدیریت می‌کند.
- **MessageChat**: پیام‌های گفتگو را با فرستنده و زمان‌نگار ذخیره می‌کند.
- **Wallet**: مانده کیف‌پول کاربران را برای پرداخت‌ها پیگیری می‌کند.
- **Payment**: تراکنش‌های پرداخت را با یکپارچگی درگاه مدیریت می‌کند.

## پیکربندی

`settings.py` جنگو را به‌روزرسانی کنید:

```python
MIDDLEWARE = [
    ...
    'drfchelseru.middlewares.TakeUserSessionMiddlaware',
]

ASGI_APPLICATION = 'yourproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

DJANGO_CHELSERU = {
    'AUTH': {
        'AUTH_METHOD': 'OTP',
        'AUTH_SERVICE': 'rest_framework_simplejwt',
        'OPTIONS': {
            'OTP_LENGTH': 8,
            'OTP_EXPIRE_PER_MINUTES': 4,
            'OTP_SMS_TEMPLATE_ID': 5,
        }
    },
    'SMS': {
        'SMS_SERVICE': 'PARSIAN_WEBCO_IR',
        'SETTINGS': {
            'PARSIAN_WEBCO_IR_API_KEY': '',
            'MELI_PAYAMAK_COM_USERNAME': '',
            'MELI_PAYAMAK_COM_PASSWORD': '',
            'MELI_PAYAMAK_COM_FROM': '',
            'KAVENEGAR_COM_API_KEY': '',
            'KAVENEGAR_COM_FROM': '',
        },
        'TEMPLATES': {
            'T1': 1,
            'T2': 2,
            'T3': 3,
        }
    },
    'BANK': {
        'GATEWAY': 'PAYPING_IR',
        'SETTINGS': {
            'MERCHANT_ID': '',
            'CALLBACK_URL': '',
            'CURRENCY': 'IRT'
        }
    }
}
```

## نقاط پایانی API

- **POST /drfchelseru/message/send/**: فرستادن پیامک.

  - درخواست: `{ "mobile_number": "09211892425", "message_text": "Hello", "template_id": 1 }`
  - پاسخ: `{ "details": "The Message was sent correctly." }` (200 OK)

- **POST /drfchelseru/otp/send/**: درخواست کد OTP.

  - درخواست: `{ "mobile_number": "09211892425" }`
  - پاسخ: `{ "details": "The OTP code was sent correctly." }` (200 OK)

- **POST /drfchelseru/authenticate/**: تایید با OTP.

  - درخواست: `{ "mobile_number": "09211892425", "code": "652479", "group": 0 }`
  - پاسخ: `{ "access": "<access_token>", "refresh": "<refresh_token>" }` (200 OK)

- **GET /drfchelseru/sessions/**: فهرست نشست‌های کاربر (فقط کاربران تاییدشده).

  - سرآیندها: `Authorization: Bearer <access_token>`
  - پاسخ: فهرست نشست‌ها (200 OK)

- **POST /drfchelseru/payment/create/**: آغاز پرداخت.

  - درخواست: `{ "order_id": "123", "amount": 1000.0, "description": "Test payment", "callback_url": "http://example.com/callback", "mobile": "09211892425", "email": "user@example.com", "currency": "IRT" }`
  - پاسخ: `{ "details": { "gateway_url": "<url>", ... } }` (200 OK)

- **GET/POST /drfchelseru/payment/verify/**: تایید پرداخت.

  - جستجوی GET: `?Authority=<authority>&Status=OK`
  - بدنه POST: `{ "paymentCode": "<code>", "paymentRefId": "<refid>", ... }`
  - پاسخ: `{ "details": { "is_pay": 1, ... } }` (200 OK)

- **/drfchelseru/chat/chatrooms/**: CRUD برای اتاق‌های گفتگو (فقط کاربران تاییدشده).

  - درخواست POST: `{ "user": 2 }` (برای ساخت اتاق با شناسه کاربر 2)
  - سرآیندها: `Authorization: Bearer <access_token>`
  - پاسخ: جزئیات اتاق گفتگو (201 Created)

- **/drfchelseru/chat/messages/**: CRUD برای پیام‌های گفتگو (فقط کاربران تاییدشده).

  - درخواست POST: `{ "chat_room": 1, "text": "Hello" }`
  - جستجوی GET: `?chat_room=1`
  - سرآیندها: `Authorization: Bearer <access_token>`
  - پاسخ: جزئیات پیام یا فهرست (200 OK / 201 Created)

## بهره‌گیری از وب‌سوکت

- پیوستن به اتاق گفتگو برای پیام‌رسانی همزمان:

  ```bash
  wscat -c wss://<your-domain>/drfchelseru/chat/<chat_room_id>/?token=<jwt_token>
  ```
  - نمونه نشانه: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMDE5NTY3LCJpYXQiOjE3NTU4MzU1NjcsImp0aSI6IjhhYTY1Y2I3ZDhmMjRmMzliYjFmNDFkZmJiYjcyYmVmIiwidXNlcl9pZCI6Mzl9.mHmIjbTl3X1cd3Ky5HFCD6gy4kGxMVcActo9JXtT9JQ`
  - &lt;chat_room_id&gt; (مانند 17) را با شناسه اتاق دلخواه جایگزین کنید و نشانه JWT معتبر فراهم کنید.

## میان‌گیرها

- **TakeUserSessionMiddlaware**: داده‌های نشست کاربر (IP، عامل کاربر، دستگاه، مرورگر) را برای درخواست‌های HTTP ثبت می‌کند.
- **JWTAuthMiddleware**: اتصال‌های وب‌سوکت را با نشانه‌های JWT تایید می‌کند.

## بهره‌گیری

- به API در `http://<your-domain>/drfchelseru/` دسترسی یابید.
- به وب‌سوکت در `ws://<your-domain>/drfchelseru/chat/<chat_room_id>/?token=<jwt_token>` وصل شوید.
- پنل مدیر: ابرکاربر را با `python manage.py createsuperuser` بسازید.

## همکاری

1. مخزن را فورک کنید.
2. شاخه نو بسازید (`git checkout -b feature-branch`).
3. تغییرات را کامیت کنید (`git commit -m "Add feature"`).
4. به شاخه بفرستید (`git push origin feature-branch`).
5. درخواست کشیدن باز کنید.

## پروانه

MIT License