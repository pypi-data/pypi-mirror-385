# mineru-vl-utils

A Python package for interacting with the MinerU Vision-Language Model.

It's a lightweight wrapper that simplifies the process of sending requests
and handling responses from the MinerU Vision-Language Model.

## About Backends

We provides 4 different backends(deployment modes):

1. **http-client**: A HTTP client for interacting with the OpenAI-compatible model server.
2. **transformers**: A backend for using HuggingFace Transformers models. (slow but simple to install)
3. **vllm-engine**: A backend for using the VLLM synchronous batching engine.
4. **vllm-async-engine**: A backend for using the VLLM asynchronous engine. (requires async programming)

## About Output Format

MinerU Vision-Language Model can handle document layout detection and
text/table/equation recognition tasks in a same model.

The output of the model is a list of `ContentBlock` objects, each representing
a detected block in the document with its content recognition results.

Each `ContentBlock` contains the following attributes:

- `type` (str): The type of the block, e.g., 'text', 'image', 'table', 'equation'.
  - For a complete list of supported block types, please refer to [structs.py](mineru_vl_utils/structs.py).
- `bbox` (list of floats): The bounding box of the block in the format [xmin, ymin, xmax, ymax],
  with coordinates normalized to the range [0, 1].
- `angle` (int or None): The rotation angle of the block, can be one of [0, 90, 180, 270].
   - `0` means upward.
   - `90` means rightward.
   - `180` means upside down.
   - `270` means leftward.
   - `None` means the angle is not specified.
- `content` (str or None): The recognized content of the block, if applicable.
  - For 'text' blocks, this is the recognized text.
  - For 'table' blocks, this is the recognized table in HTML format.
  - For 'equation' blocks, this is the recognized LaTeX code.
  - For 'image' blocks, this is `None`.

## Installation

For `http-client` backend, just install the package via pip:

```bash
pip install mineru-vl-utils==0.1.14
```

For `transformers` backend, install the package with the `transformers` extra:

```bash
pip install "mineru-vl-utils[transformers]==0.1.14"
```

For `vllm-engine` and `vllm-async-engine` backend, install the package with the `vllm` extra:

```bash
pip install "mineru-vl-utils[vllm]==0.1.14"
```

Notice:
- For using the `http-client` backend, you still need to have another
`vllm`(or other LLM deployment tool) environment to serve the model as a http server.

## Serving the Model (Optional)

> This is only needed if you want to use the `http-client` backend.

You can use `vllm` or another LLM deployment tool to serve the model.
Here we only demonstrate how to use `vllm` to serve the model.

With vllm>=0.10.1, you can use following command to serve the model.
The logits processor is used to support `no_repeat_ngram_size` sampling param,
which can help the model to avoid generating repeated content.

```bash
vllm serve opendatalab/MinerU2.5-2509-1.2B --host 127.0.0.1 --port 8000 \
  --logits-processors mineru_vl_utils:MinerULogitsProcessor
```

If you are using vllm<0.10.1, `no_repeat_ngram_size` sampling param is not supported.
You still can serve the model without logits processor:

```bash
vllm serve opendatalab/MinerU2.5-2509-1.2B --host 127.0.0.1 --port 8000
```

## Using `MinerUClient` by Code

Now you can use the `MinerUClient` class to interact with the model.
Following are examples of using different backends.

### `http-client` Example

```python
from PIL import Image
from mineru_vl_utils import MinerUClient

client = MinerUClient(
    backend="http-client",
    server_url="http://127.0.0.1:8000"
)

image = Image.open("/path/to/the/test/image.png")
extracted_blocks = client.two_step_extract(image)
print(extracted_blocks)
```

### `transformers` Example

```python
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
from PIL import Image
from mineru_vl_utils import MinerUClient

# for transformers>=4.56.0
model = Qwen2VLForConditionalGeneration.from_pretrained(
    "opendatalab/MinerU2.5-2509-1.2B",
    dtype="auto",
    device_map="auto"
)

processor = AutoProcessor.from_pretrained(
    "opendatalab/MinerU2.5-2509-1.2B",
    use_fast=True
)

client = MinerUClient(
    backend="transformers",
    model=model,
    processor=processor
)

image = Image.open("/path/to/the/test/image.png")
extracted_blocks = client.two_step_extract(image)
print(extracted_blocks)
```

If you used an old version of `transformers`(`transformers<4.56.0`),
you need to use `torch_dtype` instead of `dtype`.

```python
model = Qwen2VLForConditionalGeneration.from_pretrained(
    "opendatalab/MinerU2.5-2509-1.2B",
    torch_dtype="auto",
    device_map="auto"
)
```

### `vllm-engine` Example

```python
from vllm import LLM
from PIL import Image
from mineru_vl_utils import MinerUClient
from mineru_vl_utils import MinerULogitsProcessor  # if vllm>=0.10.1

llm = LLM(
    model="opendatalab/MinerU2.5-2509-1.2B",
    logits_processors=[MinerULogitsProcessor]  # if vllm>=0.10.1
)

client = MinerUClient(
    backend="vllm-engine",
    vllm_llm=llm
)

image = Image.open("/path/to/the/test/image.png")
extracted_blocks = client.two_step_extract(image)
print(extracted_blocks)
```

### `vllm-async-engine` Example

```python
import io
import asyncio
import aiofiles

from vllm.v1.engine.async_llm import AsyncLLM
from vllm.engine.arg_utils import AsyncEngineArgs
from PIL import Image
from mineru_vl_utils import MinerUClient
from mineru_vl_utils import MinerULogitsProcessor  # if vllm>=0.10.1

async_llm = AsyncLLM.from_engine_args(
    AsyncEngineArgs(
        model="opendatalab/MinerU2.5-2509-1.2B",
        logits_processors=[MinerULogitsProcessor]  # if vllm>=0.10.1
    )
)

client = MinerUClient(
  backend="vllm-async-engine",
  vllm_async_llm=async_llm,
)

async def main():
    image_path = "/path/to/the/test/image.png"
    async with aiofiles.open(image_path, "rb") as f:
        image_data = await f.read()
    image = Image.open(io.BytesIO(image_data))
    extracted_blocks = await client.aio_two_step_extract(image)
    print(extracted_blocks)

asyncio.run(main())

async_llm.shutdown()
```

## Other APIs

Besides the `two_step_extract` method, `MinerUClient` also provides other APIs
for interacting with the model. Following are the main APIs:

```python
class MinerUClient:

    def layout_detect(self, image: Image.Image) -> list[ContentBlock]:
        ...

    def batch_layout_detect(self, images: list[Image.Image]) -> list[list[ContentBlock]]:
        ...

    async def aio_layout_detect(self, image: Image.Image) -> list[ContentBlock]:
        ...

    async def aio_batch_layout_detect(self, images: list[Image.Image]) -> list[list[ContentBlock]]:
        ...

    def two_step_extract(self, image: Image.Image) -> list[ContentBlock]:
        ...

    def batch_two_step_extract(self, images: list[Image.Image]) -> list[list[ContentBlock]]:
        ...

    async def aio_two_step_extract(self, image: Image.Image) -> list[ContentBlock]:
        ...

    async def aio_batch_two_step_extract(self, images: list[Image.Image]) -> list[list[ContentBlock]]:
        ...
```

## Limitations

The `transformers` backend is slow and not suitable for production use.

The `MinerUClient` only supports standalone image(s) as input.
PDF and DOCX files are not planned to be supported.
Cross-page and cross-document operations are not planned to be supported, too.

For production use cases, please use [MinerU](https://github.com/opendatalab/mineru),
which is a more complete toolkit for document analyzing and data extraction.
