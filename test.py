import requests
import time
import concurrent.futures

# ✅ 여기에 실제 DB에 존재하는 UUID 값 입력
USER_UUID = "e40b988b-0aa3-4e60-9753-978fdc10cde5"

# 테스트할 API URL (예: 사용자 목록 API)
BASE_URL = "http://127.0.0.1:8001/api/users/"

# 요청 헤더 (JWT 토큰 있으면 Authorization 추가)
HEADERS = {
    "Authorization": f"UUID {USER_UUID}",
    "Content-Type": "application/json"
}

# 단일 요청 테스트
print("🔍 단일 요청 테스트")
start = time.time()
res = requests.get(BASE_URL, headers=HEADERS)
elapsed = time.time() - start
print({"status_code": res.status_code, "elapsed": round(elapsed, 4), "success": res.ok})

# 부하 테스트
print("\n🚀 부하 테스트 시작")
success_count = 0
fail_count = 0
elapsed_times = []
status_codes = {}

for _ in range(50):  # 요청 횟수
    start = time.time()
    r = requests.get(BASE_URL, headers=HEADERS)
    elapsed = time.time() - start
    elapsed_times.append(elapsed)

    if r.ok:
        success_count += 1
    else:
        fail_count += 1

    status_codes[r.status_code] = status_codes.get(r.status_code, 0) + 1

print("\n📊 부하 테스트 결과")
print(f"총 요청 수: {success_count + fail_count}")
print(f"성공 요청 수: {success_count}")
print(f"실패 요청 수: {fail_count}")
print(f"평균 응답 시간: {round(sum(elapsed_times) / len(elapsed_times), 4)}초")
print(f"응답 코드별 통계: {status_codes}")