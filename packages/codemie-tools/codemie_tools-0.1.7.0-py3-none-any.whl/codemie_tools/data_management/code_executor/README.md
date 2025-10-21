# Code Executor Tool

Secure Python code execution tool with Kubernetes-based sandboxing and comprehensive configuration support.

## Overview

The Code Executor Tool provides a secure, isolated environment for executing Python code with resource limits, security policies, and complete isolation. It supports both local development and in-cluster deployment configurations.

## Features

- **Secure Execution**: Production-grade security policy for multi-tenant environments
- **File Upload & Export**: Upload files to sandbox and export generated files
- **Resource Management**: Configurable CPU and memory limits
- **Timeout Protection**: Automatic timeout for infinite loops and long-running operations
- **Session Management**: Persistent session pooling with health checks
- **Environment Variable Configuration**: Full configuration via environment variables
- **Kubernetes Integration**: Support for both local and in-cluster Kubernetes configurations

## Configuration

### Environment Variables

The tool supports comprehensive configuration through environment variables:

#### Kubernetes Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment type: `"local"` for development (uses `load_kube_config()`), otherwise uses `load_incluster_config()` | - |
| `CODE_EXECUTOR_NAMESPACE` | Kubernetes namespace for executor pods | `codemie-runtime` |
| `CODE_EXECUTOR_DOCKER_IMAGE` | Docker image for Python execution environment | `epamairun/codemie-python:2.2.9` |
| `CODE_EXECUTOR_MAX_POD_POOL_SIZE` | Maximum number of pods to create dynamically | `5` |
| `CODE_EXECUTOR_POD_NAME_PREFIX` | Prefix for dynamically created pod names | `codemie-executor-` |

#### Working Directory

| Variable | Description | Default |
|----------|-------------|---------|
| `CODE_EXECUTOR_WORKDIR_BASE` | Base working directory for code execution | `/home/codemie` |

#### Timeout Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CODE_EXECUTOR_EXECUTION_TIMEOUT` | Code execution timeout in seconds (protects against infinite loops) | `30.0` |
| `CODE_EXECUTOR_SESSION_TIMEOUT` | Session lifetime in seconds | `300.0` |
| `CODE_EXECUTOR_DEFAULT_TIMEOUT` | Default operation timeout in seconds | `30.0` |

#### Resource Limits

| Variable | Description | Default |
|----------|-------------|---------|
| `CODE_EXECUTOR_MEMORY_LIMIT` | Memory limit for executor pods | `128Mi` |
| `CODE_EXECUTOR_MEMORY_REQUEST` | Memory request for executor pods | `128Mi` |
| `CODE_EXECUTOR_CPU_LIMIT` | CPU limit for executor pods | `1` |
| `CODE_EXECUTOR_CPU_REQUEST` | CPU request for executor pods | `500m` |

#### Security Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CODE_EXECUTOR_RUN_AS_USER` | User ID for pod execution | `1001` |
| `CODE_EXECUTOR_RUN_AS_GROUP` | Group ID for pod execution | `1001` |
| `CODE_EXECUTOR_FS_GROUP` | Filesystem group ID for pod execution | `1001` |

#### Other Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CODE_EXECUTOR_VERBOSE` | Enable verbose logging (`true`/`false`) | `true` |
| `CODE_EXECUTOR_SKIP_ENVIRONMENT_SETUP` | Skip environment setup in sandbox (`true`/`false`) | `false` |

## Usage

### Basic Usage (Environment Variables)

```python
from codemie_tools.data_management.code_executor import CodeExecutorTool

# Tool automatically loads configuration from environment variables
tool = CodeExecutorTool(
    file_repository=file_repo,
    user_id="user123"
)

result = tool.execute(code="print('Hello, World!')")
```

### With Explicit Configuration

```python
from codemie_tools.data_management.code_executor import CodeExecutorConfig, CodeExecutorTool

# Create custom configuration
config = CodeExecutorConfig(
    namespace="my-namespace",
    execution_timeout=60.0,
    memory_limit="256Mi",
    max_pod_pool_size=10,
    pod_name_prefix="my-executor-"
)

tool = CodeExecutorTool(
    config=config,
    file_repository=file_repo,
    user_id="user123"
)

result = tool.execute(code="print('Hello, World!')")
```

### Loading Configuration from Environment

```python
from codemie_tools.data_management.code_executor import CodeExecutorConfig

# Explicitly load from environment variables
config = CodeExecutorConfig.from_env()

# Inspect configuration
print(f"Namespace: {config.namespace}")
print(f"Execution Timeout: {config.execution_timeout}s")
```

### Uploading Files to Sandbox

```python
from codemie_tools.base.file_object import FileObject

# Create FileObject instances (typically provided by toolkit)
input_files = [
    FileObject(name="data.csv", mime_type="text/csv", owner="user123", content=csv_content),
    FileObject(name="config.json", mime_type="application/json", owner="user123", content=json_content)
]

# Create tool with input files
tool = CodeExecutorTool(
    file_repository=file_repo,
    user_id="user123",
    input_files=input_files
)

# Execute code - files are automatically uploaded
result = tool.execute(
    code="""
import pandas as pd

# Read uploaded CSV file (file is available by its original name)
df = pd.read_csv('data.csv')

print(f"Loaded {len(df)} rows")
print(df.head())

# Process the data
df['total'] = df['A'] + df['B']
df.to_csv('processed_data.csv', index=False)
""",
    export_files=["processed_data.csv"]
)
```

### Exporting Files

```python
# Execute code and export generated files
result = tool.execute(
    code="""
import pandas as pd
import matplotlib.pyplot as plt

# Create a sample dataset
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df.to_csv('output.csv', index=False)

# Create a plot
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig('plot.png')
""",
    export_files=["output.csv", "plot.png"]
)
```

### Complete Workflow: Upload, Process, Export

```python
from codemie_tools.base.file_object import FileObject

# Prepare input files
sales_file = FileObject(
    name="sales_data.csv",
    mime_type="text/csv",
    owner="user123",
    content=sales_csv_content
)

# Create tool with input files
tool = CodeExecutorTool(
    file_repository=file_repo,
    user_id="user123",
    input_files=[sales_file]
)

# Execute code - files are automatically uploaded before execution
result = tool.execute(
    code="""
import pandas as pd
import matplotlib.pyplot as plt

# Read uploaded file (automatically available)
df = pd.read_csv('sales_data.csv')

# Analyze data
summary = df.groupby('category')['amount'].sum()

# Create visualization
plt.figure(figsize=(10, 6))
summary.plot(kind='bar')
plt.title('Sales by Category')
plt.xlabel('Category')
plt.ylabel('Total Amount')
plt.savefig('sales_chart.png')

# Save summary
summary.to_csv('sales_summary.csv')
""",
    export_files=["sales_chart.png", "sales_summary.csv"]
)
```

## Environment Setup Examples

### Local Development

```bash
# Set environment to local for kubectl config
export ENV=local

# Optional: Override other settings
export CODE_EXECUTOR_NAMESPACE=dev-runtime
export CODE_EXECUTOR_EXECUTION_TIMEOUT=60
export CODE_EXECUTOR_VERBOSE=true

# Run your application
python app.py
```

### Production (In-Cluster)

```bash
# Don't set ENV or set to anything other than "local"
# Tool will use load_incluster_config()

# Configure resource limits for production
export CODE_EXECUTOR_MEMORY_LIMIT=512Mi
export CODE_EXECUTOR_CPU_LIMIT=2
export CODE_EXECUTOR_EXECUTION_TIMEOUT=120

# Configure dynamic pod pool
export CODE_EXECUTOR_MAX_POD_POOL_SIZE=10
export CODE_EXECUTOR_POD_NAME_PREFIX=prod-executor-

# Run your application
python app.py
```

### Docker Compose

```yaml
services:
  app:
    image: your-app
    environment:
      - ENV=local
      - CODE_EXECUTOR_NAMESPACE=docker-runtime
      - CODE_EXECUTOR_EXECUTION_TIMEOUT=45
      - CODE_EXECUTOR_MEMORY_LIMIT=256Mi
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codemie-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: your-app
        env:
        # ENV not set - uses in-cluster config
        - name: CODE_EXECUTOR_NAMESPACE
          value: "production-runtime"
        - name: CODE_EXECUTOR_EXECUTION_TIMEOUT
          value: "120"
        - name: CODE_EXECUTOR_MEMORY_LIMIT
          value: "512Mi"
        - name: CODE_EXECUTOR_CPU_LIMIT
          value: "2"
        - name: CODE_EXECUTOR_MAX_POD_POOL_SIZE
          value: "10"
        - name: CODE_EXECUTOR_POD_NAME_PREFIX
          value: "prod-exec-"
```

## Security

### Security Policy

The tool implements a production-grade security policy that blocks:
- System operations (os, subprocess, sys manipulation)
- File system operations (shutil, pathlib, glob, tempfile)
- Network operations (socket, urllib, requests, httpx)
- Process/thread manipulation (threading, multiprocessing)
- Code evaluation/compilation (eval, exec, compile)
- Inspection/introspection modules (inspect, importlib)

### Pod Security

Executor pods are configured with:
- Non-root user execution
- Read-only root filesystem
- No privilege escalation
- All capabilities dropped
- Seccomp profile for system call restriction
- No host namespace access

### User Isolation

Each user gets an isolated working directory based on their sanitized user ID, preventing directory traversal attacks and ensuring data isolation.

## Pre-installed Libraries

The sandbox environment includes:

**Data manipulation and analysis:**
- pandas
- numpy

**Plotting and visualization:**
- matplotlib
- seaborn
- plotly

**Document processing:**
- openpyxl (Excel files)
- xlrd (Legacy Excel support)
- python-docx (Word documents)
- python-pptx (PowerPoint)
- PyPDF2 (PDF processing)
- markitdown (Convert various file formats to Markdown)
- pillow (Image processing)

**Utilities:**
- tabulate (Pretty tables)

**Standard library** modules (os, sys, json, datetime, pathlib, etc.) are also available.

## File Operations

### File Upload

Files can be uploaded to the sandbox environment before code execution. Files are provided as `FileObject` instances when creating the tool (typically through the toolkit), and are automatically transferred to the sandbox's working directory.

**How it works:**
1. Files are provided as `List[FileObject]` to the tool constructor
2. The tool reads files from the repository using the file object metadata
3. Files are temporarily written to disk on the host
4. Files are uploaded to the sandbox using `session.copy_to_runtime()`
5. Files become available in the working directory by their original filenames

**Example:**
```python
from codemie_tools.base.file_object import FileObject

# Files provided to constructor
files = [FileObject(name="data.csv", mime_type="text/csv", owner="user", content=...)]
tool = CodeExecutorTool(file_repository=repo, user_id="user", input_files=files)

# Files are automatically available in code
code = "import pandas as pd; df = pd.read_csv('data.csv')"
```

### File Export

Generated files can be exported from the sandbox after execution. The tool copies files from the sandbox to the host and stores them in the file repository.

**How it works:**
1. Code generates files in the working directory
2. Specified files are copied from sandbox using `session.copy_from_runtime()`
3. Files are stored in the repository with unique names
4. URLs are returned for accessing the exported files

**Example:**
```python
code = "import pandas as pd; df.to_csv('output.csv')"
export_files = ["output.csv"]
# Returns: "File 'output.csv': sandbox:<new_encoded_url>"
```

### File Format Support

The file upload/export feature supports all file types:
- **Data files**: CSV, Excel (XLS/XLSX), JSON, XML
- **Images**: PNG, JPG, SVG, etc.
- **Documents**: PDF, Word (DOCX), PowerPoint (PPTX)
- **Text files**: TXT, MD, code files
- **Any other binary or text files**

## Architecture

### Session Management

The tool uses a singleton `SandboxSessionManager` that:
- Maintains a pool of reusable sessions mapped to pod names
- Provides thread-safe access with per-pod locking
- Performs automatic health checks and session recreation
- Dynamically discovers and reuses existing pods
- Creates new pods on-demand up to `max_pod_pool_size`

### Pod Lifecycle

1. **Pod Discovery**: List all running pods with `app=codemie-executor` label
2. **Pod Reuse**: Connects to existing healthy pods when available
3. **Pod Creation**: Creates new pods only when needed and under max capacity
4. **Code Validation**: Security policy validation before execution
5. **Execution**: Code runs with timeout protection
6. **File Export**: Optional file export to repository
7. **Session Persistence**: Session kept alive for future requests

## Configuration Object

The `CodeExecutorConfig` class provides:

```python
class CodeExecutorConfig(CodeMieToolConfig):
    workdir_base: str = "/home/codemie"
    namespace: str = "codemie-runtime"
    docker_image: str = "epamairun/codemie-python:2.2.9"
    execution_timeout: float = 30.0
    session_timeout: float = 300.0
    default_timeout: float = 30.0
    memory_limit: str = "128Mi"
    memory_request: str = "128Mi"
    cpu_limit: str = "1"
    cpu_request: str = "500m"
    max_pod_pool_size: int = 5
    pod_name_prefix: str = "codemie-executor-"
    run_as_user: int = 1001
    run_as_group: int = 1001
    fs_group: int = 1001
    verbose: bool = True
    skip_environment_setup: bool = False
```

## Troubleshooting

### Timeout Errors

If you're getting timeout errors:
- Increase `CODE_EXECUTOR_EXECUTION_TIMEOUT` for longer-running code
- Check for infinite loops in your code
- Consider optimizing resource-intensive operations

### Memory Issues

If pods are running out of memory:
- Increase `CODE_EXECUTOR_MEMORY_LIMIT`
- Also increase `CODE_EXECUTOR_MEMORY_REQUEST` to ensure resources are available
- Review code for memory leaks or large data structures

### Pod Connection Issues

If unable to connect to pods:
- For local development: Ensure `ENV=local` is set and kubectl is configured
- For in-cluster: Ensure proper RBAC permissions for service account
- Verify namespace exists and is accessible
- Check that pods have the `app=codemie-executor` label
- Ensure `max_pod_pool_size` is not set too low for your workload

### Import Errors

If getting import errors:
- Ensure the library is in the pre-installed libraries list
- Standard library modules should work out of the box
- External libraries not in the list are not available

## Contributing

When modifying the Code Executor:
1. Update configuration in `models.py`
2. Update tool logic in `code_executor_tool.py`
3. Run linting: `make ruff-fix`
4. Update this README with any new configuration options
5. Follow patterns in DEV_GUIDE.md

## References

- Main implementation: `code_executor_tool.py`
- Configuration models: `models.py`
- Security policies: `security_policies.py`
- Toolkit integration: `../file_system/toolkit.py`
