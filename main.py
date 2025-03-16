from presentation.bot import run_bot
import sys
import os

#teste webhook
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    run_bot()