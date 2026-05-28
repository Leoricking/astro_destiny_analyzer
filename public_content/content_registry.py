"""
V1.9.5 Public Content Landing Pages — Content Registry.
Provides all public-facing landing pages for the Astro Destiny Analyzer.
"""
from __future__ import annotations
from typing import List, Optional

from public_content.models import (
    PublicContentPage, PublicContentSection, SEOData, PublicContentCatalog,
)

_REGISTRY: List[PublicContentPage] = [

    # ── A. 星座內容入口 ────────────────────────────────────────────────────────

    PublicContentPage(
        slug="zodiac-overview",
        title="12 星座性格與關係速覽",
        subtitle="星座是了解自己的起點，不是全部",
        category="zodiac",
        summary=(
            "12 星座描述了太陽星座的核心傾向，但完整的星盤包含月亮、上升、金星、火星與各宮位配置。"
            "太陽星座只是命盤的一個面向；若要了解情感模式、行動節奏與人生結構，需要整合更多行星資訊。"
        ),
        hero_points=[
            "太陽星座反映核心自我傾向",
            "月亮星座影響情感與安全感需求",
            "上升星座影響外在表現與第一印象",
            "金星與火星影響感情風格與行動模式",
            "宮位決定哪個生活領域最為突出",
        ],
        sections=[
            PublicContentSection(
                heading="12 星座概覽",
                body=(
                    "牡羊到雙魚，每個星座都有其對應的能量模式與傾向。"
                    "星座描述的是傾向，不是固定的命運結果。"
                    "同一星座的人在不同的月亮、上升、行星配置下，表現可以差異很大。"
                ),
                bullets=[
                    "火象：牡羊、獅子、射手——行動力強、自我表達明確",
                    "土象：金牛、處女、摩羯——務實穩定、注重物質結構",
                    "風象：雙子、天秤、水瓶——善於溝通、概念思考靈活",
                    "水象：巨蟹、天蠍、雙魚——情感敏銳、直覺感知豐富",
                ],
            ),
            PublicContentSection(
                heading="為什麼只看太陽星座不夠",
                body=(
                    "太陽星座是最廣為人知的占星入口，但命盤是由十顆以上行星的位置、"
                    "相位與宮位共同構成的複雜系統。"
                    "了解自己的完整命盤，能提供更準確的個人特質描述與人生節奏參考。"
                ),
                warning="星座描述提供初步探索方向，不構成命運斷語或生活決策依據。",
            ),
        ],
        cta_title="想了解完整命盤？",
        cta_description="建立包含太陽、月亮、上升、行星、宮位的完整西洋占星命盤報告。",
        cta_button_label="建立完整命盤報告",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="12 星座性格速覽 | Astro Destiny Analyzer",
            meta_description="了解 12 星座的性格傾向與關係模式。太陽星座只是開始，完整命盤包含月亮、上升、金星、火星與宮位。",
            keywords=["星座", "12星座", "占星", "太陽星座", "月亮星座", "上升星座"],
            canonical_slug="zodiac-overview",
            og_title="12 星座性格與關係速覽",
            og_description="從星座開始了解自己，再建立完整整合命盤報告。",
        ),
        is_public=True,
        is_featured=False,
        tags=["zodiac", "beginner", "overview"],
    ),

    PublicContentPage(
        slug="zodiac-compatibility",
        title="12 星座配對只是開始：真正的合盤看 Synastry 與 Composite",
        subtitle="星座相合不代表關係一定順利，星座相剋也不代表不適合",
        category="zodiac",
        summary=(
            "坊間流行的星座配對表只比較太陽星座，無法反映兩人真實的互動模式。"
            "Synastry（星座對照）分析兩人行星的相位互動，Composite（合盤）顯示這段關係的共同場域。"
            "衝突相位不代表不適合，有時反而代表強烈的吸引力與成長動力。"
        ),
        hero_points=[
            "太陽星座配對只反映基本自我傾向的契合度",
            "月亮相位影響情感安全感與日常互動節奏",
            "金星與火星相位影響吸引力與感情節奏",
            "水星相位影響溝通模式與理解方式",
            "土星相位影響長期承諾與責任感",
        ],
        sections=[
            PublicContentSection(
                heading="Synastry 與 Composite 的差異",
                body=(
                    "Synastry 是將兩張星盤疊合，觀察一方行星與另一方行星形成的相位。"
                    "Composite 是取兩人對應行星的中點，生成一張代表「這段關係」的新星盤。"
                    "兩種方法提供不同維度的關係資訊，整合後更能全面理解互動模式。"
                ),
                bullets=[
                    "Synastry：分析兩人如何互相影響",
                    "Composite：分析這段關係本身的特質",
                    "衝突相位（對分、四分）不等於不合",
                    "和諧相位（三分、六分）不代表關係完全無摩擦",
                ],
            ),
            PublicContentSection(
                heading="什麼是合盤相容性分數",
                body=(
                    "本系統的合盤分析會計算情感、溝通、吸引力、穩定性等多個維度的評分，"
                    "並提供相位列表與解讀。分數是參考工具，不是關係好壞的判決。"
                ),
                warning="合盤分析提供探索視角，不構成感情決策依據。關係的質量取決於雙方的行動與選擇。",
            ),
        ],
        cta_title="想了解真實的合盤互動？",
        cta_description="建立完整合盤報告，包含 Synastry 相位分析、Composite 合盤與相容性評分。",
        cta_button_label="建立完整合盤報告",
        cta_target="💕 合盤分析",
        seo=SEOData(
            meta_title="星座配對與合盤分析 | Astro Destiny Analyzer",
            meta_description="星座配對只是開始。真正的合盤分析看 Synastry 與 Composite，了解兩人真實的互動模式與關係場域。",
            keywords=["星座配對", "合盤", "Synastry", "Composite", "感情占星"],
            canonical_slug="zodiac-compatibility",
            og_title="星座配對與合盤分析",
            og_description="超越太陽星座配對，了解真實的感情互動模式。",
        ),
        is_public=True,
        is_featured=False,
        tags=["zodiac", "compatibility", "synastry"],
    ),

    # ── B. Human Design 入口 ──────────────────────────────────────────────────

    PublicContentPage(
        slug="human-design-overview",
        title="人類圖是什麼：Type、Strategy、Authority 的使用方式",
        subtitle="人類圖不是命運，是能量運作與決策的參考系統",
        category="human_design",
        summary=(
            "人類圖整合了占星、易經、卡巴拉生命之樹與脈輪系統，"
            "提供一個描述個人能量運作模式的框架。"
            "Type 是能量類型，Strategy 是互動策略，Authority 是適合自己的決策節奏。"
            "人類圖不是宿命論，而是幫助你辨識自己的運作方式。"
        ),
        hero_points=[
            "Type：描述你的能量運作方式（共五種）",
            "Strategy：適合這種能量類型的互動策略",
            "Authority：你的決策中心，反映最適合你的決策節奏",
            "Profile：人生角色與學習模式的組合",
            "Definition：能量中心的連結方式，影響穩定性與開放性",
        ],
        sections=[
            PublicContentSection(
                heading="人類圖的基本元素",
                body=(
                    "人類圖需要精確的出生時間、日期與地點計算。"
                    "圖中包含 9 個能量中心、64 個閘門與 36 個通道。"
                    "Conscious（意識）行星在出生時計算，Design（設計）行星在出生前約 88 度太陽弧計算。"
                ),
                bullets=[
                    "9 個能量中心：頭腦、Ajna、喉嚨、G、意志力、情緒、薦骨、脾臟、根部",
                    "已定義中心：穩定且持續運作的能量",
                    "未定義中心：接收並放大外部能量的開放空間",
                    "閘門與通道：能量流動的路徑",
                ],
            ),
            PublicContentSection(
                heading="Strategy 與 Authority 的實際意義",
                body=(
                    "Strategy 不是「什麼都不做」，而是描述在互動中最適合你的啟動方式。"
                    "Authority 反映你在做重要決定時，哪個中心的感知最值得信任。"
                    "這些不是限制，而是提高決策清晰度的工具。"
                ),
                warning="人類圖提供探索工具，不構成命運斷語或生活決策依據。",
            ),
        ],
        cta_title="想知道自己的人類圖？",
        cta_description="建立完整人類圖報告，包含 Type、Strategy、Authority、Profile 與各中心解讀。",
        cta_button_label="建立完整人類圖報告",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="人類圖是什麼：Type、Strategy、Authority | Astro Destiny Analyzer",
            meta_description="了解人類圖的基本概念：Type 能量類型、Strategy 互動策略、Authority 決策中心。人類圖不是宿命，是了解自己運作方式的工具。",
            keywords=["人類圖", "Human Design", "Type", "Strategy", "Authority", "能量類型"],
            canonical_slug="human-design-overview",
            og_title="人類圖是什麼：Type、Strategy、Authority",
            og_description="了解人類圖如何幫助你辨識自己的能量運作模式與決策節奏。",
        ),
        is_public=True,
        is_featured=True,
        tags=["human_design", "beginner", "overview"],
    ),

    PublicContentPage(
        slug="human-design-types",
        title="五大人類圖類型：顯示者、生產者、顯示生產者、投射者、反映者",
        subtitle="每種類型都有其獨特的能量模式，沒有高低之分",
        category="human_design",
        summary=(
            "人類圖將人分為五種能量類型：顯示者（Manifestor）、生產者（Generator）、"
            "顯示生產者（Manifesting Generator）、投射者（Projector）、反映者（Reflector）。"
            "每種類型各有其運作節奏與互動策略，沒有哪種類型更好。"
        ),
        hero_points=[
            "顯示者：具有啟動能量，Strategy 是先告知後行動",
            "生產者：有持續的薦骨能量，Strategy 是等待回應",
            "顯示生產者：快速且多元，Strategy 是等待回應後告知",
            "投射者：善於引導與看見他人，Strategy 是等待邀請",
            "反映者：開放的月亮能量鏡，Strategy 是等待完整月亮週期",
        ],
        sections=[
            PublicContentSection(
                heading="五種類型的能量特質",
                body=(
                    "每種類型的能量運作方式不同，適合的工作節奏、互動模式與決策時機也不同。"
                    "類型不是標籤，而是提供一個理解自己能量模式的起點。"
                ),
                bullets=[
                    "顯示者（約 8%）：啟動型，先告知可減少阻力",
                    "生產者（約 37%）：回應型，等待真正的薦骨共鳴",
                    "顯示生產者（約 33%）：快速多元，跳步驟是自然節奏",
                    "投射者（約 20%）：引導型，等待真正的邀請",
                    "反映者（約 1%）：反映型，需要月亮週期（約 28 天）決策",
                ],
                warning="類型只是基本框架，完整的人類圖需要結合 Authority、Profile 與閘門通道解讀。",
            ),
        ],
        cta_title="想知道自己的人類圖類型？",
        cta_description="輸入出生資料，計算你的完整人類圖，包含 Type、Authority、Profile 與中心定義。",
        cta_button_label="查詢自己的人類圖類型",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="五大人類圖類型說明 | Astro Destiny Analyzer",
            meta_description="了解人類圖五種類型：顯示者、生產者、顯示生產者、投射者、反映者，每種類型的能量特質與 Strategy。",
            keywords=["人類圖類型", "顯示者", "生產者", "投射者", "反映者", "Human Design Type"],
            canonical_slug="human-design-types",
            og_title="五大人類圖類型",
            og_description="每種人類圖類型都有其獨特的能量模式，了解你的類型。",
        ),
        is_public=True,
        is_featured=False,
        tags=["human_design", "types", "beginner"],
    ),

    # ── C. 合盤入口 ───────────────────────────────────────────────────────────

    PublicContentPage(
        slug="relationship-compatibility",
        title="合盤不是只看星座：感情、合作與親子關係的互動模式",
        subtitle="真正的相容性來自多層次的星盤互動，而不只是太陽星座",
        category="compatibility",
        summary=(
            "合盤分析（Synastry + Composite）是了解兩人互動模式最深入的占星工具。"
            "Synastry 分析雙方行星的相位互動，Composite 揭示這段關係的共同場域。"
            "衝突相位不代表不適合；和諧相位不代表關係完全無摩擦。"
            "關係的質量取決於雙方的行動與選擇，不是命盤決定的。"
        ),
        hero_points=[
            "Synastry 分析兩人行星的相位互動模式",
            "Composite 揭示這段關係的共同能量場域",
            "感情、合作、親子、友誼等不同關係類型有不同的重點相位",
            "衝突相位反映摩擦點，也往往是成長的機會",
            "合盤分數是參考工具，不是感情判決書",
        ],
        sections=[
            PublicContentSection(
                heading="合盤分析的主要維度",
                body=(
                    "本系統的合盤分析包含情感連結（月亮、金星相位）、"
                    "溝通模式（水星相位）、吸引力（金星、火星相位）、"
                    "穩定性（土星相位）與靈魂連結（冥王、凱龍相位）。"
                    "每個維度提供不同層次的關係洞察。"
                ),
                bullets=[
                    "情感：月亮與月亮、金星的相位",
                    "溝通：水星與水星、月亮的相位",
                    "吸引力：金星與火星的相位",
                    "長期穩定：土星相位的影響",
                    "轉化成長：冥王、天王、凱龍的影響",
                ],
            ),
            PublicContentSection(
                heading="親子與合作關係",
                body=(
                    "合盤不只適用於浪漫關係。親子合盤可以了解親子溝通模式，"
                    "合作合盤可以了解工作夥伴的互補性與張力來源。"
                ),
                warning="合盤分析提供互動模式的參考，不構成感情或合作決策的依據。",
            ),
        ],
        cta_title="想了解你們的合盤互動？",
        cta_description="建立完整合盤報告，包含 Synastry 相位列表、Composite 合盤與多維度相容性分析。",
        cta_button_label="建立合盤分析報告",
        cta_target="💕 合盤分析",
        seo=SEOData(
            meta_title="合盤分析：Synastry 與 Composite | Astro Destiny Analyzer",
            meta_description="了解合盤分析如何超越星座配對，透過 Synastry 與 Composite 深入分析感情、合作與親子關係的互動模式。",
            keywords=["合盤", "合盤分析", "Synastry", "Composite", "感情相容性", "占星合盤"],
            canonical_slug="relationship-compatibility",
            og_title="合盤分析：感情、合作與親子關係",
            og_description="透過 Synastry 與 Composite 深入了解兩人真實的互動模式。",
        ),
        is_public=True,
        is_featured=True,
        tags=["compatibility", "synastry", "composite"],
    ),

    # ── D. 紫微入口 ───────────────────────────────────────────────────────────

    PublicContentPage(
        slug="ziwei-overview",
        title="紫微斗數看什麼：命宮、身宮、主星與大限",
        subtitle="紫微偏人生結構與人生階段的節奏分析",
        category="ziwei",
        summary=(
            "紫微斗數是源自中國傳統的命理系統，透過出生時間計算命宮位置，"
            "配置十二宮位與主星，描述人生的基本結構與各階段節奏。"
            "命宮反映核心特質，大限描述每 10 年的人生主題，流年反映當年節奏。"
        ),
        hero_points=[
            "命宮：核心性格與人生主軸",
            "身宮：身體能量與晚年走向",
            "主星：決定命宮基本能量特質的主要星曜",
            "大限：每 10 年的人生主題與節奏",
            "四化：化祿、化權、化科、化忌影響各宮位能量流向",
        ],
        sections=[
            PublicContentSection(
                heading="紫微斗數與西洋占星的差異",
                body=(
                    "紫微斗數以農曆出生時間計算，強調人生結構與階段性節奏；"
                    "西洋占星以行星黃道位置計算，強調心理特質與人際互動。"
                    "兩套系統可以互補，提供不同維度的自我理解。"
                ),
                bullets=[
                    "紫微：強調人生結構、階段節奏與宮位互動",
                    "西洋占星：強調心理特質、行星能量與人際相位",
                    "八字：強調五行結構與日主節奏",
                    "本系統提供外部校準流程，確保計算準確性",
                ],
            ),
            PublicContentSection(
                heading="本系統的紫微計算方式",
                body=(
                    "本系統使用標準農曆換算與十二宮位配置，並包含外部校準工具，"
                    "可與其他紫微排盤系統進行比對驗證。"
                ),
                warning="紫微斗數提供人生節奏的參考框架，不構成命運斷語。各階段的發展仍取決於個人的選擇與行動。",
            ),
        ],
        cta_title="想了解自己的紫微命盤？",
        cta_description="建立完整紫微整合命盤，包含十二宮位、主星配置、大限與流年分析。",
        cta_button_label="建立紫微整合命盤",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="紫微斗數基礎：命宮、主星與大限 | Astro Destiny Analyzer",
            meta_description="了解紫微斗數如何透過命宮、身宮、主星與大限描述人生結構與各階段節奏。",
            keywords=["紫微斗數", "命宮", "主星", "大限", "紫微", "斗數"],
            canonical_slug="ziwei-overview",
            og_title="紫微斗數看什麼：命宮、主星與大限",
            og_description="了解紫微斗數如何描述人生結構與各階段節奏。",
        ),
        is_public=True,
        is_featured=False,
        tags=["ziwei", "beginner", "overview"],
    ),

    # ── E. 八字入口 ───────────────────────────────────────────────────────────

    PublicContentPage(
        slug="bazi-overview",
        title="八字不是只看生肖：年、月、日、時與節氣",
        subtitle="八字看的是五行能量結構與日主節奏，不是生肖配對",
        category="bazi",
        summary=(
            "八字（四柱命理）使用出生的年、月、日、時各自對應的天干地支，"
            "形成四柱八字，反映個人的五行能量結構。"
            "日主（日柱天干）是分析的核心，代表個人的本質特質與能量節奏。"
            "節氣的切分是八字計算的關鍵，不是以農曆月份為準。"
        ),
        hero_points=[
            "年柱：原生家庭與社會環境傾向",
            "月柱：成長環境與核心能量傾向（節氣切分）",
            "日柱：日主，個人核心特質與能量節奏",
            "時柱：晚年走向與子女緣份",
            "五行：金、木、水、火、土的相生相剋結構",
        ],
        sections=[
            PublicContentSection(
                heading="節氣與八字計算",
                body=(
                    "八字的月份以節氣（如立春、驚蟄等）為切分點，不是農曆月份。"
                    "例如，農曆正月初一不一定是寅月；節氣之前出生的仍算前一個月柱。"
                    "本系統使用精確的節氣時間計算，確保月柱準確。"
                ),
                bullets=[
                    "立春：寅月起點",
                    "驚蟄：卯月起點",
                    "清明：辰月起點",
                    "精確節氣時間影響月柱計算",
                ],
            ),
            PublicContentSection(
                heading="五行結構分析",
                body=(
                    "八字分析的重點不在生肖，而在五行的比例與平衡。"
                    "日主旺弱、格局類型與用神分析提供個人能量傾向的框架。"
                ),
                warning="八字提供五行能量結構的參考，不構成命運斷語。生活方向的選擇始終在個人手中。",
            ),
        ],
        cta_title="想了解自己的八字五行結構？",
        cta_description="建立完整八字整合命盤，包含四柱分析、五行比例、日主特質與格局解讀。",
        cta_button_label="建立八字整合報告",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="八字基礎：四柱、五行與節氣 | Astro Destiny Analyzer",
            meta_description="了解八字如何透過年、月、日、時四柱分析五行能量結構與日主節奏。八字不是只看生肖。",
            keywords=["八字", "四柱", "五行", "日主", "節氣", "命理"],
            canonical_slug="bazi-overview",
            og_title="八字不是只看生肖：四柱與五行結構",
            og_description="了解八字如何透過節氣切分與五行結構分析個人能量節奏。",
        ),
        is_public=True,
        is_featured=False,
        tags=["bazi", "beginner", "overview"],
    ),

    # ── F. 生命靈數入口 ───────────────────────────────────────────────────────

    PublicContentPage(
        slug="numerology-overview",
        title="生命靈數適合快速理解人生主題",
        subtitle="靈數是整合命盤的入門工具，不取代完整分析",
        category="numerology",
        summary=(
            "生命靈數透過出生日期計算生命數字，提供人生主題、挑戰與潛能的初步描述。"
            "靈數計算簡單，適合快速了解自己；但要深入理解個人特質，"
            "仍需要結合占星、八字、紫微等更完整的系統。"
        ),
        hero_points=[
            "生命數字：出生日期各位數相加至個位數",
            "1-9 各有對應的人生主題與挑戰",
            "11、22、33 是主數，能量更為強烈",
            "靈數適合作為自我探索的起點",
            "與其他系統整合可提供更全面的視角",
        ],
        sections=[
            PublicContentSection(
                heading="生命靈數的計算方式",
                body=(
                    "將出生日期的年、月、日各位數全部相加，再化簡至個位數（1-9）或主數（11、22、33）。"
                    "例如：1990 年 6 月 15 日 → 1+9+9+0+6+1+5 = 31 → 3+1 = 4，生命數字為 4。"
                ),
                bullets=[
                    "1：領導力、獨立性、開創新局",
                    "2：合作、直覺、關係協調",
                    "3：表達、創意、社交能量",
                    "4：結構、穩定、系統建立",
                    "5：自由、變化、多元探索",
                    "6：責任、照顧、美感",
                    "7：深度思考、靈性探索",
                    "8：力量、資源管理、影響力",
                    "9：智慧、服務、完成循環",
                ],
            ),
            PublicContentSection(
                heading="靈數的侷限與整合",
                body=(
                    "生命靈數提供快速的人生主題參考，但單一靈數無法涵蓋個人的完整複雜性。"
                    "本系統的整合命盤報告將靈數與占星、八字、紫微、人類圖整合解讀。"
                ),
                warning="生命靈數提供人生主題的初步探索，不構成命運斷語或生活決策依據。",
            ),
        ],
        cta_title="想了解完整整合命盤？",
        cta_description="建立整合命盤報告，將生命靈數與占星、八字、紫微、人類圖整合解讀。",
        cta_button_label="建立整合命盤報告",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="生命靈數基礎與整合 | Astro Destiny Analyzer",
            meta_description="了解生命靈數如何快速描述人生主題，以及如何與占星、八字、紫微整合提供更全面的自我了解。",
            keywords=["生命靈數", "靈數", "numerology", "人生主題", "生命數字"],
            canonical_slug="numerology-overview",
            og_title="生命靈數：快速了解人生主題的入口",
            og_description="生命靈數適合快速自我探索，整合完整命盤更為深入。",
        ),
        is_public=True,
        is_featured=False,
        tags=["numerology", "beginner", "overview"],
    ),

    # ── G. Guide 頁 ───────────────────────────────────────────────────────────

    PublicContentPage(
        slug="full-report-guide",
        title="為什麼要做整合命盤：西洋占星、八字、紫微、人類圖如何互補",
        subtitle="每套系統都有其擅長的維度，整合可以提供更全面的自我理解",
        category="guide",
        summary=(
            "西洋占星、八字、紫微斗數、人類圖各自從不同維度描述個人特質與人生節奏。"
            "整合這四套系統，可以在心理特質、五行結構、人生階段與能量運作等層面提供互補的視角，"
            "幫助更全面地理解自己，做出更清醒的生活選擇。"
        ),
        hero_points=[
            "西洋占星：心理特質、情感模式、人際互動",
            "八字：五行能量結構、日主節奏、格局特質",
            "紫微斗數：人生結構、十二宮位、大限階段",
            "人類圖：能量運作模式、決策節奏、類型策略",
            "合盤：兩人關係互動的 Synastry 與 Composite",
        ],
        sections=[
            PublicContentSection(
                heading="西洋占星擅長什麼",
                body=(
                    "西洋占星以行星在黃道上的位置計算，強調個人的心理特質、情感模式、"
                    "溝通風格與人際互動傾向。太陽、月亮、上升三個核心點各自描述不同層面的自我。"
                    "行星相位揭示內在張力與資源。"
                ),
            ),
            PublicContentSection(
                heading="八字擅長什麼",
                body=(
                    "八字透過四柱的天干地支分析五行結構，強調個人的能量節奏與格局類型。"
                    "日主反映核心特質，月令反映成長環境與能量主調，格局決定能量的運用方式。"
                ),
            ),
            PublicContentSection(
                heading="紫微斗數擅長什麼",
                body=(
                    "紫微斗數透過十二宮位的主星配置，描述人生的基本結構與各生命階段（大限）的主題。"
                    "命宮主星反映核心特質，各宮位配置描述不同生活領域的傾向。"
                ),
            ),
            PublicContentSection(
                heading="人類圖擅長什麼",
                body=(
                    "人類圖透過出生時的行星位置計算能量中心與閘門，描述個人的能量運作方式、"
                    "決策節奏（Authority）與互動策略（Strategy）。"
                    "人類圖特別適合了解自己的能量邊界與決策模式。"
                ),
            ),
            PublicContentSection(
                heading="整合的意義",
                body=(
                    "每套系統都有其語言和框架。當多個系統指向相似的傾向時，這些特質往往更為突出。"
                    "當系統之間有矛盾時，提示可能存在需要整合的內在張力。"
                    "整合命盤不是要給出唯一答案，而是提供多維度的探索工具。"
                ),
                warning="任何命理系統都提供探索視角，不構成命運斷語或生活決策依據。",
            ),
        ],
        cta_title="準備好建立完整整合命盤了嗎？",
        cta_description="輸入出生資料，建立包含西洋占星、八字、紫微、人類圖的完整整合命盤報告。",
        cta_button_label="開始建立完整報告",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="為什麼做整合命盤：占星、八字、紫微、人類圖如何互補 | Astro Destiny Analyzer",
            meta_description="了解西洋占星、八字、紫微斗數與人類圖各自的分析維度，以及整合這四套系統如何提供更全面的自我理解。",
            keywords=["整合命盤", "占星八字紫微人類圖", "命盤分析", "自我探索", "整合報告"],
            canonical_slug="full-report-guide",
            og_title="為什麼要做整合命盤",
            og_description="西洋占星、八字、紫微斗數與人類圖的互補視角，幫助更全面地理解自己。",
        ),
        is_public=True,
        is_featured=True,
        tags=["guide", "overview", "integration"],
    ),
]

_FEATURED_SLUGS = [
    "human-design-overview",
    "relationship-compatibility",
    "full-report-guide",
]

_CATALOG: PublicContentCatalog = PublicContentCatalog(
    pages=_REGISTRY,
    featured_slugs=_FEATURED_SLUGS,
    updated_at="2026-05-29",
    version="1.9.5",
)


def get_public_content_catalog() -> PublicContentCatalog:
    return _CATALOG


def get_public_page(slug: str) -> Optional[PublicContentPage]:
    for page in _REGISTRY:
        if page.slug == slug:
            return page
    return None


def list_public_pages(category: Optional[str] = None) -> List[PublicContentPage]:
    if category is None:
        return [p for p in _REGISTRY if p.is_public]
    return [p for p in _REGISTRY if p.is_public and p.category == category]


def list_featured_pages() -> List[PublicContentPage]:
    slug_set = set(_FEATURED_SLUGS)
    return [p for p in _REGISTRY if p.slug in slug_set]
