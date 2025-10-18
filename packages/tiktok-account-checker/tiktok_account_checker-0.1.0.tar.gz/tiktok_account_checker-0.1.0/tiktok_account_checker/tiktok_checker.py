import requests
import secrets
import random
import os
import binascii
import uuid
import SignerPy
from time import sleep
import time
import re
from MedoSigner import Argus, Gorgon, md5, Ladon
from urllib.parse import urlencode

# --- Helper Functions (from the original script) ---

def generate_user_agent():
    """Generates a realistic User-Agent for TikTok requests."""
    app_pkg = "com.zhiliaoapp.musically.go"
    version_code = str(random.randint(360000, 380000))
    os_version = f"Android {random.randint(6, 13)}.{random.randint(0, 5)}.{random.randint(0, 5)}"
    lang_country = random.choice(["ar_IQ", "en_US", "tr_TR", "fr_FR"])
    device_model = random.choice(["ASUS_I003DD", "SM-G973F", "Redmi_Note_8", "Pixel_6", "Infinix_X682B"])
    build_id = f"Build/{random.choice(['N2G48H', 'QP1A.190711.020', 'RKQ1.210710.001'])}"
    tt_ok = f"tt-ok/{random.randint(3,4)}.{random.randint(10,15)}.{random.randint(10,30)}.{random.randint(10,40)}-ul"
    return f"{app_pkg}/{version_code} (Linux; U; {os_version}; {lang_country}; {device_model}; {build_id};{tt_ok})"

def get_level(username):
    """Fetches the supporter level for a given TikTok username."""
    username = username.strip()
    headers_info = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Android 10; Pixel 3 Build/QKQ1.200308.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6394.70 Mobile Safari/537.36 trill_350402 JsSdk/1.0 NetType/MOBILE Channel/googleplay AppName/trill app_version/35.3.1 ByteLocale/en ByteFullLocale/en Region/IN AppId/1180 Spark/1.5.9.1 AppVersion/35.3.1 BytedanceWebview/d8a21c6"
    }
    try:
        tikinfo = requests.get(f'https://www.tiktok.com/@{username}', headers=headers_info, timeout=10).text
        user_info = tikinfo.split('webapp.user-detail"')[1].split('"RecommenUserList"')[0]
        user_id = user_info.split('id":"')[1].split('",')[0]
    except Exception:
        return None  # Return None if user ID extraction fails

    iid = str(random.randint(1, 10**19))
    device_id = str(random.randint(1, 10**19))
    openudid = binascii.hexlify(os.urandom(8)).decode()
    ts = str(int(time.time()))
    cdid = str(uuid.uuid4())
    
    params = urlencode({
        "request_from": "profile_card_v2", "request_from_scene": 1, "target_uid": user_id,
        "iid": iid, "device_id": device_id, "ac": "wifi", "channel": "googleplay",
        "aid": 1233, "app_name": "musical_ly", "version_code": "300102",
        "version_name": "30.1.2", "device_platform": "android", "os": "android",
        "ab_version": "30.1.2", "ssmix": "a", "device_type": "RMX3511",
        "device_brand": "realme", "language": "ar", "os_api": 33, "os_version": 13,
        "openudid": openudid, "manifest_version_code": "2023001020",
        "resolution": "1080*2236", "dpi": 360, "update_version_code": "2023001020",
        "_rticket": f"{int(time.time() * 1000)}", "current_region": "IQ", "app_type": "normal",
        "sys_region": "IQ", "mcc_mnc": "41805", "timezone_name": "Asia/Baghdad",
        "carrier_region_v2": 418, "residence": "IQ", "app_language": "ar",
        "carrier_region": "IQ", "ac2": "wifi", "uoo": 0, "op_region": "IQ",
        "timezone_offset": 10800, "build_number": "30.1.2", "host_abi": "arm64-v8a",
        "locale": "ar", "region": "IQ", "ts": ts, "cdid": cdid,
        "webcast_sdk_version": 2920, "webcast_language": "ar", "webcast_locale": "ar_IQ"
    })

    url = f"https://webcast16-normal-no1a.tiktokv.eu/webcast/user/?{params}"
    
    payload = b""
    unix = int(time.time())
    x_ss_stub = md5(payload).hexdigest().upper()
    
    gorgon = Gorgon.get_value(params=url.split("?")[1], data=None, unix=unix)
    
    headers = {
        "x-gorgon": gorgon["X-Gorgon"],
        "x-khronos": gorgon["X-Khronos"],
        "user-agent": "com.zhiliaoapp.musically/2023001020 (Linux; U; Android 13; ar; RMX3511; Build/TP1A.220624.014; Cronet/TTNetVersion:06d6a583 2023-04-17 QuicVersion:d298137e 2023-02-13)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        level_match = re.search(r'"default_pattern":"(.*?)"', response.text)
        if level_match:
            level_str = re.search(r"\d+", level_match.group(1))
            if level_str:
                return int(level_str.group())
        return None # Return None if level is not found
    except Exception:
        return None # Return None on request failure

# --- Main Function ---

def check_tiktok_account(username):
    """
    Checks a TikTok account for binding status (email, mobile, oauth, passkey) and supporter level.

    Args:
        username (str): The TikTok username to check.

    Returns:
        dict: A dictionary containing the account information or an error message.
              Example success: {'status': 'success', 'username': 'user', 'has_email': True, ...}
              Example error: {'status': 'error', 'message': 'Error description'}
    """
    username = username.strip()
    secret = secrets.token_hex(16)
    user_agent = generate_user_agent()

    # Step 1: Find account and get token
    url_find = "https://api16-normal-c-alisg.tiktokv.com/passport/find_account/tiktok_username/"
    params_find = {
        "request_tag_from": "h5", "os_api": "25", "device_type": "ASUS_I003DD",
        "ssmix": "a", "manifest_version_code": "370402", "dpi": "240",
        "region": "IQ", "carrier_region": "IQ", "app_name": "musically_go",
        "version_name": "37.4.2", "timezone_offset": "-21600", "ts": str(int(time.time())),
        "ab_version": "37.4.2", "ac2": "wifi", "ac": "wifi", "app_type": "normal",
        "host_abi": "x86_64", "channel": "googleplay", "update_version_code": "370402",
        "_rticket": f"{int(time.time() * 1000)}", "device_platform": "android",
        "iid": str(random.randint(1, 10**19)), "build_number": "37.4.2", "locale": "ar",
        "op_region": "IQ", "version_code": "370402", "timezone_name": "America/Chicago",
        "cdid": str(uuid.uuid4()), "openudid": binascii.hexlify(os.urandom(8)).decode(),
        "device_id": str(random.randint(1, 10**19)), "sys_region": "IQ", "app_language": "ar",
        "resolution": "720*1280", "device_brand": "Asus", "language": "ar",
        "os_version": "7.1.2", "aid": "1340"
    }
    payload_find = {'username': username, 'mix_mode': "1"}
    cookies_find = {"passport_csrf_token": secret, "passport_csrf_token_default": secret}

    try:
        sign_find = SignerPy.sign(params=params_find, cookie=cookies_find, payload=payload_find)
        headers_find = {
            'User-Agent': user_agent,
            'x-ss-stub': sign_find["x-ss-stub"], 'x-ladon': sign_find["x-ladon"],
            'x-gorgon': sign_find["x-gorgon"], 'x-khronos': sign_find["x-khronos"],
            'x-argus': sign_find["x-argus"],
        }
        resp_find = requests.post(url_find, params=params_find, data=payload_find, headers=headers_find, cookies=cookies_find)
        resp_find.raise_for_status()
        resp_json = resp_find.json()
        if resp_json.get("message") != "success":
            return {'status': 'error', 'message': f'Could not find user: {resp_json.get("data", {}).get("description", "Unknown error")}'}
        token = resp_json["data"]["token"]
    except Exception as e:
        return {'status': 'error', 'message': f"حدث خطأ أثناء طلب التوكن: {e}"}

    # Step 2: Get available ways
    url_ways = "https://api16-normal-c-alisg.tiktokv.com/passport/auth/available_ways/"
    params_ways = params_find.copy()
    params_ways["not_login_ticket"] = token
    cookies_ways = {"passport_csrf_token": secret, "passport_csrf_token_default": secret}
    
    try:
        sign_ways = SignerPy.sign(params=params_ways, cookie=cookies_ways)
        headers_ways = {
            'User-Agent': user_agent,
            'x-tt-passport-csrf-token': secret,
            'x-ladon': sign_ways["x-ladon"], 'x-gorgon': sign_ways["x-gorgon"],
            'x-khronos': sign_ways["x-khronos"], 'x-argus': sign_ways["x-argus"],
        }
        resp_ways = requests.post(url_ways, params=params_ways, headers=headers_ways, cookies=cookies_ways)
        resp_ways.raise_for_status()
        response_json = resp_ways.json()
        
        # Step 3: Get supporter level
        level = get_level(username)

        # Step 4: Combine and return results
        data = response_json.get("data", {})
        return {
            "status": "success",
            "username": username,
            "has_email": data.get("has_email", False),
            "has_mobile": data.get("has_mobile", False),
            "has_oauth": data.get("has_oauth", False),
            "has_passkey": data.get("has_passkey", False),
            "supporter_level": level
        }
    except Exception as e:
        return {'status': 'error', 'message': f"حدث خطأ أثناء طلب available_ways: {e}"}

# --- Example Usage (this part will only run if the script is executed directly) ---
if __name__ == '__main__':
    # This block is for testing the library directly.
    # It will not run when you import it into another script.
    target_username = input("Enter TikTok username to check: ")
    result = check_tiktok_account(target_username)

    if result['status'] == 'success':
        print("\n--- Account Info ---")
        print(f"الحساب • @{result['username']}")
        
        passkey_status = "يوجد ربط مخفي داخل الحساب ⚠️" if result['has_passkey'] else "لا يوجد ربط مخفي داخل الحساب 🟢"
        print(passkey_status)
        
        oauth_status = "يوجد ربط خارجي داخل الحساب ⚠️" if result['has_oauth'] else "لا يوجد ربط خارجي داخل الحساب 🟢"
        print(oauth_status)
        
        phone_icon = "✔️" if result['has_mobile'] else "❌"
        email_icon = "✔️" if result['has_email'] else "❌"
        level_text = result['supporter_level'] if result['supporter_level'] is not None else "غير متاح"
        
        print(f"\nالرقم ({phone_icon}) - الايميل ({email_icon}) - مستوى الدعم ({level_text})")
    else:
        print(f"\nAn error occurred: {result['message']}")
