import random

SKIP_PREFIXES = ('/admin/', '/static/', '/media/', '/favicon')

# Записывать каждый N-й запрос с одного IP (защита от флуда)
SAMPLE_RATE = 1  # 1 = каждый, 5 = каждый 5-й, 10 = каждый 10-й
# Максимум записей с одного IP за сессию (не хранить спам)
MAX_PER_IP = 500


class VisitTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Счётчик запросов по IP в памяти (сбрасывается при рестарте)
        self._ip_counts: dict[str, int] = {}

    def __call__(self, request):
        response = self.get_response(request)
        if (request.method == 'GET'
                and response.status_code == 200
                and not any(request.path.startswith(p) for p in SKIP_PREFIXES)):
            try:
                x_fwd = request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_fwd.split(',')[0].strip() if x_fwd else request.META.get('REMOTE_ADDR')

                count = self._ip_counts.get(ip, 0) + 1
                self._ip_counts[ip] = count

                # Пропускаем если IP превысил лимит или не попал в выборку
                if count > MAX_PER_IP:
                    return response
                if SAMPLE_RATE > 1 and random.randint(1, SAMPLE_RATE) != 1:
                    return response

                from store.models import PageVisit
                PageVisit.objects.create(
                    path=request.path[:500],
                    session_key=(request.session.session_key or '')[:40],
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
                    referer=request.META.get('HTTP_REFERER', '')[:500],
                )
            except Exception:
                pass
        return response
