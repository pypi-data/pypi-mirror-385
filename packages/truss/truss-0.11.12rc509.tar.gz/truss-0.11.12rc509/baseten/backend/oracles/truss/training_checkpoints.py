from typing import List

from django.core.exceptions import ValidationError
from pydantic import BaseModel, field_validator


class ArtifactReferences(BaseModel):
    training_job_id: str
    paths: List[str]


class Checkpoint(BaseModel):
    # checkpoint IDs are in the format <training job id>/<checkpoint id>
    # they're in this format so that the composition of folderpaths in any start command
    # that references the checkpoint can be easily understood.
    id: str
    name: str
    training_job_id: str = ""
    checkpoint_id: str = ""

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        if ".." in v:
            raise ValueError("id must not contain '..'")
        if len(v.split("/")) < 2:
            raise ValueError("id must be in the format <training job id>/path/to/checkpoint")
        return v

    def to_artifact_references(self) -> ArtifactReferences:
        return ArtifactReferences(
            training_job_id=self.training_job_id, paths=[f"rank-0/{self.name}/*"]
        )

    def model_post_init(self, __context) -> None:
        """Split the id into training_job_id and checkpoint_id after initialization"""
        split = self.id.split("/")
        self.training_job_id = split[0]
        self.checkpoint_id = "/".join(split[1:])


class TrainingCheckpoints(BaseModel):
    checkpoints: list[Checkpoint] = []
    artifact_references: list[ArtifactReferences] = []
    download_folder: str

    def model_post_init(self, __context) -> None:
        for checkpoint in self.checkpoints:
            artifact_references = checkpoint.to_artifact_references()
            self.artifact_references.append(artifact_references)


def validate_training_checkpoints(training_checkpoints: dict) -> None:
    """
    Validates training checkpoints configuration using Pydantic. Example below:
    training_checkpoints:
      checkpoints:
      # format is <training job id>/<checkpoint id>
      - id: kowpeqj/checkpoint-1
        name: checkpoint-1
      download_folder: /tmp/training_checkpoints
    """
    try:
        TrainingCheckpoints.model_validate(training_checkpoints)
    except Exception as e:
        raise ValidationError(str(e))
