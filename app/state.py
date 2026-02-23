from typing import TypedDict, List, Annotated
import operator

def merge_last(left: any, right: any) -> any:
    return right

class AgentState(TypedDict):
    user_input: str
    plan: List[str]
    code: str
    is_ok: Annotated[bool, merge_last] # [수정] 마지막 값으로 업데이트
    feedback: str
    sandbox_log: str
    retry_count: int
    logs: List[str]