from .state import AgentState

def routing_logic(state: AgentState):
    if state["is_ok"]:
        print("--- [SUCCESS] 모든 검토 통과! ---")
        return "end"
    if state["retry_count"] >= 15:
        print("--- [LIMIT] 최대 재시도 횟수 도달. 종료합니다. ---")
        return "end"
    
    print(f"--- [RETRY] 검토 실패. 다시 수정을 지시합니다. (시도: {state['retry_count']}/100) ---")
    return "continue"