"""
Protected trial Streamlit entry point.
Minimal stub — contains no business logic.
Executes the compiled app module from the PyInstaller PYZ bundle.
"""
import runpy
runpy.run_module("ui.streamlit_app", run_name="__main__")
