"""Tests for CodeExecutionMiddleware."""

import pytest

from deepagents.middleware.code_execution import (
    CodeExecutionMiddleware,
    PyodideRuntime,
)
from deepagents.middleware.filesystem import _create_file_data


pytestmark = pytest.mark.skipif(
    not pytest.importorskip("pyodide", reason="pyodide not installed"),
    reason="pyodide required for code execution tests"
)


@pytest.mark.asyncio
async def test_basic_execution():
    """Test basic code execution."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="print('Hello, World!')\n2 + 2",
        mounted_files={},
    )
    
    assert result["success"] is True
    assert "Hello, World!" in result["stdout"]
    assert result["result"] == "4"
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_file_mounting():
    """Test that files are mounted correctly."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="""
with open('/data/test.txt', 'r') as f:
    content = f.read()
print(f"Read: {content}")
""",
        mounted_files={
            "/data/test.txt": "Hello from mounted file!"
        },
    )
    
    assert result["success"] is True
    assert "Hello from mounted file!" in result["stdout"]
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_output_files():
    """Test that output files are captured."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="""
with open('/output/result.txt', 'w') as f:
    f.write('Test output')
""",
        mounted_files={},
    )
    
    assert result["success"] is True
    assert "/output/result.txt" in result["output_files"]
    assert result["output_files"]["/output/result.txt"] == "Test output"
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_blocked_imports():
    """Test that dangerous imports are blocked."""
    runtime = PyodideRuntime()
    
    # Test os module blocked
    result = await runtime.execute(
        code="import os\nos.system('echo hacked')",
        mounted_files={},
    )
    
    assert result["success"] is False
    assert "blocked for security" in result["stderr"].lower()
    
    # Test subprocess blocked
    result = await runtime.execute(
        code="import subprocess",
        mounted_files={},
    )
    
    assert result["success"] is False
    assert "blocked for security" in result["stderr"].lower()
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_js_module_blocked():
    """Test that js module access is blocked."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="import js\njs.eval('alert(1)')",
        mounted_files={},
    )
    
    assert result["success"] is False
    assert "blocked" in result["stderr"].lower() or "error" in result["stderr"].lower()
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_numpy_works():
    """Test that allowed packages like numpy work."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="""
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
arr.sum()
""",
        mounted_files={},
    )
    
    assert result["success"] is True
    assert "Mean: 3.0" in result["stdout"]
    assert result["result"] == "15"
    
    await runtime.cleanup()


@pytest.mark.asyncio  
async def test_error_handling():
    """Test that errors are captured properly."""
    runtime = PyodideRuntime()
    
    result = await runtime.execute(
        code="1 / 0",
        mounted_files={},
    )
    
    assert result["success"] is False
    assert "error" in result["stderr"].lower() or "division" in result["stderr"].lower()
    
    await runtime.cleanup()


@pytest.mark.asyncio
async def test_middleware_integration():
    """Test middleware creates tool correctly."""
    middleware = CodeExecutionMiddleware()
    
    assert len(middleware.tools) == 1
    assert middleware.tools[0].name == "execute_python"
    assert "sandbox" in middleware.tools[0].description.lower()


def test_middleware_system_prompt():
    """Test that middleware adds system prompt."""
    middleware = CodeExecutionMiddleware()
    
    assert middleware.system_prompt is not None
    assert "execute_python" in middleware.system_prompt.lower()
    assert "sandbox" in middleware.system_prompt.lower()
    

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow: mount -> execute -> capture."""
    runtime = PyodideRuntime()
    
    # Create input file
    mounted_files = {
        "/data/numbers.txt": "1\n2\n3\n4\n5"
    }
    
    # Execute code that reads input and writes output
    result = await runtime.execute(
        code="""
# Read input
with open('/data/numbers.txt', 'r') as f:
    numbers = [int(line.strip()) for line in f]

# Calculate sum
total = sum(numbers)
print(f"Sum: {total}")

# Write output
with open('/output/result.txt', 'w') as f:
    f.write(f"Total: {total}")
""",
        mounted_files=mounted_files,
    )
    
    assert result["success"] is True
    assert "Sum: 15" in result["stdout"]
    assert "/output/result.txt" in result["output_files"]
    assert "Total: 15" in result["output_files"]["/output/result.txt"]
    
    await runtime.cleanup()
