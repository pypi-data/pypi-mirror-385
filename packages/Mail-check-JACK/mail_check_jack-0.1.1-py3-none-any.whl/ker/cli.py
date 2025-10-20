import sys
import re
from .core import mr, pr, EMAIL_RE
def ae():
    try:
        e = input("أدخل البريد الإلكتروني للفحص : ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nتم الإلغاء.")
        sys.exit(1)
    if not EMAIL_RE.match(e):
        print("الابريد الكتروني مو صحيح صيغه مو صحيحه")
        sys.exit(2)
    return 
def ma():
    e = ae()
    status, text = mr(e)
    if status is None:
        print("صار خطأ بل اتصال", text)
        sys.exit(3)
    print(f"\nحالة HTTP: {status}")
    if status != 200:
        print("الخادم رد مالته صحيح ")
        print(text)
        sys.exit(4)
    pr(text)

def main():
    ma()

if __name__ == '__main__':
   