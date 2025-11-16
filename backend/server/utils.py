from rest_framework.views import exception_handler

def custom_error_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['error'] = response.status_code

        if response.status_code == 400:
            response.data['error'] = '400 Bad request'
            response.data['message'] = 'При выполнении запроса произошла ошибка, попробуйте ещё раз'
            return response
        
        if response.status_code == 401:
            response.data['error'] = '401 Unauthorized'
            response.data['message'] = 'Войдите в аккаунт для выполнения этого действия'
            return response
        
        if response.status_code == 403:
            response.data['error'] = '403 Forbidden'
            response.data['message'] = 'Нет разрешения на вход'
            return response
        
        if response.status_code == 404:
            response.data['error'] = '404 Not found'
            response.data['message'] = 'Страница не найдена, проверьте URL запроса'
            return response
        
        if response.status_code == 405:
            response.data['error'] = '405 Method not allowed'
            response.data['message'] = 'Данный метод недоступен'
            return response
        
        if response.status_code == 500:
            response.data['error'] = '500 Internal server error'
            response.data['message'] = 'Непредвиденная ошибка, попробуйте позже'
            return response
        
    return response
    