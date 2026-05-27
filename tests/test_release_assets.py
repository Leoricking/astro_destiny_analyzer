"""
Tests for V1.6.3 release package and demo asset scripts.
Verifies file existence, importability, function presence, and content.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel_path: str) -> str:
    with open(os.path.join(PROJECT_ROOT, rel_path), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════════
# A. File existence
# ══════════════════════════════════════════════════════════════════════════════

class TestFilesExist:
    def test_generate_demo_assets_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "generate_demo_assets.py"))

    def test_build_release_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "build_release.py"))

    def test_quick_start_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "QUICK_START.md"))

    def test_demo_guide_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "DEMO_GUIDE.md"))

    def test_release_checklist_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "RELEASE_CHECKLIST.md"))

    def test_product_overview_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "docs", "PRODUCT_OVERVIEW.md"))

    def test_release_gitkeep_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "release", ".gitkeep"))

    def test_gitignore_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, ".gitignore"))


# ══════════════════════════════════════════════════════════════════════════════
# B. generate_demo_assets.py — importability and structure
# ══════════════════════════════════════════════════════════════════════════════

class TestGenerateDemoAssets:
    def test_importable(self):
        import scripts.generate_demo_assets as m
        assert m is not None

    def test_has_main(self):
        import scripts.generate_demo_assets as m
        assert callable(getattr(m, "main", None))

    def test_does_not_exit_on_import(self):
        import importlib
        import scripts.generate_demo_assets as m
        importlib.reload(m)  # should not raise SystemExit

    def test_has_safe_name_helper(self):
        import scripts.generate_demo_assets as m
        assert callable(getattr(m, "_safe_name", None))

    def test_safe_name_removes_spaces(self):
        import scripts.generate_demo_assets as m
        result = m._safe_name("Demo 新竹科技職涯")
        assert " " not in result

    def test_safe_name_non_empty(self):
        import scripts.generate_demo_assets as m
        assert len(m._safe_name("Demo 台北精準時間")) > 0

    def test_output_dir_defined(self):
        import scripts.generate_demo_assets as m
        assert hasattr(m, "OUTPUT_DIR")


# ══════════════════════════════════════════════════════════════════════════════
# C. build_release.py — importability and exclude list
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildRelease:
    def test_importable(self):
        import scripts.build_release as m
        assert m is not None

    def test_has_main(self):
        import scripts.build_release as m
        assert callable(getattr(m, "main", None))

    def test_does_not_exit_on_import(self):
        import importlib
        import scripts.build_release as m
        importlib.reload(m)

    def test_excludes_venv(self):
        import scripts.build_release as m
        assert ".venv" in m._EXCLUDE_DIRS or "venv" in m._EXCLUDE_DIRS

    def test_excludes_git(self):
        import scripts.build_release as m
        assert ".git" in m._EXCLUDE_DIRS

    def test_excludes_pycache(self):
        import scripts.build_release as m
        assert "__pycache__" in m._EXCLUDE_DIRS

    def test_excludes_release_dir(self):
        import scripts.build_release as m
        assert "release" in m._EXCLUDE_DIRS

    def test_excludes_db_extension(self):
        import scripts.build_release as m
        assert ".db" in m._EXCLUDE_EXTENSIONS

    def test_excludes_zip_extension(self):
        import scripts.build_release as m
        assert ".zip" in m._EXCLUDE_EXTENSIONS

    def test_should_exclude_venv_path(self):
        import scripts.build_release as m
        assert m._should_exclude(".venv/Scripts/python.exe") is True

    def test_should_not_exclude_readme(self):
        import scripts.build_release as m
        assert m._should_exclude("README.md") is False

    def test_has_copy_project(self):
        import scripts.build_release as m
        assert callable(getattr(m, "_copy_project", None))


# ══════════════════════════════════════════════════════════════════════════════
# D. .gitignore content
# ══════════════════════════════════════════════════════════════════════════════

class TestGitignore:
    @pytest.fixture(scope="class")
    def content(self):
        return _read(".gitignore")

    def test_ignores_demo_outputs(self, content):
        assert "demo_outputs/" in content

    def test_ignores_release(self, content):
        assert "release/" in content

    def test_ignores_venv(self, content):
        assert ".venv/" in content

    def test_ignores_db(self, content):
        assert "data/*.db" in content

    def test_ignores_zip(self, content):
        assert "*.zip" in content

    def test_keeps_gitkeep(self, content):
        assert "!release/.gitkeep" in content


# ══════════════════════════════════════════════════════════════════════════════
# E. Documentation content checks
# ══════════════════════════════════════════════════════════════════════════════

class TestDocContent:
    def test_product_overview_has_positioning(self):
        content = _read("docs/PRODUCT_OVERVIEW.md")
        assert "東西方命盤整合分析系統" in content

    def test_product_overview_mentions_western(self):
        content = _read("docs/PRODUCT_OVERVIEW.md")
        assert "西洋占星" in content

    def test_release_checklist_mentions_pytest(self):
        content = _read("docs/RELEASE_CHECKLIST.md")
        assert "pytest" in content

    def test_release_checklist_mentions_git_status(self):
        content = _read("docs/RELEASE_CHECKLIST.md")
        assert "git status" in content

    def test_quick_start_mentions_run_bat(self):
        content = _read("docs/QUICK_START.md")
        assert "run.bat" in content

    def test_quick_start_mentions_setup_bat(self):
        content = _read("docs/QUICK_START.md")
        assert "setup.bat" in content

    def test_demo_guide_mentions_sample(self):
        content = _read("docs/DEMO_GUIDE.md")
        assert "Demo 新竹科技職涯" in content

    def test_demo_guide_mentions_asc(self):
        content = _read("docs/DEMO_GUIDE.md")
        assert "ASC" in content or "上升" in content


# ══════════════════════════════════════════════════════════════════════════════
# F. README mentions new scripts
# ══════════════════════════════════════════════════════════════════════════════

class TestReadme:
    @pytest.fixture(scope="class")
    def readme(self):
        return _read("README.md")

    def test_mentions_generate_demo_assets(self, readme):
        assert "generate_demo_assets.py" in readme

    def test_mentions_build_release(self, readme):
        assert "build_release.py" in readme
