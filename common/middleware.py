import time, os, json, requests
from django.utils.deprecation import MiddlewareMixin

SLOW_THRESHOLD = float(os.getenv("SLOW_THRESHOLD_SECONDS", "0.8"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

class SlowRequestAlertMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_ts = time.perf_counter()

    def process_response(self, request, response):
        try:
            start = getattr(request, "_start_ts", None)
            if start is not None:
                elapsed = time.perf_counter() - start
                if elapsed >= SLOW_THRESHOLD:
                    path = request.get_full_path()
                    msg = f"SLOW REQUEST {elapsed:.3f}s {request.method} {path}"

                    # 콘솔 로그
                    print(msg)

                    # Slack/Discord 웹훅
                    if SLACK_WEBHOOK_URL:
                        requests.post(
                            SLACK_WEBHOOK_URL,
                            data=json.dumps({"text": f"⏱️ {msg}"}),
                            headers={"Content-Type": "application/json"},
                            timeout=2,
                        )
                    if DISCORD_WEBHOOK_URL:
                        requests.post(
                            DISCORD_WEBHOOK_URL,
                            json={"content": f"⏱️ {msg}"},
                            timeout=2,
                        )
        except Exception:
            pass
        return response
