from collections import deque
import math
import logging
from typing import Optional, List, Dict


from loggerBuilds import get_logger
from errors import (
    UnknownOperation,
    NotEnoughArguments,
    TooManyArguments,
    StackNotEnoughArguments,
    DivideByZero,
    NegativeFactorial,
)

#loggers
stack_logger = get_logger("stack-logger", "stack.log", default_level=logging.INFO)
independent_logger = get_logger("independent-logger", "independent.log", default_level=logging.DEBUG)

class Calculator:
    def __init__(self) -> None:
        self.stack: deque[int] = deque()
        self.history: list[dict] = []

    #checks for not enough/too many args error
    @staticmethod
    def _arity_of(op: str) -> int:
        return 2 if op in ("plus", "minus", "times", "divide", "pow") else 1


    #math
    def _apply(self, op: str, args: list[int], independent: bool) -> int:
        op_low = op.lower()
        arity = self._arity_of(op_low)

        # validate arg count
        if len(args) < arity:
            if independent:
                raise NotEnoughArguments(op)
            raise StackNotEnoughArguments(op, arity, len(args))
        if len(args) > arity:
            raise TooManyArguments(op)

        # unary & binary operations
        if op_low == "plus":
            return args[0] + args[1]
        if op_low == "minus":
            return args[0] - args[1]
        if op_low == "times":
            return args[0] * args[1]
        if op_low == "divide":
            if args[1] == 0:
                raise DivideByZero()
            return args[0] // args[1]  # integer part only
        if op_low == "pow":
            return int(math.pow(args[0], args[1]))
        if op_low == "abs":
            return abs(args[0])
        if op_low == "fact":
            if args[0] < 0:
                raise NegativeFactorial()
            return math.factorial(args[0])

        # If we got here op name was invalid
        raise UnknownOperation(op)

    #independent calculation
    def calculate(self, op: str, args: list[int], request_id: int) -> int:
        log = logging.LoggerAdapter(independent_logger, {"_request_id": request_id})

        # Core math may raise math exceptions
        result = self._apply(op, args, independent=True)

        # Record history
        self.history.append(
            {"flavor": "INDEPENDENT", "operation": op, "arguments": args, "result": result}
        )

        # Logging (INFO then DEBUG)
        log.info(f"Performing operation {op}. Result is {result}")
        log.debug(f"Performing operation: {op}({', '.join(map(str, args))}) = {result}")
        return result


    #stack helpers
    def push_args(self, args: list[int], request_id: int) -> None:
        log = logging.LoggerAdapter(stack_logger, {"_request_id": request_id})
        before = len(self.stack)

        # Last list element ends up on top of stack
        for arg in args:
            self.stack.appendleft(arg)
        after = len(self.stack)

        log.info(f"Adding total of {len(args)} argument(s) to the stack | Stack size: {after}")
        log.debug(
            f"Adding arguments: {', '.join(map(str, args))} | Stack size before {before} | stack size after {after}"
        )

    def pop_args(self, count: int, request_id: int) -> list[int]:
        if count > len(self.stack):
            raise StackNotEnoughArguments("POP", count, len(self.stack))
        popped = [self.stack.popleft() for _ in range(count)]
        return popped

    def operate_stack(self, op: str, request_id: int) -> int:
        log = logging.LoggerAdapter(stack_logger, {"_request_id": request_id})
        arity = self._arity_of(op.lower())

        if len(self.stack) < arity:
            raise StackNotEnoughArguments(op, arity, len(self.stack))

        args = [self.stack[i] for i in range(arity)]
        result = self._apply(op, args, independent=False)

        for _ in range(arity):
            self.stack.popleft()

        self.history.append({"flavor": "STACK", "operation": op, "arguments": args, "result": result})
        log.info(f"Performing operation {op}. Result is {result} | stack size: {len(self.stack)}")
        log.debug(f"Performing operation: {op}({', '.join(map(str, args))}) = {result}")
        return result

    def stack_size(self) -> int:
        return len(self.stack)

    def get_history(self, flavor: Optional[str] = None) -> List[Dict]:
        if flavor is None:
            return self.history
        return [h for h in self.history if h["flavor"] == flavor.upper()]