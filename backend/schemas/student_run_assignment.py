from pydantic import BaseModel, ConfigDict


class StudentRunAssignmentCreate(BaseModel):
    student_id: int
    run_id: int
    stop_id: int


class StudentRunAssignmentOut(BaseModel):
    id: int
    student_id: int
    run_id: int
    stop_id: int

    model_config = ConfigDict(from_attributes=True)
