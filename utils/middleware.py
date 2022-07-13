from django.http import JsonResponse

class ServerErrorExceptionHandler():
      def __init__(self, get_request):
            self.get_request = get_request

      def __call__(self, request):
            response  = self.get_request(request)
            return response

      def process_exception(self, request, exception):
            if exception:
                  return JsonResponse({
                        "error":True,
                        "message":str(exception)}, status=500)
