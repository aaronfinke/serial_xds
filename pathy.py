import os
from pathlib import Path

print(os.path.abspath(__file__))

p = Path(__file__).resolve().parent
print(p)
