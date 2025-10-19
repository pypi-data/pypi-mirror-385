# Plummy 💧

A lightweight, modern Python micro-framework for building clean, testable, and scalable event-driven applications using a **Chain of Responsibility** and **Ports and Adapters** (Hexagonal) architecture.

[![CI](https://github.com/GuillermoLB/plummy/actions/workflows/ci.yml/badge.svg)](https://github.com/GuillermoLB/plummy/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/plummy.svg)](https://pypi.org/project/plummy/)
[![codecov](https://codecov.io/gh/GuillermoLB/plummy/branch/main/graph/badge.svg)](https://codecov.io/gh/GuillermoLB/plummy)

---

## Overview

Plummy provides a set of simple, reusable building blocks to help you structure your application according to Domain-Driven Design (DDD) and Hexagonal Architecture principles. It's designed to keep your core business logic (the "hexagon") pure and isolated from external technical details like SQS, APIs, or databases (the "adapters").

The core idea is to build your application as a pipeline of independent, single-responsibility handlers that pass an event down a chain, allowing each handler to decide if it should process the event.

## Key Features

- **Clean Architecture:** Enforces a clear separation between your domain, application, and infrastructure layers.
- **Decoupled Components:** Uses protocols (Ports) and dependency injection to ensure your business logic is independent of external technologies.
- **Functional & Testable:** Encourages writing business logic as simple, pure functions that are easy to unit test.
- **Flexible Pipelines:** Built around a Chain of Responsibility pattern to create extensible event-processing pipelines.

## Installation

Install `plummy` directly from PyPI:

```bash
pip install plummy
```

## How to Use Plummy

Here's how to build a simple event-processing pipeline with plummy.

### 1. Define Your Business Logic (Pure Functions)

First, write your business logic as simple, standalone functions. These functions should have no knowledge of the plummy framework.

```python
# your_app/services.py

# A function to check if the event should be handled
def can_process_new_order(data: dict) -> bool:
    return data.get("type") == "NEW_ORDER"

# A function that contains the core business logic
def process_new_order(data: dict) -> dict:
    print(f"Processing order {data['order_id']}...")
    data["status"] = "PROCESSED"
    return data
```

### 2. Adapt Your Logic into a Processor

Use the FunctionalProcessor adapter to package your functions into a component that the framework can understand.

```python
# your_app/processors.py
from plummy import FunctionalProcessor
from .services import can_process_new_order, process_new_order

# Adapt your functions into a "Processor"
order_processor = FunctionalProcessor(
    can_handle=can_process_new_order,
    process=process_new_order
)
```

### 3. Assemble the Pipeline with Handlers

Use StepHandler to create a "step" in your pipeline for each processor. Then, link the steps together.

```python
# your_app/pipeline.py
from plummy.handlers import StepHandler
from .processors import order_processor
# ... import other processors for other steps

# Create a pipeline step for each processor
order_processing_step = StepHandler(processor=order_processor)
# another_step = StepHandler(processor=another_processor)

# Link them together to form the chain
pipeline_start = order_processing_step
# order_processing_step.set_next(another_step)

# The 'pipeline_start' is now your application's entry point.
```

### 4. Run the Pipeline

Pass your event data to the start of the pipeline.

```python
# your_app/main.py
from .pipeline import pipeline_start

def main_entry_point(event: dict):
    """This could be your AWS Lambda handler or an API endpoint."""
    return pipeline_start.handle(event)

# --- Example ---
new_order_event = {"type": "NEW_ORDER", "order_id": "123"}
result = main_entry_point(new_order_event)

print(result)
# Output: {'type': 'NEW_ORDER', 'order_id': '123', 'status': 'PROCESSED'}
```

## 🚀 Development & Contribution

Follow these steps to set up the plummy project for local development.

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Setup Instructions

#### 1. Create and Activate the Virtual Environment
Navigate to the project root and run:

```bash
uv venv
source .venv/bin/activate
```

#### 2. Install Dependencies

Install the project in editable mode, including all development dependencies:

```bash
uv pip install -e ".[dev]"
```

#### 3. Running Tests

To run the full test suite, use pytest:

```bash
pytest
```

## License
This project is licensed under the MIT License.