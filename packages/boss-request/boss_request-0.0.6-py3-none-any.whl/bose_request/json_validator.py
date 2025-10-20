import json
import re
from typing import Any, Union, List, Dict


class JSONValidator:
    """Универсальный валидатор и нормализатор JSON"""

    @staticmethod
    def normalize(data: Union[str, bytes, Dict, List], _depth: int = 0) -> Union[Dict, List, None]:
        """
        Нормализует любой JSON в стандартный формат.

        Args:
            data: Сырые данные (строка, байты, dict, list)
            _depth: Глубина рекурсии (защита от бесконечной рекурсии)

        Returns:
            Нормализованный JSON (dict или list) или None если не удалось распарсить
        """
        # Защита от бесконечной рекурсии
        if _depth > 10:
            return None

        # Если уже dict или list - вернуть как есть
        if isinstance(data, (dict, list)):
            return data

        # Конвертировать bytes в string
        if isinstance(data, bytes):
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                data = data.decode('utf-8', errors='ignore')

        # Если не строка - попробовать конвертировать
        if not isinstance(data, str):
            data = str(data)

        # Убрать пробелы по краям
        data = data.strip()

        # Если пустая строка
        if not data:
            return None

        # 1. Попробовать распарсить как обычный JSON
        try:
            result = json.loads(data)
            # Если получилась строка - рекурсивно распарсить
            if isinstance(result, str):
                return JSONValidator.normalize(result, _depth + 1)
            return result
        except json.JSONDecodeError:
            pass

        # 2. Множественные JSON объекты подряд: {...}{...}{...}
        multiple_jsons = JSONValidator._extract_multiple_jsons(data)
        if multiple_jsons is not None:
            return multiple_jsons

        # 3. JSON с комментариями или trailing commas (попробовать очистить)
        cleaned = JSONValidator._clean_json(data)
        if cleaned and cleaned != data:  # Если что-то изменилось
            try:
                result = json.loads(cleaned)
                # Если получилась строка - рекурсивно распарсить
                if isinstance(result, str):
                    return JSONValidator.normalize(result, _depth + 1)
                return result
            except json.JSONDecodeError:
                pass

        # Если ничего не помогло - вернуть None
        return None

    @staticmethod
    def _extract_multiple_jsons(data: str) -> Union[Dict, List, None]:
        """Извлечь множественные JSON объекты из строки"""
        results = []

        # Найти все JSON объекты {...}
        bracket_count = 0
        start_idx = None

        for i, char in enumerate(data):
            if char == '{':
                if bracket_count == 0:
                    start_idx = i
                bracket_count += 1
            elif char == '}':
                bracket_count -= 1
                if bracket_count == 0 and start_idx is not None:
                    json_str = data[start_idx:i + 1]
                    try:
                        obj = json.loads(json_str)
                        results.append(obj)
                    except json.JSONDecodeError:
                        pass
                    start_idx = None

        # Найти все JSON массивы [...]
        if not results:
            bracket_count = 0
            start_idx = None

            for i, char in enumerate(data):
                if char == '[':
                    if bracket_count == 0:
                        start_idx = i
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0 and start_idx is not None:
                        json_str = data[start_idx:i + 1]
                        try:
                            obj = json.loads(json_str)
                            results.append(obj)
                        except json.JSONDecodeError:
                            pass
                        start_idx = None

        # Если ничего не нашли
        if not results:
            return None

        # Если нашли только 1 объект - вернуть его, а не список
        if len(results) == 1:
            return results[0]

        return results

    @staticmethod
    def _clean_json(data: str) -> str:
        """Очистить JSON от комментариев и trailing commas"""
        # Убрать комментарии // ...
        data = re.sub(r'//.*?$', '', data, flags=re.MULTILINE)

        # Убрать комментарии /* ... */
        data = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)

        # Убрать trailing commas: ,}
        data = re.sub(r',\s*}', '}', data)
        data = re.sub(r',\s*]', ']', data)

        return data.strip()

    @staticmethod
    def safe_parse(data: Any, default: Any = None) -> Any:
        """
        Безопасный парсинг с fallback значением.

        Args:
            data: Данные для парсинга
            default: Значение по умолчанию если парсинг не удался

        Returns:
            Распарсенный JSON или default
        """
        result = JSONValidator.normalize(data)
        return result if result is not None else default

    @staticmethod
    def is_valid(data: Any) -> bool:
        """Проверить валидность JSON"""
        return JSONValidator.normalize(data) is not None


# Примеры использования
if __name__ == '__main__':
    validator = JSONValidator()

    print("=" * 60)
    # Тест 1: Обычный JSON
    test1 = '{"origin": "79.127.184.233"}'
    result1 = validator.normalize(test1)
    print("Test 1 - Обычный JSON:")
    print("  Input:", test1)
    print("  Result:", result1)
    print("  Type:", type(result1))
    if isinstance(result1, dict):
        print("  origin:", result1.get('origin'))

    print("\n" + "=" * 60)
    # Тест 2: Множественные JSON
    test2 = '{"origin": "79.127.184.233"}{"origin": "79.127.184.234"}{"origin": "79.127.184.235"}'
    result2 = validator.normalize(test2)
    print("Test 2 - Множественные JSON:")
    print("  Input:", test2[:50] + "...")
    print("  Result:", result2)
    print("  Type:", type(result2))
    if isinstance(result2, list):
        print("  Count:", len(result2))
        print("  First origin:", result2[0].get('origin'))

    print("\n" + "=" * 60)
    # Тест 3: JSON обернутый в строку
    test3 = '"{\\n  \\"origin\\": \\"79.127.184.233\\"\\n}"'
    result3 = validator.normalize(test3)
    print("Test 3 - JSON в строке:")
    print("  Input:", test3)
    print("  Result:", result3)
    print("  Type:", type(result3))
    if isinstance(result3, dict):
        print("  origin:", result3.get('origin'))
    else:
        print("  ERROR: Expected dict, got", type(result3))

    print("\n" + "=" * 60)
    # Тест 4: Двойная упаковка в строку
    test4 = '"{\\"origin\\":\\"79.127.184.233\\"}"'
    result4 = validator.normalize(test4)
    print("Test 4 - Двойная упаковка:")
    print("  Input:", test4)
    print("  Result:", result4)
    print("  Type:", type(result4))
    if isinstance(result4, dict):
        print("  origin:", result4.get('origin'))

    print("\n" + "=" * 60)
    # Тест 5: Bytes
    test5 = b'{"origin": "79.127.184.233"}'
    result5 = validator.normalize(test5)
    print("Test 5 - Bytes:")
    print("  Input:", test5)
    print("  Result:", result5)
    if isinstance(result5, dict):
        print("  origin:", result5.get('origin'))

    print("\n" + "=" * 60)
    # Тест 6: Уже dict
    test6 = {"origin": "79.127.184.233"}
    result6 = validator.normalize(test6)
    print("Test 6 - Уже dict:")
    print("  Result:", result6)
    if isinstance(result6, dict):
        print("  origin:", result6.get('origin'))

    print("\n" + "=" * 60)
    # Тест 7: С комментариями
    test7 = """
    {
        "origin": "79.127.184.233"
    }
    """
    result7 = validator.normalize(test7)
    print("Test 7 - С комментариями:")
    print("  Result:", result7)
    if isinstance(result7, dict):
        print("  origin:", result7.get('origin'))

    print("\n" + "=" * 60)
    # Тест 8: Невалидный JSON
    test8 = 'not a json'
    result8 = validator.normalize(test8)
    print("Test 8 - Невалидный:")
    print("  Result:", result8)

    print("\n" + "=" * 60)
    # Тест 9: safe_parse с default
    test9 = 'invalid'
    result9 = validator.safe_parse(test9, default={'error': 'invalid'})
    print("Test 9 - safe_parse:")
    print("  Result:", result9)

    print("\n" + "=" * 60)
    # Тест 10: Тройная упаковка
    test10 = '"\\"{\\\\\\"origin\\\\\\":\\\\\\"79.127.184.233\\\\\\"}\\"" '
    result10 = validator.normalize(test10)
    print("Test 10 - Тройная упаковка:")
    print("  Input:", test10)
    print("  Result:", result10)
    print("  Type:", type(result10))