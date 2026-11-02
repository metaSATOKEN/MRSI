"""Inspect this experiment; add --run on Colab to generate new responses."""
from pathlib import Path
import sys

if __name__ == '__main__':
    bundle = Path(__file__).resolve().parent
    sys.path.insert(0, str(bundle.parents[2] / 'tools'))
    from readable_generation import main
    main(bundle)
