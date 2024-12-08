import subprocess
from config import terminal
from pathlib import Path

subprocess.Popen(f'{terminal} /bin/python {Path(__file__).parent.resolve()}/typeToMe.py', shell = True)