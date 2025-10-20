import sys
from .core import cemail, esult

def t_email() -> str:
    try:
        email = input("أدخل البريد الإلكتروني للفحص: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nتم الإلغاء.")
        sys.exit(1)
    return email
def main():
    try:
        email = t_email()
        if not email:
            print("البريد الإلكتروني لا يمكن أن يكون فارغًا.")
            sys.exit(2)
        status, text = cemail(email)
        if status is None:
            print(f"صار خطأ في الاتصال: {text}")
            sys.exit(3)
        print(f"\nحالة HTTP: {status}")
        if status != 200:
            print("الخادم رد بشكل غير صحيح.")
            print(text)
            sys.exit(4)
        esult(text)
    except ValueError as ve:
        print(f"خطأ: {ve}")
        sys.exit(2)
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
        sys.exit(5)

if __name__ == '__main__':
    main()
