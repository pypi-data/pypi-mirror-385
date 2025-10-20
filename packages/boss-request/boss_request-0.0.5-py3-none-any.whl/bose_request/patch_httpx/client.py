import json
from typing import Dict, Any, List, Optional, Union, Literal

try:
    import httpx
    from httpx import Response
    from httpx._client import (
        AsyncByteStream,
        AuthTypes,
        CertTypes,
        CookieTypes,
        HeaderTypes,
        ProxyTypes,
        QueryParamTypes,
        RequestContent,
        RequestData,
        RequestExtensions,
        RequestFiles,
        SyncByteStream,
        TimeoutTypes,
        USE_CLIENT_DEFAULT,
        URL,
        UseClientDefault,
        typing
    )
except ImportError as e:
    raise ImportError(
        "Библиотека httpx не установлена. Установите её с помощью одной из команд:\n"
        "pip install httpx\n"
        "или\n"
        "uv add httpx"
    ) from e

from src.bose_request.json_validator import JSONValidator

CookieDict = Dict[str, Any]

class BossResponse(Response):

    def json_clean(self):
        data = self.json()
        json = JSONValidator().normalize(data)
        return json


    def import_cookies(self, cookies: Union[List[CookieDict], Dict[str, str]]):
        """
        Импорт cookies в асинхронный клиент. Автоматически определяет тип:
        - Если Dict[str, str]: преобразует в List[CookieDict] с дефолтными domain='.', path='/', secure=False, без expiration.
        - Если List[CookieDict]: использует напрямую.
        """
        if isinstance(cookies, dict):
            cookies_data: List[CookieDict] = []
            for name, value in cookies.items():
                cookies_data.append({
                    'name': name,
                    'value': value,
                    'domain': '.',  # Дефолтный domain
                    'path': '/',    # Дефолтный path
                    'secure': False,
                    'expirationDate': None,  # Без expiration
                })
        elif isinstance(cookies, list):
            cookies_data = cookies
        else:
            raise ValueError("Неверный тип: ожидается Dict[str, str] или List[Dict]")

        for cookie in cookies_data:
            self.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie.get('path', '/'),
            )

    def export_cookies(self, type: Literal["json", "dict"] = "json") -> Union[str, Dict[str, str]]:
        """
        Экспорт cookies из асинхронного клиента.
        - Если type="json": возвращает JSON-строку из списка полных CookieDict.
        - Если type="dict": возвращает Dict[str, str] (только name: value, игнорируя другие поля).
        """
        cookies_list: List[CookieDict] = []

        for cookie in self.cookies.jar:
            cookies_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expirationDate': cookie.expires,
            })

        if type == "json":
            return json.dumps(cookies_list, indent=2, ensure_ascii=False)
        elif type == "dict":
            cookies_dict: Dict[str, str] = {}
            for cookie in cookies_list:
                cookies_dict[cookie['name']] = str(cookie['value'])  # Преобразуем value в str, если нужно
            return cookies_dict
        else:
            raise ValueError("Неверный type: ожидается 'json' или 'dict'")
class BossAsyncClientHttpx(httpx.AsyncClient):
    async def request(
            self,
            method: str,
            url: Union[httpx.URL, str],
            *,
            content: Optional[Union[bytes, str, Dict[str, Any], List[Any]]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, Union[str, bytes, List[Union[str, bytes]]]]] = None,
            json: Optional[Any] = None,
            params: Optional[Dict[str, Union[str, List[str]]]] = None,
            headers: Optional[Dict[str, str]] = None,
            cookies: Optional[Dict[str, str]] = None,
            auth: Optional[httpx.Auth] = None,
            follow_redirects: bool = False,
            timeout: Optional[Union[float, httpx.Timeout]] = None,
            extensions: Optional[Dict[str, Any]] = None,
    ) -> BossResponse:



        # Вызываем оригинальный request
        response = await super().request(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

        # Создаём MyResponse из оригинального response
        my_response = BossResponse(
            status_code=response.status_code,
            headers=response.headers,
            content=response.content,
            json=response.json,
            text=response.text,
            stream=response.stream,
            extensions=response.extensions,
            default_encoding=response.default_encoding,
            request=response.request,
            history=response.history,
        )
        # Копируем другие атрибуты, если нужно (например, stream, если в stream-режиме)
        return my_response

    async def get(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault | None = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `GET` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )


    async def options(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send an `OPTIONS` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def head(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `HEAD` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def post(
        self,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: typing.Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `POST` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "POST",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def put(
        self,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: typing.Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `PUT` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "PUT",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def patch(
        self,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: typing.Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `PATCH` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "PATCH",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def delete(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        auth: AuthTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
        timeout: TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT,
        extensions: RequestExtensions | None = None,
    ) -> BossResponse:
        """
        Send a `DELETE` request.

        **Parameters**: See `httpx.request`.
        """
        return await self.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    def import_cookies(self, cookies: Union[List[CookieDict], Dict[str, str]]):
        """
        Импорт cookies в асинхронный клиент. Автоматически определяет тип:
        - Если Dict[str, str]: преобразует в List[CookieDict] с дефолтными domain='.', path='/', secure=False, без expiration.
        - Если List[CookieDict]: использует напрямую.
        """
        if isinstance(cookies, dict):
            cookies_data: List[CookieDict] = []
            for name, value in cookies.items():
                cookies_data.append({
                    'name': name,
                    'value': value,
                    'domain': '.',  # Дефолтный domain
                    'path': '/',    # Дефолтный path
                    'secure': False,
                    'expirationDate': None,  # Без expiration
                })
        elif isinstance(cookies, list):
            cookies_data = cookies
        else:
            raise ValueError("Неверный тип: ожидается Dict[str, str] или List[Dict]")

        for cookie in cookies_data:
            self.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie.get('path', '/'),
            )

    def export_cookies(self, type: Literal["json", "dict"] = "json") -> Union[str, Dict[str, str]]:
        """
        Экспорт cookies из асинхронного клиента.
        - Если type="json": возвращает JSON-строку из списка полных CookieDict.
        - Если type="dict": возвращает Dict[str, str] (только name: value, игнорируя другие поля).
        """
        cookies_list: List[CookieDict] = []

        for cookie in self.cookies.jar:
            cookies_list.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expirationDate': cookie.expires,
            })

        if type == "json":
            return json.dumps(cookies_list, indent=2, ensure_ascii=False)
        elif type == "dict":
            cookies_dict: Dict[str, str] = {}
            for cookie in cookies_list:
                cookies_dict[cookie['name']] = str(cookie['value'])  # Преобразуем value в str, если нужно
            return cookies_dict
        else:
            raise ValueError("Неверный type: ожидается 'json' или 'dict'")



# Асинхронное использование
async def main_async() -> None:
    async with BossAsyncClientHttpx(
            verify=False,
            proxy="http://127.0.0.1:8080"
    ) as client:
        res = await client.get("https://claude.ai/api/organizations")

        print(res.reason_phrase)
        return
        client.load_cookies_from_file('cookies.json')

        # Запрос
        response: httpx.Response = await client.get('https://claude.ai/api/organizations')
        print(f"Status: {response.status_code}")

        # Сохранение cookies
        cookies_data: List[CookieDict] = client.export_cookies('cookies_updated.json')
        print(f"Сохранено {len(cookies_data)} cookies")


# Запуск асинхронного кода
if __name__ == '__main__':
    import asyncio

    asyncio.run(main_async())