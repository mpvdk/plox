import sys
from plox.scanner import Scanner

class Plox:
    """
    Class representing the Plox interpreter instance
    """

    def __init__(self):
        self.had_error: bool = False

    def run(self, source: str, interactive: bool):
        scanner = Scanner(source, self.error, interactive)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token.token_type)
            print(token.lexeme)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        output = f"[line {line}] Error {where}: {message}"
        self.had_error = True
        print(output)

    def run_prompt(self):
        print(f"Welcome to the plox interactive shell")
        print("press ctrl-c to exit")

        while True:
            try:
                cmd = input("> ")
                self.run(cmd, True)
                self.had_error = False
            except (KeyboardInterrupt):
                print("\nExiting")
                sys.exit(0)

    @staticmethod
    def _read_file(file_path: str, mode: str) -> str:
        try:
            with open(file_path, mode) as f:
                lines = f.readlines()
                return "".join(lines)
        except FileNotFoundError:
            print(f"File ({file_path}) not found")
            sys.exit(1) # @TODO: find correct exit code
        except Exception as e:
            print(f"Error occurred reading {file_path}: {e}")
            sys.exit(1) # @TODO: find correct exit code

    def run_file(self, script_path: str):
        source_string = self._read_file(script_path, "r")
        self.run(source_string, False)
        
        if (self.had_error):
            sys.exit(65)

    @staticmethod
    def main():
        if len(sys.argv) == 1:
            Plox().run_prompt()
        elif len(sys.argv) == 2:
            Plox().run_file(sys.argv[1])
        else:
            print(f"Usage:")
            print(f"plox [script]         (To run a script)")
            print(f"plox                  (To run the interactive shell)")
            sys.exit(64)

