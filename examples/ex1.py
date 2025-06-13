import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import main

if __name__ == "__main__":
    font = "rockwell" 
    name = "Mt5"
    main(f"utils/tests/{font}/{name}.png", font, ["lower", "special", "polish"], 0) #0.013 max ://