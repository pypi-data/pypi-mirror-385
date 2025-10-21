import sys
import click
from typing import Iterable, List, Tuple


def try_float(s: str):
    """Спроба перетворити рядок у число (float). Якщо не виходить — повертає None."""
    try:
        return float(s)
    except Exception: # якщо не число (наприклад, текст), повертає None
        return None


def read_lines_from_files(files: List[str]) -> Iterable[str]:
    """Зчитує всі рядки з файлів або зі stdin, якщо файлів немає."""
    if not files:
        for line in sys.stdin:
            yield line
    else:
                # Якщо користувач передав список файлів

        for fname in files:
            if fname == "-":
                                # Символ "-" означає: читати з stdin замість файлу

                for line in sys.stdin:
                    yield line
            else:
                                # Відкриваємо файл у режимі читання з кодуванням UTF-8

                with open(fname, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        yield line # Повертаємо рядки один за одним


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-r", "--reverse", is_flag=True, default=False, help="Reverse sort order")
@click.option("-n", "--numeric", is_flag=True, default=False, help="Compare according to numeric value")
@click.argument("files", nargs=-1, type=click.Path(exists=False))
def cli(reverse: bool, numeric: bool, files):
    print('my sort processing')
# @click.command — визначає функцію як CLI-команду
# -r / --reverse — міняє порядок сортування на зворотний
# -n / --numeric — сортування за числовим значенням
# files — список вхідних файлів (може бути кілька або жодного)




    lines = list(read_lines_from_files(list(files)))
    
    if numeric:
        # Якщо користувач вибрав числове сортування (-n)
        def keyfunc(line: str) -> Tuple[int, object]:
            s = line.rstrip("\n") # Видаляємо \n, щоб не впливало на порівняння
            f = try_float(s) # Пробуємо перетворити рядок у число
            if f is not None:
                # (0, f) — усі числові значення сортуються перед нечисловими
                return (0, f)
            else:
                 # (1, s) — нечислові значення після числових
                return (1, s)
    else:
         # Якщо текстове сортування
        def keyfunc(line: str):
            return line # Ключ — сам рядок
    
    try:
         # Основне сортування списку in-place
        lines.sort(key=keyfunc, reverse=reverse)
    except TypeError:
         # Якщо під час сортування виникає помилка (наприклад, змішані типи),
        # використовуємо запасний варіант — перетворюємо все в рядки і сортуємо стабільно
        lines = sorted(lines, key=lambda l: str(keyfunc(l)), reverse=reverse)
    
    # Виводимо всі рядки як є
    out = sys.stdout
    for line in lines:
        out.write(line) # Пишемо рядок без додаткових \n — вони вже є в тексті


if __name__ == "__main__":
    cli()