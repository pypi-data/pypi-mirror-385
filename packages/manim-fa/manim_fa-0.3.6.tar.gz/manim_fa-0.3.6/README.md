# 🎬 manim-fa

افزونه‌ی مانیم برای نمایش دادن متن فارسی (راست به چپ) با قابلیت تبدیل خودکار آوانگاری از فنگلش به فارسی.

## نحوه نصب پلاگین


```bash
pip install manim_fa
```
یا برای نصب محلی (در حالت توسعه):

```bash
pip install -e .
```
---

## 💡 مثال‌های آموزشی

### 🔹 مثال ۱ — متن ساده
```python
from manim import *
from manim_fa import FaText

class SimpleDemo_01(Scene):
    def construct(self):
        t = FaText("به مانیم فارسی خوش آمدید!", font_size=50)
        self.play(Write(t))
        self.wait(1)
```
---
### 🔹 مثال ۲ — متن رنگی 
```python
from manim import *
from manim_fa import FaText

class SimpleDemo_02(Scene):
    def construct(self):
        t = FaText("به مانیم خوش آمدید. متن رنگی!", color=YELLOW, font_size=60)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.set_color(RED))
        self.wait(1)
```
---
### 🔹 مثال ۳ — راست‌چین و با فونت سفارشی
```python
from manim import *
from manim_fa import FaText

class SimpleDemo_03(Scene):
    def construct(self):
        t = FaText("نوشتن خط نستعلیق در مانیم", font="IranNastaliq", rtl=True)
        self.play(Write(t))
        self.wait(2)
```
---
### 🔹 مثال ۴ — تبدیل لاتین به فارسی (ترانسلیت)
```python
from manim import *
from manim_fa import FaText

class SimpleDemo_04(Scene):
    def construct(self):
        t = FaText("Ba Manim khosh Amadid", translit=True, color=BLUE)
        self.play(Write(t))
        self.wait(2)
```
---

### 🔹 مثال ۵ — انیمیشن‌های ترکیبی
```python
from manim import *
from manim_fa import FaText

class SimpleDemo_05(Scene):
    def construct(self):
        t = FaText("حرکت، رنگ، چرخش!", font_size=55)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.shift(UP))
        self.play(t.animate.scale(1.5))
        self.play(t.animate.rotate(PI / 4))
        self.play(t.animate.set_color(GREEN))
        self.wait(2)
```
---

## 🌀 فهرست کامل انیمیشن‌های کاربردی در Manim

| نام انیمیشن | کاربرد | مثال |
|--------------|---------|-------|
| `Write()` | نوشتن تدریجی متن | `self.play(Write(t))` |
| `Create()` | رسم کامل یک شیء از ابتدا | `self.play(Create(circle))` |
| `FadeIn()` | ظاهر شدن تدریجی شیء | `self.play(FadeIn(t))` |
| `FadeOut()` | محو شدن تدریجی شیء | `self.play(FadeOut(t))` |
| `FadeToColor()` | تغییر رنگ شیء با انیمیشن نرم | `self.play(FadeToColor(t, RED))` |
| `Transform()` | تبدیل یک شیء به شیء دیگر | `self.play(Transform(t1, t2))` |
| `ReplacementTransform()` | جایگزینی تدریجی یک شیء با دیگری | `self.play(ReplacementTransform(t1, t2))` |
| `Rotate()` | چرخش شیء به اندازه مشخص | `self.play(Rotate(t, angle=PI/2))` |
| `ScaleInPlace()` | بزرگ یا کوچک شدن در محل فعلی | `self.play(t.animate.scale(1.5))` |
| `MoveAlongPath()` | حرکت شیء روی مسیر مشخص | `self.play(MoveAlongPath(t, circle))` |
| `Circumscribe()` | ترسیم حاشیه دور شیء | `self.play(Circumscribe(t))` |
| `GrowFromCenter()` | رشد شیء از مرکز | `self.play(GrowFromCenter(t))` |
| `ShrinkToCenter()` | جمع شدن شیء به مرکز | `self.play(ShrinkToCenter(t))` |
| `Wiggle()` | لرزش یا تکان نرم | `self.play(Wiggle(t))` |
| `FocusOn()` | فوکوس با تغییر نور یا رنگ | `self.play(FocusOn(t))` |
| `Flash()` | درخشش سریع در محل شیء | `self.play(Flash(t))` |
| `Indicate()` | نمایش تأکید با رنگ و مقیاس | `self.play(Indicate(t))` |
| `ApplyWave()` | حرکت موجی روی شیء | `self.play(ApplyWave(t))` |
| `ApplyMethod()` | اجرای متد خاص روی شیء | `self.play(ApplyMethod(t.shift, UP))` |
| `animate.shift()` | جابه‌جایی شیء | `self.play(t.animate.shift(UP))` |
| `animate.set_color()` | تغییر رنگ شیء | `self.play(t.animate.set_color(BLUE))` |
| `animate.rotate()` | چرخش با انیمیشن نرم | `self.play(t.animate.rotate(PI/3))` |

---

## 🧭 مثال پیشرفته (ترکیب چند انیمیشن)

```python
from manim import *
from manim_fa import FaText

class ComplexDemo(Scene):
    def construct(self):
        # --- 1️⃣ نمایش متن خوش‌آمد ---
        text1 = FaText("به مانیم فارسی خوش آمدید.", font_size=48, color=BLUE)
        text1.to_edge(UP)
        self.play(Write(text1))
        self.wait(1)

        # --- 2️⃣ نمایش جمله دوم ---
        text2 = FaText("این یک مستطیل هست.", font_size=42, color=WHITE)
        text2.next_to(text1, DOWN, buff=0.8)
        self.play(Write(text2))
        self.wait(1)

        # --- 3️⃣ رسم مستطیل ---
        rect = Rectangle(width=4, height=2, color=YELLOW)
        rect.next_to(text2, DOWN, buff=1)
        self.play(Create(rect))
        self.wait(1)

        # --- 4️⃣ تبدیل مستطیل به مثلث ---
        tri = Polygon(
            [-2, -1, 0],
            [2, -1, 0],
            [0, 1, 0],
            color=GREEN
        )
        tri.move_to(rect.get_center())
        self.play(Transform(rect, tri))
        self.wait(1)

        # --- 5️⃣ تغییر جمله دوم به "این یک مثلث هست." با فونت نستعلیق ---
        new_text2 = FaText(
            "این یک مثلث هست.",
            font_size=42,
            font="IranNastaliq",
            color=GREEN
        )
        new_text2.move_to(text2.get_center())
        self.play(Transform(text2, new_text2))
        self.wait(2)

        # --- 6️⃣ افکت پایانی ---
        self.play(FadeOut(text1), FadeOut(text2), FadeOut(rect))
        self.wait(1)

```
---


## 🧾 مجوز
این پروژه تحت مجوز **MIT** منتشر می‌شود.  
ساخته‌شده توسط علی تابش برای جامعه‌ی فارسی‌زبان Manim.

---

## 🤝 مشارکت
اگر پیشنهادی برای بهبود ترانسلیت، فونت‌ها یا سازگاری با نسخه‌های جدید Manim دارید،  
Pull Request بسازید یا در بخش Issues مطرح کنید.
