import re
import urllib.parse
import json
import time
import requests
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
def mr(e: str) -> tuple[int | None, str]:
    if not EMAIL_RE.match(e):
        raise ValueError("صيغة البريد الإلكتروني غير صحيحة.")
    base = "https://www.scanmylinks.com/hibp-proxy.php"
    params = {
        "email": e,
        "_t": str(int(time.time() * 1000))
    }
    url = base + "?" + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/json",
        "Referer": "https://www.scanmylinks.com/",
        "User-Agent": "python-requests/1.0 (Mail_check_JACK)",
        "Cache-Control": "no-cache, no-store",
        "Pragma": "no-cache"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        return r.status_code, r.text
    except requests.exceptions.RequestException as exc:
        return None, str(exc)
def pr(t: str):
    try:
        d = json.loads(t)
    except json.JSONDecodeError:
        print("الرد ليس JSON صالح")
        print(t)
        return
    print("\nالنتيجة (بالعربية):")
    ok = d.get("success")
    print("نجاح:" , "نعم" if ok else "لا")
    print("البريد الإلكتروني:", d.get("email"))
    print("اجمالي الاختراقات:", d.get("total_breaches"))
    print("محاولات:", d.get("attempts"))
    breaches = d.get("breaches") or []
    if breaches:
        print("\nقائمه الخدمات حبيبييي")
        for b in breaches:
            if isinstance(b, dict):
                name = b.get("Name") or b.get("name") or b.get("domain") or str(b)
            else:
                name = str(b)
            print(" -", name)
    else:
        print("لا توجد اختراقات هاذا الايميل.")

    print("\nالبيانات الكاملة (JSON):")
    print(json.dumps(d, indent=2, ensure_ascii=False))