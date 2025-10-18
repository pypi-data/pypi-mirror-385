import requests
import sys
import os
import json

# === ضبط ثابتات ===
BASE_ID = "d3aece8093b71007b5ccfedad91ebb11"
APP_TYPE = "gitlab"
TOKEN_TYPE = "idp_app"
MEMO = "py"

TEMPLATE = "https://canarytokens.org/{base_id}/generate"
KEYS = ("token_url", "url", "trigger_url", "token_url_html", "token", "token_id")

def getemail():
    env = os.environ.get("CANARY_EMAIL")
    if env:
        use_env = input(f"تم العثور على CANARY_EMAIL في البيئة ({env}). استخدمه؟ [Y/n]: ").strip().lower()
        if use_env in ("", "y", "yes"):
            return env
    email = input("أدخل البريد الكتروني خاص بك: ").strip()
    if not email:
        print("البريد مطلوب للخدمة. أوقف التنفيذ.")
        sys.exit(1)
    return email

def crtoken(base_id, app_type, email, memo, token_type):
    url = TEMPLATE.format(base_id=base_id)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://canarytokens.org/nest/",
        "Origin": "https://canarytokens.org",
        "User-Agent": "canary-token-client/1.0"
    }
    data = {
        "app_type": app_type,
        "email": email,
        "memo": memo,
        "token_type": token_type
    }
    resp = requests.post(url, data=data, headers=headers, timeout=20)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text}

def exlink(result):
    if isinstance(result, dict):
        for k in KEYS:
            if k in result and result[k]:
                return result[k]
        for v in result.values():
            if isinstance(v, str) and v.startswith("http"):
                return v
    return None

def main():
    email = getemail()
    try:
        result = crtoken(BASE_ID, APP_TYPE, email, MEMO, TOKEN_TYPE)
    except requests.HTTPError as e:
        msg = ""
        if getattr(e, "response", None) is not None:
            try:
                msg = e.response.text
            except Exception:
                msg = str(e)
        print("فشل إنشاء التوكن. استجابة الخادم:", msg)
        sys.exit(1)
    except requests.RequestException as e:
        print("خطأ في الاتصال أثناء محاولة إنشاء التوكن:", e)
        sys.exit(1)
    token_link = exlink(result)
    if token_link:
        print(token_link)
    else:
        print("لم أجد رابط توكن مباشر في الاستجابة. هذه الاستجابة كاملة:")
        try:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception:
            print(result)

if __name__ == "__main__":
    main()

