هذه المكتبة مبنية على سكربت مقدم من المستخدم، وتقوم بفحص ما إذا كان بريد إلكتروني معين قد ظهر في أي من اختراقات. 


## التثبيت

يمكنك تثبيت المكتبة باستخدام `pip`:

```bash
pip install Mail_check_JACK
```

## الاستخدام كمكتبة Python

يمكنك استيراد الوظائف واستخدامها في مشاريعك الخاصة.

### مثال 1: فحص وطباعة النتيجة

```python
from Mail_check_JACK.core import cemail, esult
email_to_check = "gsksvsksksj@gmail.com"#مثال
status, response_text = check_email(email_to_check)
if status is None:
    print(f"صار خطأ: {response_text}")
elif status == 200:
    pretty_print_result(response_text)
else:
    print(f"صار خطأ بل خادم (HTTP {status}):\n{response_text}")
```

