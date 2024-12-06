import sys
import argparse
import yaml
import re


def convert_value(value):
    """
    Конвертирует значение из python-объекта в строку учебного конфигурационного языка.
    """
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, list):
        converted_items = [convert_value(item) for item in value]
        return "list(" + ",".join(converted_items) + ")"
    elif isinstance(value, dict):

        if len(value) == 1:
            (dict_key, dict_val), = value.items()
            if isinstance(dict_val, list):
                return convert_value(dict_val)

        raise ValueError("Недопустимый тип данных: поддерживаются только числа, строки и списки, "
                         "либо особый случай словаря с одним ключом внутри списка.")
    else:
        # Если тип неизвестен
        raise ValueError("Недопустимый тип данных: поддерживаются только числа, строки и списки.")


def is_valid_name(name):
    """
    Проверяет, соответствует ли имя шаблону [a-zA-Z]+
    """
    pattern = re.compile(r'^[a-zA-Z]+$')
    return bool(pattern.match(name))


def main():
    parser = argparse.ArgumentParser(description="YAML to custom config language converter")
    parser.add_argument("-i", "--input", required=True, help="Path to input YAML file")
    parser.add_argument("-o", "--output", required=True, help="Path to output file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Ошибка: входной файл {args.input} не найден.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Ошибка парсинга YAML: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print("Ошибка: верхний уровень должен быть словарём ключ-значение.", file=sys.stderr)
        sys.exit(1)

    lines = []
    for key, value in data.items():
        if not is_valid_name(key):
            print(f"Ошибка: имя '{key}' не соответствует шаблону [a-zA-Z]+", file=sys.stderr)
            sys.exit(1)

        try:
            val_str = convert_value(value)
        except ValueError as err:
            print(f"Ошибка: {err}", file=sys.stderr)
            sys.exit(1)

        line = f"{key} := {val_str};"
        lines.append(line)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
    except IOError as e:
        print(f"Ошибка записи в файл {args.output}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
