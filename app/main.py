import sys
from app.agent_graph import create_graph

def main():
    app = create_graph()
    config = {"configurable": {"thread_id": "defense_game_v1"}}
    
    state = app.get_state(config)
    
    if state.values:
        print(f"\n[알림] 이전 기록 발견 (시도: {state.values.get('retry_count', 0)})")
        choice = input("1: 이어하기, 2: 새로 시작 -> ")
        inputs = None if choice == "1" else {"user_input": input("새 작업: "), "retry_count": 0}
    else:
        inputs = {"user_input": input("코딩 작업 입력: "), "retry_count": 0}

    # 3. 그래프 실행
    try:
        # config를 전달해야 DB에서 해당 thread_id를 찾아 이어서 진행합니다.
        for output in app.stream(inputs, config=config):
            for key, value in output.items():
                print(f"\n[Node: {key}] 처리 완료")
                
                # Reviewer 결과 출력
                if key == "reviewer":
                    is_ok = value.get("is_ok", False)
                    print(f"결과: {'✅ PASS' if is_ok else '❌ FAIL'}")
                    print(f"피드백: {value.get('feedback', '피드백 없음')}")
                
                # 샌드박스 로그 출력
                if key == "sandbox":
                    print(f"Sandbox Log: {value.get('sandbox_log', '로그 없음')}")

                if "logs" in value and value["logs"]:
                    print(f"Log: {value['logs'][-1]}")

    except KeyboardInterrupt:
        print("\n[중단] 사용자에 의해 프로그램이 중단되었습니다. 진행 상황은 DB에 저장되었습니다.")
    except Exception as e:
        print(f"\n[오류] 실행 중 예외 발생: {e}")

if __name__ == "__main__":
    main()