"""
Astro Destiny Analyzer — Numerology Engine
Implements: Life Path, Birthday, Talent, Personal Year numbers.
All calculations are deterministic; no mock layer required.
"""
from datetime import date
from typing import Optional
from core.models import NumerologyChart


# ── Core Reduction ────────────────────────────────────────────────────────────

MASTER_NUMBERS = {11, 22, 33}


def _reduce(n: int, keep_master: bool = True) -> int:
    """Reduce an integer to a single digit (1–9) or master number (11/22/33)."""
    while n > 9:
        if keep_master and n in MASTER_NUMBERS:
            break
        n = sum(int(d) for d in str(n))
    return n


def _digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


# ── Number Descriptions ───────────────────────────────────────────────────────

_LIFE_PATH_DESC = {
    1:  "生命靈數 1：開創者。你擁有強烈的獨立意志與領導力，天生具備開拓精神。你的人生課題是學會在自信與自我中心之間取得平衡，在堅持自我主張的同時接受他人的協助與貢獻。",
    2:  "生命靈數 2：合作者。你敏感細膩、善於傾聽，天生具備外交手腕與同理心。你的人生課題是建立清晰的個人界線，學會在照顧他人的同時，也為自己的需求發聲。",
    3:  "生命靈數 3：創造者。你充滿表達欲與創意，熱愛社交、語言與藝術。你的人生課題是將豐沛的靈感落地為實際成果，避免因過度分散注意力而讓潛力空轉。",
    4:  "生命靈數 4：建造者。你務實、可靠、注重秩序，是任何組織與家庭的基石。你的人生課題是在穩定與彈性之間找到節奏，學會接受變化而非抗拒它。",
    5:  "生命靈數 5：探索者。你崇尚自由、變化與感官體驗，活力充沛、思維靈活。你的人生課題是在自由與責任之間取得平衡，找到一個讓你既能飛翔又有根基的人生定位。",
    6:  "生命靈數 6：照護者。你天生具有責任感與美感，重視家庭、和諧與付出。你的人生課題是學會接受不完美，避免因過度承擔他人問題而忽視自己的需求。",
    7:  "生命靈數 7：智者。你擅長深度思考與靈性探索，對知識與真理有強烈渴望。你的人生課題是走出內在世界，學會與他人連結，以你的智慧服務更廣泛的群體。",
    8:  "生命靈數 8：成就者。你具有天生的商業直覺與執行力，對權力與物質成就有明確追求。你的人生課題是在積累力量的同時培養內在豐盛感，避免以外在成就填補內心空洞。",
    9:  "生命靈數 9：人道主義者。你富有悲憫、理想主義與奉獻精神，渴望讓世界變得更好。你的人生課題是學會放下與完結，接受失去是為了騰出空間迎接更大的圓滿。",
    11: "生命靈數 11（大師數）：啟示者。你具有超凡的直覺與靈性敏感度，是傳遞啟示的管道。你的人生課題是克服焦慮與自我懷疑，學會接地氣地將內在洞見轉化為對他人有實際幫助的行動。",
    22: "生命靈數 22（大師數）：大師建造者。你擁有將宏大願景化為現實的罕見能力，是理想主義與實用主義的結合。你的人生課題是承擔你的使命而不迷失在自我膨脹中，讓你的工程服務人類而非服務自我。",
    33: "生命靈數 33（大師數）：大師教師。你體現了愛、療癒與奉獻的最高原則，具有深刻的同理心與無條件的關懷能力。你的人生課題是從力量而非恐懼中奉獻，先滋養自己，才能真正滋養他人。",
}

_BIRTHDAY_DESC = {
    1:  "生日數 1：你天生帶有獨立、主動的能量，渴望在生命中留下個人印記。",
    2:  "生日數 2：你具備敏銳的協調能力，是天生的調解者與合夥人。",
    3:  "生日數 3：你充滿創意與表達的才華，語言與藝術是你的自然媒介。",
    4:  "生日數 4：你踏實可靠，擅長將計畫轉化為具體結果。",
    5:  "生日數 5：你靈活多變，擁有對新知識與新體驗的強烈好奇心。",
    6:  "生日數 6：你天生散發溫暖與責任感，對家庭與社群有深厚的承諾。",
    7:  "生日數 7：你擁有深刻的分析力與靈性探求的天賦。",
    8:  "生日數 8：你的天賦在於組織、管理與驅動實際成果。",
    9:  "生日數 9：你具有廣闊的視野與服務人類的熱情。",
    10: "生日數 10：你兼具領導力（1）與全方位潛能（0），是具有開創性眼界的實踐者。",
    11: "生日數 11：你靈性敏感度極高，直覺是你最強大的工具。",
    22: "生日數 22：你擁有將遠大理想落地的非凡能力。",
    33: "生日數 33：你體現了無條件的愛與奉獻，是最高頻率的療癒能量。",
}

_TALENT_DESC = {
    1: "天賦數 1：你具有開創新局的能量，善於率先行動。",
    2: "天賦數 2：你的天賦在於聯結人與人，創造和諧共鳴。",
    3: "天賦數 3：溝通與創作是你天生的語言，你的表達能力是一種禮物。",
    4: "天賦數 4：你的天賦是建立秩序與結構，讓混亂成為系統。",
    5: "天賦數 5：你天生的適應力與靈活性讓你在變化中找到機會。",
    6: "天賦數 6：你的天賦是照顧與療癒，你所在之處自然形成溫暖的場域。",
    7: "天賦數 7：深度探究是你的本能，你天生具有研究者與哲學家的氣質。",
    8: "天賦數 8：你的天賦是將資源轉化為成就，具有天然的商業與管理直覺。",
    9: "天賦數 9：你天生具備宏觀視野與人道熱情，能夠為群體帶來啟示。",
}

_PERSONAL_YEAR_DESC = {
    1: "個人年 1：全新循環的啟動年。這一年的核心主題是重新出發、播種新計畫與確立個人意志。適合大膽採取主動行動，啟動你一直想嘗試的新項目。",
    2: "個人年 2：合作與耐心的成長年。這一年適合深化關係、培育已播下的種子，而非強行推進。重要的合作夥伴或關鍵人脈可能在此年出現。",
    3: "個人年 3：表達與創造的豐盛年。溝通、創意與社交在這一年來到高峰。適合發揮你的表達才華、拓展人際網絡，以及享受生命帶來的喜悅。",
    4: "個人年 4：建立基礎的勤耕年。這一年要求腳踏實地的努力與規劃。有助於建立長期穩定的結構——事業基礎、健康習慣、財務系統。",
    5: "個人年 5：自由與變化的轉型年。這一年充滿意外的轉折與機遇，適合嘗試新事物、擴展視野，但也要注意不要過度分散。",
    6: "個人年 6：責任與家庭的承諾年。這一年的焦點回到家庭、親密關係與社群。適合修復關係、承擔長期責任，或為他人服務。",
    7: "個人年 7：內省與靈性的深化年。這是一個向內探索的時期，適合學習、研究、靜心與靈性修煉。此年的洞見將成為未來決策的深層基礎。",
    8: "個人年 8：成就與豐收的收穫年。過去幾年的努力在此年開始顯化。事業、財富與影響力的議題來到前台，是大步邁進的好時機。",
    9: "個人年 9：完結與放下的清理年。這是九年循環的最後一年，適合清理不再服務你的人事物，為下一個循環的嶄新出發做準備。",
}


# ── Engine ────────────────────────────────────────────────────────────────────

class NumerologyEngine:
    def calculate(self, birth_date: date, current_year: Optional[int] = None) -> NumerologyChart:
        if current_year is None:
            from datetime import date as _d
            current_year = _d.today().year

        life_path = self._life_path(birth_date)
        birthday  = self._birthday_number(birth_date)
        talent    = self._talent_number(birth_date)
        personal_year = self._personal_year(birth_date, current_year)

        return NumerologyChart(
            life_path_number=life_path,
            birthday_number=birthday,
            talent_number=talent,
            personal_year=personal_year,
            life_path_description=_LIFE_PATH_DESC.get(life_path, f"生命靈數 {life_path}"),
            birthday_description=_BIRTHDAY_DESC.get(birthday, f"生日數 {birthday}"),
            talent_description=_TALENT_DESC.get(talent, f"天賦數 {talent}"),
            personal_year_description=_PERSONAL_YEAR_DESC.get(personal_year % 9 or 9,
                                                               f"個人年 {personal_year}"),
        )

    def _life_path(self, d: date) -> int:
        """Sum all digits of YYYY MM DD, reduce to single/master."""
        total = _digit_sum(d.year) + _digit_sum(d.month) + _digit_sum(d.day)
        return _reduce(total)

    def _birthday_number(self, d: date) -> int:
        day = d.day
        if day in MASTER_NUMBERS:
            return day
        return _reduce(_digit_sum(day))

    def _talent_number(self, d: date) -> int:
        """Talent = month + day reduced."""
        total = _digit_sum(d.month) + _digit_sum(d.day)
        return _reduce(total)

    def _personal_year(self, d: date, current_year: int) -> int:
        total = _digit_sum(d.month) + _digit_sum(d.day) + _digit_sum(current_year)
        n = _reduce(total, keep_master=False)
        return n if n != 0 else 9
