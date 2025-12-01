# Calculator Server with Logging

A Flask-based REST API calculator server that supports two calculation modes: **Stack-based** and **Independent**. The server includes comprehensive logging, request tracking, and operation history.

## Table of Contents

- [Features](#features)
- [Project Overview](#project-overview)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Logging System](#logging-system)
- [Error Handling](#error-handling)
- [Project Structure](#project-structure)

## Features

- **Two Calculation Modes**:
  - **Stack Mode**: Push arguments onto a stack, perform operations, and pop results
  - **Independent Mode**: Direct calculations with provided arguments

- **Supported Operations**:
  - Binary: `plus`, `minus`, `times`, `divide`, `pow`
  - Unary: `abs`, `fact` (factorial)

- **Comprehensive Logging**:
  - Request logging with unique request IDs
  - Separate loggers for stack and independent operations
  - Configurable log levels (DEBUG, INFO, ERROR)
  - Logs written to files and optionally to stdout

- **Operation History**: Track all calculations performed in both modes

- **Error Handling**: Custom exceptions with descriptive error messages

## Project Overview

This project implements a calculator service as a REST API using Flask. It's designed to demonstrate:
- RESTful API design
- Stack-based and independent calculation paradigms
- Structured logging with multiple loggers
- Request tracking and monitoring
- Error handling and validation

The server runs on port **8496** and provides endpoints for:
- Health checks
- Stack operations (push, pop, operate)
- Independent calculations
- History retrieval
- Log level management

## How It Works

### Architecture

1. **Server Layer** (`server.py`):
   - Flask application that handles HTTP requests
   - Request tracking with unique IDs
   - Request/response logging
   - Error handling middleware

2. **Calculator Layer** (`calculator.py`):
   - `Calculator` class manages the stack and history
   - Two operation modes:
     - **Stack Mode**: Operations consume values from the stack
     - **Independent Mode**: Operations use provided arguments directly
   - Validates operation arity and arguments

3. **Logging System** (`loggerBuilds.py`, `loggerRequests.py`):
   - Three separate loggers:
     - **request-logger**: Logs all incoming requests and responses
     - **stack-logger**: Logs stack-related operations
     - **independent-logger**: Logs independent calculations
   - Each request gets a unique ID for tracking

4. **Error Handling** (`errors.py`):
   - Custom exception hierarchy
   - All calculator errors return HTTP 409 (Conflict)
   - Descriptive error messages

### Calculation Flow

#### Stack Mode:
1. Push arguments onto stack using `PUT /calculator/stack/arguments`
2. Perform operation using `GET /calculator/stack/operate?operation=<op>`
3. Operation consumes required arguments from stack and pushes result back
4. Check stack size with `GET /calculator/stack/size`
5. Remove arguments with `DELETE /calculator/stack/arguments?count=<n>`

#### Independent Mode:
1. Send operation and arguments in one request: `POST /calculator/independent/calculate`
2. Result is returned immediately (no stack involved)

### Logging Flow

1. Each request receives a unique ID (incremented counter)
2. Request logger logs incoming request with ID, path, and HTTP method
3. Based on endpoint path, appropriate logger (stack/independent) is used
4. After request completes, duration is logged
5. Errors are logged to the appropriate logger based on endpoint

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd CalcServer_Logger
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or if you prefer to use the bundled libraries:
   ```bash
   # The project includes libraries in the libs/ directory
   # Make sure Python can find them (server.py handles this)
   ```

## Running the Server

### Windows

Use the provided batch file:
```bash
run.bat
```

Or run directly:
```bash
python -S -E server.py
```

### Linux/macOS

```bash
python3 server.py
```

The server will start on **http://0.0.0.0:8496** (accessible on all network interfaces).

### Verify Server is Running

Check the health endpoint:
```bash
curl http://localhost:8496/calculator/health
```

Expected response: `OK`

## API Endpoints

### Health Check
- **GET** `/calculator/health`
  - Returns: `OK` (200)

### Stack Operations

- **GET** `/calculator/stack/size`
  - Returns: Current stack size (JSON: `{"result": <size>}`)

- **PUT** `/calculator/stack/arguments`
  - Body: `{"arguments": [1, 2, 3]}`
  - Adds arguments to stack (last element becomes top)
  - Returns: New stack size

- **DELETE** `/calculator/stack/arguments?count=<n>`
  - Removes `n` arguments from top of stack
  - Returns: New stack size

- **GET** `/calculator/stack/operate?operation=<op>`
  - Performs operation using top stack values
  - Binary ops use top 2, unary ops use top 1
  - Returns: Operation result

### Independent Calculations

- **POST** `/calculator/independent/calculate`
  - Body: `{"operation": "plus", "arguments": [5, 3]}`
  - Returns: Calculation result

### History

- **GET** `/calculator/history?flavor=<STACK|INDEPENDENT>`
  - Returns: List of all operations
  - `flavor` parameter filters by mode (optional)

### Log Management

- **GET** `/logs/level?logger-name=<name>`
  - Returns: Current log level (plain text)

- **PUT** `/logs/level?logger-name=<name>&logger-level=<DEBUG|INFO|ERROR>`
  - Sets log level for specified logger
  - Returns: New log level (plain text)

## Usage Examples

### Stack Mode Example

```bash
# 1. Push arguments onto stack
curl -X PUT http://localhost:8496/calculator/stack/arguments \
  -H "Content-Type: application/json" \
  -d '{"arguments": [10, 5, 2]}'

# Response: {"result": 3}

# 2. Check stack size
curl http://localhost:8496/calculator/stack/size

# Response: {"result": 3}

# 3. Perform addition (uses top 2: 10 and 5)
curl "http://localhost:8496/calculator/stack/operate?operation=plus"

# Response: {"result": 15}
# Stack now: [15, 2] (result pushed back, then remaining 2)

# 4. Perform division (uses top 2: 15 and 2)
curl "http://localhost:8496/calculator/stack/operate?operation=divide"

# Response: {"result": 7}
# Stack now: [7]

# 5. Remove 1 argument
curl -X DELETE "http://localhost:8496/calculator/stack/arguments?count=1"

# Response: {"result": 0}
```

### Independent Mode Example

```bash
# Calculate 5 + 3
curl -X POST http://localhost:8496/calculator/independent/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "plus", "arguments": [5, 3]}'

# Response: {"result": 8}

# Calculate factorial of 5
curl -X POST http://localhost:8496/calculator/independent/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "fact", "arguments": [5]}'

# Response: {"result": 120}

# Calculate 2^8
curl -X POST http://localhost:8496/calculator/independent/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "pow", "arguments": [2, 8]}'

# Response: {"result": 256}
```

### History Example

```bash
# Get all history
curl http://localhost:8496/calculator/history

# Get only stack operations
curl "http://localhost:8496/calculator/history?flavor=STACK"

# Get only independent operations
curl "http://localhost:8496/calculator/history?flavor=INDEPENDENT"
```

### Log Level Management

```bash
# Get current log level for stack logger
curl "http://localhost:8496/logs/level?logger-name=stack-logger"

# Set stack logger to DEBUG
curl -X PUT "http://localhost:8496/logs/level?logger-name=stack-logger&logger-level=DEBUG"
```

## Logging System

The project uses three separate loggers:

1. **request-logger** (`logs/requests.log`)
   - Logs all HTTP requests and responses
   - Also outputs to stdout
   - Includes request ID, path, method, and duration

2. **stack-logger** (`logs/stack.log`)
   - Logs all stack-related operations
   - Default level: INFO

3. **independent-logger** (`logs/independent.log`)
   - Logs all independent calculations
   - Default level: DEBUG

### Log Format

```
%(asctime)s %(levelname)s: %(message)s | request #%(_request_id)d
```

Example:
```
25-01-2025 14:30:45.123456 INFO: Incoming request | #1 | resource: /calculator/stack/size | HTTP Verb GET | request #1
```

### Log Levels

- **DEBUG**: Detailed information (operation details, stack contents)
- **INFO**: General information (operations performed, stack size)
- **ERROR**: Error messages

## Error Handling

All calculator errors return HTTP status **409 (Conflict)** with a JSON error message:

```json
{
  "errorMessage": "Error: <description>"
}
```

### Error Types

- `UnknownOperation`: Invalid operation name
- `NotEnoughArguments`: Independent mode - insufficient arguments
- `StackNotEnoughArguments`: Stack mode - insufficient values on stack
- `TooManyArguments`: Too many arguments provided
- `DivideByZero`: Division by zero attempted
- `NegativeFactorial`: Factorial of negative number attempted

### Example Error Response

```bash
# Try to divide by zero
curl -X POST http://localhost:8496/calculator/independent/calculate \
  -H "Content-Type: application/json" \
  -d '{"operation": "divide", "arguments": [10, 0]}'

# Response (409):
# {
#   "errorMessage": "Error while performing operation Divide: division by 0"
# }
```

## Project Structure

```
CalcServer_Logger/
├── server.py              # Main Flask server and API endpoints
├── calculator.py          # Calculator logic (stack and independent modes)
├── errors.py              # Custom exception classes
├── loggerBuilds.py        # Logger setup and management
├── loggerRequests.py      # Request ID tracking
├── requirements.txt       # Python dependencies
├── run.bat               # Windows startup script
├── libs/                 # Bundled Python libraries
└── logs/                 # Log files directory
    ├── requests.log      # Request/response logs
    ├── stack.log         # Stack operation logs
    └── independent.log   # Independent calculation logs
```

## Supported Operations

### Binary Operations (require 2 arguments)
- `plus`: Addition (a + b)
- `minus`: Subtraction (a - b)
- `times`: Multiplication (a * b)
- `divide`: Integer division (a // b)
- `pow`: Exponentiation (a^b)

### Unary Operations (require 1 argument)
- `abs`: Absolute value
- `fact`: Factorial

## Notes

- The server uses integer arithmetic (division returns integer part only)
- Stack operations consume arguments from the top (leftmost in the deque)
- Request IDs are sequential and unique per server instance
- Log files are created automatically in the `logs/` directory
- The server binds to `0.0.0.0:8496`, making it accessible from other machines on the network

## Troubleshooting

**Server won't start:**
- Check if port 8496 is already in use
- Verify Python version (3.9+)
- Ensure all dependencies are installed

**Logs not appearing:**
- Check that `logs/` directory exists and is writable
- Verify log level settings (use `/logs/level` endpoint)

**Operations failing:**
- Check stack size before stack operations
- Verify operation names are lowercase
- Ensure correct number of arguments for operation arity

