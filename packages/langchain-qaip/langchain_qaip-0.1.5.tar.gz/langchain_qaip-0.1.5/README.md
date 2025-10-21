# langChain-qaip

This package contains the LangChain integrations with QAIP.

## Setup

Create an API Key on [QAIP](https://developer.qaip.com/dashboard/apikeys).

We can then set API key as environment variables.

```python
import os

os.environ["QAIP_API_KEY"] = "<YOUR_API_KEY>"
```

## Installation

```bash
pip install langchain-qaip
```

## Retrievers
`QAIPRetriever` class provides a retriever to connect with QAIP Search API.

```python
from langchain_qaip import QAIPRetriever

retriever = QAIPRetriever()

retriever.invoke("What is the meaning of life?")
```
