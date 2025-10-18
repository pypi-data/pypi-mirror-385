# Cognitora Python SDK

The official Python SDK for Cognitora - Operating System for Autonomous AI Agents.

## Features

- **Code Interpreter**: Execute Python, JavaScript, and Bash code in secure sandboxed environments
- **Containers Platform**: Run containerized workloads with flexible resource allocation
- **Session Management**: Persistent sessions with state management and automatic cleanup
- **Execution Control**: Start, monitor, and cancel long-running compute tasks
- **File Operations**: Upload and manipulate files in execution environments
- **Networking Control**: Optional internet access with security-focused defaults
- **Async Support**: Full async/await support for high-performance applications
- **Type Safety**: Comprehensive type hints and data validation

## Installation

```bash
pip install cognitora
```

## Quick Start

```python
from cognitora import Cognitora

# Initialize the client
client = Cognitora(api_key="your_api_key_here")

# Execute Python code with networking
result = client.code_interpreter.execute(
    code="print('Hello from Cognitora!')",
    language="python",
    networking=True  # Enable internet access (default for code interpreter)
)

print(f"Status: {result.data.status}")
for output in result.data.outputs:
    print(f"{output.type}: {output.data}")
```

## Authentication

Get your API key from the [Cognitora Dashboard](https://www.cognitora.dev/home/api-keys) and set it:

```python
# Method 1: Pass directly
client = Cognitora(api_key="cgk_1234567890abcdef")

# Method 2: Environment variable
import os
os.environ['COGNITORA_API_KEY'] = 'cgk_1234567890abcdef'
client = Cognitora()  # Will use environment variable

# Method 3: With custom configuration
client = Cognitora(
    api_key="your_api_key",
    base_url="https://api.cognitora.dev",  # Production default
    timeout=30
)
```

## Code Interpreter

### Basic Execution with Networking Control

```python
# Execute Python code with internet access (default)
result = client.code_interpreter.execute(
    code="""
import requests
import numpy as np
import matplotlib.pyplot as plt

# Fetch data from API (requires networking)
response = requests.get('https://api.github.com/repos/microsoft/typescript')
repo_data = response.json()

print(f"Repository: {repo_data['name']}")
print(f"Stars: {repo_data['stargazers_count']}")

# Create visualization
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.show()
""",
    language="python",
    networking=True  # Explicitly enable networking (default for code interpreter)
)

# Execute code without internet access for security
secure_result = client.code_interpreter.execute(
    code="""
import numpy as np
# No external requests - isolated execution
data = np.random.randn(1000)
print(f"Mean: {np.mean(data)}")
""",
    language="python",
    networking=False  # Disable networking for secure execution
)
```

### Session Persistence

**Sessions maintain state between executions**, making them perfect for:
- Interactive data analysis workflows
- Long-running machine learning experiments  
- Multi-step data processing pipelines
- Collaborative coding environments

```python
# Create a persistent session (defaults to 1 day if no timeout specified)
session = client.code_interpreter.create_session(
    language="python",
    timeout_seconds=3600,  # 1 hour (optional)
    resources={
        "cpu_cores": 2,
        "memory_mb": 2048,
        "storage_gb": 10
    }
)

print(f"Session created: {session.session_id}")

# Execute code in session (variables persist)
result1 = client.code_interpreter.execute(
    code="x = 42; y = 'Hello World'; import pandas as pd",
    session_id=session.session_id,
    networking=True  # Enable networking for package installs
)

result2 = client.code_interpreter.execute(
    code="print(f'x = {x}, y = {y}'); print(f'Pandas version: {pd.__version__}')",
    session_id=session.session_id
)

# Variables and imports are maintained across executions
print(result2.data.outputs[0].data)  # Output: x = 42, y = Hello World

# Get session execution history
session_executions = client.code_interpreter.get_session_executions(session.session_id)
print(f"Session has {len(session_executions)} executions")

# Always clean up sessions when done
client.code_interpreter.delete_session(session.session_id)
```

### New Execution Management Features

```python
# List all interpreter executions across all sessions
all_executions = client.code_interpreter.list_all_executions(
    limit=20,
    status='completed'
)

print(f"Found {len(all_executions)} completed executions")

# Get specific execution details
execution_details = client.code_interpreter.get_execution('exec_123456')
print(f"Execution status: {execution_details['status']}")

# Get executions for a specific session
session_executions = client.code_interpreter.get_session_executions(
    'session_123456',
    limit=10
)
```

### File Operations

```python
from cognitora import FileUpload

# Prepare files
files = [
    FileUpload(
        name="data.csv",
        content="name,age,city\nJohn,30,NYC\nJane,25,LA",
        encoding="string"
    ),
    FileUpload(
        name="script.py",
        content="import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())",
        encoding="string"
    )
]

# Execute with files
result = client.code_interpreter.run_with_files(
    code="exec(open('script.py').read())",
    files=files,
    language="python"
)
```

## Containers Platform

The Containers Platform allows you to run containerized workloads with **full execution control** and **networking security**.

### Basic Container Execution

```python
# Run a secure container (isolated by default)
execution = client.containers.create_container(
    image="docker.io/library/python:3.11-slim",
    command=["python", "-c", "print('Hello from secure container!')"],
    cpu_cores=1.0,
    memory_mb=512,
    max_cost_credits=5,
    networking=False  # Default: isolated for security
)

print(f"Container ID: {execution.id}")
print(f"Status: {execution.status}")

# Run container with internet access when needed
networking_execution = client.containers.create_container(
    image="docker.io/library/python:3.11",
    command=["python", "-c", """
import requests
response = requests.get('https://api.github.com/users/octocat')
user_data = response.json()
print(f"GitHub user: {user_data['name']}")
"""],
    cpu_cores=1.0,
    memory_mb=512,
    max_cost_credits=10,
    networking=True  # Enable networking for API calls
)
```

### Advanced Container Management

```python
# List all container executions
container_executions = client.containers.list_all_container_executions(
    limit=50,
    status='running'
)

print(f"Active containers: {len(container_executions)}")

# Get specific container execution details
container_execution = client.containers.get_container_execution('exec_123456')
print(f"Container execution: {container_execution['status']}")

# Get executions for a specific container
container_history = client.containers.get_container_executions('container_123456')
print(f"Container has {len(container_history)} executions")
```

### Execution Control & Cancellation

```python
# Run a long-running task with networking control
execution = client.containers.create_container(
    image="docker.io/library/python:3.11-slim",
    command=["python", "-c", """
import time
import requests

for i in range(100):
    print(f'Processing step {i+1}/100')
    
    # Make API call every 10 steps (requires networking)
    if i % 10 == 0:
        try:
            response = requests.get('https://httpbin.org/delay/1')
            print(f'API call {i//10 + 1} completed')
        except Exception as e:
            print(f'Network error: {e}')
    
    time.sleep(2)
print('Processing complete!')
"""],
    cpu_cores=2.0,
    memory_mb=1024,
    max_cost_credits=50,
    timeout_seconds=3600,
    networking=True  # Enable networking for API calls
)

print(f"Started container: {execution.id}")

# Monitor execution status
try:
    # Wait for completion with timeout  
    completed = client.containers.wait_for_completion(
        execution.id, 
        timeout_seconds=30,  # 30 seconds timeout for demo
        poll_interval=2
    )
    print(f"Container completed: {completed.status}")
    
except Exception as e:
    print(f"Container taking too long, cancelling...")
    
    # Cancel the container
    result = client.containers.cancel_container(execution.id)
    print(f"Cancellation result: {result}")
    
    # Verify cancellation
    cancelled_container = client.containers.get_container(execution.id)
    print(f"Final status: {cancelled_container.status}")
```

### Resource Management Best Practices

```python
# Always estimate costs before running expensive operations
estimate = client.containers.estimate_cost(
    cpu_cores=4.0,
    memory_mb=8192,
    storage_gb=20,
    gpu_count=1,
    timeout_seconds=3600
)

print(f"Estimated cost: {estimate['estimated_credits']} credits")

if estimate['estimated_credits'] <= 100:
    # Proceed with execution
    execution = client.containers.create_container(
        image="docker.io/tensorflow/tensorflow:latest-gpu",
        command=["python", "train.py"],
        cpu_cores=4.0,
        memory_mb=8192,
        storage_gb=20,
        gpu_count=1,
        max_cost_credits=int(estimate['estimated_credits'] * 1.2),  # 20% buffer
        networking=False  # Secure by default
    )
    
    try:
        # Monitor execution
        result = client.containers.wait_for_completion(execution.id)
        logs = client.containers.get_container_logs(execution.id)
        print(f"Training completed: {result.status}")
        
    except KeyboardInterrupt:
        # Handle user interruption gracefully
        print("Interruption detected, cancelling container...")
        client.containers.cancel_container(execution.id)
        
    except Exception as e:
        # Handle errors and cleanup
        print(f"Error occurred: {e}")
        client.containers.cancel_container(execution.id)
        
else:
    print(f"Execution too expensive ({estimate['estimated_credits']} credits), skipping...")
```

## Async Support

```python
import asyncio
from cognitora import CognitoraAsync

async def main():
    async with CognitoraAsync(api_key="your_api_key") as client:
        # Parallel execution
        tasks = [
            client.code_interpreter.execute(
                code=f"import time; time.sleep(1); print('Task {i} completed')",
                language="python"
            )
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            print(f"Task {i}: {result.data.outputs[0].data}")

# Run async code
asyncio.run(main())
```

## Error Handling

```python
from cognitora import CognitoraError, AuthenticationError, RateLimitError

try:
    result = client.code_interpreter.execute(
        code="raise ValueError('Test error')",
        language="python"
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except CognitoraError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response data: {e.response_data}")
```

## API Reference

### CodeInterpreter Class

#### Methods

- `execute(code, language='python', session_id=None, files=None, timeout_seconds=60, environment=None, networking=None)` - Execute code with networking control
- `create_session(language='python', timeout_seconds=None, expires_at=None, environment=None, resources=None)` - Create persistent session
- `list_sessions()` - List active sessions
- `get_session(session_id)` - Get session details
- `delete_session(session_id)` - Delete session
- `get_session_logs(session_id, limit=50, offset=0)` - Get session logs
- `list_all_executions(limit=50, offset=0, status=None)` - **NEW**: List all interpreter executions
- `get_execution(execution_id)` - **NEW**: Get specific execution details
- `get_session_executions(session_id, limit=50, offset=0)` - **NEW**: List executions for specific session
- `run_python(code, session_id=None)` - Execute Python code
- `run_javascript(code, session_id=None)` - Execute JavaScript code
- `run_bash(command, session_id=None)` - Execute bash command
- `run_with_files(code, files, language='python', session_id=None)` - Execute with files

### Containers Class

#### Methods

- `create_container(image, command, cpu_cores, memory_mb, max_cost_credits, networking=None, **kwargs)` - Create container with networking control
- `list_containers(limit=50, offset=0, status=None)` - List containers
- `get_container(container_id)` - Get container details
- `cancel_container(container_id)` - Cancel container
- `get_container_logs(container_id)` - Get container logs
- `get_container_executions(container_id)` - Get container executions
- `list_all_container_executions(limit=50, offset=0, status=None)` - **NEW**: List all container executions
- `get_container_execution(execution_id)` - **NEW**: Get specific container execution details
- `estimate_cost(cpu_cores, memory_mb, storage_gb=5, gpu_count=0, timeout_seconds=300)` - Estimate cost
- `wait_for_completion(container_id, timeout_seconds=300, poll_interval=5)` - Wait for completion
- `run_and_wait(image, command, cpu_cores, memory_mb, max_cost_credits, **kwargs)` - Create and wait

## Security & Networking

### Default Networking Behavior

| Service | Default Networking | Security Rationale |
|---------|-------------------|-------------------|
| **Code Interpreter** | `True` (enabled) | Needs package installs, data fetching |
| **Containers** | `False` (disabled) | Security-first: isolated by default |

### Networking Best Practices

```python
# For data analysis that needs external data
data_analysis = client.code_interpreter.execute(
    code="""
import pandas as pd
import requests

# Fetch external data
response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
data = response.json()
print(f"Bitcoin price: {data['bpi']['USD']['rate']}")
""",
    networking=True  # Required for external API calls
)

# For secure computation without external access
secure_computation = client.containers.create_container(
    image="docker.io/library/python:3.11",
    command=["python", "-c", "print('Secure isolated computation')"],
    cpu_cores=1.0,
    memory_mb=512,
    max_cost_credits=5,
    networking=False  # Isolated execution (default)
)

# For containers that need external resources
data_processing = client.containers.create_container(
    image="docker.io/library/python:3.11",
    command=["pip", "install", "requests", "&&", "python", "process.py"],
    cpu_cores=2.0,
    memory_mb=1024,
    max_cost_credits=20,
    networking=True  # Enable for pip install and external APIs
)
```

## Configuration

### Environment Variables

```bash
export COGNITORA_API_KEY="your_api_key_here"
export COGNITORA_BASE_URL="https://api.cognitora.dev"  # Optional
export COGNITORA_TIMEOUT="30"  # Optional, seconds
```

## Best Practices

### 1. Resource Management

```python
# Always specify appropriate resources
session = client.code_interpreter.create_session(
    language="python",
    timeout_seconds=1800,  # 30 minutes - don't set too high
    resources={
        "cpu_cores": 1.0,    # Start small
        "memory_mb": 1024,   # Adjust based on needs
        "storage_gb": 5      # Minimum required
    }
)
```

### 2. Session Lifecycle

```python
# Create session
session = client.code_interpreter.create_session()

try:
    # Use session for multiple operations
    for code_snippet in code_snippets:
        result = client.code_interpreter.execute(
            code=code_snippet,
            session_id=session.session_id
        )
        process_result(result)
finally:
    # Clean up
    client.code_interpreter.delete_session(session.session_id)
```

### 3. Error Recovery

```python
import time

def execute_with_retry(client, code, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.code_interpreter.execute(code=code)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except CognitoraError as e:
            if e.status_code >= 500 and attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise
```

## Recent Updates 

### API Refactor Alignment
- ✅ **Updated endpoint paths**: Code interpreter now uses `/api/v1/interpreter/*`
- ✅ **Container-focused architecture**: All compute operations use `/api/v1/compute/containers/*`
- ✅ **Networking parameter**: Security-focused networking control for all operations
- ✅ **New execution endpoints**: Comprehensive execution management and history
- ✅ **Production-ready defaults**: All clients default to `https://api.cognitora.dev`

### New Features
- ✅ **Networking Control**: Optional `networking` parameter with security-focused defaults
- ✅ **Execution Management**: List, filter, and retrieve execution details across all services
- ✅ **Session History**: Track and manage executions within persistent sessions
- ✅ **Container Execution History**: Detailed tracking of container execution lifecycle

### Breaking Changes from Previous Versions
- **Method Names**: `compute.*` methods renamed to `containers.*`
- **Endpoint Paths**: Code interpreter paths changed from `/code-interpreter/` to `/interpreter/`
- **Default Networking**: Containers now default to `networking=False` for security

## Data Classes and Types

```python
from cognitora import (
    ExecuteCodeRequest,
    ExecuteCodeResponse, 
    ComputeExecutionRequest,
    FileUpload,
    Session,
    Execution
)

# All request and response types are provided as dataclasses
request = ExecuteCodeRequest(
    code="print('Hello')",
    language="python",
    networking=True  # NEW: networking control
)

container_request = ComputeExecutionRequest(
    image="python:3.11",
    command=["python", "-c", "print('test')"],
    cpu_cores=1.0,
    memory_mb=512,
    max_cost_credits=5,
    networking=False  # NEW: networking control
)
```

## Support

- **Documentation**: [docs.cognitora.dev](https://www.cognitora.dev/docs/)
- **Support or get an early access**: [hello@cognitora.dev](mailto:hello@cognitora.dev)

## License

MIT License - see [LICENSE](LICENSE) file for details. 