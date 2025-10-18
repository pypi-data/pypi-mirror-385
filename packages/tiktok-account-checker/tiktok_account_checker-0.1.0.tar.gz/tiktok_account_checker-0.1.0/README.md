# TikTok Account Checker Library

هذه مكتبة بايثون تمكنك من فحص حسابات TikTok للحصول على معلومات حول حالة الربط (البريد الإلكتروني، الهاتف، OAuth، مفتاح المرور) ومستوى الدعم.

## الاستخدام

يمكنك استيراد الدالة `check_tiktok_account` مباشرة من المكتبة بعد تثبيتها.

### مثال

```python
from tiktok_account_checker import check_tiktok_account
# فحص حساب TikTok
username_to_check = "tiktok"
result = check_tiktok_account(username_to_check)
if result["status"] == "success":
    print(f"--- معلومات حساب @{result["username"]} ---") 
    passkey_status = "يوجد ربط مخفي ⚠️" if result["has_passkey"] else "لا يوجد ربط مخفي 🟢"
    oauth_status = "يوجد ربط خارجي ⚠️" if result["has_oauth"] else "لا يوجد ربط خارجي 🟢"
    phone_icon = "✔️" if result["has_mobile"] else "❌"
    email_icon = "✔️" if result["has_email"] else "❌"
    level_text = result["supporter_level"] if result["supporter_level"] is not None else "غير متاح"
    print(f"  {passkey_status}")
    print(f"  {oauth_status}")
    print(f"  الرقم: {phone_icon} | الايميل: {email_icon} | مستوى الدعم: {level_text}")
    print("-" * 25)
else:
    print(f"  حدث خطأ أثناء فحص @{username_to_check}: {result["message"]}")
    print("-" * 25)
```

