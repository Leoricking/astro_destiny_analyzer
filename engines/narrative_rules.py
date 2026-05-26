"""
Astro Destiny Analyzer — V1.2 Narrative Rules
Provides rich, paragraph-form text builders used by SynthesisEngine.
All functions return plain strings; no dependency on UI or DB layers.
"""
from typing import Optional, List


# ── Sign deep profiles ────────────────────────────────────────────────────────

_SIGN_DEEP: dict[str, dict] = {
    "牡羊座": {
        "personality": (
            "牡羊座是黃道的起點，象徵純粹的衝動與開創力。你的天性是勇敢出發、率先行動，"
            "甚至在策略尚未成形時便已踏出第一步。這份能量讓你在眾人還在觀望時已然起步，"
            "成為率先開闢路徑的先行者。然而，牡羊能量的挑戰在於持久力——"
            "點燃一把火容易，讓它持續燃燒則需要刻意的練習。"
            "你的領導力是天生的，不依賴頭銜，而來自那股讓人無法忽視的內在炎光。"
        ),
        "love": (
            "在感情中，你是熱情的追求者，享受愛情初期的激情與征服感。"
            "你需要一段有足夠火花與挑戰性的關係，以免熱情過快冷卻。"
            "給你空間與自主是維繫感情的關鍵——任何試圖束縛你的關係都會讓你感到窒息。"
        ),
        "career": (
            "在事業上，你最適合能夠快速看到成果的工作。"
            "長期等待回報的職涯容易讓你失去動力，而競爭性強的環境則能激發你最好的一面。"
            "創業或獨立工作往往比在大型官僚體系中更適合你的節奏。"
        ),
        "intimacy_boundary": "需要在激情中保有個人空間，避免在關係初期過度燃燒",
        "communication_advice": "直接坦率是你的優勢，但學習在溝通中加入停頓與傾聽，能讓關係更深化",
    },
    "金牛座": {
        "personality": (
            "金牛座是五感最敏銳的星座，你對物質世界有天生的鑑賞力。"
            "穩定、持久與可靠是你的核心特質，你不喜歡被倉促推入未知，"
            "但一旦決定，便以驚人的耐力堅持到底。"
            "你對生活品質的追求不是奢靡，而是一種對「值得」的堅持——你花時間與金錢的對象，"
            "必須通過你嚴格的內在審查。"
            "金牛的陰影面是固執：當改變真正必要時，你的穩定性可能演變為抗拒。"
        ),
        "love": (
            "在感情中，你是最忠誠的守護者之一。你的愛是用行動堆砌而成的——"
            "穩定的陪伴、物質的照顧、以及一個你用心構建的安全堡壘。"
            "你需要一個同樣重視穩定與承諾的伴侶，一段搖擺不定的關係會讓你感到極度不安。"
        ),
        "career": (
            "你在需要耐心積累的領域中往往能超越所有人。"
            "金融、地產、農業、工藝或任何需要長期眼光的行業都適合你。"
            "你不急於求成，但當成果到來，往往是最紮實且可持續的。"
        ),
        "intimacy_boundary": "在關係建立初期給予足夠時間，避免被催促作出承諾",
        "communication_advice": "學習在感到不安全時主動開口，而非以沉默或固執回應",
    },
    "雙子座": {
        "personality": (
            "雙子座是水星守護的空氣星座，你的心智永遠在高速運轉。"
            "你對世界的好奇心幾乎是貪婪的——你想同時了解一切、嘗試一切、討論一切。"
            "這份靈活讓你成為最具適應力的人，能夠在不同圈子間自如切換；"
            "然而，深度往往是你需要刻意培養的功課，"
            "因為跳躍的心智容易讓你在每個領域都只觸及表面。"
        ),
        "love": (
            "在感情中，你需要一個能夠在智識上刺激你的伴侶。"
            "無聊是你最大的感情殺手。你享受幽默、機智的對話，"
            "以及一段不斷有新鮮感注入的關係。"
            "讓你感到受限的伴侶，往往會讓你的心思飄向別處。"
        ),
        "career": (
            "你天生適合需要多工處理、快速思考與溝通的工作。"
            "媒體、寫作、銷售、教育或任何需要表達才能的領域都是你的舞台。"
            "固定單調的工作環境容易讓你感到枯萎。"
        ),
        "intimacy_boundary": "需要在關係中保有思想的自由度與社交空間",
        "communication_advice": "練習在輕盈的對話之外，也允許深度與脆弱的時刻出現",
    },
    "巨蟹座": {
        "personality": (
            "巨蟹座由月亮守護，是十二星座中情感能量最深厚的星座之一。"
            "你對氣氛的敏感幾乎像是一種超感知——你能感受到房間裡每個人的情緒狀態，"
            "甚至在對方尚未開口前便察覺到他們的需求。"
            "這份直覺是你最強大的天賦，也是你最大的脆弱點：當你的感受被誤解或忽視時，"
            "你可能退入外殼，用間接的方式表達受傷，而非正面溝通。"
        ),
        "love": (
            "在感情中，你是最有滋養能量的伴侶之一。"
            "你照顧對方的方式是細水長流的——記住對方說過的每件事、在他們脆弱時守候。"
            "你需要在感情中感到安全，才能完全打開自己。"
            "任何讓你感到情感不確定的關係，都會啟動你的自我保護機制。"
        ),
        "career": (
            "你在需要照顧、滋養與支持他人的職業中找到最深的滿足感。"
            "醫療、教育、諮商、餐飲或社會服務業都與你的天性契合。"
            "家族事業或有強烈歸屬感的職場環境能讓你發揮最佳狀態。"
        ),
        "intimacy_boundary": "需要感到情感安全後才能完全投入，不應被催促過早卸下防備",
        "communication_advice": "練習直接表達感受，而非等待對方猜測你的內心",
    },
    "獅子座": {
        "personality": (
            "獅子座由太陽守護，你的存在本身就帶有一種讓人無法忽視的光芒。"
            "你渴望被看見，不只是表面的注目，而是被真正理解和欣賞。"
            "這份渴望驅動著你創造、表達、領導——"
            "你用自己最好的一面回應這個世界，因為你相信分享這份光是一種責任。"
            "獅子的挑戰在於，當被忽視或受批評時，可能陷入防禦性的自大，"
            "需要學習區分真實的自我肯定與對外部認可的依賴。"
        ),
        "love": (
            "在感情中，你是熱情慷慨的伴侶，你愛得大方、守護得有力。"
            "你需要一個能夠欣賞你、讓你感到被珍視的伴侶。"
            "任何讓你長期感到被貶低或忽視的關係，"
            "都會讓獅子的傲氣成為保護自尊的盔甲。"
        ),
        "career": (
            "你在有舞台的工作中如魚得水——表演、領導、創作、公開演說。"
            "你需要一份讓你感到有意義、能夠展現才能的工作，"
            "而非僅僅是填滿時間的職位。"
        ),
        "intimacy_boundary": "需要被真誠欣賞而非奉承，區別二者的能力需要刻意培養",
        "communication_advice": "在表達自我的同時，練習主動為伴侶的光芒讓出空間",
    },
    "處女座": {
        "personality": (
            "處女座由水星守護，你的思維是一台高效的分析機器。"
            "你注意到其他人看不見的細節，這讓你成為任何系統最精準的維護者。"
            "你對品質的要求不是挑剔，而是一種對「事物應有最好狀態」的深刻信念。"
            "然而，完美主義的陰暗面是永無止境的自我批評——"
            "你對自己的標準往往遠高於對他人，而這可能成為你最大的內在消耗源。"
        ),
        "love": (
            "在感情中，你以服務和實際行動表達愛。"
            "你記得伴侶說過的每件事，並用具體的協助展現你的關心。"
            "你需要一個能夠接收你的細膩付出、不嘲笑你的完美傾向的伴侶。"
            "學習放下對關係「應有完美模樣」的執念，是你最重要的感情課題。"
        ),
        "career": (
            "你在需要精確度、分析力與系統思維的工作中天賦異稟。"
            "醫療、研究、編輯、數據分析、品管或任何需要高標準執行的職業都適合你。"
            "給你足夠的自主空間做到正確，比快速但粗糙的工作環境更能讓你發揮。"
        ),
        "intimacy_boundary": "需要在關係中保有個人時間用於自我整理，避免過度服務而消耗自我",
        "communication_advice": "練習接受「夠好就夠了」，允許伴侶以不完美的方式付出愛",
    },
    "天秤座": {
        "personality": (
            "天秤座由金星守護，你天生對和諧、美感與公平有強烈的渴望。"
            "你能夠本能地感受到任何情境中的不平衡，並有驅動去修正它。"
            "這讓你成為傑出的調解者與外交家，但也讓你在面對衝突時容易過度迴避。"
            "天秤的深層課題是學習在維護和諧的同時，也堅守自己的立場，"
            "而非為了迎合而放棄真實的自我。"
        ),
        "love": (
            "在感情中，你是最重視「我們」而非「我」的星座之一。"
            "伴侶關係對你而言有著幾乎存在性的重要——"
            "你在關係中找到鏡子，照見自己更完整的樣貌。"
            "你需要一個能夠欣賞你的優雅與平衡感，同時也能給你清晰立場的伴侶。"
        ),
        "career": (
            "你在需要協調、談判、美學判斷或公正裁量的工作中大放異彩。"
            "法律、外交、設計、藝術策展、人力資源或任何需要維持多方平衡的職業都與你相配。"
        ),
        "intimacy_boundary": "需要在關係中保有個人立場，避免為維持和諧而消融自我",
        "communication_advice": "練習在表達不同意見時不道歉，直接、尊重地說出你的真實想法",
    },
    "天蠍座": {
        "personality": (
            "天蠍座是十二星座中最具深度的存在。你的感知穿透表面，直達核心——"
            "你能看見別人的動機、感受到隱藏的議題，以及察覺到表面和諧下的真實張力。"
            "這份洞察力讓你成為最有力量的盟友，也可能成為令人敬畏的對手。"
            "天蠍的人生課題是學習運用這份穿透力來創造而非控制，"
            "以及在面對失去與背叛時找到真正的寬恕之道。"
        ),
        "love": (
            "在感情中，你是最全情投入的星座。你的愛是深水型的——"
            "緩慢沉入，但一旦扎根便難以撼動。"
            "你對伴侶的忠誠是絕對的，同樣地，你對背叛也幾乎不設容忍空間。"
            "學習在親密中允許脆弱，而非用控制換取安全感，是你最重要的感情修煉。"
        ),
        "career": (
            "你在需要深度研究、危機處理、財務操作或心理工作的領域中極具競爭力。"
            "投資、保險、心理治療、偵查、外科或任何需要穿透表面的工作都是你的領域。"
        ),
        "intimacy_boundary": "需要信任是緩慢建立的，不可被催促或強迫提前交出脆弱",
        "communication_advice": "練習在感受到威脅時用語言表達，而非用沉默或報復行動回應",
    },
    "射手座": {
        "personality": (
            "射手座由木星守護，你的靈魂渴望廣闊——廣闊的地理、廣闊的思想、廣闊的可能性。"
            "你是天生的哲學家與探索者，對「為什麼」和「更遠的地方」有永遠止不住的好奇。"
            "樂觀是你與生俱來的心理底色，即使在最黑暗的時刻你也能找到意義的光點。"
            "射手的課題是學習讓承諾落地，而非永遠活在下一個旅程的幻想中。"
        ),
        "love": (
            "在感情中，你需要一個能夠成為你冒險夥伴的人——"
            "一個能夠與你共同探索世界，同時尊重你對自由的根本需求的伴侶。"
            "任何試圖讓你定住的關係都會讓你感到窒息。"
            "你的感情課題是學習在保有自由的同時，也能深深地、承諾地愛一個人。"
        ),
        "career": (
            "你在能夠開拓視野、跨越邊界的工作中發光。"
            "教育、出版、國際業務、旅遊、哲學、法律或宗教領域都能容納你的探索需求。"
        ),
        "intimacy_boundary": "需要關係給予思想和行動的自由度，而非監控和限制",
        "communication_advice": "練習在承諾後的日常中尋找細節的美，而非只在宏大冒險中感受生命",
    },
    "摩羯座": {
        "personality": (
            "摩羯座由土星守護，你是十二星座中最有長遠戰略眼光的建構者。"
            "你對時間的理解是複利式的——"
            "今天的每一個選擇都在為未來的某個版本的你鋪路。"
            "這份能力讓你能夠忍受短期的困難、接受漫長的學習曲線，"
            "並在他人早已放棄的地方繼續前進。"
            "摩羯的課題是學習在攀登的途中也允許自己感受當下的喜悅，"
            "而非永遠以「還未到達頂峰」為由推遲快樂。"
        ),
        "love": (
            "在感情中，你是用行動和承諾表達愛的人。"
            "你不輕易說愛，但一旦承諾，便是完整的給出。"
            "你需要一個同樣重視長期關係、能夠欣賞你的踏實與可靠的伴侶。"
            "你的感情課題是學習在關係中允許脆弱和情緒的流動，"
            "而非永遠以「強者」的姿態出現。"
        ),
        "career": (
            "你在需要長期規劃、嚴格自律與專業積累的領域中無可匹敵。"
            "企業管理、金融、工程、政府部門或任何需要一步一腳印建立的事業都是你的舞台。"
        ),
        "intimacy_boundary": "需要以自己的節奏建立信任和親密，不應被催促展現脆弱",
        "communication_advice": "練習表達情感需求和脆弱，而非只有任務和計畫的溝通",
    },
    "水瓶座": {
        "personality": (
            "水瓶座由天王星（現代）與土星（傳統）共同守護，你的靈魂來自未來。"
            "你對現狀的反應往往是「這可以更好」——"
            "這份革新衝動是推動你創造、發明與顛覆的核心動力。"
            "你的思維超越個人範疇，習慣以集體、系統和長遠的視角思考問題。"
            "水瓶的課題是學習在仰望星空的同時，也照顧到身邊人的情感需求，"
            "不讓智識上的距離演變為人際上的冷漠。"
        ),
        "love": (
            "在感情中，你需要一個能夠做你精神同伴的人。"
            "普通的甜蜜對你的吸引力有限，你需要思想的刺激、價值觀的共鳴，"
            "以及一段能夠讓你保有個人空間的關係。"
            "你的感情課題是學習在智識距離與情感親密之間找到平衡。"
        ),
        "career": (
            "你在可以改變現狀的工作中找到使命感。"
            "科技、社會創新、研究、人道主義工作或任何需要顛覆性思維的領域都適合你。"
        ),
        "intimacy_boundary": "需要關係尊重個人的思想自由與生活方式選擇",
        "communication_advice": "練習從對方的情感體驗出發溝通，而非總是從邏輯和概念層面分析",
    },
    "雙魚座": {
        "personality": (
            "雙魚座由海王星（現代）與木星（傳統）守護，你是十二星座的終點——"
            "你在靈魂層面融合了所有前十一個星座的能量。"
            "你的直覺穿透現實的邊界，你的同理心幾乎沒有邊界。"
            "這讓你成為最具療癒能量的存在，同時也讓你容易在人群中失去自我的輪廓。"
            "雙魚的課題是學習在深情之中保持自我，"
            "以及分辨何時是出於愛而付出、何時是因為無法說「不」而耗損。"
        ),
        "love": (
            "在感情中，你有幾乎無限的包容與理想化傾向。"
            "你能看見伴侶最好的可能，並傾向用你的愛去喚醒它。"
            "你的感情課題是學習愛一個真實存在的人，"
            "而非你幻想中的版本，以及在親密關係中建立清晰的邊界。"
        ),
        "career": (
            "你在需要直覺、創意、療癒或服務他人的工作中找到靈魂的出口。"
            "藝術、音樂、心理治療、靈性工作、醫療護理或海洋相關領域都與你的頻率相符。"
        ),
        "intimacy_boundary": "需要在關係中建立清晰的個人邊界，避免在伴侶的情緒海洋中迷失自我",
        "communication_advice": "練習用語言表達需求，而非期待對方感應你的感受",
    },
}

# Fallback for any sign not in the table
_SIGN_DEEP_DEFAULT = {
    "personality": "你的星座帶來獨特的能量與天賦，是你個人風格的重要組成部分。",
    "love": "在感情中，你有自己獨特的表達方式與需求。",
    "career": "你的星座賦予你特定的職業優勢與傾向。",
    "intimacy_boundary": "需要伴侶尊重你的個人節奏與邊界",
    "communication_advice": "開放且誠實的溝通是關係健康的基礎",
}


def get_sign_profile(sign_name: str) -> dict:
    return _SIGN_DEEP.get(sign_name, _SIGN_DEEP_DEFAULT)


# ── Love Narrative Builder ────────────────────────────────────────────────────

def build_love_narrative(
    sun_sign: Optional[str] = None,
    venus_sign: Optional[str] = None,
    moon_sign: Optional[str] = None,
    descendant: Optional[str] = None,
    bazi_wealth_star: Optional[str] = None,
    ziwei_spouse_stars: Optional[List[str]] = None,
    blood_love: Optional[str] = None,
    intimacy_boundary: str = "",
    communication_advice: str = "",
) -> str:
    """
    Build a rich, paragraph-form love pattern narrative.

    Parameters
    ----------
    sun_sign            : 太陽星座
    venus_sign          : 金星星座（愛的語言）
    moon_sign           : 月亮星座（情感底層需求）
    descendant          : 下降點星座（第七宮）
    bazi_wealth_star    : 八字財星（感情緣分）
    ziwei_spouse_stars  : 紫微夫妻宮主星
    blood_love          : 血型感情反應文字
    intimacy_boundary   : 自訂親密邊界描述（可覆蓋預設值）
    communication_advice: 自訂溝通建議（可覆蓋預設值）
    """
    parts: List[str] = []

    # Venus
    if venus_sign:
        vp = get_sign_profile(venus_sign)
        parts.append(
            f"**金星語言（{venus_sign}）**\n\n"
            f"金星落在{venus_sign}，是你愛與美的主要頻率。{vp['love']}"
        )

    # Moon emotional foundation
    if moon_sign:
        mp = get_sign_profile(moon_sign)
        parts.append(
            f"**月亮情感底層（{moon_sign}）**\n\n"
            "月亮代表你最深層的情感安全感需求，是你在私密關係中真正被滿足的頻率。"
            f"月亮在{moon_sign}：{mp['love']}"
        )

    # Descendant
    if descendant:
        dp = get_sign_profile(descendant)
        parts.append(
            f"**第七宮（下降點：{descendant}）——你吸引的伴侶類型**\n\n"
            f"下降點揭示了你在長期關係中需要的互補能量，以及你容易吸引的對象特質。"
            f"你下降點位於{descendant}，{dp['personality']}"
            "這些特質的人往往既讓你著迷，也帶來你最深刻的成長挑戰。"
        )

    # BaZi
    if bazi_wealth_star:
        parts.append(
            f"**八字財星觀點（{bazi_wealth_star}）**\n\n"
            f"八字中，財星（{bazi_wealth_star}）在傳統命理中代表你的感情緣分與伴侶特質。"
            "財星的強弱與位置，影響了你在感情中是主動追求還是等待時機，"
            "以及你與伴侶的能量如何相互流動。"
        )

    # Zi Wei
    if ziwei_spouse_stars:
        stars_str = "、".join(ziwei_spouse_stars) if ziwei_spouse_stars else "無主星"
        parts.append(
            f"**紫微夫妻宮（主星：{stars_str}）**\n\n"
            "紫微夫妻宮揭示了婚姻或長期伴侶關係的核心格局，"
            "反映了你在親密關係中的主要互動模式，以及關係中可能出現的挑戰與資源。"
        )

    # Blood type
    if blood_love:
        parts.append(f"**血型輔助觀點**\n\n{blood_love}")

    # Intimacy boundary
    ib = intimacy_boundary or "在感情中建立清晰的個人邊界，有助於維持長期關係的健康"
    ca = communication_advice or "開放與誠實的溝通是所有深度關係的基礎"
    parts.append(
        f"**親密邊界與溝通建議**\n\n"
        f"邊界建議：{ib}\n\n"
        f"溝通建議：{ca}"
    )

    return "\n\n---\n\n".join(parts) if parts else "感情模式分析需要更完整的出生資料。"


# ── Career Narrative Builder ──────────────────────────────────────────────────

def build_career_narrative(
    sun_sign: Optional[str] = None,
    mc_sign: Optional[str] = None,
    mars_sign: Optional[str] = None,
    bazi_power_star: Optional[str] = None,
    ziwei_career_stars: Optional[List[str]] = None,
    lp_careers: Optional[List[str]] = None,
    life_path_number: Optional[int] = None,
    career_star_descs: Optional[dict] = None,
) -> str:
    parts: List[str] = []

    if sun_sign:
        sp = get_sign_profile(sun_sign)
        parts.append(
            f"**太陽星座事業能量（{sun_sign}）**\n\n{sp['career']}"
        )

    if mc_sign:
        mp = get_sign_profile(mc_sign)
        parts.append(
            f"**天頂 MC（{mc_sign}）——社會舞台與職業聲望**\n\n"
            f"天頂是你在職業領域對外展現的最高形象，也是你渴望在社會上被認可的方式。"
            f"MC位於{mc_sign}：{mp['career']}"
        )

    if mars_sign:
        mp2 = get_sign_profile(mars_sign)
        parts.append(
            f"**火星（{mars_sign}）——執行力與工作驅力**\n\n"
            f"火星揭示你在工作中的衝勁、競爭風格與面對挑戰的方式。"
            f"火星在{mars_sign}：{mp2['career']}"
        )

    if bazi_power_star:
        parts.append(
            f"**八字官殺（{bazi_power_star}）——職場關係與權威互動**\n\n"
            f"官殺代表你與職場規範、上司、體制的關係模式。"
            f"官殺（{bazi_power_star}）的強弱決定了你在組織中的適應度與自主性需求。"
            "官殺旺者事業心強，但需注意避免過度對抗體制；官殺弱者較適合獨立工作或創業。"
        )

    if ziwei_career_stars and career_star_descs:
        star_texts = []
        for star in ziwei_career_stars:
            desc = career_star_descs.get(star, "")
            if desc:
                star_texts.append(f"- {star}：{desc}")
        if star_texts:
            parts.append(
                "**紫微官祿宮——事業格局**\n\n"
                + "\n".join(star_texts)
            )

    if life_path_number and lp_careers:
        parts.append(
            f"**生命靈數 {life_path_number} 建議職業方向**\n\n"
            f"與你生命靈數頻率最契合的職業包括：{'、'.join(lp_careers)}。"
            "這些方向不是限制，而是與你天生能量最共鳴的起點。"
        )

    return "\n\n---\n\n".join(parts) if parts else "事業模式分析需要更完整的出生資料。"


# ── Stress & Shadow Narrative Builder ────────────────────────────────────────

def build_stress_narrative(
    saturn_sign: Optional[str] = None,
    chiron_sign: Optional[str] = None,
    unfav_elements: Optional[List[str]] = None,
    blood_stress: Optional[str] = None,
) -> str:
    parts: List[str] = []

    if saturn_sign:
        sp = get_sign_profile(saturn_sign)
        parts.append(
            f"**土星課題（{saturn_sign}）**\n\n"
            f"土星標記了你最深的成長障礙與終生功課。它不是懲罰，"
            f"而是一份要求你付出比任何人更多努力才能精熟的禮物。"
            f"土星在{saturn_sign}：{sp['personality']}\n\n"
            f"在這個領域，每一次遭遇挫折都是土星在邀請你深化根基。"
            "長期在此領域持續積累的人，往往在中年以後成為這個領域真正的權威。"
        )

    if chiron_sign:
        cp = get_sign_profile(chiron_sign)
        parts.append(
            f"**凱龍傷口（{chiron_sign}）——受傷之處即療癒之源**\n\n"
            f"凱龍星揭示你最深的靈性傷口——那個你覺得自己「就是不行」或「不夠好」的地方。"
            f"凱龍在{chiron_sign}：{cp['personality']}\n\n"
            "弔詭的是，你在這個領域最深的傷，往往也是你能夠為他人帶來最深療癒的地方。"
            "當你開始接觸並整合這份傷，你的使命往往從中浮現。"
        )

    if unfav_elements:
        elems = "、".join(unfav_elements)
        parts.append(
            f"**八字忌神（{elems}）——容易遭遇阻力的能量頻率**\n\n"
            f"忌神代表當這些五行能量在你的生命環境中過旺時，往往帶來阻礙與挑戰。"
            "忌神流年是需要守成、謹慎的時期，但也是快速成長的契機——"
            "因為阻力本身是最誠實的老師。了解忌神，能讓你在困難期做出更明智的選擇，"
            "而非只是被動承受。"
        )

    if blood_stress:
        parts.append(f"**壓力反應模式（血型輔助）**\n\n{blood_stress}")

    return "\n\n---\n\n".join(parts) if parts else "壓力與陰影分析需要更完整的出生資料。"


# ── Contradiction Analysis ────────────────────────────────────────────────────

def build_contradiction_analysis(
    bazi_element_strength: Optional[dict] = None,
    sun_sign: Optional[str] = None,
    life_path_number: Optional[int] = None,
    dm_is_strong: bool = False,
) -> tuple[List[str], List[str]]:
    """Returns (contradictions, integration_suggestions)."""
    contradictions: List[str] = []
    suggestions: List[str] = []

    if bazi_element_strength and sun_sign:
        fire_str = bazi_element_strength.get("火", "均衡")
        water_str = bazi_element_strength.get("水", "均衡")
        sun_water = sun_sign in ("天蠍座", "雙魚座", "巨蟹座")
        sun_fire  = sun_sign in ("牡羊座", "獅子座", "射手座")

        if fire_str == "強" and sun_water:
            contradictions.append(
                "**矛盾一：八字火旺 ╳ 水象太陽**\n\n"
                "八字五行火旺，代表你天生具有強烈的熱情、驅動力與對外能量；"
                "然而太陽星座屬水象（內省、敏感、需要深度），這兩種能量在你身上形成一種"
                "「外熱內冷」的雙重性——對外你充滿活力、積極主動，"
                "內心深處卻需要大量獨處時間與情感沉澱。"
                "他人可能對你的「突然安靜」感到困惑，而你自己也可能在這兩種衝動之間感到撕裂。"
            )
            suggestions.append(
                "**整合方向**：與其在「外向衝動」與「內省需求」之間二選一，"
                "不如設計一個循環節奏——強烈的對外行動期之後，刻意安排同等比例的深度獨處時間。"
                "讓這兩種能量輪流工作，而非相互壓制。"
            )

        if water_str == "強" and sun_fire:
            contradictions.append(
                "**矛盾二：八字水旺 ╳ 火象太陽**\n\n"
                "八字水旺代表你有豐富的情感直覺與思慮深度，容易過度分析和多愁善感；"
                "但太陽位於火象星座，本能渴望熱情行動與即時回饋。"
                "這可能讓你在行動之前花費過多時間在內部分析，"
                "或者衝動行動後又陷入深度自省與懊悔。"
            )
            suggestions.append(
                "**整合方向**：為自己設置決策時限——給直覺一個明確的截止時間，"
                "在期限前盡情分析，時間到了就允許行動力接手。"
                "避免讓思慮演變為行動的阻礙。"
            )

    if life_path_number and bazi_element_strength:
        if life_path_number in (1, 8) and not dm_is_strong:
            contradictions.append(
                f"**矛盾：生命靈數 {life_path_number} ╳ 八字日主偏弱**\n\n"
                f"生命靈數 {life_path_number} 帶來強烈的成就驅力與獨立意志；"
                "然而八字日主偏弱，意味著你的底層能量可能不足以長期支撐這份雄心。"
                "這可能表現為：你有強大的志向，卻在執行過程中容易耗盡，"
                "或者需要依賴外部力量才能落地。"
            )
            suggestions.append(
                "**整合方向**：優先投資於強化喜用神的生活習慣——"
                "包括居住環境的五行調整、飲食選擇、運動方式——"
                "為你的雄心建立更穩固的能量基礎。同時，學習策略性借力，"
                "讓合適的合作夥伴補足你的短板，而非強行單打獨鬥。"
            )

        if life_path_number in (2, 6) and dm_is_strong:
            contradictions.append(
                f"**矛盾：生命靈數 {life_path_number} ╳ 八字日主旺**\n\n"
                f"生命靈數 {life_path_number} 帶來服務、協作與和諧的使命感；"
                "但八字日主偏強，天生具有強烈的自主意識與獨立性。"
                "你可能在想要幫助他人與想要主導一切之間感到拉扯，"
                "或者在服務模式中無意識地加入控制傾向。"
            )
            suggestions.append(
                "**整合方向**：將你的強大日主能量用於「賦能他人而非主導他人」——"
                "從提供資源、清除障礙的角度去服務，而非定義他人應走的路。"
            )

    return contradictions, suggestions
