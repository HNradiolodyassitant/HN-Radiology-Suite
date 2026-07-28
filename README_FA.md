# HN Radiology Suite v2.3 — Stability & Modular Architecture

این نسخه یک **Stability Release** است و قابلیت پزشکی جدیدی اضافه نمی‌کند. هدف آن جداکردن اجزای اجرایی، کاهش احتمال خرابی کل صفحه و فراهم‌کردن پایه مناسب برای Device Sync Bridge است.

## اجرا

تمام محتویات این پوشه را بدون تغییر ساختار روی شاخه اصلی GitHub Pages قرار دهید. فایل `index.html` باید کنار پوشه `assets` باشد.

برای تست محلی، بهتر است پوشه با یک وب‌سرور محلی باز شود:

```bash
python -m http.server 8080
```

سپس آدرس `http://localhost:8080` را در Chrome یا Edge باز کنید.

## ساختار

- `assets/js/modules/20-core.js`: پوسته برنامه، صفحه اصلی، آرشیو و خروجی گزارش
- `assets/js/modules/30-report-engine.js`: موتور تولید گزارش و اعتبارسنجی
- `assets/js/modules/40-ultrasound.js`: رابط موتورهای سونوگرافی معمولی
- `assets/js/modules/41-43`: Phrase libraries کلیه، کبد و پروستات
- `assets/js/modules/50-doppler.js`: کالر داپلر و واریکوسل
- `assets/js/modules/60-obgyn.js`: زنان، بارداری، FGR و نمودارها
- `assets/js/modules/90-vendor.js`: React و وابستگی‌های اجرایی
- `assets/js/voice-assistant.js`: دستیار صوتی مستقل
- `assets/js/stability.js`: ثبت خطا و Diagnostics محلی

## حریم خصوصی

Diagnostics فقط در همان مرورگر اجرا می‌شود و هیچ داده‌ای را به اینترنت ارسال نمی‌کند. اطلاعات بیمار نباید در فایل گزارش فنی ذخیره شود.

## نسخه جایگزین

پوشه `fallback-single-file` یک نسخه تک‌فایلی برای شرایط اضطراری دارد. نسخه اصلی و توصیه‌شده، ساختار modular است.
