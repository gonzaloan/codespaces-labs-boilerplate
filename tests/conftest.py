import sys
from pathlib import Path

# Make .grader/ importable in boilerplate tests
sys.path.insert(0, str(Path(__file__).parent.parent / "templates" / "python-ai" / ".grader"))
