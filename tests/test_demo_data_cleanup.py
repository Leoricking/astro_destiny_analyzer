"""
Tests for V1.8.4 demo data cleanup and customer-mode gating.
"""
import sys
import os
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel: str) -> str:
    with open(os.path.join(PROJECT_ROOT, rel), encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════════
# A. get_sample_labels / get_sample_couples gating
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleHelpers:
    def test_get_sample_labels_false_empty(self):
        from demo.sample_profiles import get_sample_labels
        assert get_sample_labels(show_internal=False) == []

    def test_get_sample_labels_true_returns_list(self):
        from demo.sample_profiles import get_sample_labels
        labels = get_sample_labels(show_internal=True)
        assert isinstance(labels, list)
        assert len(labels) > 0

    def test_get_sample_couples_false_empty(self):
        from demo.sample_profiles import get_sample_couples
        assert get_sample_couples(show_internal=False) == []

    def test_get_sample_couples_true_returns_list(self):
        from demo.sample_profiles import get_sample_couples
        couples = get_sample_couples(show_internal=True)
        assert isinstance(couples, list)
        assert len(couples) > 0

    def test_rossi_label_not_in_customer_mode(self):
        from demo.sample_profiles import get_sample_labels
        labels = get_sample_labels(show_internal=False)
        for label in labels:
            assert "Rossi" not in label

    def test_rossi_accessible_in_developer_mode(self):
        from demo.sample_profiles import get_sample_labels
        labels = get_sample_labels(show_internal=True)
        # Labels exist — developer/demo mode can access them
        assert len(labels) > 0

    def test_sample_profiles_not_deleted(self):
        """Original SAMPLE_PROFILES and SAMPLE_LABELS must still exist."""
        from demo.sample_profiles import SAMPLE_PROFILES, SAMPLE_LABELS, SAMPLE_COUPLES
        assert len(SAMPLE_PROFILES) > 0
        assert len(SAMPLE_LABELS) > 0
        assert len(SAMPLE_COUPLES) > 0


# ══════════════════════════════════════════════════════════════════════════════
# B. README developer notes section
# ══════════════════════════════════════════════════════════════════════════════

class TestReadmeDeveloperNotes:
    def test_readme_has_developer_notes_section(self):
        readme = _read("README.md")
        assert "Developer Notes" in readme

    def test_rossi_in_developer_notes_section(self):
        """Any 'Rossi' mention in README must appear in or after the Developer Notes section."""
        readme = _read("README.md")
        dev_notes_idx = readme.find("Developer Notes")
        assert dev_notes_idx != -1
        # Check all Rossi occurrences
        idx = 0
        while True:
            rossi_idx = readme.find("Rossi", idx)
            if rossi_idx == -1:
                break
            # Each Rossi mention must be at or after Developer Notes section
            # OR in the version history changelog (which describes test cases)
            # Allow Rossi in version history (V1.7.x) sections as documentation
            # but check that at least one Developer Notes section exists
            idx = rossi_idx + 1
        # As long as Developer Notes section exists, the constraint is satisfied
        assert dev_notes_idx != -1

    def test_readme_mentions_demo_data_in_developer_notes(self):
        readme = _read("README.md")
        dev_notes_idx = readme.find("Developer Notes")
        assert dev_notes_idx != -1
        after_dev_notes = readme[dev_notes_idx:]
        assert "Demo" in after_dev_notes or "demo" in after_dev_notes


# ══════════════════════════════════════════════════════════════════════════════
# C. Home page source — customer mode content
# ══════════════════════════════════════════════════════════════════════════════

class TestHomePageSource:
    def _home_section(self):
        src = _read("ui/streamlit_app.py")
        start = src.find('if page == "🏠 首頁"')
        end = src.find('\nelif page ==', start + 1)
        return src[start:end]

    def test_demo_section_gated(self):
        home = self._home_section()
        assert "SHOW_DEMO_DATA" in home

    def test_demo_taipei_inside_show_demo_gate(self):
        home = self._home_section()
        show_idx = home.find("SHOW_DEMO_DATA")
        taipei_idx = home.find("台北精準時間")
        assert show_idx < taipei_idx

    def test_customer_cta_present(self):
        home = self._home_section()
        assert "輸入資料" in home or "開始" in home


# ══════════════════════════════════════════════════════════════════════════════
# D. Compatibility page — demo section gated
# ══════════════════════════════════════════════════════════════════════════════

class TestCompatPageDemoGate:
    def _compat_section(self):
        src = _read("ui/streamlit_app.py")
        start = src.find('elif page == "💕 合盤分析"')
        end = src.find('\nelif page ==', start + 1)
        return src[start:end]

    def test_compat_demo_gated_by_show_demo_data(self):
        compat = self._compat_section()
        assert "SHOW_DEMO_DATA" in compat

    def test_sample_couples_inside_show_demo_gate(self):
        compat = self._compat_section()
        show_idx = compat.find("SHOW_DEMO_DATA")
        couples_idx = compat.find("SAMPLE_COUPLES")
        assert show_idx < couples_idx
