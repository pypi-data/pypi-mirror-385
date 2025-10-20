# manim_fa/fonts.py بسته فونت فارسی

from matplotlib import font_manager

# لیست فونت‌های فارسی پیش‌فرض که پلاگین از آن‌ها استفاده می‌کند
_DEFAULT_FONTS = [
    "IrTitr", "Ordibehesht", "IRXLotus", "IRTabassom",
    "IRDastNevis", "IREntezar", "Behistun", "IRKamran",
    "IRMaryam", "Shekasteh_Beta", "IRAmir", "IranNastaliq-Web", "IranNastaliq"
]

def _font_installed(font_name: str) -> bool:
    """
    بررسی می‌کند که فونت مورد نظر در سیستم نصب شده باشد.
    """
    installed_fonts = [f.name for f in font_manager.fontManager.ttflist]
    return font_name in installed_fonts

def get_persian_font(preferred: str | None = None) -> str:
    """
    بازگرداندن یک فونت فارسی معتبر برای استفاده در FaText.
    اگر preferred داده شود، ابتدا آن بررسی می‌شود.
    اگر هیچ فونت پیدا نشد، Arial برگردانده می‌شود.
    """
    candidates = [preferred] + _DEFAULT_FONTS if preferred else _DEFAULT_FONTS
    for font in candidates:
        if font and _font_installed(font):
            return font

    print("[manim-fa] ⚠️ هیچ فونت فارسی یافت نشد، استفاده از 'Arial' به عنوان جایگزین.")
    return "Arial"
