
#base error class
class CalcError(Exception):
    """Parent for every calculator error (maps to HTTP 409)."""
    http_status: int = 409

#input error handling

class UnknownOperation(CalcError):
    def __init__(self, op: str):
        super().__init__(f"Error: unknown operation: {op}")


#independent mode
class NotEnoughArguments(CalcError):
    def __init__(self, op: str):
        super().__init__(f"Error: Not enough arguments to perform the operation {op}")

#stack mode
class StackNotEnoughArguments(CalcError):
    """Stack-mode: stack holds fewer values than operation arity."""
    def __init__(self, op: str, required: int, on_stack: int):
        if op == "POP":
            super().__init__(
                f"Error: cannot remove {required} from the stack. It has only {on_stack} arguments."
            )
        else:
            super().__init__(
            f"Error: cannot implement operation {op}. "
            f"It requires {required} arguments and the stack has only {on_stack} arguments"
            )


class TooManyArguments(CalcError):
    def __init__(self, op: str):
        super().__init__(f"Error: Too many arguments to perform the operation {op}")


class StackUnderflow(CalcError):
    def __init__(self, requested: int, available: int):
        super().__init__(
            f"Error: cannot remove {requested} from the stack. It has only {available} arguments"
        )


#math errors

class DivideByZero(CalcError):
    def __init__(self):
        super().__init__("Error while performing operation Divide: division by 0")


class NegativeFactorial(CalcError):
    def __init__(self):
        super().__init__(
            "Error while performing operation Factorial: not supported for the negative number"
        )