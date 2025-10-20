import typer, pyfiglet
from rich.console import Console

cn = Console()
app = typer.Typer()

@app.command()
def main(name: str,
         mode: str = typer.Option("normal", "--mode", "-m", help=
         """<< Choose a mode (Optional) >>
            
                modes: 
                       normal
                       colorful
                       ascii
                       asciicolor
                       emoji
                       emojicolor""")):
    if mode == "normal":
        print("Hello",name)
    elif mode == "colorful":
        cn.print(f"[bold green]Hello[/bold green] [bold blue]{name}[/bold blue][bold white].[/bold white]")
    elif mode == "ascii":
        h = f"Hello   {name}"
        f = pyfiglet.figlet_format(h, "big")
        print(f)
    elif mode == "asciicolor":
        h = f"Hello   {name}"
        f = pyfiglet.figlet_format(h, "big")
        cn.print(f"[bold green]{f}[/bold green]")
    elif mode == "emoji":
        print(f"Hello {name}! 🎉✨")
    elif mode == "emojicolor":
        cn.print(f"[bold green]Hello[/bold green] [bold blue]{name}[/bold blue][bold white]![/bold white] 🎉✨")
    else:
        raise typer.BadParameter("You must choose one of the modes when using '-m' or '--mode'.")



if __name__ == "__main__":
    app()