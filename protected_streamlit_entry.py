"""
Protected trial Streamlit entry point.
Minimal stub — contains no business logic.
Executes the compiled app module from the PyInstaller PYZ bundle.
"""
import os
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"
os.environ["STREAMLIT_BROWSER_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_BROWSER_SERVER_ADDRESS"] = "127.0.0.1"
import runpy
runpy.run_module("ui.streamlit_app", run_name="__main__")
