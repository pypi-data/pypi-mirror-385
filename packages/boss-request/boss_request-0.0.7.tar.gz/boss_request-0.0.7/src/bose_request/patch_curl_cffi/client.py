import json
from pathlib import Path
from typing import List, Optional
from curl_cffi.requests import Session  # Используем оригинальный Session (без alias)
from curl_cffi.requests import HttpMethod, RequestParams, Unpack, Response, ThreadType

from src.bose_request.json_validator import JSONValidator


class MyResponse(Response):

    def json_clean(self):
        data = self.json()
        json = JSONValidator().normalize(data)
        return json

    def export_cookies(self) -> List[dict[str, str]]:
        """
        Экспорт cookies из response.

        Args:
            filepath: Путь для сохранения (опционально)

        Returns:
            Список cookies
        """
        cookies_list = []

        for cookie in self.cookies.jar:
            cookies_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expirationDate': cookie.expires,
            })

        return cookies_list

    def import_cookies(self, cookies):
        """
        Импорт cookies в response (в его jar).

        Args:
            cookies: Список словарей с cookies или путь к JSON файлу

        Returns:
            self для chaining
        """
        if isinstance(cookies, (str, Path)):
            with open(str(cookies), 'r', encoding='utf-8') as f:
                cookies = json.load(f)

        for cookie in cookies:
            self.cookies.jar.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie.get('path', '/'),
            )

def request(
    method: HttpMethod,
    url: str,
    thread: Optional[ThreadType] = None,
    curl_options: Optional[dict] = None,
    debug: Optional[bool] = None,
    **kwargs: Unpack[RequestParams],
) -> MyResponse:
    """Send an http request (теперь возвращает MyResponse)."""
    debug = False if debug is None else debug
    # Передаём response_class=MyResponse
    with Session(thread=thread, curl_options=curl_options, debug=debug, response_class=MyResponse) as s:
        return s.request(method=method, url=url, **kwargs)  # Теперь это MyResponse

# Остальные методы используют request, так что они автоматически вернут MyResponse
def get(url: str, **kwargs: Unpack[RequestParams]):
    return request(method="GET", url=url, **kwargs)

def head(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="HEAD", url=url, **kwargs)

def post(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="POST", url=url, **kwargs)

def put(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="PUT", url=url, **kwargs)

def patch(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="PATCH", url=url, **kwargs)

def delete(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="DELETE", url=url, **kwargs)

def options(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="OPTIONS", url=url, **kwargs)

def trace(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="TRACE", url=url, **kwargs)

def query(url: str, **kwargs: Unpack[RequestParams]) -> MyResponse:
    return request(method="QUERY", url=url, **kwargs)  # Не стандартный метод, но оставил

def fetch_data(url: str) -> None:


    response = get(url)  # Теперь response — это MyResponse
    response.export_cookies("cookies.json")  # Работает!

    print(f"Status code: {response.status_code}")
    print(f"Content: {response.text[:100]}...")  # Первые 100 символов для примера

# Запуск функции
def main() -> None:
    fetch_data("https://x.com/")

if __name__ == "__main__":
    main()