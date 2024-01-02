import sys
from plox.scanner import Scanner
from plox.parser import Parser
from plox.resolver import Resolver
from plox.statement import Statement
from plox.token import Token
from plox.token_type import TokenType
from plox.interpreter import Interpreter
from plox.plox_runtime_error import PloxRuntimeError

class Plox:
    """
    Main class for the plox interpreter
    """

    def __init__(self):
        self.had_lexical_error: bool = False
        self.had_syntactic_error: bool = False
        self.had_semantic_error: bool = False
        self.interpreter = Interpreter(self.semantic_error) 

    def _run(self, source: str, interactive: bool):
        """
        Run source code. Can be a whole script or single statement (interactive mode)
        """
        scanner = Scanner(source, self.lexical_error, interactive)
        tokens: list[Token] = scanner.scan_tokens()

        parser = Parser(tokens, self.syntactic_error)
        statements: list[Statement] = parser.parse()

        if self.had_lexical_error or self.had_syntactic_error:
            self.had_lexical_error = False
            self.had_syntactic_error = False
            return

        resolver = Resolver(self.interpreter, self.semantic_error)
        resolver.resolve_statements(statements)

        if self.had_semantic_error:
            self.had_semantic_error = False
            return

        self.interpreter.interpret(statements)

    def lexical_error(self, line: int, message: str):
        """
        Handle lexical error
        """
        self.had_lexical_error = True
        print(f"[line {line}] Scan error : {message}")

    def syntactic_error(self, token: Token, message: str):
        """
        Handle parse error.
        """
        self.had_syntactic_error = True
        if token.token_type == TokenType.EOF:
            print(f"[line {token.line}] Parse error at end: {message}")
        else:
            print(f"[line {token.line}] Parse error at {token.lexeme}: {message}")

    def semantic_error(self, token: Token, message: str):
        """
        Handle semantic error.
        """
        self.had_semantic_error = True
        print(f"[line {token.line}] Semantic error: {message}")

    def _run_prompt(self):
        """
        Start the interactive lox shell
        """
        print(f"Welcome to the plox interactive shell")
        print("press ctrl-c to exit")

        while True:
            try:
                cmd = input("> ")
                self._run(cmd, True)
                self.had_error = False
            except (KeyboardInterrupt):
                print("\nExiting")
                sys.exit(0)

    @staticmethod
    def _read_file(file_path: str) -> str:
        """
        Read a given file and return contents as string
        """
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                return "".join(lines)
        except FileNotFoundError:
            print(f"File ({file_path}) not found")
            sys.exit(1) # @TODO: find correct exit code
        except Exception as e:
            print(f"Error occurred reading {file_path}: {e}")
            sys.exit(1) # @TODO: find correct exit code

    def _run_file(self, script_path: str):
        """
        Read and run a source script file
        """
        source_string = self._read_file(script_path)
        self._run(source_string, False)
        
        if (self.had_lexical_error or self.had_syntactic_error):
            sys.exit(65)
        if (self.had_semantic_error):
            sys.exit(70)

    @staticmethod
    def main():
        """
        Check arguments and run either script or interactive shell
        """
        if len(sys.argv) == 1:
            Plox()._run_prompt()
        elif len(sys.argv) == 2:
            Plox()._run_file(sys.argv[1])
        else:
            print(f"Usage:")
            print(f"plox [script]         (To run a script)")
            print(f"plox                  (To run the interactive shell)")
            sys.exit(64)

