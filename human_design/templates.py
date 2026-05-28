"""
Astro Destiny Analyzer — Human Design Narrative Templates (V1.9.1)

Deep interpretive text for Type, Strategy, Authority, Profile, Centers.
Language: Traditional Chinese.
Tone: exploratory, non-absolute, self-reflection focused.
"""
from __future__ import annotations
from typing import Optional


# ── Type Narratives ───────────────────────────────────────────────────────────

_TYPE_NARRATIVES = {
    "Generator": {
        "energy": (
            "生產者擁有持續充沛的薦骨能量，是世界的建構者與工作的核心力量。"
            "你的能量像一個不斷充電的電池——只要在做真正熱愛的事，能量就會源源不絕；"
            "一旦陷入不對的工作或關係，則會感到枯竭與挫折。"
            "薦骨回應是你最可靠的羅盤：那個來自腹部的「嗯嗯」或「哼哼」，"
            "往往比大腦分析更早知道正確答案。"
        ),
        "misuse": (
            "生產者最常見的誤用，是「主動出擊」——在薦骨尚未回應前，"
            "就被大腦或外界期待驅動去開啟事物。這樣的行動往往缺乏持久力，"
            "也容易在中途感到迷失。另一個誤用是「壓抑挫折感」——"
            "挫折是生產者告訴自己「這條路不對」的訊號，值得正視，而非忽略。"
        ),
        "strategy_practice": (
            "等待回應不是被動等待，而是先讓世界來觸碰你，再觀察薦骨的真實反應。"
            "練習方式：在面對邀請或問題時，先停頓一下，感受身體的回應，"
            "而不是立刻用大腦判斷。薦骨回應常常是一個即時的、"
            "幾乎是生理層面的「yes」或「no」。"
        ),
        "relationship": (
            "在關係與工作中，生產者最大的貢獻是穩定的投入與創造能力。"
            "建議：讓他人提問，而非自己不斷主動解說；"
            "在被邀請進入計畫前，先確認薦骨是否真的有回應。"
            "滿足感是生產者健康狀態的標誌——若長期感到沉悶或機械化，"
            "是時候重新審視當前的投入方向。"
        ),
    },
    "Manifesting Generator": {
        "energy": (
            "顯示生產者兼具生產者的持久薦骨能量與顯示者的主動啟動能力，"
            "天生效率極高，常常同時推進多個方向。"
            "你可能跳步驟、跨越傳統流程——這是你的本能，不是錯誤。"
            "當薦骨有了清楚的回應，你的行動力往往讓人側目。"
        ),
        "misuse": (
            "最常見的挑戰是「遺漏步驟導致回頭重做」，以及「在回應前就先衝」。"
            "由於行動速度快，有時會在行動前忘記告知相關者，"
            "因而引發他人的阻力或誤解。"
            "另一個課題是「中途換方向」——這對顯示生產者是正常的，"
            "但需要誠實溝通，而非默默放棄。"
        ),
        "strategy_practice": (
            "等待薦骨回應後告知：先確認薦骨說「是」，然後在行動前，"
            "簡短告知會受到影響的人你接下來的計畫。"
            "告知不是請求批准，而是降低阻力的溝通動作。"
            "練習：在衝動行動前停頓三秒，問自己「薦骨有回應嗎？」"
        ),
        "relationship": (
            "在團隊或關係中，你是強大的推進者，但需要夥伴能跟上你的節奏。"
            "最適合你的協作方式是給予對方明確的更新，而非假設對方跟你一樣了解全局。"
            "滿足感來自真正投入熱愛的事；挫折感或憤怒是身體在說「方向需要調整」。"
        ),
    },
    "Manifestor": {
        "energy": (
            "顯示者是人類圖中罕見的啟動者，天生具備無需外部許可就能啟動事物的能量。"
            "你的存在本身就對周遭有影響力——這不是誇張，而是顯示者的能量場運作方式。"
            "薦骨不是顯示者的決策中心，你的動力來自更深層的意志或情緒清晰。"
        ),
        "misuse": (
            "最常見的誤用是「不告知就行動」，導致周遭人感到措手不及或被排除在外，"
            "繼而形成阻力與衝突。顯示者往往對這種阻力感到憤怒，"
            "卻沒意識到阻力其實是可以透過告知來預防的。"
        ),
        "strategy_practice": (
            "告知不是請求允許，而是降低阻力的主動姿態。"
            "在採取行動前，簡短告知會受到影響的人：「我接下來打算做這件事。」"
            "這個動作不削弱你的主導權，反而讓你的行動更順暢。"
            "平靜感是顯示者健康狀態的標誌；持續的憤怒往往指向未被聽見的受阻感。"
        ),
        "relationship": (
            "在關係中，顯示者需要保有一定程度的自主空間。"
            "最舒適的連結往往來自真正尊重你主導性的夥伴。"
            "建議：練習主動說出你的計畫與狀態，即使你覺得不需要解釋；"
            "告知讓關係更流暢，也讓他人有機會跟上你。"
        ),
    },
    "Projector": {
        "energy": (
            "投射者不具備持續的薦骨生命力，但擁有看見系統、洞察他人潛能的天賦。"
            "你的能量不是用來持續工作的，而是用來深度觀察、引導，以及在被認可時分享洞見。"
            "休息對投射者不是奢侈，而是能量補充的必要方式。"
        ),
        "misuse": (
            "最常見的誤用是「主動分享洞見卻沒被邀請」——"
            "即使你的建議非常精準，沒有被邀請的分享往往不被接收，還可能被忽略甚至反感。"
            "另一個誤用是「模仿生產者工作節奏」，長時間高強度工作後陷入精疲力竭。"
        ),
        "strategy_practice": (
            "等待邀請不是被動等待機會，而是等待正確的場域看見你。"
            "重要的邀請通常來自對方真誠地認可你、希望你投入的場合。"
            "練習：允許自己成為被看見的人，而不是主動推銷自己。"
            "成功感是投射者健康的標誌；苦澀感通常來自在未被邀請的地方過度付出。"
        ),
        "relationship": (
            "投射者在關係中是深刻的觀察者與理解者。"
            "最舒適的關係是對方真誠地想要聽你說話、"
            "想要理解你的觀點的那種連結。"
            "建議：在關係中設定健康的能量邊界，不要承接超過自己能量範圍的工作量。"
            "需要被看見、被認可，是投射者深層的正當需求，不是依賴。"
        ),
    },
    "Reflector": {
        "energy": (
            "反映者是人類圖中最罕見的類型，所有 9 個中心皆為開放狀態。"
            "你如同一面鏡子，反映出周遭社群與環境的健康狀況。"
            "你的感受與能量狀態高度受環境影響——這不是弱點，而是你獨特的感知天賦。"
        ),
        "misuse": (
            "最常見的誤用是「吸收他人情緒後以為是自己的感受」，"
            "導致情緒混亂或能量耗竭。另一個誤用是「在尚未度過完整月亮週期時做重大決定」，"
            "因而後悔。對反映者而言，環境的選擇至關重要——你在哪裡，就會映照哪裡的狀態。"
        ),
        "strategy_practice": (
            "等待月亮週期不是拖延，而是讓不同能量場充分映照一個問題。"
            "在面對重大決策時，給自己約 28 天，與不同的朋友討論、"
            "在不同環境中感受自己的反應，讓清晰自然浮現。"
            "驚喜感是反映者健康的標誌；長期的失望感往往指向環境需要改變。"
        ),
        "relationship": (
            "反映者需要真正支持性、健康的環境來活得自在。"
            "最重要的事是找到讓你感到舒適、被滋養的人際圈與物理空間。"
            "建議：定期清空與獨處，幫助自己辨識哪些感受是真正屬於自己的。"
            "不要急於給出答案——你的洞察力在時間的醞釀後往往最為精準。"
        ),
    },
    "Unknown": {
        "energy": "類型尚未確定，需要完整命盤數據。",
        "misuse": "─",
        "strategy_practice": "─",
        "relationship": "─",
    },
}

# ── Authority Narratives ──────────────────────────────────────────────────────

_AUTHORITY_NARRATIVES = {
    "Emotional": (
        "情緒權威意味著你的決策清晰度需要透過情緒波浪的時間推移才能浮現。"
        "在情緒高峰時，你可能過度樂觀；在低谷時，可能過度悲觀。"
        "真正的清晰通常出現在情緒相對平靜的時候，不是完全中性，而是「足夠清楚」。\n\n"
        "練習：在做重要決定時，給自己至少一夜的時間，甚至幾天。"
        "不是等「感覺對了」，而是等情緒波浪自然落定後，看看那個決定是否仍然有吸引力。"
    ),
    "Sacral": (
        "薦骨權威是生產者最原始的決策工具——那個來自腹部的即時反應。"
        "薦骨回應通常是即時的、身體層面的，而不是大腦思考後的結論。\n\n"
        "練習：讓別人直接問你 yes/no 問題，觀察薦骨的第一個回應。"
        "那個「嗯嗯」（yes）或「哼哼」（no）往往比任何邏輯分析都更可靠。"
        "注意：薦骨回應是即時的；思考後才出現的「應該說是」不算薦骨回應。"
    ),
    "Splenic": (
        "直覺權威是即時、當下的，往往只出現一次。"
        "脾臟中心的直覺聲音非常安靜，像一個微弱但清晰的「感覺」，"
        "不會反覆出現，也不會大聲提醒你。\n\n"
        "練習：相信第一個直覺感知，即使它沒有邏輯依據。"
        "這種感知通常與安全感 / 健康有關：這件事感覺「對」或「不太對」。"
        "挑戰：不要讓大腦的事後分析說服你放棄了第一個直覺。"
    ),
    "Ego": (
        "意志力權威（Ego / Heart）的決策來自真實的意志力與欲望。"
        "問題不是「我應該做嗎？」而是「我真的想要嗎？」\n\n"
        "練習：聽自己說話的方式——若你說「我真的想要這個」，那是真實訊號；"
        "若你說「我想我應該…」或「我覺得我必須…」，則可能是社會化的壓力，而非真實意志。"
        "注意：心中心的能量需要充分休息才能持續有效運作。"
    ),
    "Self": (
        "自我投射權威（Self-Projected）的清晰來自傾聽自己說話。"
        "在可信任的人面前大聲表達你的感受與想法，往往是找到答案的方式。\n\n"
        "練習：找一個安全的傾聽者，讓自己完整說出心中的感受，"
        "不需要對方給建議，只是聽你說。在說的過程中，你往往能聽到自己的真實方向。"
    ),
    "Mental": (
        "環境 / 心智權威意味著你的清晰來自在正確的環境中傾聽他人的聲音。"
        "你不是用大腦「思考出答案」，而是透過說話、對話、在不同環境中感受，"
        "讓清晰自然浮現。\n\n"
        "練習：在做重大決策前，與幾個你信任的人討論，注意在哪個環境中、"
        "跟哪些人說話時，你感到最清晰。選擇環境，讓環境幫助你做決定。"
    ),
    "Lunar": (
        "月亮權威（反映者專屬）需要等待完整的月亮週期（約 28 天）來處理重大決策。"
        "在這 28 天中，月亮會運行過所有 64 個閘門，讓不同的能量場依次映照這個問題。\n\n"
        "練習：把你的問題記錄下來，每天簡短記錄當天對這個決策的感受。"
        "28 天後，回頭看整體模式，而非某一天的強烈感受。"
        "不要在情緒高峰或低谷時做決定。"
    ),
}

# ── Profile Narratives ────────────────────────────────────────────────────────

_PROFILE_NARRATIVES = {
    "1/3": (
        "**1/3 研究者 / 殉道者**\n\n"
        "你的學習模式需要紮實的知識基礎（第 1 爻），同時透過親身的試驗與錯誤積累實際智慧（第 3 爻）。"
        "你可能常常覺得自己「還需要再多了解一些」才有安全感——這是你的學習驅力，而非缺陷。\n\n"
        "與人互動方式：你的真實性格往往在多次互動後才充分展現。"
        "早期的嘗試與失敗不是失敗，而是你收集人生材料的方式。\n\n"
        "成長節奏：允許自己有試錯的空間；每一次「不成功」都在為下一次更穩健的行動奠基。"
    ),
    "1/4": (
        "**1/4 研究者 / 機會主義者**\n\n"
        "你需要以深厚的知識基礎（第 1 爻）作為支撐，同時透過固定的人脈網絡傳遞影響力（第 4 爻）。"
        "你的機會往往來自你認識的人，而非陌生的投遞。\n\n"
        "與人互動方式：對你而言，關係的深度比廣度更重要。"
        "你的影響力在熟識的圈子中最為自然。\n\n"
        "成長節奏：持續投資你的核心知識，同時滋養你的人際關係網絡。"
    ),
    "2/4": (
        "**2/4 隱士 / 機會主義者**\n\n"
        "你需要獨處充電的空間（第 2 爻的隱士特質），同時透過人脈網絡被召喚展現天賦（第 4 爻）。"
        "你的才能常常在你自己不知不覺中被他人看見，並被邀請出來發揮。\n\n"
        "與人互動方式：等待真誠的邀請，而不是主動推銷自己。"
        "你在自然放鬆的狀態下最能展現真實能力。\n\n"
        "成長節奏：保護你的獨處空間不被過度佔用；充飽電後，你的貢獻會更持久。"
    ),
    "2/5": (
        "**2/5 隱士 / 異端者**\n\n"
        "你擁有天然的才能（第 2 爻），卻常被他人投射為「能解決問題的實踐者」（第 5 爻）。"
        "管理他人的期待是你的主要課題之一。\n\n"
        "與人互動方式：你的影響力常常超出你自己的預期，因為他人在你身上投射了強烈的期待。"
        "辨識哪些期待是真正符合你本質的，哪些是他人的投影，很重要。\n\n"
        "成長節奏：允許自己說「不」；並在被邀請前，先確認這個邀請是否符合你真實的方向。"
    ),
    "3/5": (
        "**3/5 殉道者 / 異端者**\n\n"
        "你透過反覆的試錯與突破積累人生的實際智慧（第 3 爻），"
        "同時被他人視為能提供實際解決方案的人（第 5 爻）。\n\n"
        "與人互動方式：你的人生可能充滿各種「嘗試」的痕跡，這是你的學習方式，而非不穩定。"
        "你的實踐經驗是你最大的資產。\n\n"
        "成長節奏：允許事物自然結束，不要因為「感覺應該繼續」就堅持不適合的關係或計畫。"
    ),
    "3/6": (
        "**3/6 殉道者 / 角色模範**\n\n"
        "你的人生分三個階段：前半生以試錯學習（第 3 爻），中期退後觀察，後半生成為他人效仿的角色模範（第 6 爻）。\n\n"
        "與人互動方式：你在人生後段往往成為別人欣賞的對象，但你自己可能渾然不覺。"
        "你的人生本身就是示範。\n\n"
        "成長節奏：不要對早期的嘗試感到羞愧；那些「失敗」正是你後來智慧的來源。"
    ),
    "4/6": (
        "**4/6 機會主義者 / 角色模範**\n\n"
        "你透過人脈網絡建立影響力（第 4 爻），並在人生後段逐步成為社群的典範（第 6 爻）。\n\n"
        "與人互動方式：你的人際關係是你的核心資源；深化而非擴散它們。\n\n"
        "成長節奏：三段式人生——年輕時學習與建立，中期觀察與反思，後期活出典範。"
    ),
    "4/1": (
        "**4/1 機會主義者 / 研究者**\n\n"
        "你以人脈為核心資源（第 4 爻），同時需要穩固的知識基礎來支撐影響力（第 1 爻）。\n\n"
        "與人互動方式：你的影響力來自你認識的人以及你能展示的專業深度。\n\n"
        "成長節奏：投資你的核心知識，讓人際網絡成為傳遞這些知識的管道。"
    ),
    "5/1": (
        "**5/1 異端者 / 研究者**\n\n"
        "你被他人投射為「能解決普遍問題的實踐者」（第 5 爻），"
        "同時需要以紮實知識支撐這種形象（第 1 爻）。\n\n"
        "與人互動方式：他人對你的期待往往高於你自認的能力；這是投射，不是壓力。\n\n"
        "成長節奏：持續建構你的知識基底，讓形象與實力相符。"
    ),
    "5/2": (
        "**5/2 異端者 / 隱士**\n\n"
        "你在被召喚時展現強大的問題解決能力（第 5 爻），同時需要獨處的空間來充電（第 2 爻）。\n\n"
        "與人互動方式：不是每次出現都要全力以赴；選擇真正值得你貢獻的場合。\n\n"
        "成長節奏：保護你的私人空間，讓充足的休息成為你強大輸出的基礎。"
    ),
    "6/2": (
        "**6/2 角色模範 / 隱士**\n\n"
        "你的人生是三段式旅程：前段試錯、中段觀察、後段活出典範（第 6 爻）；"
        "同時需要充足的獨處空間（第 2 爻）。\n\n"
        "與人互動方式：你的智慧來自觀察，而非說教。"
        "活出你相信的生命方式，本身就是最強的影響力。\n\n"
        "成長節奏：允許自己在觀察期「退後」，那不是停滯，而是蓄積。"
    ),
    "6/3": (
        "**6/3 角色模範 / 殉道者**\n\n"
        "你透過豐富的人生試煉（第 3 爻）積累了足夠的材料，"
        "最終活出值得效仿的生命（第 6 爻）。\n\n"
        "與人互動方式：你的故事——包括那些跌倒的部分——本身就是激勵他人的素材。\n\n"
        "成長節奏：接受人生的各種轉折；每一次轉變都是你通往角色模範的必要積累。"
    ),
}


# ── Public API ────────────────────────────────────────────────────────────────

def get_type_narrative(type_name: str) -> dict:
    """Return the Type narrative dict for the given type."""
    return _TYPE_NARRATIVES.get(type_name, _TYPE_NARRATIVES["Unknown"])


def get_authority_narrative(authority: str) -> str:
    """Return the Authority narrative text. Matches on keyword."""
    authority_lower = authority.lower()
    if "情緒" in authority or "emotional" in authority_lower:
        return _AUTHORITY_NARRATIVES["Emotional"]
    if "薦骨" in authority or "sacral" in authority_lower:
        return _AUTHORITY_NARRATIVES["Sacral"]
    if "直覺" in authority or "splenic" in authority_lower:
        return _AUTHORITY_NARRATIVES["Splenic"]
    if "意志" in authority or "ego" in authority_lower:
        return _AUTHORITY_NARRATIVES["Ego"]
    if "自我投射" in authority or "self-projected" in authority_lower:
        return _AUTHORITY_NARRATIVES["Self"]
    if "月亮" in authority or "lunar" in authority_lower:
        return _AUTHORITY_NARRATIVES["Lunar"]
    return _AUTHORITY_NARRATIVES["Mental"]


def get_profile_narrative(profile: str) -> str:
    """Return the Profile narrative text."""
    return _PROFILE_NARRATIVES.get(profile, f"**人生角色 {profile}**\n\n繼續探索屬於你的人生主題。")


def render_hd_full_narrative(chart) -> str:
    """
    Render a complete Human Design narrative section as Markdown.
    chart: HumanDesignChart instance
    """
    from human_design.visuals import build_hd_visuals, render_centers_markdown_table
    from human_design.validation import build_validation_status, render_validation_markdown

    type_n = get_type_narrative(chart.type_name)
    authority_n = get_authority_narrative(chart.authority)
    profile_n = get_profile_narrative(chart.profile)
    bundle = build_hd_visuals(chart)
    centers_table = render_centers_markdown_table(bundle)
    val_status = build_validation_status(chart)
    val_md = render_validation_markdown(val_status)

    lines = []

    # ── Overview ──────────────────────────────────────────────────────────────
    lines += [
        "## 人類圖 Human Design",
        "",
        "> **重要說明**：人類圖需要精確出生時間；若出生時間不確定，Type / Authority / Centers 可能出現偏差。"
        "本分析定位為自我探索與決策模式參考，不代表絕對命運，不構成醫療、法律或投資建議。",
        "",
        "### 人類圖總覽",
        "",
        "| 項目 | 內容 |",
        "|------|------|",
        f"| 類型 Type | {chart.type_name}（{chart.type_name_zh}） |",
        f"| 策略 Strategy | {chart.strategy} |",
        f"| 內在權威 Authority | {chart.authority} |",
        f"| 人生角色 Profile | {chart.profile} |",
        f"| 輪迴交叉 Incarnation Cross | {chart.incarnation_cross} |",
        f"| 計算模式 | {chart.calculation_mode} |",
        "",
    ]

    # ── Type deep narrative ───────────────────────────────────────────────────
    lines += [
        "### 類型解讀 Type",
        "",
        f"**{chart.type_name}（{chart.type_name_zh}）**",
        "",
        "**能量運作方式**",
        "",
        type_n.get("energy", ""),
        "",
        "**常見誤用**",
        "",
        type_n.get("misuse", ""),
        "",
        "**策略實踐建議**",
        "",
        type_n.get("strategy_practice", ""),
        "",
        "**關係與工作互動**",
        "",
        type_n.get("relationship", ""),
        "",
        "---",
        "",
    ]

    # ── Authority ─────────────────────────────────────────────────────────────
    lines += [
        "### 內在權威 Authority",
        "",
        f"**{chart.authority}**",
        "",
        authority_n,
        "",
        "---",
        "",
    ]

    # ── Profile ───────────────────────────────────────────────────────────────
    lines += [
        "### 人生角色 Profile",
        "",
        profile_n,
        "",
        "---",
        "",
    ]

    # ── Incarnation Cross ─────────────────────────────────────────────────────
    lines += [
        "### 輪迴交叉 Incarnation Cross（初版）",
        "",
        chart.incarnation_cross,
        "",
        "> 本版以意識太陽 / 意識地球 / 設計太陽 / 設計地球四個閘門建立初版輪迴交叉主題。"
        "尚未等同完整商業人類圖十字命名；後續版本可外部校準正式十字名稱。",
        "",
        "---",
        "",
    ]

    # ── Centers visual ────────────────────────────────────────────────────────
    lines += [
        "### Centers 視覺化表格",
        "",
        bundle.summary,
        "",
        "> **重要**：已定義中心代表穩定輸出，不代表「比較好」；開放中心代表接收與放大環境能量，不代表弱點。",
        "",
        centers_table,
        "",
        "---",
        "",
    ]

    # ── Defined centers interpretation ───────────────────────────────────────
    if chart.defined_centers:
        lines += ["### 已定義中心解讀", ""]
        for c in chart.centers:
            if c.is_defined:
                from human_design.constants import CENTER_INFO
                ci = CENTER_INFO.get(c.name, {})
                lines.append(f"**{ci.get('zh', c.name)}（{c.name}）**：{c.defined_interpretation}")
                lines.append("")
        lines += ["---", ""]

    # ── Open centers conditioning ─────────────────────────────────────────────
    if chart.open_centers:
        lines += [
            "### 開放中心與制約覺察",
            "",
            "開放中心是你從環境中吸收與放大他人能量的區域，也是你容易受到制約的地方。",
            "覺察這些模式，而非試圖「關閉」它們，是成長的關鍵。",
            "",
        ]
        for c in chart.centers:
            if not c.is_defined:
                from human_design.constants import CENTER_INFO
                ci = CENTER_INFO.get(c.name, {})
                lines.append(
                    f"- **{ci.get('zh', c.name)}（{c.name}）**："
                    f"容易在此中心吸收外界壓力。{c.open_interpretation}"
                    "建議練習辨識哪些感受來自外界，哪些是自己本有的。"
                )
        lines += ["", "---", ""]

    # ── Channels ─────────────────────────────────────────────────────────────
    lines += ["### 已定義通道 Channels", ""]
    if chart.defined_channels:
        for ch in chart.defined_channels:
            lines.append(f"**通道 {ch.channel}（{ch.name}）**：{ch.interpretation}")
            lines.append("")
    else:
        lines.append(
            "目前沒有已定義通道。這在反映者或開放型圖中是正常的，"
            "代表你的能量場高度接受性，能與各種能量類型的人和諧互動。"
        )
    lines += ["", "---", ""]

    # ── Top gates ─────────────────────────────────────────────────────────────
    top_gates = chart.activated_gates[:10]
    lines += ["### 主要已啟動閘門 Gates（前 10 個）", ""]
    if top_gates:
        lines.append("| Gate | 名稱 | 中心 | 主題 |")
        lines.append("|------|------|------|------|")
        for g in top_gates:
            lines.append(f"| {g.gate} | {g.name} | {g.center} | {g.theme} |")
    else:
        lines.append("無閘門資料。")
    lines += ["", "---", ""]

    # ── Conscious / Design planets ────────────────────────────────────────────
    lines += [
        "### Conscious 行星（意識面）",
        "",
        "> Conscious Personality 行星代表你較容易自覺的表達層面，"
        "通常是你認識自己的那一面。",
        "",
        "| 行星 | 星座 | 黃經 | Gate | Line |",
        "|------|------|------|------|------|",
    ]
    for act in chart.conscious_activations:
        lines.append(f"| {act.planet} | {act.sign} | {act.longitude:.2f}° | {act.gate} | {act.line} |")

    lines += [
        "",
        "---",
        "",
        "### Design 行星（設計面）",
        "",
        "> Design 行星代表較身體化、潛意識層面的運作模式，"
        "通常需要他人指出才會發現自己有這些特質。兩者沒有優劣，只是覺察層次不同。",
        "",
        "| 行星 | 星座 | 黃經 | Gate | Line |",
        "|------|------|------|------|------|",
    ]
    for act in chart.design_activations:
        lines.append(f"| {act.planet} | {act.sign} | {act.longitude:.2f}° | {act.gate} | {act.line} |")

    lines += ["", "---", ""]

    # ── Validation ────────────────────────────────────────────────────────────
    lines += [val_md, ""]

    return "\n".join(lines)
