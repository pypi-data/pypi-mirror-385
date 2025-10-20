# -*- coding: utf-8 -*-
# Універсальний ANSI-«кольоризатор» для Python

class _Color:
    # спец
    reset = "\033[0m"

    # стилі
    bold = "\033[1m"
    dim = "\033[2m"
    italic = "\033[3m"
    underline = "\033[4m"
    inverse = "\033[7m"
    strike = "\033[9m"

    # 8 кольорів (текст)
    black   = "\033[30m"
    red     = "\033[31m"
    green   = "\033[32m"
    yellow  = "\033[33m"
    blue    = "\033[34m"
    magenta = "\033[35m"
    cyan    = "\033[36m"
    white   = "\033[37m"

    # яскраві 8 (текст)
    bright_black   = "\033[90m"
    bright_red     = "\033[91m"
    bright_green   = "\033[92m"
    bright_yellow  = "\033[93m"
    bright_blue    = "\033[94m"
    bright_magenta = "\033[95m"
    bright_cyan    = "\033[96m"
    bright_white   = "\033[97m"

    # 8 кольорів (фон)
    bg_black   = "\033[40m"
    bg_red     = "\033[41m"
    bg_green   = "\033[42m"
    bg_yellow  = "\033[43m"
    bg_blue    = "\033[44m"
    bg_magenta = "\033[45m"
    bg_cyan    = "\033[46m"
    bg_white   = "\033[47m"

    # яскравий фон
    bg_bright_black   = "\033[100m"
    bg_bright_red     = "\033[101m"
    bg_bright_green   = "\033[102m"
    bg_bright_yellow  = "\033[103m"
    bg_bright_blue    = "\033[104m"
    bg_bright_magenta = "\033[105m"
    bg_bright_cyan    = "\033[106m"
    bg_bright_white   = "\033[107m"

    # -------- 256-колірні та RGB помічники --------
    @staticmethod
    def idx(n: int) -> str:
        """256-color foreground: 0..255"""
        n = max(0, min(255, int(n)))
        return f"\033[38;5;{n}m"

    @staticmethod
    def bg_idx(n: int) -> str:
        """256-color background: 0..255"""
        n = max(0, min(255, int(n)))
        return f"\033[48;5;{n}m"

    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """TrueColor foreground"""
        r, g, b = (max(0, min(255, int(x))) for x in (r, g, b))
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """TrueColor background"""
        r, g, b = (max(0, min(255, int(x))) for x in (r, g, b))
        return f"\033[48;2;{r};{g};{b}m"

    # -------- утиліти --------
    @classmethod
    def paint(cls, text: str, *, fg: str | None = None,
              bg: str | None = None, styles: list[str] | None = None) -> str:
        """
        fg/bg — імена атрибутів класу (наприклад, 'red', 'bg_blue', 'bright_green')
        styles — список імен стилів (наприклад, ['bold','underline'])
        """
        seqs = []
        if fg:
            seqs.append(getattr(cls, fg))
        if bg:
            seqs.append(getattr(cls, bg))
        if styles:
            for s in styles:
                seqs.append(getattr(cls, s))
        return "".join(seqs) + str(text) + cls.reset

    @classmethod
    def wrap(cls, code: str) -> str:
        """Вручну скласти послідовність і обгорнути текст: color.wrap(color.red + color.bold)"""
        return f"{code}{{}}{cls.reset}"

# зручний екземпляр
color = _Color()
