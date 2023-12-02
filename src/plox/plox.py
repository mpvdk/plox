import sys

class Plox:
    def __init__(self):
        print("running __init__")

    def run_interactive(self):
        print("starting interactive shell")

    def run_script(self, script_path):
        print(f"running script: ${script_path}")

    @staticmethod
    def main():
        if len(sys.argv) == 1:
            Plox().run_interactive()
        elif len(sys.argv) == 2:
            Plox().run_script(sys.argv[1])
        else:
            print(f"Usage:")
            print(f"python src [script]         (To run a script)")
            print(f"python src                  (To run the interactive shell)")
            sys.exit(64)

