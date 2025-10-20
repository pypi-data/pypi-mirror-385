# wrapcolor

Універсальний ANSI-«кольоризатор» для Python: простий спосіб стилізувати текст у консолі.
Підтримує 8/16 базових кольорів, 256‑кольорову палітру (xterm) та TrueColor (RGB), а також стилі шрифту.

- Легкий і без залежностей (опційно: colorama для Windows)
- Зручний екземпляр color із готовими кодами та утилітами
- Працює з будь‑якою бібліотекою, що виводить у термінал (logging, click, argparse тощо)

## Встановлення

```bash
pip install wrapcolor
# (опційно для Windows консоль/PowerShell)
pip install colorama
```

Якщо ви на Windows, рекомендовано ініціалізувати colorama на старті:

```python
try:
    from colorama import justFixWindowsConsole
    justFixWindowsConsole()
except Exception:
    pass
```

## Швидкий старт

```python
from wrapcolor import color

print(color.paint("Привіт!", fg="red", styles=["bold"]))
print(color.rgb(255, 100, 0) + "TrueColor текст" + color.reset)
print(color.bg_idx(24) + "Фон 256‑кольорів" + color.reset)
```

## Приклади використання

### 1) Базові кольори тексту
```python
from wrapcolor import color

print(color.red + "Червоний" + color.reset)
print(color.green + "Зелений" + color.reset)
print(color.bright_blue + "Яскраво‑синій" + color.reset)
```

### 2) Кольори фону
```python
from wrapcolor import color

print(color.bg_yellow + color.black + "Чорний на жовтому" + color.reset)
print(color.bg_bright_red + color.white + "Білий на яскраво‑червоному" + color.reset)
```

### 3) Стилі шрифту
```python
from wrapcolor import color

print(color.bold + "Жирний" + color.reset)
print(color.italic + "Курсив" + color.reset)
print(color.underline + "Підкреслений" + color.reset)
print(color.inverse + "Інверсія" + color.reset)
print(color.strike + "Закреслений" + color.reset)
```

### 4) Комбінування стилів і кольорів
```python
from wrapcolor import color

print(color.red + color.bold + "Червоний жирний" + color.reset)
print(color.bright_green + color.underline + "Зелений підкреслений" + color.reset)
```

### 5) Зручний paint()
```python
from wrapcolor import color

print(color.paint("OK", fg="green", styles=["bold"]))
print(color.paint("УВАГА", fg="bright_yellow", bg="bg_black", styles=["underline"]))
print(color.paint("ПОМИЛКА", fg="bright_white", bg="bg_red", styles=["bold"]))
```

Перевага paint() — воно автоматично додає reset наприкінці.

### 6) Шаблон wrap() для багаторазового використання
```python
from wrapcolor import color

warn = color.wrap(color.bright_yellow + color.bold)
err  = color.wrap(color.bg_red + color.white + color.bold)

print(warn.format("Попередження"))
print(err.format("Помилка"))
```

### 7) 256‑кольорів (xterm)
```python
from wrapcolor import color

for i in range(16, 32):
    print(color.idx(i) + f" idx({i}) " + color.reset, end=" ")
print()

for i in [196, 202, 208, 214, 220, 226]:
    print(color.idx(i) + "●" + color.reset, end=" ")
print()

print(color.bg_idx(24) + color.bright_white + "Текст на фоні idx(24)" + color.reset)
```

### 8) TrueColor (RGB)
```python
from wrapcolor import color

print(color.rgb(12, 200, 155) + "RGB передній план" + color.reset)
print(color.bg_rgb(20, 20, 20) + color.bright_cyan + "Яскравий на темному" + color.reset)
```

### 9) Допоміжні функції для статусів
```python
from wrapcolor import color

def ok(msg):
    return color.paint(msg, fg="green", styles=["bold"])

def warn(msg):
    return color.paint(msg, fg="bright_yellow")

def err(msg):
    return color.paint(msg, fg="bright_white", bg="bg_red", styles=["bold"]) 

print(ok("Готово"))
print(warn("Увага"))
print(err("Збій"))
```

### 10) Інтеграція з logging
```python
import logging
from wrapcolor import color

class ColorFormatter(logging.Formatter):
    LEVEL_COLOR = {
        logging.DEBUG: color.dim,
        logging.INFO: color.bright_green,
        logging.WARNING: color.bright_yellow,
        logging.ERROR: color.bright_red,
        logging.CRITICAL: color.bg_red + color.white + color.bold,
    }
    def format(self, record):
        base = super().format(record)
        code = self.LEVEL_COLOR.get(record.levelno, "")
        return f"{code}{base}{color.reset}" if code else base

h = logging.StreamHandler()
fmt = ColorFormatter("%(levelname)s: %(message)s")
h.setFormatter(fmt)
log = logging.getLogger("demo")
log.addHandler(h)
log.setLevel(logging.DEBUG)

log.debug("debug")
log.info("info")
log.warning("warning")
log.error("error")
log.critical("critical")
```

### 11) Поважайте NO_COLOR і TTY
```python
import os, sys
from wrapcolor import color as _color

USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None

class _NoColor:
    reset = ""
    bold = dim = italic = underline = inverse = strike = ""
    black = red = green = yellow = blue = magenta = cyan = white = ""
    bright_black = bright_red = bright_green = bright_yellow = ""
    bright_blue = bright_magenta = bright_cyan = bright_white = ""
    bg_black = bg_red = bg_green = bg_yellow = bg_blue = bg_magenta = bg_cyan = bg_white = ""
    bg_bright_black = bg_bright_red = bg_bright_green = bg_bright_yellow = ""
    bg_bright_blue = bg_bright_magenta = bg_bright_cyan = bg_bright_white = ""
    @staticmethod
    def idx(n): return ""
    @staticmethod
    def bg_idx(n): return ""
    @staticmethod
    def rgb(r,g,b): return ""
    @staticmethod
    def bg_rgb(r,g,b): return ""
    @classmethod
    def paint(cls, text, *, fg=None, bg=None, styles=None): return str(text)
    @classmethod
    def wrap(cls, code): return "{}"

color = _color if USE_COLOR else _NoColor()

print(color.paint("Це працює навіть без кольорів", fg="green"))
```

### 12) Підказки та нюанси
- Якщо поєднуєте коди вручну, не забудьте в кінці додати color.reset.
- paint() та wrap() самі додають reset, що зручно для безпечного форматування.
- Не всі термінали підтримують 256/TrueColor — на старих системах кольори можуть знижуватись.

## Довідка API (скорочено)

Об’єкти й методи доступні з:
```python
from wrapcolor import color, _Color
```

- Атрибути стилів: bold, dim, italic, underline, inverse, strike
- 8 кольорів переднього плану: black, red, green, yellow, blue, magenta, cyan, white
- Яскраві варіанти: bright_black .. bright_white
- Фон: bg_black .. bg_white, bg_bright_black .. bg_bright_white
- Методи:
  - idx(n: int) -> str — 256‑кольорів (0..255), передній план
  - bg_idx(n: int) -> str — 256‑кольорів (0..255), фон
  - rgb(r,g,b) -> str — TrueColor (0..255) передній план
  - bg_rgb(r,g,b) -> str — TrueColor (0..255) фон
  - paint(text, *, fg=None, bg=None, styles=None) -> str — безпечно обгортає текст і додає reset
  - wrap(code: str) -> str — повертає шаблон "{code}{}\x1b[0m" для багаторазового format()

## Сумісність
- Python 3.10+
- Linux/macOS/Windows (для Windows бажано colorama)

## Чому wrapcolor?
- Мінімалістичний інтерфейс: використовуй властивості або утиліти
- Не нав’язує залежностей
- Добре працює з існуючими бібліотеками

## Ліцензія
MIT

## Внесок
Issue/PR вітаються.