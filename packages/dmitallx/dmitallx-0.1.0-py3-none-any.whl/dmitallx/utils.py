import os
import importlib.util
import math
import functools
from rich.progress import Progress
def clear():
    os.system("cls" if os.name == 'nt' else "clear")

def nod(numbers):
    return functools.reduce(math.gcd, numbers)

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def nok(numbers):
    return functools.reduce(lcm, numbers)

def importlibs(libs):
    with Progress() as progress:
        task = progress.add_task("[green]Loading libraries...", total=len(libs))
        for lib in libs:
            spec = importlib.util.find_spec(lib)
            if spec is None:
                os.system(f"pip install --quiet {lib}")
            progress.update(task, advance=1)