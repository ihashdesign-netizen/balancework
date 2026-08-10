import os

from django.http import HttpResponse


class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin", "")
        if not origin:
            return self.get_response(request)

        allowed = {
            o.strip()
            for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
            if o.strip()
        }

        if request.method == "OPTIONS":
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        if "*" in allowed or origin in allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response
