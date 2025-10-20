# bose_request/__init__.py

try:
    from .patch_httpx.client import BossResponse as HttpxBossResponse, BossAsyncClientHttpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from .patch_curl_cffi.async_client import BossAsyncSessionCurlCffi, BossResponse as CurlCffiBossResponse

    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

_HTTPX_NAMES = {'BossAsyncClientHttpx', 'HttpxBossResponse'}
_CURL_NAMES = {'BossAsyncSessionCurlCffi', 'CurlCffiBossResponse'}


def __getattr__(name):
    if name in _HTTPX_NAMES:
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "Библиотека httpx не установлена. Установите её с помощью одной из команд:\n"
                "pip install httpx\n"
                "или\n"
                "uv add httpx"
            )
        from .patch_httpx.client import BossAsyncClientHttpx, BossResponse as HttpxBossResponse
        return locals()[name]

    if name in _CURL_NAMES:
        if not CURL_CFFI_AVAILABLE:
            raise ImportError(
                "Библиотека curl_cffi не установлена. Установите её с помощью одной из команд:\n"
                "pip install curl_cffi\n"
                "или\n"
                "uv add curl_cffi"
            )
        from .patch_curl_cffi.async_client import BossAsyncSessionCurlCffi, BossResponse as CurlCffiBossResponse
        return locals()[name]

    raise AttributeError(f"module 'bose_request' has no attribute '{name}'")


def check_dependencies():
    return {'httpx': HTTPX_AVAILABLE, 'curl_cffi': CURL_CFFI_AVAILABLE}


__all__ = [*_HTTPX_NAMES, *_CURL_NAMES, 'HTTPX_AVAILABLE', 'CURL_CFFI_AVAILABLE', 'check_dependencies']