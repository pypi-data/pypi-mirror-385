![FunPay Parsers logo](https://repository-images.githubusercontent.com/987755633/dc43078b-d948-4a54-8beb-e76cd864b9d7)

<h3 align=center>Набор удобных и структурированных парсеров для популярной биржи игровых ценностей <a href="https://funpay.com">FunPay</a>.</h3>
<hr>

### ⚡ Скорость
FunPay Parser использует [Selectolax](https://github.com/rushter/selectolax) на [Lexbor](https://github.com/lexbor/lexbor),
что делает скорость парсинга крайне высокой. Например, парсинг 4000 лотов занимает всего ~0.2 секунды!

### ✅ Удобство
Парсеры преобразуют HTML в удобные и структурированные датаклассы.

### 📊 Покрытие
С помощью FunPay Parser можно спарсить 99% всех сущностей FunPay. Начиная с бейджиков и заканчивая целыми страницами.

### 🛠️ Надёжность
Для большинства парсеров написано по несколько тест-кейсов, основанных на реальном HTML [FunPay](https://funpay.com).

### 🧪 Поддержка MyPy
FunPay Parsers полностью поддерживает Mypy и обеспечивает строгую статическую типизацию для повышения надёжности кода.

## Установка
```commandline
pip install funpayparsers
```

## Пример использования
```python
from funpayparsers.parsers.page_parsers import MainPageParser
import requests

html = requests.get('https://funpay.com').content.decode()
main_page = MainPageParser(html).parse()

for i in main_page.categories:
    print(f'{i.full_name} (ID: {i.id})')
```
```
Abyss of Dungeons (ID: 754)
Acrobat (ID: 655)
Adobe (ID: 652)
AFK Arena (ID: 250)
AFK Journey (ID: 503)
After Effects (ID: 654)
Age of Empires Mobile (ID: 628)
Age of Mythology: Retold (ID: 534)
Age of Wonders 4 (ID: 344)
...
```

## 🗨️ Telegram чат
Если у вас возникли какие-либо вопросы, вы можете задать их в нашем [Telegram чате](https://t.me/funpay_hub)


## ⭐ Понравился проект?
Если вы нашли использование `funpayparsers` удобным, будем рады, если вы поставите звезду 😀
