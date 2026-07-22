# ELINK — خطة مشروع التجارة الإلكترونية

## نظرة عامة
- النوع: متجر إلكتروني متوسط إلى كبير الحجم
- الستاك: Django + Django REST Framework (DRF) + AJAX (النمط المعتاد للمطور — بدون SPA framework منفصل)
- قاعدة البيانات: PostgreSQL (لو محلياً بالبداية ممكن SQLite للتطوير السريع، لكن الإنتاج PostgreSQL)
- الموقع/السياق: المطور بقطر، الحساب البنكي التجاري وبوابة الدفع لسا غير جاهزين

## قاعدة مهمة: بوابة الدفع
**لا تربط أي بوابة دفع فعلية الآن.** بوابة الدفع هي آخر خطوة بالمشروع، ولازم تبنى بشكل قابل للفصل (pluggable) من البداية، مو مربوطة بمنطق الطلبات مباشرة.

- سوّي app اسمه `payments` فيه:
  - موديل `Payment` عام (order, amount, status: pending/paid/failed, gateway: string, transaction_id, created_at)
  - interface/abstract class بسيط لأي "gateway" (مثلاً `BasePaymentGateway` بميثود `initiate_payment()` و`verify_payment()`)
  - تطبيق مؤقت واحد بس شغّال فعلياً: **الدفع عند الاستلام (Cash on Delivery / يدوي)** — عشان يكمل تدفق الطلب end-to-end بدون الحاجة لبوابة حقيقية
  - لا تسوي أي تكامل حقيقي مع PayPal أو أي بوابة ثانية قبل ما يتوفر الحساب البنكي (QNB) — بس خلي الكود جاهز يستقبل gateway جديدة بسهولة (استراتيجية/plugin pattern)

## هيكلة الـ Apps المقترحة
```
ELINK/
├── core/              # Django project settings
├── accounts/          # تسجيل دخول/تسجيل مستخدمين، ممكن custom user model
├── products/          # منتجات، تصنيفات، متغيرات (variants: مقاس/لون)
├── cart/              # سلة التسوق (session أو DB-based)، APIs عبر AJAX
├── orders/            # الطلبات، checkout flow
├── payments/          # عام + COD الآن فقط، جاهز للتوسعة لاحقاً (راجع القسم فوق)
├── templates/
├── static/
└── media/
```

## ملاحظات تقنية
- استخدام `django-environ` أو `.env` لأي secrets (لا تحط مفاتيح مباشرة بالكود)
- DRF عبر `djangorestframework` + `django-filter` للفلترة/البحث بالمنتجات
- AJAX (fetch/jQuery) للتفاعل مع DRF endpoints: إضافة للسلة، تحديث الكمية، فلترة المنتجات بدون reload
- Pillow لمعالجة صور المنتجات
- لاحقاً (اختياري حسب الحمل): Redis للـ caching، Celery للمهام الخلفية (إيميلات تأكيد الطلب، تقارير)

## ترتيب التنفيذ المقترح (checklist)
- [x] إنشاء virtualenv وتثبيت: `django`, `djangorestframework`, `django-filter`, `pillow`, `django-environ`
- [x] `django-admin startproject core .`
- [x] إنشاء الـ apps: `accounts`, `products`, `cart`, `orders`, `payments`
- [x] إعداد `settings.py` (INSTALLED_APPS, DRF, STATIC/MEDIA, templates, .env)
- [x] موديلات `products` (Category, Product, ProductImage, Variant)
- [x] موديلات `accounts` (custom user model مع phone/address/city)
- [x] موديلات `cart` + منطق السلة (session أو user، merge عند تسجيل الدخول)
- [x] موديلات `orders` (Order, OrderItem) + ربطها بالسلة (checkout flow كامل)
- [x] موديل `payments.Payment` + `BasePaymentGateway` + تطبيق COD فقط
- [x] DRF serializers + viewsets/APIViews للمنتجات، السلة، الطلبات
- [x] Templates أساسية (base, product list/detail, cart, checkout) + AJAX JS — بتصميم موحد (static/css/style.css) بألوان الشعار
- [x] git init + أول commit
- [ ] لاحقاً (بعد جهوزية الحساب البنكي): تفعيل تكامل بوابة دفع حقيقية داخل `payments` بدون تعديل بقية النظام

## ما لا يجب فعله الآن
- لا تربط PayPal أو أي بوابة دفع حقيقية بالكود
- لا تفترض وجود حساب بنكي أو QNB جاهز
- لا تبني الـ frontend كـ SPA منفصل (React/Vue/Next.js) — التزم بـ Django templates + AJAX
