## ماژول پایتون برای پردازش متن فراسی در مانیم
from .text import FaText
from .fonts import get_persian_font
from .translit import translit_to_fa

__all__ = ["FaText", "get_persian_font", "translit_to_fa"]


