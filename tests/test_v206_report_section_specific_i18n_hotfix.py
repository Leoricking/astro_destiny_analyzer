from types import SimpleNamespace

from reports.localized_renderer import localized_section_bodies


def _enum(value):
    return SimpleNamespace(value=value)


def _report(language_length="complete_10k"):
    western = SimpleNamespace(
        planet_positions=[
            SimpleNamespace(planet=_enum("太陽"), sign=_enum("摩羯座"), house=1),
            SimpleNamespace(planet=_enum("月亮"), sign=_enum("射手座"), house=2),
        ],
        aspects=[
            SimpleNamespace(
                planet1=_enum("太陽"),
                planet2=_enum("月亮"),
                aspect_type=_enum("合相 0°"),
                orb=4.8,
            )
        ],
        houses=[object()] * 12,
        ascendant_accuracy="precise",
        ascendant=_enum("天秤座"),
    )
    bazi = SimpleNamespace(
        day_master=_enum("乙"),
        favorable_elements=[_enum("水"), _enum("木")],
        five_element_percentages={"木": 40, "水": 30},
    )
    numerology = SimpleNamespace(life_path_number=3)
    human_design = SimpleNamespace(
        type_name="Generator",
        strategy="等待回應",
        authority="薦骨權威",
        defined_centers=["Sacral", "G"],
        defined_channels=[SimpleNamespace(channel="29-46")],
    )
    ziwei = SimpleNamespace(
        calculation_mode="formal_layout_phase1",
        ming_palace=SimpleNamespace(main_stars=["貪狼"]),
    )
    profile = SimpleNamespace(report_length=SimpleNamespace(value=language_length))
    return SimpleNamespace(
        western_chart=western,
        bazi_chart=bazi,
        numerology_chart=numerology,
        human_design_chart=human_design,
        ziwei_chart=ziwei,
        profile=profile,
    )


def test_english_complete_sections_are_distinct():
    bodies = localized_section_bodies(_report(), "en")
    assert len(bodies) == 10
    assert len(set(bodies)) == 10


def test_english_evidence_does_not_leak_chinese_display_values():
    bodies = localized_section_bodies(_report(), "en")
    joined = "\n".join(bodies)
    for forbidden in ("太陽", "月亮", "合相", "貪狼"):
        assert forbidden not in joined
    assert "Sun" in joined
    assert "Moon" in joined
    assert "Conjunction" in joined
    assert "Tan Lang" in joined


def test_thai_spanish_arabic_sections_are_not_repeated():
    for language in ("th", "es", "ar"):
        bodies = localized_section_bodies(_report("standard"), language)
        assert len(bodies) == 10
        assert len(set(bodies)) == 10
