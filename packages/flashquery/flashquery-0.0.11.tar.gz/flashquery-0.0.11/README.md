# custom\_openai

`custom_openai` is a drop-in replacement for the official [OpenAI Python SDK](https://github.com/openai/openai-python), enabling you to easily **customize, standardize, and enrich** the API responses for your own post-processing, logging, RAG pipelines, or monitoring needs.
It supports both **synchronous and asynchronous** usage, with robust support for streaming and complete compatibility with the OpenAI API.

---

## 🚀 Features

* **Plug-and-play:** Fully compatible with the OpenAI client interface. Just swap your import and go.
* **Custom response fields:** Every `.create()` call (sync/async/streaming) includes a `.flashquery` attribute for easy extraction of processed or enriched response data.
* **Streaming support:** Automatically injects your custom data into the final item in async generator streams.
* **No monkey-patching:** Cleanly extends OpenAI’s classes without risky global side effects.

---

## 📦 Installation

```bash
pip install flashquery
```

---

## 🔥 Quickstart

### Synchronous Example

```python
from flashquery.client import CustomLangchainClient

client = CustomLangchainClient(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0,
    api_key="sk-..."
)

response = client.generate([{"role": "user", "content": "Say hello?"}])

print(response.flashquery)  # Your custom field!
```

### Streaming Example

```python
import asyncio
from flashquery.client import CustomLangchainClient

async def main():
    client = CustomLangchainClient(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0,
        api_key="sk-..."
    )
    response = client.astream([{"role": "user", "content": "Oi, tudo bem?"}])

    async for chunk in response:
        print("Chunk:", chunk.flashquery)

asyncio.run(main())
```


## ⚙️ How it Works

* **CustomOpenAIClient** and **CustomAsyncOpenAIClient** inherit from the official OpenAI clients, overriding `.create()` methods of `responses` and `chat.completions`.
* After each response is created, a new `.flashquery` attribute is attached.
* In streaming mode, `.flashquery` is set on the **last chunk** yielded from the generator.

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

MIT License

---

> Need help? Open an issue or contribute on GitHub!
