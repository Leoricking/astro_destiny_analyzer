"""
Astro Destiny Analyzer — Zi Wei Dou Shu (紫微斗數) Engine
V1: Mock layout layer with complete palace structure and major star placements.
TODO: Replace _layout_mock() with a full 紫微排盤 algorithm that:
  - Computes 命宮 from birth month and hour
  - Places 紫微星 and 天府星 via the 安星訣 algorithm
  - Distributes all 14 主星 and auxiliary stars
  - Applies 四化 (化祿/化權/化科/化忌) based on year stem
The palace structure and ZiWeiChart model are already production-ready.
"""
import hashlib
from datetime import date, time
from typing import Optional, List, Dict
from core.models import ZiWeiChart, ZiWeiPalace


_PALACE_NAMES = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

_EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

_MAIN_STARS_14 = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府",
    "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍",
]

_MINOR_STARS = [
    "文昌", "文曲", "左輔", "右弼", "天魁", "天鉞",
    "祿存", "天馬", "擎羊", "陀羅", "火星", "鈴星",
]

_FOUR_TRANSFORMATIONS = ["化祿", "化權", "化科", "化忌"]

_YEAR_STEM_SIHUA: Dict[str, Dict[str, str]] = {
    "甲": {"廉貞": "化祿", "破軍": "化權", "武曲": "化科", "太陽": "化忌"},
    "乙": {"天機": "化祿", "天梁": "化權", "紫微": "化科", "太陰": "化忌"},
    "丙": {"天同": "化祿", "天機": "化權", "文昌": "化科", "廉貞": "化忌"},
    "丁": {"太陰": "化祿", "天同": "化權", "天機": "化科", "巨門": "化忌"},
    "戊": {"貪狼": "化祿", "太陰": "化權", "右弼": "化科", "天機": "化忌"},
    "己": {"武曲": "化祿", "貪狼": "化權", "天梁": "化科", "文曲": "化忌"},
    "庚": {"太陽": "化祿", "武曲": "化權", "太陰": "化科", "天同": "化忌"},
    "辛": {"巨門": "化祿", "太陽": "化權", "文曲": "化科", "文昌": "化忌"},
    "壬": {"天梁": "化祿", "紫微": "化權", "左輔": "化科", "武曲": "化忌"},
    "癸": {"破軍": "化祿", "巨門": "化權", "太陰": "化科", "貪狼": "化忌"},
}

_PALACE_INTERPRETATIONS = {
    "命宮": "命宮是紫微命盤的核心，代表你的根本個性、外在氣質與人生主軸。",
    "兄弟宮": "兄弟宮代表手足關係、平輩緣分，以及你與同儕的互動模式。",
    "夫妻宮": "夫妻宮顯示你在婚姻或長期伴侶關係中的模式與運勢。",
    "子女宮": "子女宮代表子息緣分、部屬關係，以及你的創造力展現。",
    "財帛宮": "財帛宮揭示你的財富獲取方式、金錢觀與理財模式。",
    "疾厄宮": "疾厄宮代表身體健康、挫折承受力，以及生命中的考驗模式。",
    "遷移宮": "遷移宮代表你在外部世界的表現、異鄉發展潛力與外緣。",
    "交友宮": "交友宮顯示你的友情模式、貴人小人，以及社交場域中的能量。",
    "官祿宮": "官祿宮是事業格局的核心，揭示你的職涯走向、工作模式與成就方式。",
    "田宅宮": "田宅宮代表家庭環境、不動產運與你對安全感的追求方式。",
    "福德宮": "福德宮顯示你的內在精神世界、享樂方式，以及前世業力帶來的福分。",
    "父母宮": "父母宮代表與父母的關係、長輩緣分，以及你在社會中接受規範的模式。",
}


def _seed(birth_date: date, birth_time: Optional[time]) -> int:
    raw = f"{birth_date.isoformat()}:{birth_time.isoformat() if birth_time else 'noon'}"
    return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 10000


class ZiWeiEngine:
    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None) -> ZiWeiChart:
        """
        TODO (production upgrade):
          1. Determine 命宮 earthly branch from birth month + birth hour.
          2. Calculate 紫微星 position using the 紫微安星訣 table.
          3. Distribute all 14 主星 based on 紫微/天府 positions.
          4. Place auxiliary stars (文昌/文曲/左輔/右弼 etc.) by formula.
          5. Apply 四化 from the year stem.
          6. Set is_mock=False.
        """
        return self._layout_mock(birth_date, birth_time)

    def _layout_mock(self, birth_date: date,
                     birth_time: Optional[time]) -> ZiWeiChart:
        s = _seed(birth_date, birth_time)

        # Year stem for 四化
        stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        year_stem = stems[(birth_date.year - 4) % 10]
        sihua_map = _YEAR_STEM_SIHUA.get(year_stem, {})

        # 命宮 earthly branch (mock: derive from birth month and hour index)
        ming_branch_idx = (birth_date.month + (birth_time.hour // 2 if birth_time else 0)) % 12
        ming_branch = _EARTHLY_BRANCHES[ming_branch_idx]

        # Distribute 14 main stars across 12 palaces
        star_palace: Dict[int, List[str]] = {i: [] for i in range(12)}
        for i, star in enumerate(_MAIN_STARS_14):
            palace_idx = (s // (i + 1) + i * 13) % 12
            star_palace[palace_idx].append(star)

        # Distribute minor stars
        minor_palace: Dict[int, List[str]] = {i: [] for i in range(12)}
        for i, star in enumerate(_MINOR_STARS):
            palace_idx = (s * (i + 2) + i * 7) % 12
            minor_palace[palace_idx].append(star)

        # Four transformations
        four_trans: Dict[str, str] = {}
        for star, transform in sihua_map.items():
            four_trans[star] = transform

        # Build per-palace transformation list
        def _palace_transforms(stars: List[str]) -> List[str]:
            return [f"{st}{sihua_map[st]}" for st in stars if st in sihua_map]

        def _build_palace(idx: int, name: str) -> ZiWeiPalace:
            branch = _EARTHLY_BRANCHES[(ming_branch_idx + idx) % 12]
            mstars = star_palace[idx]
            mnstars = minor_palace[idx]
            transforms = _palace_transforms(mstars + mnstars)
            return ZiWeiPalace(
                name=name,
                earthly_branch=branch,
                main_stars=mstars,
                minor_stars=mnstars,
                transformations=transforms,
                interpretation=_PALACE_INTERPRETATIONS.get(name, ""),
            )

        palaces = [_build_palace(i, _PALACE_NAMES[i]) for i in range(12)]

        # 身宮 (mock: place opposite 命宮)
        shen_idx = (ming_branch_idx + 6) % 12
        shen_palace = _build_palace(shen_idx, "身宮")

        # Identify all main stars present
        all_main = [s for stars in star_palace.values() for s in stars]

        return ZiWeiChart(
            ming_palace=palaces[0],
            shen_palace=shen_palace,
            brother_palace=palaces[1],
            spouse_palace=palaces[2],
            children_palace=palaces[3],
            wealth_palace=palaces[4],
            health_palace=palaces[5],
            travel_palace=palaces[6],
            friends_palace=palaces[7],
            career_palace=palaces[8],
            property_palace=palaces[9],
            fortune_palace=palaces[10],
            parents_palace=palaces[11],
            main_stars=all_main,
            four_transformations=four_trans,
            is_mock=True,
        )
