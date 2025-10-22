from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from .base import File, ResponseMode


class WorkflowStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STOPPED = "stopped"


class ExecutionMetadata(BaseModel):
    total_tokens: Optional[int]
    total_price: Optional[str]
    currency: Optional[str]


class WorkflowStartedData(BaseModel):
    id: str  # workflow run id
    workflow_id: str  # workflow id
    sequence_number: Optional[int] = None
    inputs: Optional[dict] = None
    created_at: int  # unix timestamp seconds


class NodeStartedData(BaseModel):
    id: str  # workflow run id
    node_id: str
    node_type: str
    title: str
    index: int
    predecessor_node_id: Optional[str] = None
    inputs: Optional[dict] = None
    created_at: int
    extras: dict = {}


class NodeFinishedData(BaseModel):
    id: str  # workflow run id
    node_id: str
    node_type: str
    title: str
    index: int
    predecessor_node_id: Optional[str] = None
    inputs: Optional[dict] = None
    process_data: Optional[dict] = None
    outputs: Optional[dict] = {}
    status: WorkflowStatus
    error: Optional[str] = None
    elapsed_time: Optional[float]  # seconds
    execution_metadata: Optional[ExecutionMetadata] = None
    created_at: int
    finished_at: int
    files: List = []


class WorkflowFinishedData(BaseModel):
    id: str  # workflow run id
    workflow_id: str  # workflow id
    status: WorkflowStatus
    outputs: Optional[dict]
    error: Optional[str]
    elapsed_time: Optional[float]
    total_tokens: Optional[int]
    total_steps: Optional[int] = 0
    created_at: int
    finished_at: int
    created_by: dict = {}
    files: List = []


class WorkflowsRunRequest(BaseModel):
    inputs: Dict = {}
    response_mode: ResponseMode
    user: str
    conversation_id: Optional[str] = ""
    files: List[File] = []


class WorkflowsRunResponse(BaseModel):
    workflow_run_id: str
    task_id: str
    data: WorkflowFinishedData
