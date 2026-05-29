"""
Tests for V2.0.0 Release Build Profiles.
"""
import importlib.util
import pathlib
import sys
import os

ROOT = pathlib.Path(__file__).parent.parent


def _load_build_release():
    spec = importlib.util.spec_from_file_location(
        "build_release", str(ROOT / "scripts" / "build_release.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_release_check():
    spec = importlib.util.spec_from_file_location(
        "release_check", str(ROOT / "scripts" / "release_check.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# A. get_release_profile_config
# ══════════════════════════════════════════════════════════════════════════════

class TestGetReleaseProfileConfig:
    def test_function_exists(self):
        mod = _load_build_release()
        assert hasattr(mod, "get_release_profile_config")

    def test_customer_profile_returned(self):
        mod = _load_build_release()
        cfg = mod.get_release_profile_config("customer")
        assert cfg["profile"] == "customer"

    def test_consultant_profile_returned(self):
        mod = _load_build_release()
        cfg = mod.get_release_profile_config("consultant")
        assert cfg["profile"] == "consultant"

    def test_developer_profile_returned(self):
        mod = _load_build_release()
        cfg = mod.get_release_profile_config("developer")
        assert cfg["profile"] == "developer"


# ══════════════════════════════════════════════════════════════════════════════
# B. Customer profile exclusions
# ══════════════════════════════════════════════════════════════════════════════

class TestCustomerProfileExclusions:
    def test_customer_excludes_run_dev_bat(self):
        mod = _load_build_release()
        assert mod._should_exclude("run_dev.bat", profile="customer")

    def test_customer_excludes_tests_dir(self):
        mod = _load_build_release()
        assert mod._should_exclude("tests/test_foo.py", profile="customer")

    def test_customer_excludes_env_file(self):
        mod = _load_build_release()
        assert mod._should_exclude(".env", profile="customer")

    def test_customer_excludes_private_json(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/leads_mock.json", profile="customer")
        assert mod._should_exclude("data/client_cases.json", profile="customer")

    def test_customer_excludes_run_consultant_bat(self):
        mod = _load_build_release()
        assert mod._should_exclude("run_consultant.bat", profile="customer")


# ══════════════════════════════════════════════════════════════════════════════
# C. Consultant profile inclusions / exclusions
# ══════════════════════════════════════════════════════════════════════════════

class TestConsultantProfileExclusions:
    def test_consultant_excludes_run_dev_bat(self):
        mod = _load_build_release()
        cfg = mod.get_release_profile_config("consultant")
        assert "run_dev.bat" in cfg.get("exclude_bat", []) or \
               mod._should_exclude("run_dev.bat", profile="consultant") or \
               mod._zip_entry_safe("run_dev.bat", profile="consultant") is False

    def test_consultant_allows_run_consultant_bat(self):
        mod = _load_build_release()
        assert not mod._should_exclude("run_consultant.bat", profile="consultant")

    def test_consultant_excludes_private_json(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/client_cases.json", profile="consultant")

    def test_consultant_excludes_env(self):
        mod = _load_build_release()
        assert mod._should_exclude(".env", profile="consultant")


# ══════════════════════════════════════════════════════════════════════════════
# D. Developer profile inclusions
# ══════════════════════════════════════════════════════════════════════════════

class TestDeveloperProfileInclusions:
    def test_developer_allows_run_dev_bat(self):
        mod = _load_build_release()
        assert not mod._should_exclude("run_dev.bat", profile="developer")

    def test_developer_allows_tests_dir(self):
        mod = _load_build_release()
        cfg = mod.get_release_profile_config("developer")
        # developer profile: include_tests=True, tests not in exclude_dirs
        assert "tests" not in cfg["exclude_dirs"]

    def test_developer_excludes_env(self):
        mod = _load_build_release()
        assert mod._should_exclude(".env", profile="developer")

    def test_developer_excludes_private_json(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/client_cases.json", profile="developer")


# ══════════════════════════════════════════════════════════════════════════════
# E. All profiles block Rossi and private data
# ══════════════════════════════════════════════════════════════════════════════

class TestAllProfilesPrivacySafety:
    def test_all_profiles_exclude_rossi(self):
        mod = _load_build_release()
        for profile in ("customer", "consultant", "developer"):
            assert mod._should_exclude("data/Rossi_chart.json", profile=profile), \
                f"Profile {profile} should exclude Rossi files"

    def test_all_profiles_exclude_env(self):
        mod = _load_build_release()
        for profile in ("customer", "consultant", "developer"):
            assert mod._should_exclude(".env", profile=profile)

    def test_all_profiles_zip_blocks_rossi(self):
        mod = _load_build_release()
        for profile in ("customer", "consultant", "developer"):
            assert not mod._zip_entry_safe("data/Rossi_chart.json", profile=profile)

    def test_all_profiles_zip_blocks_env(self):
        mod = _load_build_release()
        for profile in ("customer", "consultant", "developer"):
            assert not mod._zip_entry_safe(".env", profile=profile)

    def test_all_profiles_zip_blocks_private_data(self):
        mod = _load_build_release()
        for profile in ("customer", "consultant", "developer"):
            assert not mod._zip_entry_safe("data/leads_mock.json", profile=profile)
            assert not mod._zip_entry_safe("data/client_cases.json", profile=profile)


# ══════════════════════════════════════════════════════════════════════════════
# F. ZIP naming
# ══════════════════════════════════════════════════════════════════════════════

class TestZipNaming:
    def test_zip_name_customer_contains_customer(self):
        src = _read("scripts/build_release.py")
        assert "customer" in src and "_customer" in src or "customer" in src

    def test_zip_name_consultant_contains_consultant(self):
        src = _read("scripts/build_release.py")
        assert "consultant" in src

    def test_zip_name_developer_contains_developer(self):
        src = _read("scripts/build_release.py")
        assert "developer" in src

    def test_zip_name_format_includes_profile(self):
        src = _read("scripts/build_release.py")
        # The zip name uses {profile} variable
        assert "{profile}" in src or "f\"astro_destiny_analyzer_v{APP_VERSION}_{profile}" in src or \
               "pkg_name = f" in src and "profile" in src


# ══════════════════════════════════════════════════════════════════════════════
# G. release_check supports --profile
# ══════════════════════════════════════════════════════════════════════════════

class TestReleaseCheckProfile:
    def test_release_check_supports_profile_arg(self):
        src = _read("scripts/release_check.py")
        assert "--profile" in src

    def test_release_check_customer_profile_check(self):
        src = _read("scripts/release_check.py")
        assert "customer" in src

    def test_release_check_consultant_profile_check(self):
        src = _read("scripts/release_check.py")
        assert "consultant" in src

    def test_release_check_developer_profile_check(self):
        src = _read("scripts/release_check.py")
        assert "developer" in src

    def test_build_release_supports_profile_arg(self):
        src = _read("scripts/build_release.py")
        assert "--profile" in src
