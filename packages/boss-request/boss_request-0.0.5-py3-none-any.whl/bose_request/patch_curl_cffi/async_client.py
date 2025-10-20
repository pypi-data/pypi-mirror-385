import asyncio
from typing import Any, Callable, Coroutine, List, Literal, Optional, TypedDict, Union, Dict
from pathlib import Path
import json
from ..json_validator import JSONValidator

from io import BytesIO
try:
    from curl_cffi import CurlHttpVersion, CurlMime
    from curl_cffi.requests import AsyncSession, Response, Unpack  # Импортируем оригинальные
    from curl_cffi.requests import (
        BrowserTypeLiteral, Cookies, CookieTypes, ExtraFingerprints,
        HeaderTypes, HttpMethod, ProxySpec, RequestParams
    )


    from curl_cffi.requests.impersonate import ExtraFpDict
    from curl_cffi.requests.utils import not_set, HttpVersionLiteral

except ImportError as e:
    raise ImportError(
        "Библиотека curl_cffi не установлена. Установите её с помощью одной из команд:\n"
        "pip install curl_cffi\n"
        "или\n"
        "uv add curl_cffi"
    ) from e

CookieDict = Dict[str, Any]

# Ваш MyResponse из предыдущего кода (предполагаю, что он уже определён)
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
            

# Кастомный MyAsyncSession, наследующий от AsyncSession
class BossAsyncSessionCurlCffi(AsyncSession[BossResponse]):
    def __init__(self, **kwargs):
        # Передаём response_class
        # =MyResponse в супер-класс
        super().__init__(response_class=BossResponse, **kwargs)

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
                    'path': '/',  # Дефолтный path
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


    # Переопределяем request с полной сигнатурой для подсказок в IDE
    async def request(
        self,
        method: HttpMethod,
        url: str,
        params: Optional[Union[dict, list, tuple]] = None,
        data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
        json: Optional[dict | list] = None,
        headers: Optional[HeaderTypes] = None,
        cookies: Optional[CookieTypes] = None,
        files: Optional[dict] = None,
        auth: Optional[tuple[str, str]] = None,
        timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
        allow_redirects: Optional[bool] = None,
        max_redirects: Optional[int] = None,
        proxies: Optional[ProxySpec] = None,
        proxy: Optional[str] = None,
        proxy_auth: Optional[tuple[str, str]] = None,
        verify: Optional[bool] = None,
        referer: Optional[str] = None,
        accept_encoding: Optional[str] = "gzip, deflate, br",
        content_callback: Optional[Callable] = None,
        impersonate: Optional[BrowserTypeLiteral] = None,
        ja3: Optional[str] = None,
        akamai: Optional[str] = None,
        extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
        default_headers: Optional[bool] = None,
        default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
        quote: Union[str, Literal[False]] = "",
        http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
        interface: Optional[str] = None,
        cert: Optional[Union[str, tuple[str, str]]] = None,
        stream: Optional[bool] = None,
        max_recv_speed: int = 0,
        multipart: Optional[CurlMime] = None,
        discard_cookies: bool = False,
    ) -> BossResponse:
        return await super().request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    # Переопределяем get с полной сигнатурой для подсказок в IDE
        # Аналогично для get — используем Unpack[RequestParams] как в оригинале
    async def get(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="GET",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    # Аналогично добавьте для post, put и других методов, если нужно
    async def post(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="POST",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    async def put(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    async def patch(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="PATCH",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    async def options(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="OPTIONS",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    async def delete(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="DELETE",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

    async def head(
            self,
            url: str,
            params: Optional[Union[dict, list, tuple]] = None,
            data: Optional[Union[dict[str, str], list[tuple], str, BytesIO, bytes]] = None,
            json: Optional[dict | list] = None,
            headers: Optional[HeaderTypes] = None,
            cookies: Optional[CookieTypes] = None,
            files: Optional[dict] = None,
            auth: Optional[tuple[str, str]] = None,
            timeout: Optional[Union[float, tuple[float, float], object]] = not_set,
            allow_redirects: Optional[bool] = None,
            max_redirects: Optional[int] = None,
            proxies: Optional[ProxySpec] = None,
            proxy: Optional[str] = None,
            proxy_auth: Optional[tuple[str, str]] = None,
            verify: Optional[bool] = None,
            referer: Optional[str] = None,
            accept_encoding: Optional[str] = "gzip, deflate, br",
            content_callback: Optional[Callable] = None,
            impersonate: Optional[BrowserTypeLiteral] = None,
            ja3: Optional[str] = None,
            akamai: Optional[str] = None,
            extra_fp: Optional[Union[ExtraFingerprints, ExtraFpDict]] = None,
            default_headers: Optional[bool] = None,
            default_encoding: Union[str, Callable[[bytes], str]] = "utf-8",
            quote: Union[str, Literal[False]] = "",
            http_version: Optional[Union[CurlHttpVersion, HttpVersionLiteral]] = None,
            interface: Optional[str] = None,
            cert: Optional[Union[str, tuple[str, str]]] = None,
            stream: Optional[bool] = None,
            max_recv_speed: int = 0,
            multipart: Optional[CurlMime] = None,
            discard_cookies: bool = False,
    ) -> BossResponse:
        return await self.request(
            method="HEAD",
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            max_redirects=max_redirects,
            proxies=proxies,
            proxy=proxy,
            proxy_auth=proxy_auth,
            verify=verify,
            referer=referer,
            accept_encoding=accept_encoding,
            content_callback=content_callback,
            impersonate=impersonate,
            ja3=ja3,
            akamai=akamai,
            extra_fp=extra_fp,
            default_headers=default_headers,
            default_encoding=default_encoding,
            quote=quote,
            http_version=http_version,
            interface=interface,
            cert=cert,
            stream=stream,
            max_recv_speed=max_recv_speed,
            multipart=multipart,
            discard_cookies=discard_cookies,
        )

