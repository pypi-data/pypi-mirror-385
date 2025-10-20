import click
import sys

@click.command()
@click.option('-c', '--count', is_flag=True, help='Prefix lines by the number of occurrences.')
@click.option('-i', '--ignore-case', is_flag=True, help='Ignore differences in case when comparing.')
@click.argument('input_file', type=click.File('r'), default=sys.stdin)
def pyuniq(count, ignore_case, input_file):
    """
    Filters adjacent matching lines from INPUT_FILE (or stdin).
    Note: 'pyuniq' expects sorted input, just like the real 'uniq'.
    """
    prev_line = None
    line_count = 0

    def format_line(line_text, current_count):
        """Форматує вивід з лічильником або без."""
        if count:
            # Вирівнюємо лічильник для красивого виводу
            return f"{current_count: >7} {line_text}"
        return line_text

    def compare_lines(l1, l2):
        """Порівнює рядки, враховуючи --ignore-case."""
        if ignore_case:
            return l1.lower() == l2.lower()
        return l1 == l2

    try:
        for line in input_file:
            if prev_line is None:
                # Це перший рядок
                prev_line = line
                line_count = 1
                continue

            if compare_lines(line, prev_line):
                # Рядок такий самий, як попередній
                line_count += 1
            else:
                # Рядок змінився, друкуємо попередню групу
                click.echo(format_line(prev_line, line_count), nl=False)
                # і починаємо нову групу
                prev_line = line
                line_count = 1
        
        # Не забути вивести останню групу рядків після завершення файлу
        if prev_line is not None:
             click.echo(format_line(prev_line, line_count), nl=False)

    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
    finally:
        if input_file is not sys.stdin:
            input_file.close()

if __name__ == '__main__':
    pyuniq()