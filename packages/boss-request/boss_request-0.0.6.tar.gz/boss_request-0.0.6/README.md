# Boss Request

Патч для библиотек `httpx` и `curl-cffi`, расширяет оригинальный функционал:

1. `json_clean()` - Нормализует невалидные json:
2. `export_cookies()` - Экспорта куки в браузерный формат
3. `import_cookies(json)` - Импорт куки в браузерный формат
4. Можно вызывать прямо из response или client
5. Одинаковый интерфейс для `httpx` и `curl-cffi`

## Установка
```bash

uv add boss-request | pip install boss-request
```


Патч для curl-cffi (требует установки оригинального `curl-cffi`)
```python
from bose_request import BossAsyncSessionCurlCffi
```
```python
uv add curl-cffi | pip install curl-cffi
```

Патч для httpx (требует установки оригинального `httpx`)
```python
from bose_request import BossAsyncClientHttpx
```
```python
uv add httpx | pip install httpx
```

## Переноси куки прям из браузера

![img_3.png](img_3.png)

#### Вызови `import_cookies(json) - вставь json`

```python

async with BossAsyncSessionCurlCffi() as client:
    await client.get("https://claude.ai/api/organizations")

    cookies = client.import_cookies(json)
    
    
```
## Или же экспорт куки в браузер


```python

async with BossAsyncSessionCurlCffi() as client:
    await client.get("https://claude.ai/api/organizations")

    cookies_json = client.export_cookies()
    
    # Или возьми сессонные куки прямо из response
    response = await client.get("https://google.com/")
    cookies_json = response.export_cookies() 
    
    # Или экспортируй в формате dict
    response = await client.get("https://google.com/")
    cookies_dict = response.export_cookies("dict") 
    
    # Результат
    {'__fcd': 'OQKJQOVUCAZWJXHN','isRedirectLang': '1',}


    
```

## Нормализуй невалидный json


```python

async with BossAsyncSessionCurlCffi() as client:
    response = await client.get("https://claude.ai/api/organizations")
    
    #Новый метод
    valid_json = response.json_clean()
    
    #Оригинальный метод остался на месте
    ivnalid_json = response.json()
    
    
```

Библиотека на изменяет оригинальный функционал, она лишь дополняет
