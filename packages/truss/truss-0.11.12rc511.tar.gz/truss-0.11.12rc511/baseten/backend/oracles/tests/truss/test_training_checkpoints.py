import pytest
from django.core.exceptions import ValidationError

from oracles.truss.training_checkpoints import (
    Checkpoint,
    TrainingCheckpoints,
    validate_training_checkpoints,
)


def test_checkpoint_valid_id():
    checkpoint = Checkpoint(id="job123/checkpoint-1", name="checkpoint-1")
    assert checkpoint.training_job_id == "job123"
    assert checkpoint.checkpoint_id == "checkpoint-1"
    assert checkpoint.name == "checkpoint-1"


def test_checkpoint_invalid_id():
    with pytest.raises(ValueError, match="id must be in the format"):
        Checkpoint(id="invalid_id", name="checkpoint-1")
    with pytest.raises(ValueError, match="id must not contain '..'"):
        Checkpoint(id="job123/..", name="checkpoint-1")


def test_training_checkpoints_valid():
    config = {
        "checkpoints": [
            {"id": "job123/checkpoint-1", "name": "checkpoint-1"},
            {"id": "job123/checkpoint-2", "name": "checkpoint-2"},
            {"id": "job123/.", "name": "root"},
            {"id": "jobs123/some_model_name/checkpoint-1", "name": "some_model_name/checkpoint_1"},
        ],
        "download_folder": "/tmp/checkpoints",
    }
    training_checkpoints = TrainingCheckpoints.model_validate(config)
    assert len(training_checkpoints.checkpoints) == 4
    assert training_checkpoints.download_folder == "/tmp/checkpoints"


def test_validate_training_checkpoints_valid():
    config = {
        "checkpoints": [{"id": "job123/checkpoint-1", "name": "checkpoint-1"}],
        "download_folder": "/tmp/checkpoints",
    }
    # Should not raise any exception
    validate_training_checkpoints(config)


def test_validate_training_checkpoints_invalid():
    invalid_config = {
        "checkpoints": [{"id": "invalid_id", "name": "checkpoint-1"}],
        "download_folder": "/tmp/checkpoints",
    }
    with pytest.raises(ValidationError):
        validate_training_checkpoints(invalid_config)


def test_validate_training_checkpoints_missing_fields():
    incomplete_config = {
        "checkpoints": [
            {"id": "job123/checkpoint-1"}  # missing name
        ],
        "download_folder": "/tmp/checkpoints",
    }
    with pytest.raises(ValidationError):
        validate_training_checkpoints(incomplete_config)
