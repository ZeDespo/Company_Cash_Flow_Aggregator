from django.http import HttpRequest, JsonResponse


def deployment_status(request: HttpRequest) -> JsonResponse:
    return JsonResponse({'server': 'main'})