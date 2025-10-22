from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_502_BAD_GATEWAY, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from rest_framework.exceptions import NotFound, ValidationError
from django.contrib.auth.models import User as UserDefault

from .services import send_message, create_payment, verify_payment
from .settings import sms_init_check, auth_init_check
from .validators import mobile_number as mobile_validator
from .serializers import MessageSerializer, OTPCodeSerializer, SessionSerializer, ChatRoomSerializer, MessageChatSerializer, PaymentSerializer
from .models import User, ChatRoom
from django.utils.timezone import now, timedelta
from django.db import transaction, IntegrityError, OperationalError

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import traceback
import time
import logging


logger = logging.getLogger(__name__)


class MessageSend(APIView):
    permission_classes = (AllowAny, )
    serializer_class = MessageSerializer

    def post(self, request):
        """
        prams:
            mobile_number:      str (len: 11)  (exp: 09211892425)
            message_text:       str (len: 290)
            template_id:        int (required for PARSIAN_WEBCO_IR)

        response:
            HTTP_400_BAD_REQUEST            {'error': [params requirements and validations]}
            HTTP_500_INTERNAL_SERVER_ERROR  {'error': 'contact the support..'}
            HTTP_200_OK                     {'details': 'The Message was sent correctly.'}
            HTTP_502_BAD_GATEWAY            {'details': 'The SMS service provider was unable to process the request.'}
            HTTP_401_UNAUTHORIZED           {'details': 'Authentication is not accepted...'}
        """
        try:
            serializer = self.serializer_class(data=request.data)

            # 1. Validate data using serializer
            if not serializer.is_valid():
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

            # 2. Extract validated data and create the message object
            mobile_number = serializer.validated_data.get('mobile_number')
            message_text = serializer.validated_data.get('message_text')
            
            # Use serializer.save() to create the object instance initially
            obj = serializer.save() # -1 as a temporary status

            response = send_message(mobile_number, message_text, request.data)

            response_data = response[1].get('data')
            obj_status = response[1].get('obj_status')
            response_status_code = response[1].get('status')

            # Save the updated object once at the end
            obj.status = obj_status
            obj.save()
            
            # Return the response with updated data and status
            return Response(response_data, status=response_status_code)

        except Exception as e:
            # Catch all unexpected errors and return a generic 500
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An error occurred, please contact support.'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class OTPCodeSend(APIView):
    permission_classes = (AllowAny,)
    # Use a separate serializer for the request data validation
    serializer_class = OTPCodeSerializer 
    model = OTPCodeSerializer.Meta.model

    def post(self, request):
        """
        Sends an OTP code to the provided mobile number.
        """
        # 1. Validate the request data using a serializer.
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        mobile_number = serializer.validated_data['mobile_number']
        
        try:
            # 2. Get authentication settings.
            icheck = auth_init_check()
            if not (icheck and icheck.get('AUTH_METHOD') == 'OTP'):
                return Response({'error': 'Authentication method is not configured correctly.'}, 
                                status=HTTP_500_INTERNAL_SERVER_ERROR)
            
            otp_exp_time = icheck['OPTIONS']['exp_time']
            template_id = icheck['OPTIONS'].get('default_sms_template')
            
            # 3. Use an atomic transaction to prevent race conditions.
            with transaction.atomic():
                # Attempt to get an existing OTP code and lock the row for the duration of the transaction.
                obj = self.model.objects.filter(mobile_number=mobile_number).first()

                if obj:
                    # An OTP code already exists. Check if it's expired.
                    expiration_time = obj.created_at + timedelta(minutes=otp_exp_time)
                    if now() < expiration_time:
                        # The existing code is still valid. Tell the user to wait.
                        remaining_seconds = (expiration_time - now()).total_seconds()
                        return Response({
                            'details': f'An OTP code has already been sent. Please wait {int(remaining_seconds)} seconds before trying again.'
                        }, status=HTTP_409_CONFLICT)
                    else:
                        # The code has expired. Delete it.
                        obj.delete()

            # 4. Create a new OTP code instance.
            new_otp_obj = self.model.objects.create(mobile_number=mobile_number)

            # 5. Send the message using a dedicated service function.
            # Assuming 'send_message' returns a tuple: (success_bool, response_dict)
            success, sms_response = send_message(
                mobile_number=new_otp_obj.mobile_number, 
                message_text=new_otp_obj.code, 
                data=request.data,
                template_id=template_id
            )
            
            if success:
                # If the SMS was sent successfully, return success response.
                return Response({'details': 'The OTP code was sent correctly.'}, status=HTTP_200_OK)
            else:
                # If the SMS sending failed, delete the newly created OTP object
                # and return the error from the service.
                new_otp_obj.delete()
                return Response(sms_response, status=sms_response.get('status', HTTP_500_INTERNAL_SERVER_ERROR))

        except Exception as e:
            # Catch and log unexpected errors for debugging.
            new_otp_obj.delete()
            print(f"An unexpected error occurred: {e}")
            return Response({'error': 'An internal server error occurred.'},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)


class Authentication(APIView):
    permission_classes = (AllowAny, )
    serializer_class = OTPCodeSerializer
    model = serializer_class.Meta.model

    def post(self, request):
        """
        prams:
            mobile_number:   str (len: 11)     (exp: 09211892425)
            code: str (len: otp_code_length()) (exp: 652479)
            group: str (len: 7)         (exp: service)

        response:
            HTTP_204_NO_CONTENT             {'error': [params requirements and validations]}
            HTTP_500_INTERNAL_SERVER_ERROR  {'error': 'contact the support..'}
            HTTP_200_OK                     {'access': '', 'refresh': ''}
        """
        try:
            if 'mobile_number' not in request.data:
                return Response({'error': 'mobile_number is required.'}, status=HTTP_204_NO_CONTENT)
            mobile_number = request.data['mobile_number']
            if not mobile_number:
                return Response({'error': 'mobile_number may not be blank.'}, status=HTTP_204_NO_CONTENT)
            mobile_number_isvalid = mobile_validator(mobile_number)
            if mobile_number_isvalid != True:
                return Response({'error': mobile_number_isvalid}, status=HTTP_204_NO_CONTENT)
            if 'code' not in request.data:
                return Response({'error': 'code is required.'}, status=HTTP_204_NO_CONTENT)
            
            icheck = auth_init_check()
            if icheck and isinstance(icheck, dict) and 'AUTH_SERVICE' in icheck and 'AUTH_METHOD' in icheck:
                otp_code = request.data['code']
                otp = self.model.objects.filter(mobile_number=mobile_number).filter(code=otp_code).first()
                if not otp:
                    return Response({'error': 'The code sent to this mobile number was not found.'}, status=HTTP_401_UNAUTHORIZED)
                
                if otp.check_code():
                    user = None
                    # login / signup
                    try:
                        group = int(request.data.get('group'), 0)
                    except (ValueError, TypeError):
                        group = 0

                    try:
                        with transaction.atomic():
                            user, created = User.objects.get_or_create(mobile=mobile_number, group=group)
                    
                    except IntegrityError as e:
                        logger.warning("IntegrityError on get_or_create for mobile=%s, group=%s: %s", mobile_number, group, e)
                        time.sleep(0.05)
                        try:
                            user = User.objects.get(mobile=mobile_number, group=group)
                            created = False
                        except User.DoesNotExist:
                            logger.error("After IntegrityError, user still not exists for mobile=%s. Trace: %s", mobile_number, traceback.format_exc())
                            return Response({'error': 'Server error while creating user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    except OperationalError as e:
                        logger.error("OperationalError when accessing DB for mobile=%s: %s\n%s", mobile_number, e, traceback.format_exc())
                        return Response({'error': 'Database operational error, try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    except Exception as e:
                        logger.exception("Unexpected error in user get_or_create for mobile=%s: %s", mobile_number, e)
                        return Response({'error': 'An internal error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    

                    # user, created = User.objects.get_or_create(mobile=mobile_number, group=group)
                    if user:
                        auth_method = icheck['AUTH_METHOD']
                        auth_service = icheck['AUTH_SERVICE']
                        if auth_method == 'OTP':
                            match auth_service:
                                case 'rest_framework_simplejwt':
                                    from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, BlacklistedToken
                                    access_token = AccessToken.for_user(user=user.user)
                                    refresh_token = RefreshToken.for_user(user=user.user)
                                    return Response({'access': str(access_token), 'refresh': str(refresh_token)}, status=HTTP_200_OK)
                        else:
                            try:
                                raise ImproperlyConfigured('Authentication configurations in DJANGO_CHELSERU are not done correctly, specify AUTH_METHOD and AUTH_SERVICE.')
                            except ImproperlyConfigured as e:
                                print(f"Configuration Error: {e}")
                                raise   
        except AssertionError as e:
            return Response({'error': str(e)}, status=HTTP_204_NO_CONTENT)
        except Exception:
            logger.exception("Error while creating tokens for user (mobile=%s). user object: %r", mobile_number, user)
            return Response({'error': 'Token generation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return Response({'error': 'An error occurred while generating or sending the otpcode, please contact the www.chelseru.com support team.'}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class SessionList(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = SessionSerializer
    queryset = serializer_class.Meta.model.objects.all()


class ChatRoomViewSet(ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    model = serializer_class.Meta.model

    def get_queryset(self):
        return self.model.objects.filter(user_1=self.request.user) | self.model.objects.filter(user_2=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        user_id = self.request.data.get('user', None)
        user_2 = UserDefault.objects.filter(id=user_id).first()
        if not user_2:
            raise NotFound("کاربر مورد نظر با آی دی فرستاده شده یافت نشد.")
                
        chat_room = serializer.save(user_1=user, user_2=user_2)
    

class MessageViewSet(ModelViewSet):
    serializer_class = MessageChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = self.serializer_class.Meta.model.objects.all()
        chat_room_id = self.request.query_params.get('chat_room')
        if chat_room_id:
            queryset = queryset.filter(chat_room_id=chat_room_id)
        return queryset

    def perform_create(self, serializer):
        chat_room_id = self.request.data.get('chat_room')
        if not chat_room_id:
            raise ValidationError("فیلد chat_room اجباریه.")

        try:
            chat = ChatRoom.objects.get(id=chat_room_id)
        except ChatRoom.DoesNotExist:
            raise NotFound("چت‌روم پیدا نشد.")

        message = serializer.save(sender=self.request.user, chat_room=chat)
        chat = message.chat_room
        chat.save()



class PaymentCreate(APIView):
    permission_classes = (AllowAny, )
    serializer_class = PaymentSerializer
    model = serializer_class.Meta.model
    
    def post(self, request):
        '''
        order_id        str
        amount          float
        description     str
        callback_url    str
        mobile          str
        email           str
        currency        str
        '''

        try:
            # assert 'order_id' in self.request.data, 'order_id is required.'
            assert 'amount' in self.request.data, 'amount is required.'
            # assert 'description' in self.request.data, 'description is required.'

            data = {
                # 'order_id': self.request.data['order_id'],
                'amount': self.request.data['amount'],
                'description': 'django-chelseru: new order',
                'mobile': '',
                'email': '',
            }

            if self.request.user.mobile_drf_chelseru.mobile:
                data['mobile'] = self.request.user.mobile_drf_chelseru.mobile
            
            if self.request.user.email:
                data['email'] = self.request.user.email
            
            obj = self.model.objects.create(user=request.user, amount=data['amount'], description=data['description'], mobile=data['mobile'], email=data['email'])
            data['client_refid'] = obj.user.id
            
            if 'callback_url' in request.data:
                data['callback_url'] = request.data['callback_url']
                obj.callback_url = data['callback_url']

            if 'order_id' in self.request.data:
                data['order_id'] = self.request.data['order_id']
                obj.order_id = data['order_id']
            
            if 'description' in self.request.data:
                data['description'] = self.request.data['description']
                obj.description = data['description']

            if 'mobile' in self.request.data:
                data['mobile'] = self.request.data['mobile']
                obj.mobile = data['mobile']

            if 'email' in self.request.data:
                data['email'] = self.request.data['email']
                obj.email = data['email']

            if 'currency' in self.request.data:
                data['currency'] = self.request.data['currency']
                obj.currency = data['currency']
            
            obj.save()
            response = create_payment(**data)
            obj.set_request_data(**response)

            return Response({'details': response}, status=HTTP_200_OK)
        except AssertionError as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)


class PaymentCallback(APIView):
    permission_classes = (AllowAny, )
    serializer_class = PaymentSerializer
    model = serializer_class.Meta.model
    
    def get(self, request):
        '''
        query params:
            Authority
            Status (OK, NOK)
        '''
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        if status  and authority:
            # and status == 'OK'
            try:
                obj = self.model.objects.get(authority=authority)
                response = verify_payment(authority=authority, amount=obj.amount)
                if response is None:
                    return Response({'error': 'callback data is none, please check your gateway settings.'}, status=HTTP_400_BAD_REQUEST)
                
                obj.set_verify_data(**response)
                return Response({'details': response}, status=HTTP_200_OK)
            except self.model.DoesNotExist:
                return Response({'error': 'payment not found.'}, status=HTTP_404_NOT_FOUND)

        return Response({'error': 'The transaction was unsuccessful or canceled.'}, status=HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        # print(request.data)
        if 'paymentCode' in request.data:
            authority = request.POST.get('paymentCode')
        else:
            authority = request.POST.get('authority')

        if 'paymentRefId' in request.data:
            payment_refid = request.POST.get('paymentRefId')
        else:
            payment_refid = None
        
        if 'gatewayAmount' in request.data:
            gateway_amount = request.POST.get('gatewayAmount')

        if 'cardNumber' in request.data:
            card_number = request.POST.get('cardNumber')
        else:
            card_number = None
        
        if 'cardHashPan' in request.data:
            card_hash_pan = request.POST.get('cardHashPan')
        else:
            card_hash_pan = None

        try:
            obj = self.model.objects.get(authority=authority)
            response = verify_payment(authority=authority, amount=obj.amount, payment_refid=payment_refid, card_number=card_number, card_hash_pan=card_hash_pan)
            
            if response is None:
                return Response({'error': 'callback data is none, please check your gateway settings.'}, status=HTTP_400_BAD_REQUEST)
            
            obj.set_verify_data(**response)
            return Response({'details': response}, status=HTTP_200_OK)
        
        except self.model.DoesNotExist:
            return Response({'error': 'payment not found.'}, status=HTTP_404_NOT_FOUND)
        return Response({})