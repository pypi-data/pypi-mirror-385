import click
import sys

@click.command()
@click.option('-n', '--lines', 'num_lines', 
              default=10, 
              type=int, 
              help='Print the first NUM lines instead of the first 10.')
@click.argument('file', 
              type=click.File('r'), 
              default=sys.stdin)
def pyhead(num_lines, file):
    """
    Prints the first NUM lines (default 10) of a FILE, or standard input.
    """
    if num_lines < 0:
        click.echo("Error: number of lines must be a non-negative integer.", err=True)
        sys.exit(1)
        
    try:
        # Ми перебираємо рядки і зупиняємось, коли досягаємо ліміту
        for i, line in enumerate(file):
            if i >= num_lines:
                break
            # nl=False, тому що 'line' вже містить символ нового рядка \n
            click.echo(line, nl=False)
            
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        
    finally:
        # Важливо закрити файл, якщо це не стандартний ввід
        if file is not sys.stdin:
            file.close()

if __name__ == '__main__':
    pyhead()