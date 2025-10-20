from .fonts import get_persian_font
from .translit import translit_to_fa
from manim import Text

def FaText(
    content,
    font=None,
    font_size=48,
    color="WHITE",
    weight=None,
    slant=None,
    translit=False,
    rtl=True,
    **kwargs
):
    """
     : نمایش و راست چین کردن متن فارسی در مانیم با قابلیت آوا نگاری از فنگش به متن فارسی

    پارامترها:
    - content: متن فارسی یا لاتین
    - font: نام فونت فارسی (پیش‌فرض از get_persian_font استفاده می‌شود)
    - font_size: اندازه فونت
    - color: رنگ متن
    - بدون پشتیبانی از بولد و ایتالیک
    - translit: اگر True باشد، متن لاتین به فارسی تبدیل می‌شود
    - rtl: اگر True باشد، متن راست‌چین می‌شود
    - kwargs: سایر پارامترهای Text
    """
    if translit:
        content = translit_to_fa(content)

    font = get_persian_font(font)
    text = Text(content, font=font, font_size=font_size, color=color, **kwargs)

    if weight:
        text.set_weight(weight)
    if slant:
        text.set_slant(slant)

    if rtl:
        text.submobjects.reverse()

    return text

## فایل اصلی پلاگین مانیم-فا
