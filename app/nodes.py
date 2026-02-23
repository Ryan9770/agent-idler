import json
import os
import subprocess
import tempfile
from langchain_core.output_parsers import JsonOutputParser
from .llm import planner_llm, executor_llm, reviewer_llm
from .prompts import (
    PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE,
    EXECUTOR_SYSTEM_PROMPT, EXECUTOR_USER_TEMPLATE,
    REVIEWER_SYSTEM_PROMPT, REVIEWER_USER_TEMPLATE
)
from .state import AgentState

# 1. Planner Node: 작업 설계
def planner_node(state: AgentState):
    print("\n--- [PLANNER] 작업 설계 중... ---")
    safe_input = state["user_input"].encode('utf-8', 'ignore').decode('utf-8')
    prompt = PLANNER_SYSTEM_PROMPT + "\n\n" + PLANNER_USER_TEMPLATE.format(user_input=safe_input)
    
    response = planner_llm.invoke(prompt)
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        plan_data = json.loads(content)
    except:
        plan_data = {"steps": [response.content], "goal": "요청 처리 계획 수립"}

    return {
        "plan": plan_data.get("steps", []),
        "logs": [f"Planner: {plan_data.get('goal', '계획 수립 완료')}"]
    }
    
def save_snapshot(code, retry_count):
    """실시간 코드 스냅샷 저장"""
    os.makedirs("snapshots", exist_ok=True)
    # 회차별 저장
    with open(f"snapshots/iter_{retry_count}.py", "w", encoding="utf-8") as f:
        f.write(code)
    # 최신본 업데이트 (실시간 확인용)
    with open("current_working_code.py", "w", encoding="utf-8") as f:
        f.write(code)

def executor_node(state: AgentState):
    retry_num = state.get('retry_count', 0) + 1
    print(f"--- [EXECUTOR] 코드 작성 중 (시도: {retry_num}) ---")
    
    prompt = EXECUTOR_SYSTEM_PROMPT + "\n\n" + EXECUTOR_USER_TEMPLATE.format(
        plan="\n".join(state["plan"]),
        feedback=state.get("feedback", "첫 시도"),
        sandbox_log=state.get("sandbox_log", "로그 없음")
    )
    
    response = executor_llm.invoke(prompt)
    code_content = response.content
    # 마크다운 제거 로직 적용
    if "```python" in code_content:
        code_content = code_content.split("```python")[1].split("```")[0].strip()
    
    # [추가] 중간 저장 실행
    save_snapshot(code_content, retry_num)
    
    return {
        "code": code_content,
        "retry_count": retry_num,
        "logs": [f"Executor: {retry_num}회차 스냅샷 저장 완료"]
    }

def execution_node(state: AgentState):
    print(f"--- [SANDBOX] 실행 테스트 중... (시도: {state.get('retry_count', 0)}) ---")
    code = state.get("code", "")
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(code.encode('utf-8'))
        temp_path = f.name

    try:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy" 
        result = subprocess.run(["python3", temp_path], env=env, capture_output=True, text=True, timeout=3)
        sandbox_result = (result.stdout + "\n" + result.stderr).strip()
        is_valid = (result.returncode == 0)
    except Exception as e:
        sandbox_result = f"에러 발생: {str(e)}"
        is_valid = False
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

    # [추가] 로그 파일에 누적 기록
    with open("agent_idler_history.log", "a", encoding="utf-8") as f:
        f.write(f"\n--- 시도 {state.get('retry_count')} 결과 ---\n{sandbox_result}\n")

    return {"is_ok": is_valid, "sandbox_log": sandbox_result}

# 4. Reviewer Node: 최종 검증
def reviewer_node(state: AgentState):
    print("--- [REVIEWER] 아트 디렉터의 최종 심사 중... ---")
    
    # [수정] 로그 정보를 포함하여 리뷰어에게 전달
    prompt = REVIEWER_SYSTEM_PROMPT + "\n\n" + REVIEWER_USER_TEMPLATE.format(
        user_input=state["user_input"],
        code=state["code"],
        sandbox_log=state.get("sandbox_log", "로그 없음")
    )
    
    response = reviewer_llm.invoke(prompt)
    content = response.content
    is_ok = "[PASS]" in content
    
    return {
        "is_ok": is_ok,
        "feedback": content,
        "logs": [f"Reviewer: {'승인' if is_ok else '반려'}"]
    }
    
def finalizer_node(state: AgentState):
    print("\n--- [FINALIZER] 결과물 저장 중... ---")
    code = state.get("code", "")
    
    if not code:
        return {"logs": ["Finalizer: 저장할 코드가 없습니다."]}
    
    # 루트 디렉토리에 output.py로 저장
    file_path = "output.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"✅ 파일 저장 완료: {os.path.abspath(file_path)}")
    
    return {
        "logs": [f"Finalizer: 최종 코드를 {file_path}에 저장했습니다."]
    }