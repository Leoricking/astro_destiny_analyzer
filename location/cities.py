"""Built-in city data for common locations."""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CityRecord:
    country_code: str
    city: str                  # canonical English name
    display_names: dict        # lang_key -> display name
    latitude: float
    longitude: float
    timezone: str              # IANA
    region: Optional[str] = None

# Built-in city database
BUILTIN_CITIES = [
    # Taiwan
    CityRecord("TW", "Taipei", {"en": "Taipei", "zh_tw": "台北", "th": "ไทเป", "ja": "台北", "es": "Taipéi", "ar": "تايبيه"}, 25.0330, 121.5654, "Asia/Taipei"),
    CityRecord("TW", "New Taipei", {"en": "New Taipei", "zh_tw": "新北", "th": "นิวไทเป", "ja": "新北", "es": "Nueva Taipéi", "ar": "نيو تايبيه"}, 25.0169, 121.4628, "Asia/Taipei"),
    CityRecord("TW", "Taoyuan", {"en": "Taoyuan", "zh_tw": "桃園", "th": "เถาหยวน", "ja": "桃園", "es": "Taoyuan", "ar": "تاويوان"}, 24.9937, 121.3010, "Asia/Taipei"),
    CityRecord("TW", "Hsinchu", {"en": "Hsinchu", "zh_tw": "新竹", "th": "ซินจู", "ja": "新竹", "es": "Hsinchu", "ar": "شينجو"}, 24.8138, 120.9675, "Asia/Taipei"),
    CityRecord("TW", "Miaoli", {"en": "Miaoli", "zh_tw": "苗栗", "th": "เมียวลี่", "ja": "苗栗", "es": "Miaoli", "ar": "مياولي"}, 24.5602, 120.8214, "Asia/Taipei"),
    CityRecord("TW", "Taichung", {"en": "Taichung", "zh_tw": "台中", "th": "ไทจง", "ja": "台中", "es": "Taizhong", "ar": "تاي تشونغ"}, 24.1477, 120.6736, "Asia/Taipei"),
    CityRecord("TW", "Changhua", {"en": "Changhua", "zh_tw": "彰化", "th": "ฉางฮัว", "ja": "彰化", "es": "Changhua", "ar": "تشانغهوا"}, 24.0518, 120.5161, "Asia/Taipei"),
    CityRecord("TW", "Nantou", {"en": "Nantou", "zh_tw": "南投", "th": "หนานโถว", "ja": "南投", "es": "Nantou", "ar": "نانتو"}, 23.9609, 120.9719, "Asia/Taipei"),
    CityRecord("TW", "Yunlin", {"en": "Yunlin", "zh_tw": "雲林", "th": "ยุนหลิน", "ja": "雲林", "es": "Yunlin", "ar": "يونلين"}, 23.7092, 120.4315, "Asia/Taipei"),
    CityRecord("TW", "Chiayi", {"en": "Chiayi", "zh_tw": "嘉義", "th": "เจียยี่", "ja": "嘉義", "es": "Chiayi", "ar": "جياي"}, 23.4801, 120.4491, "Asia/Taipei"),
    CityRecord("TW", "Tainan", {"en": "Tainan", "zh_tw": "台南", "th": "ไทหนาน", "ja": "台南", "es": "Tainan", "ar": "تاينان"}, 22.9999, 120.2269, "Asia/Taipei"),
    CityRecord("TW", "Kaohsiung", {"en": "Kaohsiung", "zh_tw": "高雄", "th": "เกาสง", "ja": "高雄", "es": "Kaohsiung", "ar": "كاوهسيونغ"}, 22.6273, 120.3014, "Asia/Taipei"),
    CityRecord("TW", "Pingtung", {"en": "Pingtung", "zh_tw": "屏東", "th": "ผิงตง", "ja": "屏東", "es": "Pingtung", "ar": "بينغتونغ"}, 22.5519, 120.5487, "Asia/Taipei"),
    CityRecord("TW", "Yilan", {"en": "Yilan", "zh_tw": "宜蘭", "th": "อี้หลาน", "ja": "宜蘭", "es": "Yilan", "ar": "يلان"}, 24.7021, 121.7378, "Asia/Taipei"),
    CityRecord("TW", "Hualien", {"en": "Hualien", "zh_tw": "花蓮", "th": "หัวเหลียน", "ja": "花蓮", "es": "Hualien", "ar": "هوالين"}, 23.9872, 121.6015, "Asia/Taipei"),
    CityRecord("TW", "Taitung", {"en": "Taitung", "zh_tw": "台東", "th": "ไถตง", "ja": "台東", "es": "Taitung", "ar": "تايتونغ"}, 22.7972, 121.0714, "Asia/Taipei"),
    CityRecord("TW", "Penghu", {"en": "Penghu", "zh_tw": "澎湖", "th": "เผิงหู", "ja": "澎湖", "es": "Penghu", "ar": "بنغهو"}, 23.5711, 119.5793, "Asia/Taipei"),
    CityRecord("TW", "Kinmen", {"en": "Kinmen", "zh_tw": "金門", "th": "จินเหมิน", "ja": "金門", "es": "Kinmen", "ar": "كينمن"}, 24.4493, 118.3767, "Asia/Taipei"),
    CityRecord("TW", "Lienchiang", {"en": "Lienchiang", "zh_tw": "連江", "th": "เหลียนเจียง", "ja": "連江", "es": "Lienchiang", "ar": "ليانجيانغ"}, 26.1605, 119.9527, "Asia/Taipei"),
    # Japan
    CityRecord("JP", "Tokyo", {"en": "Tokyo", "zh_tw": "東京", "th": "โตเกียว", "ja": "東京", "es": "Tokio", "ar": "طوكيو"}, 35.6762, 139.6503, "Asia/Tokyo"),
    CityRecord("JP", "Osaka", {"en": "Osaka", "zh_tw": "大阪", "th": "โอซาก้า", "ja": "大阪", "es": "Osaka", "ar": "أوساكا"}, 34.6937, 135.5023, "Asia/Tokyo"),
    CityRecord("JP", "Kyoto", {"en": "Kyoto", "zh_tw": "京都", "th": "เกียวโต", "ja": "京都", "es": "Kioto", "ar": "كيوتو"}, 35.0116, 135.7681, "Asia/Tokyo"),
    CityRecord("JP", "Sapporo", {"en": "Sapporo", "zh_tw": "札幌", "th": "ซัปโปโร", "ja": "札幌", "es": "Sapporo", "ar": "سابورو"}, 43.0618, 141.3545, "Asia/Tokyo"),
    CityRecord("JP", "Fukuoka", {"en": "Fukuoka", "zh_tw": "福岡", "th": "ฟุกุโอกะ", "ja": "福岡", "es": "Fukuoka", "ar": "فوكوكا"}, 33.5904, 130.4017, "Asia/Tokyo"),
    # Thailand
    CityRecord("TH", "Bangkok", {"en": "Bangkok", "zh_tw": "曼谷", "th": "กรุงเทพมหานคร", "ja": "バンコク", "es": "Bangkok", "ar": "بانكوك"}, 13.7563, 100.5018, "Asia/Bangkok"),
    CityRecord("TH", "Chiang Mai", {"en": "Chiang Mai", "zh_tw": "清邁", "th": "เชียงใหม่", "ja": "チェンマイ", "es": "Chiang Mai", "ar": "شيانغ ماي"}, 18.7883, 98.9853, "Asia/Bangkok"),
    CityRecord("TH", "Phuket", {"en": "Phuket", "zh_tw": "普吉", "th": "ภูเก็ต", "ja": "プーケット", "es": "Phuket", "ar": "بوكيت"}, 7.8804, 98.3923, "Asia/Bangkok"),
    # US
    CityRecord("US", "New York", {"en": "New York", "zh_tw": "紐約", "th": "นิวยอร์ก", "ja": "ニューヨーク", "es": "Nueva York", "ar": "نيويورك"}, 40.7128, -74.0060, "America/New_York"),
    CityRecord("US", "Los Angeles", {"en": "Los Angeles", "zh_tw": "洛杉磯", "th": "ลอสแองเจลิส", "ja": "ロサンゼルス", "es": "Los Ángeles", "ar": "لوس أنجلوس"}, 34.0522, -118.2437, "America/Los_Angeles"),
    CityRecord("US", "Chicago", {"en": "Chicago", "zh_tw": "芝加哥", "th": "ชิคาโก", "ja": "シカゴ", "es": "Chicago", "ar": "شيكاغو"}, 41.8781, -87.6298, "America/Chicago"),
    CityRecord("US", "Houston", {"en": "Houston", "zh_tw": "休士頓", "th": "ฮูสตัน", "ja": "ヒューストン", "es": "Houston", "ar": "هيوستن"}, 29.7604, -95.3698, "America/Chicago"),
    CityRecord("US", "San Francisco", {"en": "San Francisco", "zh_tw": "舊金山", "th": "ซานฟรานซิสโก", "ja": "サンフランシスコ", "es": "San Francisco", "ar": "سان فرانسيسكو"}, 37.7749, -122.4194, "America/Los_Angeles"),
    CityRecord("US", "Honolulu", {"en": "Honolulu", "zh_tw": "檀香山", "th": "โฮโนลูลู", "ja": "ホノルル", "es": "Honolulu", "ar": "هونولولو"}, 21.3069, -157.8583, "Pacific/Honolulu"),
    CityRecord("US", "Anchorage", {"en": "Anchorage", "zh_tw": "安克拉治", "th": "แองเคอเรจ", "ja": "アンカレッジ", "es": "Anchorage", "ar": "أنكوراج"}, 61.2181, -149.9003, "America/Anchorage"),
    # UK
    CityRecord("GB", "London", {"en": "London", "zh_tw": "倫敦", "th": "ลอนดอน", "ja": "ロンドン", "es": "Londres", "ar": "لندن"}, 51.5074, -0.1278, "Europe/London"),
    # Australia
    CityRecord("AU", "Sydney", {"en": "Sydney", "zh_tw": "雪梨", "th": "ซิดนีย์", "ja": "シドニー", "es": "Sídney", "ar": "سيدني"}, -33.8688, 151.2093, "Australia/Sydney"),
    CityRecord("AU", "Melbourne", {"en": "Melbourne", "zh_tw": "墨爾本", "th": "เมลเบิร์น", "ja": "メルボルン", "es": "Melbourne", "ar": "ملبورن"}, -37.8136, 144.9631, "Australia/Melbourne"),
    # Canada
    CityRecord("CA", "Toronto", {"en": "Toronto", "zh_tw": "多倫多", "th": "โตรอนโต", "ja": "トロント", "es": "Toronto", "ar": "تورنتو"}, 43.6532, -79.3832, "America/Toronto"),
    CityRecord("CA", "Vancouver", {"en": "Vancouver", "zh_tw": "溫哥華", "th": "แวนคูเวอร์", "ja": "バンクーバー", "es": "Vancouver", "ar": "فانكوفر"}, 49.2827, -123.1207, "America/Vancouver"),
    # Singapore
    CityRecord("SG", "Singapore", {"en": "Singapore", "zh_tw": "新加坡", "th": "สิงคโปร์", "ja": "シンガポール", "es": "Singapur", "ar": "سنغافورة"}, 1.3521, 103.8198, "Asia/Singapore"),
    # South Korea
    CityRecord("KR", "Seoul", {"en": "Seoul", "zh_tw": "首爾", "th": "โซล", "ja": "ソウル", "es": "Seúl", "ar": "سيول"}, 37.5665, 126.9780, "Asia/Seoul"),
    # Hong Kong
    CityRecord("HK", "Hong Kong", {"en": "Hong Kong", "zh_tw": "香港", "th": "ฮ่องกง", "ja": "香港", "es": "Hong Kong", "ar": "هونغ كونغ"}, 22.3193, 114.1694, "Asia/Hong_Kong"),
    # France
    CityRecord("FR", "Paris", {"en": "Paris", "zh_tw": "巴黎", "th": "ปารีส", "ja": "パリ", "es": "París", "ar": "باريس"}, 48.8566, 2.3522, "Europe/Paris"),
    # Germany
    CityRecord("DE", "Berlin", {"en": "Berlin", "zh_tw": "柏林", "th": "เบอร์ลิน", "ja": "ベルリン", "es": "Berlín", "ar": "برلين"}, 52.5200, 13.4050, "Europe/Berlin"),
    # UAE
    CityRecord("AE", "Dubai", {"en": "Dubai", "zh_tw": "杜拜", "th": "ดูไบ", "ja": "ドバイ", "es": "Dubái", "ar": "دبي"}, 25.2048, 55.2708, "Asia/Dubai"),
    # Saudi Arabia
    CityRecord("SA", "Riyadh", {"en": "Riyadh", "zh_tw": "利雅德", "th": "ริยาด", "ja": "リヤド", "es": "Riad", "ar": "الرياض"}, 24.7136, 46.6753, "Asia/Riyadh"),
    # Egypt
    CityRecord("EG", "Cairo", {"en": "Cairo", "zh_tw": "開羅", "th": "ไคโร", "ja": "カイロ", "es": "El Cairo", "ar": "القاهرة"}, 30.0444, 31.2357, "Africa/Cairo"),
    # India
    CityRecord("IN", "Mumbai", {"en": "Mumbai", "zh_tw": "孟買", "th": "มุมไบ", "ja": "ムンバイ", "es": "Bombay", "ar": "مومباي"}, 19.0760, 72.8777, "Asia/Kolkata"),
    CityRecord("IN", "Delhi", {"en": "Delhi", "zh_tw": "德里", "th": "เดลี", "ja": "デリー", "es": "Delhi", "ar": "دلهي"}, 28.7041, 77.1025, "Asia/Kolkata"),
    # China
    CityRecord("CN", "Beijing", {"en": "Beijing", "zh_tw": "北京", "th": "ปักกิ่ง", "ja": "北京", "es": "Pekín", "ar": "بكين"}, 39.9042, 116.4074, "Asia/Shanghai"),
    CityRecord("CN", "Shanghai", {"en": "Shanghai", "zh_tw": "上海", "th": "เซี่ยงไฮ้", "ja": "上海", "es": "Shanghái", "ar": "شنغهاي"}, 31.2304, 121.4737, "Asia/Shanghai"),
    # Brazil
    CityRecord("BR", "São Paulo", {"en": "São Paulo", "zh_tw": "聖保羅", "th": "เซาเปาลู", "ja": "サンパウロ", "es": "São Paulo", "ar": "ساو باولو"}, -23.5505, -46.6333, "America/Sao_Paulo"),
    # Mexico
    CityRecord("MX", "Mexico City", {"en": "Mexico City", "zh_tw": "墨西哥城", "th": "เม็กซิโกซิตี้", "ja": "メキシコシティ", "es": "Ciudad de México", "ar": "مكسيكو سيتي"}, 19.4326, -99.1332, "America/Mexico_City"),
]


def search_builtin_cities(country_code: str, query: str = "", language: str = "en") -> list:
    """Search built-in cities by country and optional query string."""
    lang_key_map = {"zh-TW": "zh_tw", "en": "en", "th": "th", "ja": "ja", "es": "es", "ar": "ar"}
    lang_key = lang_key_map.get(language, "en")

    results = [c for c in BUILTIN_CITIES if c.country_code == country_code.upper()]

    if query:
        q = query.lower().strip()
        filtered = []
        for c in results:
            # Match against canonical name or any display name
            if q in c.city.lower():
                filtered.append(c)
                continue
            for name in c.display_names.values():
                if q in name.lower():
                    filtered.append(c)
                    break
        results = filtered

    return results


def get_city_display_name(city_record, language: str = "en") -> str:
    lang_key_map = {"zh-TW": "zh_tw", "en": "en", "th": "th", "ja": "ja", "es": "es", "ar": "ar"}
    lang_key = lang_key_map.get(language, "en")
    return city_record.display_names.get(lang_key) or city_record.display_names.get("en") or city_record.city
