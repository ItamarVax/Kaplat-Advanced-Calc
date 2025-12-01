import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
import logging, time
from flask import Flask, request, jsonify, g
from loggerBuilds import get_logger, get_logger_level, set_logger_level
from loggerRequests import next_request_id
from calculator import Calculator
from errors import CalcError  #custom exceptions


#initializations
app = Flask(__name__)
calc = Calculator()
req_log = get_logger("request-logger", "requests.log", to_stdout=True)
stack_logger = get_logger("stack-logger", "stack.log", default_level=logging.INFO)
independent_logger = get_logger("independent-logger", "independent.log", default_level=logging.DEBUG)

#JSon response for a successful calculation
def ok(result):
    return jsonify({"result": result})

#request number for logs
def adapter():
    return logging.LoggerAdapter(req_log, {"_request_id": g.request_id})

@app.before_request
def before():
    g.request_id = next_request_id()
    g.start_time = time.time()
    adapter().info(
        f"Incoming request | #{g.request_id} | resource: {request.path} | HTTP Verb {request.method}"
    )

@app.after_request
def after(response):
    duration = int((time.time() - g.start_time) * 1000)
    adapter().debug(f"request #{g.request_id} duration: {duration}ms")
    return response


#Json response for a failed calculation
@app.errorhandler(CalcError)
def handle_calc_error(exc):
    #choose logger based on request path prefix
    if request.path.startswith("/calculator/stack"):
        log = logging.LoggerAdapter(stack_logger, {"_request_id": g.request_id})
    elif request.path.startswith("/calculator/independent"):
        log = logging.LoggerAdapter(independent_logger, {"_request_id": g.request_id})
    else:
        log = adapter()   # default to request-logger

    log.error(f"Server encountered an error ! message: {str(exc)}")
    return jsonify({"errorMessage": str(exc)}), exc.http_status


#Health port
@app.get("/calculator/health")
def health():
    return "OK", 200


#get the current stack size
@app.get("/calculator/stack/size")
def stack_size():
    size = calc.stack_size()
    contents = ", ".join(map(str, list(calc.stack)))   # left-to-right view
    slog = logging.LoggerAdapter(stack_logger, {"_request_id": g.request_id})

    slog.info(f"Stack size is {size}")
    slog.debug(f"Stack content (first == top): [{contents}]")
    return ok(size)

#add integers to the stack
@app.put("/calculator/stack/arguments")
def push_args():
    data = request.get_json(force=True)
    calc.push_args(data["arguments"], g.request_id)
    return ok(calc.stack_size())

#delete integers from the stack
@app.delete("/calculator/stack/arguments")
def pop_args():
    count = int(request.args.get("count", 0))
    calc.pop_args(count, g.request_id)
    return ok(calc.stack_size())

#calculate in stack mode
@app.get("/calculator/stack/operate")
def operate_stack():
    op = request.args.get("operation", "")
    result = calc.operate_stack(op, g.request_id)
    return ok(result)

#calculate in independent mode
@app.post("/calculator/independent/calculate")
def independent_calculate():
    data = request.get_json(force=True)
    result = calc.calculate(data["operation"], data["arguments"], g.request_id)
    return ok(result)

#History port
@app.get("/calculator/history")
def history():
    flavor = request.args.get("flavor")   # STACK, INDEPENDENT, None

    if flavor is None or flavor.upper() == "STACK":
        slog = logging.LoggerAdapter(stack_logger, {"_request_id": g.request_id})
        slog.info(f"History: So far total {len(calc.get_history('STACK'))} stack actions")

    if flavor is None or flavor.upper() == "INDEPENDENT":
        ilog = logging.LoggerAdapter(independent_logger, {"_request_id": g.request_id})
        ilog.info(f"History: So far total {len(calc.get_history('INDEPENDENT'))} independent actions")

    return ok(calc.get_history(flavor))

#get the log level
@app.get("/logs/level")
def get_level():
    name = request.args.get("logger-name")
    level = get_logger_level(name)
    return level, 200   # plain text

#set the log level
@app.put("/logs/level")
def set_level():
    name  = request.args.get("logger-name")
    level = request.args.get("logger-level")
    try:
        set_logger_level(name, level)
    except ValueError as e:
        return str(e), 400  # plain text failure
    return level.upper(), 200




if __name__ == "__main__":
    app.run(port=8496, host="0.0.0.0")
