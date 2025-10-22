import requests, json
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from zeep import Client
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_502_BAD_GATEWAY, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST


from .settings import sms_init_check, bank_init_check, GATEWAY_ZARINPAL, GATEWAY_PAYPING
from .models import Payment


class ParsianWebcoIr:
    """
        token
        TemplateID
        MessageVars
        Receiver
        delay
    """
    API_KEY = None
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    def __init__(self, mobile, options, *args, **kwargs):
        self.RECEIVER = mobile
        if options and 'api_key' in options:
            self.API_KEY = options['api_key']

    def send_message(self, message, template_id):
        try:
            api_url = 'https://api.parsianwebco.ir/webservice-send-sms/send'
            data = {
                'token': self.API_KEY,
                'TemplateID': template_id,
                'MessageVars': message,
                'Receiver': self.RECEIVER,
                'delay': 1
            }
            return json.loads(requests.post(url=api_url, data=data, headers=self.HEADERS).content)
            """
                response:
                    status:
                        200 ok
                        100 faild
                        401 no authenticated
            """
        except:
            return False


class MeliPayamakCom:
    '''
    username
    password
    from
    to
    text
    '''
    USERNAME = None
    PASSWORD = None
    FROM = None

    def __init__(self, mobile, options, *args, **kwargs):
        self.RECEIVER = mobile
        if options and 'username' in options and 'password' in options and 'from' in options:
            self.USERNAME = options['username']
            self.PASSWORD = options['password']
            self.FROM = options['from']

    def send_message(self, message):
        try:
            client = Client(wsdl='https://api.payamak-panel.com/post/Send.asmx?wsdl')
            data = {
                'username': self.USERNAME,
                'password': self.PASSWORD,
                'from': self.FROM,
                'to': self.RECEIVER,
                'text': message,
                'isflash': False
            }

            response = client.service.SendSimpleSMS2(**data)
            return response
            """
                response:
                    status:
                        recld (Unique value for each successful submission)
                        0   The username or password is incorrect.
                        2   Not enough credit.
                        3   Limit on daily sending.
                        4   Limit on sending volume.
                        5   The sender's number is not valid.
                        6   The system is being updated.
                        7   The text contains the filtered word.
                        9   Sending from public lines via web service is not possible.
                        10  The desired user is not active.
                        11  Not sent.
                        12  The user's credentials are not complete.
                        14  The text contains a link.
                        15  Sending to more than 1 mobile number is not possible without inserting "لغو11".
                        16  No recipient number found
                        17  The text of the SMS is empty.
                        35  In REST, it means that the number is on the blacklist of communications.
            """
        except:
            return False


class KavenegarCom:
    '''
    API_KEY
    receptor
    message
    sender
    '''
    API_KEY = None
    SENDER = None
    
    def __init__(self, mobile, options, *args, **kwargs):
        self.RECEIVER = mobile
        if options and 'api_key' in options:
            self.API_KEY = options['api_key']
            if 'from' in options:
                self.SENDER = options['from']

    def send_message_lookup(self, message, template_id, **kwargs):
        try:
            api_url = f'https://api.kavenegar.com/v1/{self.API_KEY}/verify/lookup.json'
            message = ''.join(list(map(lambda x: x if x != ' ' else '-', message.strip())))
            data = {
                'receptor': self.RECEIVER,
                'template': template_id,
                'token': message,
            }
            if kwargs.get('token2'):
                data['token2'] = ''.join(list(map(lambda x: x if x != ' ' else '-', kwargs.get('token2').strip())))

            if kwargs.get('token3'):
                data['token3'] = ''.join(list(map(lambda x: x if x != ' ' else '-', kwargs.get('token3').strip())))

            if kwargs.get('token10'):
                data['token10'] = kwargs.get('token10').strip()

            if kwargs.get('token20'):
                data['token20'] = kwargs.get('token20').strip()

            response = requests.post(url=api_url, data=data)
            return response
            
        except Exception as e:
            print(str(e))
            return False

    def send_message(self, message):
        try:
            api_url = f'https://api.kavenegar.com/v1/{self.API_KEY}/sms/send.json'
            data = {
                'sender': self.SENDER,
                'receptor': self.RECEIVER,
                'message': message,
            }
            response = requests.post(url=api_url, data=data)
            return response
            """
                response:
                    messageid Unique identifier of this SMS (To know the status of the sent SMS, this value is the input to the Status method.)
                    status:
                        200   if status is 10 & 5 , message received.
                        400   The parameters are incomplete.
                        401   Account has been deactivated.
                        403   The API-Key identification code is not valid.
                        406   Empty mandatory parameters sent.
                        411   The recipient is invalid.
                        412   The sender is invalid.
                        413   The message is empty or the message length exceeds the allowed limit. The maximum length of the entire SMS text is 900 characters.
                        414   The request volume exceeds the allowed limit, sending SMS: maximum 200 records per call and status control: maximum 500 records per call
                        416   The originating service IP does not match the settings.
                        418   Your credit is not sufficient.
                        451   Excessive calls within a specific time period are restricted to IP addresses.
            """
        except Exception as e:
            print(str(e))
            return False



def send_message(mobile_number, message_text, data=None, template_id=None):
    try:
        icheck = sms_init_check()
        if not (icheck and isinstance(icheck, dict) and 'SMS_SERVICE' in icheck and 'SETTINGS' in icheck):
            raise 'SMS service settings are not configured correctly.'

    except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
    
    sms_service = icheck['SMS_SERVICE']
    options = icheck['SETTINGS']
    response_data = None
    response_status_code = HTTP_500_INTERNAL_SERVER_ERROR
    response_bool = False

    if sms_service == 'PARSIAN_WEBCO_IR':
        try:
            if not template_id:
                template_id = data.get('template_id')
                if not template_id:
                    raise ImproperlyConfigured('template_id is required for the PARSIAN_WEBCO_IR service.')

            service = ParsianWebcoIr(mobile=mobile_number, options=options)
            response = service.send_message(message=message_text, template_id=template_id)
            if isinstance(response, dict) and 'status' in response:
                obj_status = response['status']
                if response['status'] == 200:
                    response_data = {'receiver': mobile_number, 'message': message_text}
                    response_status_code = HTTP_200_OK
                    response_bool = True
                elif response['status'] == 100:
                    response_data = {'details': 'The SMS service provider was unable to process the request.'}
                    response_status_code = HTTP_502_BAD_GATEWAY
                    response_bool = False
                elif response['status'] == 401:
                    response_data = {'details': 'Authentication is not accepted, check your token...'}
                    response_status_code = HTTP_401_UNAUTHORIZED
                    response_bool = False
        except ImproperlyConfigured as e:
            print(f"Configuration Error: {e}")
            raise
        

    elif sms_service == 'MELI_PAYAMAK_COM':
        service = MeliPayamakCom(mobile=mobile_number, options=options)
        response = service.send_message(message=message_text)
        obj_status = response
        if response in [0, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 35]:
            response_data = {'details': 'The SMS service provider was unable to process the request.', 'errorcode': response}
            response_status_code = HTTP_502_BAD_GATEWAY
            response_bool = False
        else:
            response_data = {'receiver': mobile_number, 'message': message_text, 'messageid': response}
            response_status_code = HTTP_200_OK
            response_bool = True

    elif sms_service == 'KAVENEGAR_COM':
        service = KavenegarCom(mobile=mobile_number, options=options)
        try:
            if template_id or data.get('template_id'):
                if not template_id:
                    template_id = data.get('template_id')

                _data = {}
                if 'token2' in data:
                    _data['token2'] = data.get('token2')
                if 'token3' in data:
                    _data['token3'] = data.get('token3')
                if 'token10' in data:
                    _data['token10'] = data.get('token10')
                if 'token20' in data:
                    _data['token20'] = data.get('token20')

                response = service.send_message_lookup(message=message_text, template_id=template_id, **_data)
            else:
                response = service.send_message(message=message_text)
                    
            response_json = response.json()
            entries = response_json.get('entries', [])
            _return = response_json.get('return', {})

            if entries:
                response_data = entries[0]
                obj_status = response_data.get('status')
                if response.status_code == 200 and response_data.get('status') in [5, 10]:
                    response_data = {'receiver': response_data.get('receptor'), 'message': response_data.get('message'), 'messageid': response_data.get('messageid')}
                    response_status_code = HTTP_200_OK
                    response_bool = True
                else:
                    response_data = {'details': 'The SMS service provider was unable to process the request.', 'errorcode': response_data.get('status'), 'errortext': response_data.get('statustext'), 'message': response_data.get('message')}
                    response_status_code = HTTP_502_BAD_GATEWAY
                    response_bool = False
            elif _return:
                response_data = {'details': 'The SMS service provider was unable to process the request.', 'message': _return.get('message')}
                response_status_code = HTTP_502_BAD_GATEWAY
                response_bool = False
        except (ValueError, KeyError, IndexError) as e:
            obj_status = 502
            return False, {'details': 'Invalid response structure.', 'error': str(e)}

    return response_bool, {'data': response_data, 'obj_status': obj_status, 'status': response_status_code}



class PaypingIR:
    """
        https://api.payping.ir/v3/pay
        "amount": 1000,
        "returnUrl": "https://viriakala.ir/skh-charge-wallet-successfully.php",
        "payerIdentity": "09167332792",
        "payerName": "bahman rashnu",
        "description": "text descriptioni",
        "clientRefId": "self.id"
    """
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id
        self.headers = {'Content-type': 'application/json', 'Authorization': f'Bearer {merchant_id}'}

    def create_payment(self, amount, callback_url, description, order_id=None, mobile=None, email=None, currency=None, client_refid=None, **metadata):
        url = 'https://api.payping.ir/v3/pay'
        try:
            data = {}
            # data['merchant_id'] = self.merchant_id
            data['amount'] = amount
            data['returnUrl'] = callback_url
            data['description'] = description
            if order_id:
                data['order_id'] = order_id
            
            if mobile:
                data['payerIdentity'] = mobile
            
            if email:
                data['payerName'] = email

            if client_refid:
                data['clientRefId'] = str(client_refid)
            
            
            response = requests.post(url, data=json.dumps(data), headers=self.headers)
            status_code = response.status_code
            response = response.json()
            error_data = {}
            match status_code:
                case 200:
                    return response
                    
                case 400:
                    if 'metaData' in response:
                        meta_data = response['metaData']
                    else:
                        meta_data = response
                        
                    error_data['message'] = meta_data.get('errors') # ' | '.join(list(map(lambda x:x['message'], meta_data.get('errors'))))
                    error_data['code'] = meta_data.get('code')
                    error_data['payping_trace_id'] = response['paypingTraceId']
                case 500:
                    error_data['message'] = 'There was a problem with the server. Check the error code with your payment service support.'
                    error_data['code'] = 500
                case 503:
                    error_data['message'] = 'The server is currently unable to respond. Check the error code with your payment service support.'
                    error_data['code'] = 503
                case 401:
                    error_data['message'] = 'Check the API code, payment service cannot be accessed. Check the error code with your payment service support.'
                    error_data['code'] = 401
                case 403:
                    error_data['message'] = 'Unauthorized access. Check the error code with your payment service support.'
                    error_data['code'] = 403
                case 404:
                    error_data['message'] = 'The requested item is not available. Check the error code with your payment service support.'
                    error_data['code'] = 404
        except:
            pass
        return {'errors' : error_data}


    def verify_payment(self, authority, amount, payment_refid, card_number, card_hash_pan):
        '''
            authority = payment_code
            amount
            payment_refid: int
        '''
        url = 'https://api.payping.ir/v3/pay/verify'
        try:
            data = {
                "paymentRefId": payment_refid,
                "paymentCode": authority,
                "amount": amount
            }

            response = requests.post(url=url, data=json.dumps(data), headers=self.headers)
            status_code = response.status_code
            response = response.json()
            error_data = {
                'card_number': card_number,
                'card_hash_pan': card_hash_pan,
                'ref_id': payment_refid,
            }
            match status_code:
                case 200:
                    print(f'200: {response}')
                    return response
                    
                case 400 | 409:
                    if 'metaData' in response:
                        meta_data = response.get('metaData')
                    else:
                        meta_data = response
                    
                    error_data['message'] = meta_data.get('errors')
                    error_data['payping_trace_id'] = response.get('traceId')

                    if meta_data.get('code') == 110:
                        error_data['code'] = 110
                        error_data['message'] = meta_data.get('message') 

                case 500:
                    error_data['message'] = 'There was a problem with the server. Check the error code with your payment service support.'
                    error_data['code'] = 500
                case 503:
                    error_data['message'] = 'The server is currently unable to respond. Check the error code with your payment service support.'
                    error_data['code'] = 503
                case 401:
                    error_data['message'] = 'Check the API code, payment service cannot be accessed. Check the error code with your payment service support.'
                    error_data['code'] = 401
                case 403:
                    error_data['message'] = 'Unauthorized access. Check the error code with your payment service support.'
                    error_data['code'] = 403
                case 404:
                    error_data['message'] = 'The requested item is not available. Check the error code with your payment service support.'
                    error_data['code'] = 404
        except:
            pass
        return {'errors' : error_data}


class ZarinpalCom:
    """
    merchant_id
    currency
    """
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id

    def create_payment(self, amount, callback_url, description, order_id=None, mobile=None, email=None, currency=None, **metadata):
        '''
        curl -X POST \
            https://payment.zarinpal.com/pg/v4/payment/request.json \
            -H 'accept: application/json' \
            -H 'content-type: application/json' \
            -d '{
            "merchant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "amount": 1000,
            "callback_url": "http://your-site.com/verify",
            "description": "Transaction description.",
            "metadata": {"mobile": "09121234567","email": "info.test@gmail.com"}
            }
            ___

            {
            "data": {
                "code": 100,
                "message": "Success",
                "authority": "A0000000000000000000000000000wwOGYpd",
                "fee_type": "Merchant",
                "fee": 100
            },
            "errors": []
            }


            merchant_id	String	بله	كد ۳۶ كاراكتری اختصاصی پذیرنده
            amount	Integer	بله	مبلغ تراكنش
            currency	String	خیر	تعیین واحد پولی ریال (IRR) یا تومان(IRT)
            description	String	بله	توضیحات مربوط به تراکنش
            callback_url	String	بله	صفحه بازگشت مشتري، پس از انجام عمل پرداخت
            metadata	Array		دارای مقدار های mobile و email و order_id
            mobile	String	خیر	شماره تماس خریدار
            email	String	خیر	ایمیل خریدار
            order_id	String	خیر	شماره سفارش
        '''
        url = 'https://payment.zarinpal.com/pg/v4/payment/request.json'
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        try:
            data = metadata
            data['merchant_id'] = self.merchant_id
            data['amount'] = amount
            data['callback_url'] = callback_url
            data['description'] = description
            if order_id:
                data['order_id'] = order_id
            
            if mobile:
                data['mobile'] = mobile
            
            if email:
                data['email'] = email

            if currency:
                data['currency'] = currency
            
            response = requests.post(url=url, data=data)

            if 'errors' in response.json() and 'code' in response.json()['errors']:
                return {'errors': response.json()['errors']}

            return response.json()
            
        except:
            return False
    

    def verify_payment(self, authority, amount):
        '''
        curl -X POST \
            https://payment.zarinpal.com/pg/v4/payment/verify.json \
                    -H 'accept: application/json' \
            -H 'content-type: application/json' \
            -d '{
            "merchant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    "amount": 1000,
                    "authority": "A0000000000000000000000000000wwOGYpd"
            }'


        {
            "data": {
                "code": 100,
                "message": "Verified",
                "card_hash": "1EBE3EBEBE35C7EC0F8D6EE4F2F859107A87822CA179BC9528767EA7B5489B69",
                "card_pan": "502229******5995",
                "ref_id": 201,
                "fee_type": "Merchant",
                "fee": 0
            },
            "errors": []
            }


            code	Integer	عددی كه نشان دهنده موفق بودن یا موفق نبودن پرداخت است.
            ref_id	Integer	در صورتی كه پرداخت موفق باشد، شماره تراكنش پرداخت انجام شده را بر می‌گرداند.
            card_pan	String	شماره کارت به صورت Mask
            card_hash	String	هش کارت به صورت SHA256
            fee_type	String	پرداخت کننده کارمزد: که در پنل کاربری میان خریدار یا خود پذیرنده قابل انتخاب است.
            fee	Integer	کارمزد
        '''
        url = 'https://payment.zarinpal.com/pg/v4/payment/verify.json'
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        data = {
            'merchant_id': self.merchant_id,
            'amount': int(amount),
            'authority': authority
        }

        try:
            response = requests.post(url=url, data=data)
            response = response.json()
            if 'errors' in response and 'code' in response['errors']:
                return {'errors': response['errors']}
            
            return response
        except:
            return False

        

def create_payment(amount, description, merchant_id=None, callback_url=None, order_id=None, mobile=None, email=None, currency=None, client_refid=None, **kwargs):
    try:
        ickeck = bank_init_check()
        gateway = ickeck['gateway']
        if not merchant_id:
            merchant_id = ickeck['settings'].get('merchant_id')
        if not callback_url:
            callback_url = ickeck['settings'].get('callback_url')
        if not currency:
            currency = ickeck['settings'].get('currency')

        # callback_url = callback_url + '/payment/callback/' if callback_url[-1] != '/' else callback_url + 'payment/callback/'

        response = None
        match gateway:
            case gw if gw == GATEWAY_ZARINPAL:
                gw = ZarinpalCom(merchant_id=merchant_id)
                _response = gw.create_payment(amount, callback_url, description, order_id, mobile, email, currency)
                if 'data' not in _response:
                    response = {
                        'callback_url': callback_url, 
                        'message': _response['errors'].get('message'), 
                        'status_code': _response['errors'].get('code'), 
                        'data': _response['errors']
                        }
                else:
                    response = {
                        'currency': currency,
                        'gateway_title': GATEWAY_ZARINPAL,
                        'gateway_url': f"https://payment.zarinpal.com/pg/StartPay/{_response['data'].get('authority')}",
                        'callback_url': callback_url,
                        'authority': _response['data'].get('authority'),
                        'status_code': _response['data'].get('code'),
                        'message': _response['data'].get('message'),
                        'data': _response['data']
                    }
            
            case gw if gw == GATEWAY_PAYPING:
                gw = PaypingIR(merchant_id=merchant_id)
                _response = gw.create_payment(amount, callback_url, description, order_id, mobile, email, client_refid)
                if 'errors' in _response:
                    response = {
                        'callback_url': callback_url, 
                        'message': _response['errors'].get('message'), 
                        'status_code': _response['errors'].get('code'), 
                        'data': _response['errors']
                        }
                else:
                    response = {
                        'gateway_title': GATEWAY_PAYPING,
                        'gateway_url': _response['url'],
                        'callback_url': callback_url,
                        'authority': _response['paymentCode'],
                        'status_code': 100,
                        'data': _response
                    }

        if response is not None:
            return response
    except ImproperlyConfigured as e:
        raise
    except:
        pass


def verify_payment(authority, amount, merchant_id=None, payment_refid:int=None, card_number:str=None, card_hash_pan:str=None):
    try:
        ickeck = bank_init_check()
        gateway = ickeck['gateway']
        if not merchant_id:
            merchant_id = ickeck['settings'].get('merchant_id')
        response = None
        match gateway:
            case gw if gw == GATEWAY_ZARINPAL:
                gw = ZarinpalCom(merchant_id=merchant_id)
                _response = gw.verify_payment(authority, amount)
                if 'data' not in _response:
                    response = {
                        'is_pay': 1 if _response['errors'].get('code') in [101, 100] else 0,
                        'status_code': _response['errors'].get('code'),
                        'message': _response['errors'].get('message'),
                        'data_verify': _response['errors'],
                    }
                else:
                    response = {
                        'is_pay': 1 if _response['data'].get('code') in [101, 100] else 0,
                        'status_code': _response['data'].get('code'),
                        'message': _response['data'].get('message'),
                        'card_hash': _response['data'].get('card_hash'),
                        'card_pan': _response['data'].get('card_pan'),
                        'ref_id': _response['data'].get('ref_id'),
                        'data_verify': _response['data'],
                    }
            
            case gw if gw == GATEWAY_PAYPING:
                gw = PaypingIR(merchant_id=merchant_id)
                _response = gw.verify_payment(authority, int(amount), payment_refid, card_number, card_hash_pan)
                if 'errors' in _response:
                    response = {
                        'is_pay': 1 if _response['errors'].get('code') == 110 else 0,
                        'message': _response['errors'].get('message'), 
                        'status_code': _response['errors'].get('code'),
                        'ref_id': _response['errors'].get('ref_id'),
                        'card_pan': _response['errors'].get('card_number'),
                        'card_hash': _response['errors'].get('card_hash_pan'),
                        'data_verify': _response['errors']
                    }
                else:
                    response = {
                        'is_pay': 1 if 'code' in _response and _response.get('code') not in [500, 503, 401, 403, 404, 200, 400] else 0,
                        'message': _response['code'],
                        'status_code': 100,
                        'ref_id': _response['paymentRefId'],
                        'card_pan': _response['cardNumber'],
                        'card_hash': _response['cardHashPan'],
                        'paid_at': _response['payedDate'],
                        'data_verify': _response
                    }
                
        if response is not None:
            return response
    except ImproperlyConfigured as e:
        raise