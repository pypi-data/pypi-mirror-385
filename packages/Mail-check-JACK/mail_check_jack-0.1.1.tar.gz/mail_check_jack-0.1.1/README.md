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
from mail_check_jack.core import mr, pr    
status, response_text = mr("")#ايميلك اخليه هنا
if status == 200:
    pr(response_text)
```

