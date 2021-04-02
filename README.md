## Virtex
Virtex is a ML serving framework for running inference on GPUs in poduction.

![release](https://github.com/virtexlabs/virtex/workflows/release/badge.svg)

### Contents
|                     Section                      |               Description             |
|:------------------------------------------------:|:-------------------------------------:|
| [Design Principles](#design-principles)          | Philosopy & implementation            |
| [Features](#features)                            | Feature overview                      |
| [Installation](#installation)                    | How to install the package            |
| [Framework](#framework)                          | Virtex overview                       |
| [Prometheus](#prometheus)                        | Prometheus metrics integration        |
| [Examples](#examples)                            | Link to full examples                 |
| [Performance](#performance)                      | Performance comparison                |
| [Documentation][(0.1.4)](http://virtex.ai/docs)  | Full API documentation and more       |

### Design principles

##### Philosophy
- Flexibility: Python native serving implementation no vendor lock-in. Use your packages of choice.
- Shared-nothing: Performant serving implementation on an event loop, offload expensive compute to an accelerator. No interprocess communication!

##### Implementation
- Dynamic batching
- Asyncronous serving built on top of [uvicorn](https://www.uvicorn.org/) and [uvloop](https://github.com/MagicStack/uvloop).
- Serving and model execution on same thread via coroutines and futures.
- Parallelism via gunicorn process manager

### Features
- A completely abstracted networking plane.
- Prometheus metrics with support for scraping and push consumption models.
- Built-in (de)serialization for transporting commonly used Python data structures:
    - Numpy arrays
    - Pandas objects
    - PIL Images
    - Torch Tensors
    - Tensorflow Tensors
    - MxNet ND Arrays
    - Pickled Python data/code
    - Bytes

### Installation
Virtex is Python 3.6.5+ compatible.

#### With pip
```bash
$ pip install virtex
```

#### From source
```bash
$ git clone https://github.com/virtexlabs/virtex-python.git && cd virtex && pip install .
```

### Framework

See <a href="https://virtex.ai/docs/virtex/types">API documentation</a> for full details.

Virtex consists of four primary components: (1) an `HttpClient` for sending data to the server, (2) an `http_server` function that returns an http endpoint for handling client requests, (3) a `RequestHandler` to define the computation that runs on the server, and (4) an `HttpMessage` that defines the client/server messaging format. These components are described below.

#### HttpMessage

Http requests and responses are built on top of the `HttpMessage` class. It uses a `.data` attribute to store data sent between client and server. It takes the form

 `data: [ x1, ..., xn ]`
 
where `xi` is the *ith* data element of the message. Virtex sends json formatted data internally, so each element in `.data` must be encoded into a valid json datatype. `HttpMessage` has built-in methods to support this in a flexible way via the `.encode(func)` and `.decode(func)` methods, where `func` is a callback that encodes or decodes the elements in `data`, operating on data elements, not the entire `.data` array. Virtex comes with out-of-the-box serialization functions for commonly used data structures such as numpy arrays, pandas objects (dataframes and series), tensorflow tensors (v2.0+), torch tensors, mxnet ndarrays, as well as pickled python objects and bytes. These are contained in the `virtex.serial` module. Below is an example of how to construct a batched message with two numpy array, serialize it into a json string, and then deserialize the json string back into the original message.

```python
import numpy as np
import orjson as json

from virtex import HttpMessage
from virtex.serial import encode_numpy, decode_numpy

# Request data
req1 = np.array([[0.3, 0.1],
                 [1.0, 0.5]], dtype=np.float32)
req2 = np.array([[0.0, 0.4], 
                 [0.0, 0.2]], dtype=np.float32)

# Request message
msg = HttpMessage(data=[req1, req2])

# Encode numpy array to bytestring
msg.encode(encode_numpy)

# Validate that the message is serializable
msg.validate()

# Get json string
msg_str = msg.json

# Recover original message
msg = HttpMessage(**json.loads(msg_str))

# Recover the original data
msg.decode(decode_numpy)
req1_decoded = msg.data[0]
req2_decoded = msg.data[1]
```

#### RequestHandler

Inference on the server is defined using the `RequestHandler` class, which has three abstract methods:

##### `.process_request(self, data: List[Union[str, int, float, bool]]) -> Any`
When triggered, the server will remove items from it's internal request queue (up to `max_batch_size`) and pass them to the `.process_request()` function. This method always accepts a list of json serialized data elements, and returns a batched input. Note that the number of items in the `data` argument will vary from 1 to `max_batch_size` when running on the server, and is decoupled from the size of `HttpMessage.data`. Within the context of machine learning applications, this method invariably consist of some variant of the following: (1) deserialize the data, and (2) stack the individual inputs into a batched model input. 

##### `.run_inference(self,  model_input: Any) -> Iterable[Any]`
Model execution, or inference, gets invoked in this function. Typically a one-liner (something akin to `model.predict(batch)`), this function should consist of model execution code, and little if not nothing more. Importantly, it must return an object that, when iterated over, is ordered w.r.t. `model_input`. Keep in mind that common data structures from numpy, pandas, tensorflow, torch, and mxnet are iterateable in this way so long as the zeroth dimension is the batch dimension.

##### `.process_response(self, model_output_item : Any) -> Union[str, int, float, bool]`
The server takes the batched output of the inference method, iterates through it along the batch dimension, passing each output to the `process_response()` function, which performs post-processing and serialization necessary to form each response data element. In many cases, this function will simply return `encode_fn(model_output_item)`, where `encode_fn` produces a valid json datatype from the model output item.

##### Testing a request handler

To ensure that a given request handler will run on the server, use the `RequestHandler.validate()` method, which accepts an HttpMessage with encoded data elements and executes the computational pipeline that you've defined. In unit tests, keep the following in mind:

* Always validate on data of length equal to 1 and ``max_batch_size`` (which you set on the server).
* For large models with variable sized inputs along any feature dimension (as is common when processing batched LM inputs), make sure to run tests on data of maximum length along those dimension in combination with the maximum batch size to avoid OOM errors.
* Always include a unit test that runs these validations in a loop to ensure that GPU memory behaves as expected over multiple model executions.


#### http_server
The `http_server` function returns a Uvicorn web application. Incoming requests get deserialzed into a `HttpMessage`, and the `data` elements in that message get unpacked onto an input queue. A coroutine continously polls the input queue; its behavior is controlled through the `max_batch_size` and `max_time_on_queue` flags, which specify the maximum queue size and maximum time (in seconds) between successesive model executions. The server will accumulate items on the queue until one of these conditions is met, and then proceed to run the request handler. In the below example, we instantiate a service called `service_x` and specify these two parameters:

```python 
# server.py

from virtex.http import Server

app = http_server(
    name='service_x',
    handler=request_handler_x,
    max_batch_size=128,
    max_time_on_queue=0.01
)
```

To run Virtex servers, we use the Gunicorn process manager to fork our server (`app` in `server.py`) into multiple application instances. Any of the configuration options in Gunicorn can be utilized here; the only requirement is that we specify a special `--worker-class=virtex.VirtexWorker` to ensure that the correct event loop and http networking components get used in the ASGI. As an example, the following bash command will spin up 10 instances of our `service_x` application:

```bash
gunicorn server:app \
  --workers 10 \
  --worker-class virtex.VirtexWorker \
  --bind 0.0.0.0:8081 \
  --worker-connections 100000 \
  --timeout 120 \
  --log-level CRITICAL
```

#### HttpClient
Data is posted to the Virtex server using the `HttpClient`. Let's assume that our inference pipeline accepts pillow image inputs and returns numpy array responses. The flow will look something like:

```python 
import numpy as np
from PIL import Image

from virtex import HttpMessage, HttpClient
from virtex.serial import encode_pil, decode_numpy

img = Image.load_img("path/to/image_file")
msg = HttpMessage(data=[img])
msg.encode(encode_pil)

client = HttpClient()
resp = client.post(msg)
resp.decode(decode_numpy)

# The response data elements are here
prediction = resp.data
```

### Prometheus

Virtex comes with a built-in Prometheus metrics integration that supports both `scrape` and `push` consumption models. Prometheus metrics are turned off by default. Metrics can be configured using the `prom_host` (default='http://127.0.0.1'), `prom_port` (default=9090), `prom_mode` (default='off'), and `prom_interval` (default=0.01, seconds) arguments in `http_server`. 

#### Scrape

To launch your server in scrape mode use the following:

```python
from virtex import http_server

app = http_server(
    name='service_x',
    handler=request_handler_x,
    prom_host='127.0.0.1',
    prom_port=9090,
    prom_mode='scrape',
    prom_push_interval=0.01
)
```

#### Push gateway
Ensure that you have a Prometheus pushgateway to push to. To test locally run the following:

```bash
$ docker run -d -p 9091:9091 prom/pushgateway
```

And then run the server in push-mode:

```python
from virtex import http_server

app = http_server(
    name='service_x',
    handler=request_handler_x,
    prom_host='127.0.0.1',
    prom_port=9091,
    prom_mode='push',
    prom_push_interval=0.01
)
```

### Examples

Examples are a WIP, two full deep learning examples can be found in the [virtex-benchmarks repository](https://github.com/virtexlabs/virtex-benchmarks.git).

### Load testing

Virtex come out-of-the-box with a bare-bones load testing client (`HttpLoadTest`) that can be used to profile performance when building and configuring servers. At the moment it is limited to a single thread (i.e., it's not distributed to simultate multiple clients, this is todo), but even on a single thread it can produce about 3500 requests per second which should be sufficient to evaluate the throughput of most servers running largeish models. Each of the examples in the examples folder demonstrate its use.


### Performance
Coming soon.


### Citation
If you use Virtex in your research, feel free to cite it!
```bibtex
@misc{Larson2021,
  author = {Larson, Chris},
  title = {Virtex},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/virtexlabs/virtex}},
  commit = {}
}
```
