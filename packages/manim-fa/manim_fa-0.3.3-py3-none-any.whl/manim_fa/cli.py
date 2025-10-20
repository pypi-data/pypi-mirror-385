import json
import sys
from pathlib import Path

DICT_PATH = Path(__file__).parent / "dictionary.json"

def load_dict() -> dict:
    if DICT_PATH.exists():
        try:
            with open(DICT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[manim-fa] ⚠️ خطا در خواندن فایل dictionary.json. ایجاد فایل جدید.")
    return {}

def save_dict(data: dict):
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"[manim-fa] ✅ فایل dictionary.json با {len(data)} واژه ذخیره شد.")

def add_word(latin: str, persian: str):
    data = load_dict()
    data[latin.lower()] = persian
    save_dict(data)
    print(f"[manim-fa] 🆕 واژه‌ی '{latin}' → '{persian}' اضافه شد.")

def remove_word(latin: str):
    data = load_dict()
    latin = latin.lower()
    if latin in data:
        del data[latin]
        save_dict(data)
        print(f"[manim-fa] 🗑 واژه‌ی '{latin}' حذف شد.")
    else:
        print(f"[manim-fa] ⚠️ واژه‌ی '{latin}' در فرهنگ‌نامه یافت نشد.")

def list_words():
    data = load_dict()
    if not data:
        print("[manim-fa] فرهنگ‌نامه خالی است.")
        return
    print("[manim-fa] 📘 فهرست واژه‌های موجود:")
    for latin, persian in data.items():
        print(f"  {latin} → {persian}")

def show_help():
    print("استفاده: manim-fa <دستور> [آرگومان‌ها]")
    print("دستورات موجود:")
    print("  add-word <latin> <persian>   افزودن واژه‌ی جدید")
    print("  remove-word <latin>          حذف واژه از فرهنگ‌نامه")
    print("  list-words                   نمایش همه‌ی واژه‌ها")
    print("  help                         نمایش این راهنما")

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1]

    if command == "add-word" and len(sys.argv) == 4:
        add_word(sys.argv[2], sys.argv[3])
    elif command == "remove-word" and len(sys.argv) == 3:
        remove_word(sys.argv[2])
    elif command == "list-words":
        list_words()
    elif command in ["help", "--help", "-h"]:
        show_help()
    else:
        print("[manim-fa] ❌ دستور یا آرگومان اشتباه.")
        show_help()

if __name__ == "__main__":
    main()
