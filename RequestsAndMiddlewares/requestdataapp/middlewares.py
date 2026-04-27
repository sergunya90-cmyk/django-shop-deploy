import time
from django.http import HttpResponse

class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_records = {}

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        current_time = time.time()

        if ip_address in self.ip_records:
            last_request_time = self.ip_records[ip_address]
            if current_time - last_request_time < 2.0:
                return HttpResponse("Ошибка 429: Слишком много запросов. Подождите пару секунд.", status=429)

        self.ip_records[ip_address] = current_time

        return self.get_response(request)