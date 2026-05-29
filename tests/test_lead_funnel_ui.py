"""
Tests for V2.0.0 Lead Funnel UI page.
Verifies the Lead Funnel page is properly gated and structured.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
SRC_PATH = ROOT / "ui" / "streamlit_app.py"


def _src() -> str:
    return SRC_PATH.read_text(encoding="utf-8")


class TestLeadFunnelPageExists:
    def test_lead_funnel_page_in_source(self):
        assert '== "📊 Lead Funnel"' in _src()

    def test_lead_funnel_in_consultant_pages(self):
        src = _src()
        # V2.0.0: CONSULTANT_PAGES: list = [...]
        idx = src.find("CONSULTANT_PAGES")
        end = src.find("]", idx)
        block = src[idx:end] if idx != -1 else ""
        assert "Lead Funnel" in block

    def test_lead_funnel_in_developer_pages(self):
        src = _src()
        idx = src.find("_PAGES_DEV = [")
        end = src.find("]", idx)
        block = src[idx:end] if idx != -1 else ""
        assert "Lead Funnel" in block

    def test_lead_funnel_not_in_customer_pages(self):
        src = _src()
        idx = src.find("_PAGES_BASE = [")
        end = src.find("]", idx)
        block = src[idx:end] if idx != -1 else ""
        assert "Lead Funnel" not in block


class TestLeadFunnelPageGating:
    def _get_funnel_block(self) -> str:
        src = _src()
        start = src.find('elif page == "📊 Lead Funnel"')
        if start == -1:
            return ""
        end = src.find("\n\n# ", start + 10)
        return src[start:end] if end != -1 else src[start:start + 2000]

    def test_lead_funnel_gated_by_consultant_mode(self):
        block = self._get_funnel_block()
        assert "CONSULTANT_MODE" in block

    def test_lead_funnel_calls_st_stop_if_not_consultant(self):
        block = self._get_funnel_block()
        assert "st.stop()" in block

    def test_lead_funnel_shows_metrics(self):
        block = self._get_funnel_block()
        assert "metric" in block.lower()

    def test_lead_funnel_loads_leads(self):
        block = self._get_funnel_block()
        assert "load_leads" in block or "leads" in block.lower()

    def test_lead_funnel_shows_funnel_section(self):
        block = self._get_funnel_block()
        assert "漏斗" in block or "funnel" in block.lower() or "Lead Funnel" in block

    def test_lead_funnel_developer_mode_extra_tools(self):
        block = self._get_funnel_block()
        assert "DEVELOPER_MODE" in block


class TestLeadFunnelImports:
    def test_lead_funnel_imports_load_leads(self):
        src = _src()
        funnel_start = src.find('elif page == "📊 Lead Funnel"')
        funnel_block = src[funnel_start:funnel_start + 1000] if funnel_start != -1 else ""
        assert "load_leads" in funnel_block
