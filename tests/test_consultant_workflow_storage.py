"""
Tests for V1.9.8 Consultant Workflow Storage.
"""
import json
import os
import pytest
import tempfile
from pathlib import Path

from consultant_workflow.models import (
    ClientCase, ClientProfile, CaseNote, CaseTask, ReportDelivery, ClientCaseSnapshot,
)
from consultant_workflow.storage import (
    load_cases, save_cases, append_case, update_case, get_case,
    add_note, add_task, update_task_status, add_delivery,
    export_cases_csv, delete_all_cases,
    make_case_id, make_note_id, make_task_id, make_delivery_id,
)


def _tmp_path():
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    f.close()
    os.unlink(f.name)
    return Path(f.name)


class TestLoadSave:
    def test_load_missing_returns_empty(self):
        p = _tmp_path()
        snap = load_cases(p)
        assert snap.cases == []

    def test_save_load_roundtrip(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Alice", email="a@a.com"))
        snap = ClientCaseSnapshot(cases=[c])
        save_cases(snap, p)
        loaded = load_cases(p)
        assert len(loaded.cases) == 1
        assert loaded.cases[0].client.name == "Alice"

    def test_bad_json_raises_value_error(self):
        p = _tmp_path()
        p.write_text("{bad json{{", encoding="utf-8")
        with pytest.raises(ValueError):
            load_cases(p)

    def test_empty_file_returns_empty(self):
        p = _tmp_path()
        p.write_text("", encoding="utf-8")
        snap = load_cases(p)
        assert snap.cases == []


class TestAppendCase:
    def test_append_case_auto_case_id(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Bob"))
        result = append_case(c, p)
        assert result.case_id != ""
        assert result.case_id.startswith("case_")

    def test_append_case_fills_created_at(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Carol"))
        result = append_case(c, p)
        assert result.created_at != ""

    def test_append_case_fills_birth_country_taiwan_when_empty(self):
        p = _tmp_path()
        profile = ClientProfile(name="Dave", birth_country="")
        c = ClientCase(client=profile)
        result = append_case(c, p)
        assert result.client.birth_country == "台灣"

    def test_append_case_preserves_existing_birth_country(self):
        p = _tmp_path()
        profile = ClientProfile(name="Eve", birth_country="日本")
        c = ClientCase(client=profile)
        result = append_case(c, p)
        assert result.client.birth_country == "日本"

    def test_append_case_persists(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Frank"))
        append_case(c, p)
        snap = load_cases(p)
        assert len(snap.cases) == 1


class TestGetCase:
    def test_get_case_returns_case(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Gina"))
        result = append_case(c, p)
        retrieved = get_case(result.case_id, p)
        assert retrieved is not None
        assert retrieved.client.name == "Gina"

    def test_get_case_missing_returns_none(self):
        p = _tmp_path()
        result = get_case("nonexistent_id", p)
        assert result is None


class TestUpdateCase:
    def test_update_case_updates_status(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Han"))
        saved = append_case(c, p)
        saved.case_status = "contacted"
        update_case(saved.case_id, saved, p)
        loaded = get_case(saved.case_id, p)
        assert loaded.case_status == "contacted"

    def test_update_case_missing_raises(self):
        p = _tmp_path()
        c = ClientCase(case_id="bad_id", client=ClientProfile(name="Ivy"))
        with pytest.raises(ValueError):
            update_case("bad_id", c, p)


class TestAddNote:
    def test_add_note_adds_note_id(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Jack"))
        saved = append_case(c, p)
        note = CaseNote(content="first note")
        updated = add_note(saved.case_id, note, p)
        assert len(updated.notes) == 1
        assert updated.notes[0].note_id != ""

    def test_add_note_fills_created_at(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Kara"))
        saved = append_case(c, p)
        note = CaseNote(content="hello")
        updated = add_note(saved.case_id, note, p)
        assert updated.notes[0].created_at != ""


class TestAddTask:
    def test_add_task_adds_task_id(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Leo"))
        saved = append_case(c, p)
        task = CaseTask(title="Do X")
        updated = add_task(saved.case_id, task, p)
        assert len(updated.tasks) == 1
        assert updated.tasks[0].task_id != ""


class TestUpdateTaskStatus:
    def test_update_task_status_works(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Mia"))
        saved = append_case(c, p)
        task = CaseTask(title="Task A")
        updated = add_task(saved.case_id, task, p)
        task_id = updated.tasks[0].task_id
        result = update_task_status(saved.case_id, task_id, "done", p)
        assert result.tasks[0].status == "done"
        assert result.tasks[0].completed_at != ""


class TestAddDelivery:
    def test_add_delivery_works(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Nate"))
        saved = append_case(c, p)
        d = ReportDelivery(report_type="natal", format="html")
        updated = add_delivery(saved.case_id, d, p)
        assert len(updated.deliveries) == 1
        assert updated.deliveries[0].delivery_id != ""


class TestExportCasesCSV:
    def test_csv_headers(self):
        snap = ClientCaseSnapshot(cases=[
            ClientCase(case_id="c1", client=ClientProfile(name="Olivia", email="o@o.com"),
                       case_status="new_lead", report_status="not_started")
        ])
        csv_str = export_cases_csv(snap)
        assert "case_id" in csv_str
        assert "client_name" in csv_str
        assert "client_email" in csv_str
        assert "case_status" in csv_str
        assert "report_status" in csv_str

    def test_csv_excludes_birth_time(self):
        profile = ClientProfile(name="Pat", birth_time="12:00")
        snap = ClientCaseSnapshot(cases=[ClientCase(client=profile)])
        csv_str = export_cases_csv(snap)
        assert "birth_time" not in csv_str

    def test_csv_excludes_note_content(self):
        c = ClientCase(client=ClientProfile(name="Quinn"))
        c.notes.append(CaseNote(content="SECRET_CONTENT"))
        snap = ClientCaseSnapshot(cases=[c])
        csv_str = export_cases_csv(snap)
        assert "SECRET_CONTENT" not in csv_str


class TestDeleteAllCases:
    def test_delete_all_cases_works(self):
        p = _tmp_path()
        c = ClientCase(client=ClientProfile(name="Ray"))
        append_case(c, p)
        delete_all_cases(p)
        snap = load_cases(p)
        assert snap.cases == []


class TestIDGenerators:
    def test_make_case_id_not_empty(self):
        assert make_case_id("Alice") != ""

    def test_make_note_id_not_empty(self):
        assert make_note_id() != ""

    def test_make_task_id_not_empty(self):
        assert make_task_id() != ""

    def test_make_delivery_id_not_empty(self):
        assert make_delivery_id() != ""

    def test_make_case_id_no_full_email(self):
        cid = make_case_id("Bob", "secret@example.com")
        assert "secret@example.com" not in cid
