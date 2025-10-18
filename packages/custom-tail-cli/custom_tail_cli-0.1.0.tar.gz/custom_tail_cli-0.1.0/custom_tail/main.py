# custom_tail/main.py
import click
import sys
import time

@click.command()
@click.argument('file', type=click.File('r'))
@click.option('-n', '--lines', type=int, default=10, help='Number of lines to show.')
@click.option('-f', '--follow', is_flag=True, help='Output appended data as the file grows.')
def cli(file, lines, follow):
    """
    Displays the last part of a file. Mimics the GNU tail command.
    """
    if not follow:
        # Простий режим: показати останні N рядків і вийти
        all_lines = file.readlines()
        last_lines = all_lines[-lines:]
        sys.stdout.writelines(last_lines)
    else:
        # Режим -f: стежити за файлом
        # Спочатку виводимо останні N рядків
        all_lines = file.readlines()
        last_lines = all_lines[-lines:]
        sys.stdout.writelines(last_lines)
        sys.stdout.flush()

        # Починаємо стежити
        while True:
            where = file.tell()
            new_line = file.readline()
            if not new_line:
                time.sleep(0.5) # Затримка, щоб не навантажувати CPU
                file.seek(where)
            else:
                sys.stdout.write(new_line)
                sys.stdout.flush()

if __name__ == '__main__':
    cli()