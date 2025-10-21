## Maniac Python Client

A minimal python client for Maniac's API. Supports chat completions and dataset uploads.

### Installation

```bash
pip install maniac
```

### Initialize the client

```py
from maniac import Maniac

maniac = Maniac()
```

### Run inference

```py
#responses api
response = maniac.responses.create(
    model="openai/gpt-5",
    input="Hello!"
)

#completions api
completion = maniac.chat.completions.create(
    model="openai/gpt-5",
    messages=[
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
)
```

### Create a container

```py
container = maniac.containers.create(
    label = "my-container",
    model = "openai/gpt-5",
    instructions = "You can only speak spanish",
)

response = maniac.responses.create(
    container=container,
    input="Hello!"
)
print(response.output_text) #hola
```

### Run inference with containers

```py
# method 01: with container object
container = maniac.containers.get("my-container")
response = maniac.responses.create(
    container=container,
    input="Hello!"
)

# method 02: with model name
response = maniac.responses.create(
    model="maniac:my-container",
    input="hello!"
)
```

**method 1** allows you to observe the container's functionality directly from the codebase, since the container object contains things like the optimized system prompt.  
**method 2** allows for full container functionality (telemetry, optimization, routing) while being directly compatible with third party tooling. For instance:

### Usage with the OpenAI client

```py
from openai import OpenAI

client = OpenAI(
    base_url = "https://inference.maniac.ai",
    api_key = os.getenv("MANIAC_API_KEY")
)

response = client.responses.create(
    model = "maniac:my-container",
    input = "Hello!",
)
```

### Optimization

```py
container = maniac.containers.get("my-container")
run = maniac.optimizations.create(
    container = container,
    stages = ["sft", "gepa", "grpo"]
)
```
