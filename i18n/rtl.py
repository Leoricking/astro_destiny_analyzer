# -*- coding: utf-8 -*-
"""RTL layout support."""
import streamlit as st

RTL_LANGUAGES = {"ar"}


def is_rtl(language: str) -> bool:
    return language in RTL_LANGUAGES


def get_text_direction(language: str) -> str:
    return "rtl" if is_rtl(language) else "ltr"


def render_direction_css(language: str) -> str:
    if not is_rtl(language):
        return ""
    return """<style>
.stApp { direction: rtl; text-align: right; }
.stSidebar { direction: rtl; text-align: right; }
code, pre, .stCodeBlock, input[type="number"] { direction: ltr !important; text-align: left !important; unicode-bidi: embed !important; }
.stDataFrame th, .stDataFrame td { text-align: right !important; }
</style>"""


def apply_streamlit_direction(language: str) -> None:
    css = render_direction_css(language)
    if css:
        st.markdown(css, unsafe_allow_html=True)
