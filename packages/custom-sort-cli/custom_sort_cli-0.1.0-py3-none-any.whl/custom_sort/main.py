# custom_sort/main.py
import click
import sys

@click.command()
@click.argument('file', type=click.File('r'), default=sys.stdin)
@click.option('-r', '--reverse', is_flag=True, help='Sort in reverse order.')
@click.option('-n', '--numeric', is_flag=True, help='Compare according to string numerical value.')
@click.option('-u', '--unique', is_flag=True, help='Output only the first of an equal run.')
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout, help='Write result to a file instead of stdout.')
def cli(file, reverse, numeric, unique, output):
    """
    Sorts lines of text from a FILE or standard input.

    This tool mimics the basic functionality of the GNU sort command.
    """
    try:
        lines = file.readlines()

        # Застосовуємо унікальність, якщо потрібно
        if unique:
            lines = sorted(list(set(lines))) # Найпростіший спосіб зробити унікальними і посортувати

        # Визначаємо ключ сортування
        sort_key = None
        if numeric:
            def sort_key(line):
                try:
                    # Спробуємо перетворити рядок (або його першу частину) в число
                    return float(line.strip().split()[0])
                except (ValueError, IndexError):
                    return 0.0 # Якщо не число, вважаємо за 0

        # Сортування
        sorted_lines = sorted(lines, key=sort_key, reverse=reverse)

        # Вивід результату
        output.writelines(sorted_lines)

    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()