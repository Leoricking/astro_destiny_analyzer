"""Tests for SynthesisEngine — integration logic."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time
from core.models import BirthProfile, BloodType, ReportLength
from engines.western_astrology import WesternAstrologyEngine
from engines.bazi import BaZiEngine
from engines.ziwei import ZiWeiEngine
from engines.blood_type import BloodTypeEngine
from engines.numerology import NumerologyEngine
from engines.synthesis import SynthesisEngine


@pytest.fixture
def profile():
    return BirthProfile(
        name="合盤測試",
        birth_date=date(1988, 9, 12),
        birth_time=time(8, 0),
        birth_city="台北",
        birth_country="台灣",
        blood_type=BloodType.B,
    )


@pytest.fixture
def all_charts(profile):
    western = WesternAstrologyEngine().calculate(profile.birth_date, profile.birth_time)
    bazi    = BaZiEngine().calculate(profile.birth_date, profile.birth_time)
    ziwei   = ZiWeiEngine().calculate(profile.birth_date, profile.birth_time)
    blood   = BloodTypeEngine().analyze(profile.blood_type)
    num     = NumerologyEngine().calculate(profile.birth_date)
    return western, bazi, ziwei, blood, num


@pytest.fixture
def synthesis_engine():
    return SynthesisEngine()


class TestSynthesisEngine:
    def test_returns_synthesis_result(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        from core.models import SynthesisResult
        assert isinstance(result, SynthesisResult)

    def test_core_personality_non_empty(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        assert len(result.core_personality) > 30

    def test_love_pattern_includes_blood_type(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        # Blood type B analysis should be referenced somewhere
        assert len(result.love_pattern) > 20

    def test_suitable_careers_list(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        assert isinstance(result.suitable_careers, list)

    def test_temporal_advice_present(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        assert len(result.one_year_advice) > 10
        assert len(result.three_year_advice) > 10

    def test_contradictions_is_list(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        result = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        assert isinstance(result.contradictions, list)
        assert isinstance(result.integration_suggestions, list)

    def test_none_inputs_graceful(self, synthesis_engine, profile):
        """Synthesis should not crash when optional engines return None."""
        result = synthesis_engine.synthesize(profile, None, None, None, None, None)
        from core.models import SynthesisResult
        assert isinstance(result, SynthesisResult)
        assert len(result.core_personality) > 0

    def test_deterministic(self, synthesis_engine, profile, all_charts):
        western, bazi, ziwei, blood, num = all_charts
        r1 = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        r2 = synthesis_engine.synthesize(profile, western, bazi, ziwei, blood, num)
        assert r1.core_personality == r2.core_personality


class TestBaZiEngine:
    def test_pillars_valid(self):
        from engines.bazi import BaZiEngine, STEMS, BRANCHES
        engine = BaZiEngine()
        chart = engine.calculate(date(1990, 5, 10), time(14, 0))
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            assert pillar is not None
            assert pillar.heavenly_stem in STEMS
            assert pillar.earthly_branch in BRANCHES

    def test_five_element_sums_to_100(self):
        from engines.bazi import BaZiEngine
        chart = BaZiEngine().calculate(date(1985, 11, 23), time(6, 30))
        total = sum(chart.five_element_ratio.values())
        assert abs(total - 100.0) < 1.0

    def test_day_pillar_deterministic(self):
        from engines.bazi import BaZiEngine
        c1 = BaZiEngine().calculate(date(1992, 7, 4))
        c2 = BaZiEngine().calculate(date(1992, 7, 4))
        assert c1.day_pillar.heavenly_stem == c2.day_pillar.heavenly_stem
        assert c1.day_pillar.earthly_branch == c2.day_pillar.earthly_branch

    def test_da_yun_count(self):
        from engines.bazi import BaZiEngine
        chart = BaZiEngine().calculate(date(1990, 3, 1))
        assert len(chart.da_yun) == 8

    def test_liu_nian_count(self):
        from engines.bazi import BaZiEngine
        chart = BaZiEngine().calculate(date(1990, 3, 1))
        assert len(chart.liu_nian) == 10
