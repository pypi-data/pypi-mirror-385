from pathlib import Path

import pytest

from subtask_manager import EtlStage, FileClassifier, Subtask, SystemType, TaskType


def test_classify_simple_sql_file(tmp_path: Path):
    base = tmp_path
    entity_dir = base / "customers"
    stage_dir = entity_dir / "01_extract"
    sys_dir = stage_dir / "pg"
    sys_dir.mkdir(parents=True)

    file_path = sys_dir / "extract_customers.sql"
    _ = file_path.write_text("SELECT * FROM customers;")

    classifier = FileClassifier(base)
    subtask = classifier.classify(file_path)

    assert isinstance(subtask, Subtask)
    assert subtask.stage == EtlStage.Extract
    assert subtask.system_type == SystemType.PostgreSQL
    assert subtask.task_type == TaskType.Sql
    assert subtask.entity == "customers"
    assert subtask.is_common is False


def test_classify_common_file(tmp_path: Path):
    file_path = tmp_path / "utils.py"
    _ = file_path.write_text("print('common')")

    classifier = FileClassifier(tmp_path)
    subtask = classifier.classify(file_path)

    assert subtask.is_common is True
    assert subtask.task_type == TaskType.Python


def test_classify_invalid_extension(tmp_path: Path):
    file_path = tmp_path / "weirdfile.unknown"
    _ = file_path.write_text("???")

    classifier = FileClassifier(tmp_path)

    with pytest.raises(ValueError, match="Unknown task type"):
        _ =  classifier.classify(file_path)
