from pydantic import BaseModel, Field, UUID4, StringConstraints, field_validator
from typing import Annotated, List, Optional, Dict
from datetime import datetime

ConstrainedStr = Annotated[str, StringConstraints(min_length=1)]

class MilvusDbCp4dParameters(BaseModel):
    connection_id: UUID4 = Field(
        ...,
        title="Connection ID",
        description="A unique identifier for the database connection."
    )
    collection_name: ConstrainedStr = Field(
        ...,
        title="Collection Name",
        description="The name of the collection in Milvus database."
    )
    milvus_feature_mappings: List = Field(
        ...,
        min_items=1,
        description="A list of feature mappings. At least one feature mapping is required."
    )

class FlowStep(BaseModel):
    type: str = Field(
        ...,
        title="Step Type",
        description="The type of the flow step, e.g., 'milvusdb_cp4d'."
    )
    parameters: Optional[Dict] = Field(
        None,
        title="Parameters",
        description="Parameters specific to the flow step."
    )

    @field_validator("parameters", mode="before")
    @classmethod
    def validate_parameters(cls, value, info):
        step_type = info.data.get("type")

        if value is None:
            return None

        if not isinstance(value, dict):
            raise ValueError(f"Expected dictionary for parameters, got {type(value)}")

        if step_type == "milvusdb_cp4d":
            return MilvusDbCp4dParameters.model_validate(value).model_dump()

class FlowModel(BaseModel):
    flow_name: str = Field(
        ...,
        title="Flow Name",
        description="The name of the flow."
    )
    project_id: UUID4 = Field(
        ...,
        title="Project ID",
        description="A unique identifier for the project."
    )
    orchestrator: ConstrainedStr = Field(
        ...,
        title="Orchestrator",
        description="The orchestrator used to manage the flow."
    )
    flow: List[FlowStep] = Field(
        ...,
        title="Flow Steps",
        description="A list of steps in the flow."
    )
