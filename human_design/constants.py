"""
Astro Destiny Analyzer — Human Design Constants (V1.9.0 Phase 1)

Gate wheel, channel definitions, center info, type/authority tables.

NOTE: I_CHING_WHEEL_ORDER_PHASE1 is based on the standard Human Design Mandala
gate sequence starting from 0° Aries. This table should be externally validated
against a reference Human Design software for production use.
"""

# ── I-Ching Wheel Gate Order ──────────────────────────────────────────────────
# 64 gates in ecliptic order starting from 0° Aries (Vernal Equinox = Gate 41).
# Each gate spans 5.625°. This is the standard HD Mandala sequence.
# Phase 1 — external validation recommended before production deployment.

I_CHING_WHEEL_ORDER_PHASE1 = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
    27, 24, 2,  23, 8,  20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
    31, 33, 7,  4,  29, 59, 40, 64, 47, 6,  46, 18, 48, 57, 32, 50,
    28, 44, 1,  43, 14, 34, 9,  5,  26, 11, 10, 58, 38, 54, 61, 60,
]

assert len(I_CHING_WHEEL_ORDER_PHASE1) == 64
assert len(set(I_CHING_WHEEL_ORDER_PHASE1)) == 64

# ── Gate Info ─────────────────────────────────────────────────────────────────
# Fields: name, center, theme, interpretation

GATE_INFO = {
    1:  {"name": "Self-Expression",     "center": "G",            "theme": "創造力與自我表達",    "interpretation": "Gate 1 帶來強烈的創造衝動，渴望透過獨特方式展現自我。"},
    2:  {"name": "Receptive",           "center": "G",            "theme": "接收與方向",          "interpretation": "Gate 2 是方向感的來源，接收宇宙指引，自然吸引資源流入。"},
    3:  {"name": "Ordering",            "center": "Sacral",       "theme": "混沌中建立秩序",      "interpretation": "Gate 3 面對開始時的混亂，帶來突破性的新秩序。"},
    4:  {"name": "Formulization",       "center": "Ajna",         "theme": "邏輯公式化",          "interpretation": "Gate 4 擅長將複雜問題轉化為清晰公式與解答。"},
    5:  {"name": "Fixed Patterns",      "center": "Sacral",       "theme": "固定節奏與習慣",      "interpretation": "Gate 5 建立穩定的節奏與模式，為周遭帶來可預測性。"},
    6:  {"name": "Friction",            "center": "Solar Plexus", "theme": "情緒摩擦與親密",      "interpretation": "Gate 6 透過情緒摩擦探索親密關係的邊界與可能性。"},
    7:  {"name": "The Army",            "center": "G",            "theme": "領導角色",            "interpretation": "Gate 7 帶有自然的領導潛力，能在關鍵時刻被推舉為方向引導者。"},
    8:  {"name": "Contribution",        "center": "Throat",       "theme": "個人貢獻",            "interpretation": "Gate 8 渴望以獨特方式為集體作出真實貢獻。"},
    9:  {"name": "Focus",               "center": "Sacral",       "theme": "細節專注力",          "interpretation": "Gate 9 帶來精細專注的能力，能深入鑽研特定細節。"},
    10: {"name": "Behavior of the Self","center": "G",            "theme": "愛自己的行為",        "interpretation": "Gate 10 強調真實自我表達，活出符合本性的行為模式。"},
    11: {"name": "Ideas",               "center": "Ajna",         "theme": "豐富的想法",          "interpretation": "Gate 11 是思想的泉源，自然流溢各種創意概念。"},
    12: {"name": "Caution",             "center": "Throat",       "theme": "謹慎表達",            "interpretation": "Gate 12 在表達前需要情緒準備，謹慎選擇開口時機。"},
    13: {"name": "Listener",            "center": "G",            "theme": "傾聽與保密",          "interpretation": "Gate 13 是天生的傾聽者，能接收並保存他人的故事與秘密。"},
    14: {"name": "Power Skills",        "center": "Sacral",       "theme": "資源累積能力",        "interpretation": "Gate 14 帶來累積資源與財富的強大能力，方向正確時事半功倍。"},
    15: {"name": "Extremes",            "center": "G",            "theme": "涵容各種極端",        "interpretation": "Gate 15 擁抱人類行為的各種極端，帶來極大的包容性。"},
    16: {"name": "Skills",              "center": "Throat",       "theme": "技能與熱情",          "interpretation": "Gate 16 帶來對技能精進的熱情，透過反覆練習達到卓越。"},
    17: {"name": "Opinions",            "center": "Ajna",         "theme": "觀點與意見",          "interpretation": "Gate 17 能形成具體觀點，並以邏輯方式表達與辯護。"},
    18: {"name": "Correction",          "center": "Spleen",       "theme": "修正與批判",          "interpretation": "Gate 18 帶來敏銳的辨識能力，能看見需要改進之處。"},
    19: {"name": "Wanting",             "center": "Root",         "theme": "需求與渴望",          "interpretation": "Gate 19 對情感連結與被需要有深刻渴望，善於感知他人需求。"},
    20: {"name": "Contemplation",       "center": "Throat",       "theme": "當下覺知",            "interpretation": "Gate 20 帶來活在當下的能力，思考能立即轉化為行動或語言。"},
    21: {"name": "Biting Through",      "center": "Heart",        "theme": "控制與掌握",          "interpretation": "Gate 21 需要掌控自身資源，帶來強烈的自主意志與執行力。"},
    22: {"name": "Openness",            "center": "Solar Plexus", "theme": "情緒開放性",          "interpretation": "Gate 22 帶來優雅的情緒表達，以開放的心態吸引特殊時刻。"},
    23: {"name": "Assimilation",        "center": "Throat",       "theme": "化繁為簡",            "interpretation": "Gate 23 能將複雜知識轉化為清晰簡單的概念傳遞給他人。"},
    24: {"name": "Return",              "center": "Ajna",         "theme": "反覆思考",            "interpretation": "Gate 24 透過反覆回顧與沉思，最終得出深刻洞見。"},
    25: {"name": "Innocence",           "center": "G",            "theme": "純真之愛",            "interpretation": "Gate 25 帶來無條件的普世之愛，以純真視角看待人類。"},
    26: {"name": "The Taming Power",    "center": "Heart",        "theme": "說服與影響力",        "interpretation": "Gate 26 是強大的說服者，善於傳遞訊息並影響他人行動。"},
    27: {"name": "Caring",              "center": "Sacral",       "theme": "滋養與照顧",          "interpretation": "Gate 27 帶來強烈的照顧衝動，關注他人的健康與福祉。"},
    28: {"name": "The Game Player",     "center": "Spleen",       "theme": "生存挑戰",            "interpretation": "Gate 28 帶來深刻的生命意義探索，透過挑戰找到存在價值。"},
    29: {"name": "Perseverance",        "center": "Sacral",       "theme": "承諾與堅持",          "interpretation": "Gate 29 帶來強大的堅持力，一旦承諾便全力以赴。"},
    30: {"name": "Feelings",            "center": "Solar Plexus", "theme": "情感深度",            "interpretation": "Gate 30 帶有強烈的情感渴望，追求豐富深刻的人生體驗。"},
    31: {"name": "Influence",           "center": "Throat",       "theme": "民主影響力",          "interpretation": "Gate 31 帶來集體領導的潛力，能影響群體方向。"},
    32: {"name": "Continuity",          "center": "Spleen",       "theme": "延續與保存",          "interpretation": "Gate 32 具備辨識什麼值得保存的直覺，重視傳承與延續。"},
    33: {"name": "Retreat",             "center": "Throat",       "theme": "隱退與記憶",          "interpretation": "Gate 33 帶來從過去汲取智慧並知道何時退場的能力。"},
    34: {"name": "Power",               "center": "Sacral",       "theme": "強大生命力",          "interpretation": "Gate 34 是純粹的生命動能，帶來充沛的行動力與自主能量。"},
    35: {"name": "Change",              "center": "Throat",       "theme": "渴望變化",            "interpretation": "Gate 35 帶來對新體驗的渴望，在多樣化經歷中積累人生智慧。"},
    36: {"name": "Crisis",              "center": "Solar Plexus", "theme": "情緒危機與成長",      "interpretation": "Gate 36 透過情緒危機與黑暗期，最終轉化為深刻的人生智慧。"},
    37: {"name": "Friendship",          "center": "Solar Plexus", "theme": "家族與盟約",          "interpretation": "Gate 37 重視家族與社群，透過協議和信任建立緊密連結。"},
    38: {"name": "Opposition",          "center": "Root",         "theme": "奮鬥精神",            "interpretation": "Gate 38 帶來頑強的奮鬥意志，在阻力中找到人生意義。"},
    39: {"name": "Provocation",         "center": "Root",         "theme": "激發潛能",            "interpretation": "Gate 39 透過挑戰他人激發潛能，測試情緒靈活度。"},
    40: {"name": "Aloneness",           "center": "Heart",        "theme": "獨處需求",            "interpretation": "Gate 40 需要獨處時間來恢復能量，並為社群作出回饋。"},
    41: {"name": "Contraction",         "center": "Root",         "theme": "開始新循環",          "interpretation": "Gate 41 是新循環的開端，帶來對新體驗的原始渴望與期待。"},
    42: {"name": "Completion",          "center": "Sacral",       "theme": "完成週期",            "interpretation": "Gate 42 帶來善始善終的能力，能感知何時一個週期已完成。"},
    43: {"name": "Breakthrough",        "center": "Ajna",         "theme": "突破性洞見",          "interpretation": "Gate 43 帶來內在的獨特洞見，突破常規思維模式。"},
    44: {"name": "Coming to Meet",      "center": "Spleen",       "theme": "直覺辨識模式",        "interpretation": "Gate 44 能本能辨識過去的模式，避免重蹈覆轍。"},
    45: {"name": "Gathering Together",  "center": "Throat",       "theme": "群體資源分配",        "interpretation": "Gate 45 具備集結資源、管理社群的天然傾向。"},
    46: {"name": "Pushing Upward",      "center": "G",            "theme": "身體覺知",            "interpretation": "Gate 46 重視身體感知，帶來對物質世界的樂觀與幸運感。"},
    47: {"name": "Oppression",          "center": "Ajna",         "theme": "回顧與理解",          "interpretation": "Gate 47 能從過去的困境中提煉意義，轉化壓力為智慧。"},
    48: {"name": "The Well",            "center": "Spleen",       "theme": "深度能力",            "interpretation": "Gate 48 帶有深厚的知識底蘊，但容易擔憂自身能力不足。"},
    49: {"name": "Revolution",          "center": "Solar Plexus", "theme": "原則與革命",          "interpretation": "Gate 49 依據原則決定接受或拒絕，帶來革命性的轉變。"},
    50: {"name": "Cauldron",            "center": "Spleen",       "theme": "價值觀守護",          "interpretation": "Gate 50 守護社群法則與道德標準，帶來強烈的責任感。"},
    51: {"name": "Shock",               "center": "Heart",        "theme": "震撼與競爭",          "interpretation": "Gate 51 在震驚與衝擊中找到勇氣，帶來初始競爭的能量。"},
    52: {"name": "Stillness",           "center": "Root",         "theme": "靜止專注",            "interpretation": "Gate 52 帶來靜定的能力，能在靜止中保持高度專注。"},
    53: {"name": "Development",         "center": "Root",         "theme": "漸進發展",            "interpretation": "Gate 53 帶來開啟新循環的能量，以穩定步伐推進成長。"},
    54: {"name": "Ambition",            "center": "Root",         "theme": "向上驅動力",          "interpretation": "Gate 54 帶來強烈的上升驅動力，渴望實現物質與精神的提升。"},
    55: {"name": "Abundance",           "center": "Solar Plexus", "theme": "情緒豐盛",            "interpretation": "Gate 55 帶來豐盛感，情緒如波浪起伏，尋找靈魂深度。"},
    56: {"name": "Stimulation",         "center": "Throat",       "theme": "故事與刺激",          "interpretation": "Gate 56 透過故事與概念刺激他人，帶來豐富的表達能量。"},
    57: {"name": "Intuitive Clarity",   "center": "Spleen",       "theme": "直覺清晰",            "interpretation": "Gate 57 帶來敏銳的當下直覺，能即時感知環境中的微妙訊號。"},
    58: {"name": "Joy",                 "center": "Root",         "theme": "喜悅活力",            "interpretation": "Gate 58 帶來對生命的喜悅感，推動持續改善與精益求精。"},
    59: {"name": "Sexuality",           "center": "Sacral",       "theme": "親密連結",            "interpretation": "Gate 59 具備突破隔閡、建立親密連結的能力。"},
    60: {"name": "Limitation",          "center": "Root",         "theme": "接受限制",            "interpretation": "Gate 60 帶來在限制中找到突變可能的智慧。"},
    61: {"name": "Inner Truth",         "center": "Head",         "theme": "內在真理探索",        "interpretation": "Gate 61 帶來對神秘知識的強烈好奇，追尋內在真理。"},
    62: {"name": "Preponderance",       "center": "Throat",       "theme": "細節表達",            "interpretation": "Gate 62 帶來透過細節與事實進行精確表達的能力。"},
    63: {"name": "After Completion",    "center": "Head",         "theme": "完成後的疑問",        "interpretation": "Gate 63 在事物完成後仍帶來疑問與審視，推動更高品質。"},
    64: {"name": "Before Completion",   "center": "Head",         "theme": "混沌的靈感",          "interpretation": "Gate 64 在混沌中孕育靈感，帶來對過去經驗的反思與理解。"},
}

# ── Channel Info ──────────────────────────────────────────────────────────────
# 36 defined channels: (gate_a, gate_b), name, centers, circuit, interpretation

CHANNEL_INFO = {
    "1-8":   {"gates": (1, 8),   "name": "Inspiration",        "centers": ("G", "Throat"),       "circuit": "Individual",   "interpretation": "將創造靈感轉化為真實貢獻，展現獨特自我表達。"},
    "2-14":  {"gates": (2, 14),  "name": "The Beat",           "centers": ("G", "Sacral"),       "circuit": "Individual",   "interpretation": "掌握方向的同時累積豐盛資源，引導能量流向正確目標。"},
    "3-60":  {"gates": (3, 60),  "name": "Mutation",           "centers": ("Sacral", "Root"),    "circuit": "Individual",   "interpretation": "在限制中推動突變，帶來間歇性的脈衝式轉化能量。"},
    "4-63":  {"gates": (4, 63),  "name": "Logic",              "centers": ("Ajna", "Head"),      "circuit": "Collective",   "interpretation": "將疑問轉化為邏輯公式，為集體提供清晰解答框架。"},
    "5-15":  {"gates": (5, 15),  "name": "Rhythm",             "centers": ("Sacral", "G"),       "circuit": "Collective",   "interpretation": "以固定節奏融入生命流動，為集體帶來和諧規律。"},
    "6-59":  {"gates": (6, 59),  "name": "Intimacy",           "centers": ("Solar Plexus", "Sacral"), "circuit": "Tribal", "interpretation": "透過情緒摩擦與親密連結，深化關係品質。"},
    "7-31":  {"gates": (7, 31),  "name": "The Alpha",          "centers": ("G", "Throat"),       "circuit": "Collective",   "interpretation": "具備影響集體方向的領導潛力，能為大眾指引未來。"},
    "9-52":  {"gates": (9, 52),  "name": "Concentration",      "centers": ("Sacral", "Root"),    "circuit": "Collective",   "interpretation": "在靜定中深度專注，積累精熟技能的強大能量。"},
    "10-20": {"gates": (10, 20), "name": "Awakening",          "centers": ("G", "Throat"),       "circuit": "Individual",   "interpretation": "活在當下並展現真實自我，以覺醒狀態激勵他人。"},
    "10-34": {"gates": (10, 34), "name": "Exploration",        "centers": ("G", "Sacral"),       "circuit": "Individual",   "interpretation": "以強大生命力探索真實自我的各種可能性。"},
    "10-57": {"gates": (10, 57), "name": "Perfected Form",     "centers": ("G", "Spleen"),       "circuit": "Individual",   "interpretation": "以直覺維護身體健康與自我存活的本能行為。"},
    "11-56": {"gates": (11, 56), "name": "Curiosity",          "centers": ("Ajna", "Throat"),    "circuit": "Collective",   "interpretation": "以豐富想法與生動故事刺激集體好奇心。"},
    "12-22": {"gates": (12, 22), "name": "Openness",           "centers": ("Throat", "Solar Plexus"), "circuit": "Individual", "interpretation": "以情緒優雅表達謹慎開口，在適當時機展現深度。"},
    "13-33": {"gates": (13, 33), "name": "The Prodigal",       "centers": ("G", "Throat"),       "circuit": "Collective",   "interpretation": "傾聽並保存人類故事，在退場時分享累積的智慧。"},
    "16-48": {"gates": (16, 48), "name": "The Wavelength",     "centers": ("Throat", "Spleen"),  "circuit": "Collective",   "interpretation": "在深度能力與熱情表達之間找到共鳴頻率。"},
    "17-62": {"gates": (17, 62), "name": "Acceptance",         "centers": ("Ajna", "Throat"),    "circuit": "Collective",   "interpretation": "以邏輯觀點與細節表達，為集體帶來可驗證的意見。"},
    "18-58": {"gates": (18, 58), "name": "Judgment",           "centers": ("Spleen", "Root"),    "circuit": "Collective",   "interpretation": "以喜悅精神持續改善不足，追求更高生命品質。"},
    "19-49": {"gates": (19, 49), "name": "Synthesis",          "centers": ("Root", "Solar Plexus"), "circuit": "Tribal",   "interpretation": "以原則決定接受或拒絕，建立有意義的情感盟約。"},
    "20-34": {"gates": (20, 34), "name": "Charisma",           "centers": ("Throat", "Sacral"),  "circuit": "Individual",   "interpretation": "將充沛能量即時轉化為行動與表達，展現強大魅力。"},
    "20-57": {"gates": (20, 57), "name": "The Brain Wave",     "centers": ("Throat", "Spleen"),  "circuit": "Individual",   "interpretation": "直覺洞察立即轉化為清晰言語，帶來即時智慧表達。"},
    "21-45": {"gates": (21, 45), "name": "Money",              "centers": ("Heart", "Throat"),   "circuit": "Tribal",       "interpretation": "管理集體資源，以掌控力確保族群的物質安全。"},
    "23-43": {"gates": (23, 43), "name": "Structuring",        "centers": ("Throat", "Ajna"),    "circuit": "Individual",   "interpretation": "將內在突破性洞見轉化為簡明清晰的語言表達。"},
    "24-61": {"gates": (24, 61), "name": "Awareness",          "centers": ("Ajna", "Head"),      "circuit": "Individual",   "interpretation": "在反覆沉思中追尋內在真理，孕育深刻靈性洞見。"},
    "25-51": {"gates": (25, 51), "name": "Initiation",         "centers": ("G", "Heart"),        "circuit": "Individual",   "interpretation": "以純真勇氣在震驚中開啟靈性覺醒的旅程。"},
    "26-44": {"gates": (26, 44), "name": "Surrender",          "centers": ("Heart", "Spleen"),   "circuit": "Tribal",       "interpretation": "憑藉直覺辨識哪些過去模式值得繼續，以說服力傳遞價值。"},
    "27-50": {"gates": (27, 50), "name": "Preservation",       "centers": ("Sacral", "Spleen"),  "circuit": "Tribal",       "interpretation": "守護社群價值觀與傳承，以滋養能量照顧集體健康。"},
    "28-38": {"gates": (28, 38), "name": "Struggle",           "centers": ("Spleen", "Root"),    "circuit": "Individual",   "interpretation": "在生存奮鬥中探索生命意義，以頑強精神應對挑戰。"},
    "29-46": {"gates": (29, 46), "name": "Discovery",          "centers": ("Sacral", "G"),       "circuit": "Collective",   "interpretation": "全身心投入承諾，在身體力行中發現生命的豐盛。"},
    "30-41": {"gates": (30, 41), "name": "Recognition",        "centers": ("Solar Plexus", "Root"), "circuit": "Collective", "interpretation": "對新體驗的渴望與情感深度共振，推動人生新循環。"},
    "32-54": {"gates": (32, 54), "name": "Transformation",     "centers": ("Spleen", "Root"),    "circuit": "Tribal",       "interpretation": "憑直覺辨識值得投資的轉化機會，以野心推動向上躍升。"},
    "35-36": {"gates": (35, 36), "name": "Transitoriness",     "centers": ("Throat", "Solar Plexus"), "circuit": "Collective", "interpretation": "在情緒危機中累積豐富體驗，不斷尋求新刺激與改變。"},
    "37-40": {"gates": (37, 40), "name": "Community",          "centers": ("Solar Plexus", "Heart"), "circuit": "Tribal",   "interpretation": "以情感盟約建立互惠社群，守護休息與工作的平衡。"},
    "39-55": {"gates": (39, 55), "name": "Emoting",            "centers": ("Root", "Solar Plexus"), "circuit": "Individual", "interpretation": "以情緒挑衅激發豐盛，在波動中尋找靈魂的深層意義。"},
    "42-53": {"gates": (42, 53), "name": "Maturation",         "centers": ("Sacral", "Root"),    "circuit": "Collective",   "interpretation": "以穩定步伐開始並完成週期，帶來漸進成熟的能量。"},
    "47-64": {"gates": (47, 64), "name": "Abstraction",        "centers": ("Ajna", "Head"),      "circuit": "Collective",   "interpretation": "在混沌過去經驗中提煉抽象智慧，轉化困境為理解。"},
    "34-57": {"gates": (34, 57), "name": "Power",              "centers": ("Sacral", "Spleen"),  "circuit": "Individual",   "interpretation": "以強大生命力與直覺感知維護自身健康與生存，帶來當下的行動智慧。"},
}

# ── Center Info ───────────────────────────────────────────────────────────────

CENTER_INFO = {
    "Head": {
        "zh": "頭頂中心",
        "theme": "靈感與壓力",
        "defined_interpretation": "穩定的靈感來源，持續推動思考與問題探索。",
        "open_interpretation": "容易受他人思想影響，可能感到來自外部的精神壓力。",
    },
    "Ajna": {
        "zh": "邏輯中心",
        "theme": "思維與確定性",
        "defined_interpretation": "思維方式固定清晰，有一套穩定的分析框架。",
        "open_interpretation": "思維靈活多變，容易在意他人是否認為自己夠確定。",
    },
    "Throat": {
        "zh": "喉嚨中心",
        "theme": "表達與行動",
        "defined_interpretation": "表達方式穩定，能以一致的方式溝通與行動。",
        "open_interpretation": "表達方式靈活多樣，容易為吸引注意而說話。",
    },
    "G": {
        "zh": "G中心 / 方向中心",
        "theme": "身份認同與方向",
        "defined_interpretation": "方向感穩固，身份認同清晰，不輕易被外界動搖。",
        "open_interpretation": "身份感較流動，容易受環境影響而改變方向。",
    },
    "Heart": {
        "zh": "意志中心",
        "theme": "意志力與自我價值",
        "defined_interpretation": "意志力強，能持續完成承諾，自我價值感穩定。",
        "open_interpretation": "意志力需要休息，過度承諾容易耗盡。應避免用行動來證明自我價值。",
    },
    "Sacral": {
        "zh": "薦骨中心",
        "theme": "生命力與回應",
        "defined_interpretation": "擁有持續的生命力，適合以薦骨回應（嗯嗯 / 哼哼）作為決策依據。",
        "open_interpretation": "生命力非固定，需要注意不過度消耗能量。",
    },
    "Spleen": {
        "zh": "直覺中心",
        "theme": "直覺、健康與當下安全感",
        "defined_interpretation": "直覺感知穩定，能即時接收關於健康與安全的訊號。",
        "open_interpretation": "安全感較脆弱，可能執著於不再有益的事物。",
    },
    "Solar Plexus": {
        "zh": "情緒中心",
        "theme": "情緒波浪與清晰",
        "defined_interpretation": "情緒具有波浪特質，需要等待情緒清晰後再做重要決策。",
        "open_interpretation": "容易吸收他人情緒，需分辨哪些情緒真正屬於自己。",
    },
    "Root": {
        "zh": "根部中心",
        "theme": "壓力與推進力",
        "defined_interpretation": "有穩定的腎上腺壓力，帶來持續推進事物的動力。",
        "open_interpretation": "容易被外部壓力驅動而倉促行動，需練習在壓力中保持從容。",
    },
}

# ── Type Info ─────────────────────────────────────────────────────────────────

TYPE_INFO = {
    "Generator": {
        "zh": "生產者",
        "strategy": "等待回應",
        "strategy_zh": "等待外部事物觸發薦骨回應，再決定是否投入能量。",
        "not_self": "挫折感",
        "signature": "滿足感",
        "description": "擁有持續充沛的生命力，是世界的建構者。透過做自己熱愛的事，自然吸引正確機會。",
    },
    "Manifesting Generator": {
        "zh": "顯示生產者",
        "strategy": "等待回應後告知",
        "strategy_zh": "等待薦骨回應後，在行動前告知相關者，以減少阻力。",
        "not_self": "挫折感與憤怒",
        "signature": "滿足感與平靜",
        "description": "兼具生產者的持久力與顯示者的主動性，效率極高但需注意遺漏步驟。",
    },
    "Manifestor": {
        "zh": "顯示者",
        "strategy": "告知後行動",
        "strategy_zh": "在採取行動前主動告知會受影響的人，以減少阻力並獲得支持。",
        "not_self": "憤怒",
        "signature": "平靜",
        "description": "天生具備獨立啟動能量，是帶來改變的先行者。需學習告知他人以減少衝突。",
    },
    "Projector": {
        "zh": "投射者",
        "strategy": "等待邀請",
        "strategy_zh": "等待正式邀請後再分享見解或進入重要關係，以確保被正確認可。",
        "not_self": "苦澀感",
        "signature": "成功感",
        "description": "天生的引導者與系統洞察者，能看見他人的潛能。需要等待真誠邀請才能發揮最大影響力。",
    },
    "Reflector": {
        "zh": "反映者",
        "strategy": "等待月亮週期",
        "strategy_zh": "重大決策需等待約 28 天月亮週期，讓不同能量場充分映照後再行動。",
        "not_self": "失望感",
        "signature": "驚喜感",
        "description": "極為罕見，能映照出社群的健康狀況。高度受環境影響，需要在支持的環境中生活。",
    },
    "Unknown": {
        "zh": "未知",
        "strategy": "─",
        "strategy_zh": "─",
        "not_self": "─",
        "signature": "─",
        "description": "類型計算需要完整命盤數據。",
    },
}

# ── Authority Priority ─────────────────────────────────────────────────────────

AUTHORITY_PRIORITY = [
    ("Solar Plexus", "情緒權威 (Emotional Authority)",
     "需要在情緒波浪中等待清晰，避免在高峰或低谷時做重大決策。"),
    ("Sacral",       "薦骨權威 (Sacral Authority)",
     "傾聽薦骨的即時回應聲音（嗯嗯/哼哼），以此作為決策依據。"),
    ("Spleen",       "直覺權威 (Splenic Authority)",
     "相信當下的直覺感知，第一個念頭往往是最正確的。"),
    ("Heart",        "意志力權威 (Ego Authority)",
     "依據自己真實的欲望與意志力做決定，問自己「我真的想要嗎？」"),
    ("G",            "自我投射權威 (Self-Projected Authority)",
     "透過傾聽自己說話，在可信任的人面前表達，從而找到清晰方向。"),
]

# ── Profile Descriptions ──────────────────────────────────────────────────────

PROFILE_DESCRIPTIONS = {
    "1/3": "研究者 / 殉道者：需要建立穩固的知識基礎，透過親身試錯積累實際智慧。",
    "1/4": "研究者 / 機會主義者：以深厚知識為基礎，透過固定人脈圈傳遞影響力。",
    "2/4": "隱士 / 機會主義者：需要獨處充電，透過人脈網絡被召喚展現天賦。",
    "2/5": "隱士 / 異端者：被他人投射為實際問題的解決者，需管理他人的期待。",
    "3/5": "殉道者 / 異端者：透過反覆試錯建立智慧，被視為實際解決方案的提供者。",
    "3/6": "殉道者 / 角色模範：前半生試錯學習，後半生成為他人的角色模範。",
    "4/6": "機會主義者 / 角色模範：透過人脈建立影響力，逐步成為社群的典範。",
    "4/1": "機會主義者 / 研究者：以人脈為核心，同時需要穩固的知識基礎作支撐。",
    "5/1": "異端者 / 研究者：被期待提供實際解決方案，需以紮實知識支持形象。",
    "5/2": "異端者 / 隱士：在被召喚時展現解決問題的能力，同時需要獨處空間。",
    "6/2": "角色模範 / 隱士：三段式人生，最終成為他人仰望的角色模範。",
    "6/3": "角色模範 / 殉道者：透過豐富的人生試煉，最終活出值得效仿的生命。",
}
