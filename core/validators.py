"""
Astro Destiny Analyzer — Input Validators
"""
from datetime import date, time
from typing import Optional, Tuple


def validate_birth_date(year: int, month: int, day: int) -> Tuple[bool, str]:
    try:
        d = date(year, month, day)
        if d > date.today():
            return False, "出生日期不能晚於今日。"
        if year < 1800:
            return False, "年份需在 1800 年以後。"
        return True, ""
    except ValueError as e:
        return False, f"日期格式錯誤：{e}"


def validate_birth_time(hour: int, minute: int) -> Tuple[bool, str]:
    if not (0 <= hour <= 23):
        return False, "小時需在 0–23 之間。"
    if not (0 <= minute <= 59):
        return False, "分鐘需在 0–59 之間。"
    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    name = name.strip()
    if not name:
        return False, "姓名不得為空。"
    if len(name) > 100:
        return False, "姓名不得超過 100 個字元。"
    return True, ""


def validate_city(city: str) -> Tuple[bool, str]:
    city = city.strip()
    if not city:
        return False, "城市不得為空。"
    if len(city) > 100:
        return False, "城市名稱不得超過 100 個字元。"
    return True, ""
