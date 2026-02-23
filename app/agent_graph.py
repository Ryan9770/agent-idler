import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import AgentState
from .nodes import planner_node, executor_node, execution_node, reviewer_node, finalizer_node

def create_graph():
    # DB 연결 (자동 생성)
    conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    workflow = StateGraph(AgentState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("sandbox", execution_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("finalizer", finalizer_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "sandbox")
    workflow.add_edge("sandbox", "reviewer")
    

    # 4. 리뷰 결과에 따른 조건부 분기 (Conditional Edge)
    workflow.add_conditional_edges(
        "reviewer",             # 출발 노드
        routing_logic,          # 결정 로직 (router.py에 정의)
        {
            "continue": "executor", # 반려 시 다시 코드 수정(executor)으로
            "end": "finalizer"              # 통과 시 워크플로우 종료
        }
    )
    
    workflow.add_conditional_edges("reviewer", routing_logic, {"continue": "executor", "end": "finalizer"})
    workflow.add_edge("finalizer", END)

    return workflow.compile(checkpointer=memory)