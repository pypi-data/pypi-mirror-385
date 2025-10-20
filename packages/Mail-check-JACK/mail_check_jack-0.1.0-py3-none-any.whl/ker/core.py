import re
import urllib.parse
import json
import time
import requests

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def cemail(email: str) -> tuple[int | None, str]:
    if not EMAIL_RE.match(email):
        raise ValueError("صيغة البريد الإلكتروني غير صحيحة.")
    base = "https://www.scanmylinks.com/hibp-proxy.php"
    params = {
        "email": email,
        "_t": str(int(time.time() * 1000))
    }
    url = base + "?" + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/json",
        "Referer": "https://www.scanmylinks.com/",
        "User-Agent": "python-requests/1.0 (hibp_checker)",
        "Cache-Control": "no-cache, no-store",
        "Pragma": "no-cache"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        return r.status_code, r.text
    except requests.exceptions.RequestException as exc:
        return None, str(exc)

def esult(response_text: str):
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        print("الرد ليس JSON صالح")
        print(response_text)
        return
    print("\nالنتيجة (بالعربية):")
    ok = data.get("success")
    print("النجاح:" , "نعم" if ok else "لا")
    print("البريد الإلكتروني:", data.get("email"))
    print("إجمالي الاختراقات:", data.get("total_breaches"))
    print("محاولات:", data.get("attempts"))
    breaches = data.get("breaches") or []
    if breaches:
        print("\nقائمة الخدمات المخترقة:")
        for b in breaches:
            if isinstance(b, dict):
                name = b.get("Name") or b.get("name") or b.get("domain") or str(b)
            else:
                name = str(b)
            print(" -", name)
    else:
        print("لا توجد اختراقات لهذا الإيميل.")
    print("\nالبيانات الكاملة (JSON):")
    print(json.dumps(data, indent=2, ensure_ascii=False))
