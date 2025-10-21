import typer
from rich.console import Console
from pathlib import Path
import re

console = Console()
app = typer.Typer(add_completion=False, rich_markup_mode="rich")

# ---------- Mirror modes ----------
def mirror_word_by_word(text: str) -> str:
    words = text.split(" ")
    mirrored = []
    for word in words:
        letters = [c for c in word if c.isalnum()]
        reversed_letters = letters[::-1]
        ri = 0
        result = ""
        for ch in word:
            if ch.isalnum():
                result += reversed_letters[ri]
                ri += 1
            else:
                result += ch
        mirrored.append(result)
    return " ".join(mirrored)

def mirror_lines_only(text: str) -> str:
    lines = text.splitlines(keepends=True)
    reversed_lines = lines[::-1]
    return ''.join(reversed_lines)


def mirror_text_mode(text: str, mode: str) -> str:
    if mode == "w":
        return text[::-1]
    elif mode == "t":
        return mirror_word_by_word(text)
    elif mode == "k":
        return "".join([s[::-1] if s.isalpha() else s for s in re.split(r"(\W+)", text)])
    return text


# ---------- CLI ----------
@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def mirror(
    source: str = typer.Argument(..., help="Text or file path to mirror"),
    mode: str = typer.Option(
        "w",
        "-m",
        "--mode",
        help="Choose one mirror mode (default=w). See details in examples.",
    ),
    save: bool = typer.Option(False, "-s", help="Overwrite the original file"),
    new_file: bool = typer.Option(False, "-n", help="Create a new mirrored file"),
    just_show: bool = typer.Option(False, "-j", help="Just show output, don’t modify files"),
):
    """
    Mirrorit — mirror text or file content.

Mirror modes (choose one with -m):
  w → reverse the whole text as one string
  t → reverse each word separately, keep symbols in place
  k → reverse each word and do not change the index of the words
  l → reverse the order of lines only, words stay the same

Examples:
  mirrorit hello world! -m t
  mirrorit file.txt -m k -j
  mirrorit file.txt -m w -s
  mirrorit file.txt -m t -n
  mirrorit file.txt -m l -j
"""
    path = Path(source)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        mirrored = mirror_text_mode(text, mode)

        if just_show:
            console.print(f"[bold cyan]Output:[/]\n{mirrored}")
        elif save:
            path.write_text(mirrored, encoding="utf-8")
            console.print(f"[green]File updated:[/] {path}")
        elif new_file:
            new_path = path.parent / f"mirrored_{path.name}"
            new_path.write_text(mirrored, encoding="utf-8")
            console.print(f"[cyan]New file created:[/] {new_path}")
        elif mode == "l":
            return mirror_lines_only(text)
        else:
            console.print("[red]Error:[/] You must use one of -s, -n, or -j!")
    else:
        # input is text, not file
        mirrored = mirror_text_mode(source, mode)
        console.print(f"[bold cyan]Output:[/] {mirrored}")


if __name__ == "__main__":
    app()
