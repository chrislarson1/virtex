# -------------------------------------------------------------------
# Copyright 2021 Virtex authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
# -------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from typing import Any, List, Iterable, Union

from virtex.core.logging import LOGGER
from virtex.http.message import HttpMessage

__all__ = ['RequestHandler']


class RequestHandler(metaclass=ABCMeta):
    """
    Base class for server side computation. Define a computation
    by implementing the three abstract methods provided, and then
    plug it into your virtex server via the `request_handle`
    constructor argument.

        1. ``process_request(data: List[Any]) -> Any``
        2. ``run_inference(model_input: Any) -> Iterable[Any]``
        3. ``process_response(model_output_item: Any) -> str``

    This processing pattern is designed to to efficiently run
    I/O constrained computations (e.g., DNNs on a GPU) on an
    event loop. Even for compute constrained workloads, this
    seperation of tasks is important to ensure that the server
    isn't being starved of cpu cycles from blocking calls
    to time-consuming subroutines during model execution.

    Examples
    --------
    Use the following pattern to specify arbitrary computations
    that can be run on a Virtex server:

    >>> class CustomModelRequestHandler(RequestHandler)
    >>>
    >>>     def __init__(self, *args, **kwargs):
    >>>         self.model = SomeModel(*args, **kwargs)
    >>>
    >>>     def process_request(self, data):
    >>>         # Decode your data
    >>>         batch = [decode_fn(item) for item in data]
    >>>         # Perform additional processing as necessary
    >>>         # ... e.g., batch = np.array(batch)
    >>>         return batch
    >>>
    >>>     def run_inference(self, batch):
    >>>         result = self.model.predict(batch)
    >>>         return result
    >>>
    >>>     def process_response(self, result):
    >>>         response_data_item = encode_fn(result)
    >>>         return response_data_item
    """

    @abstractmethod
    def process_request(self, data: List[Union[str, int, float, bool]]) -> Any:
        """
        Processes a dynamically sized list of encoded ``Message.data``
        objects from the input queue. The purpose of this method is
        to perform all preprocessing necessary to convert the list
        of incoming data objects into a batched model input. Typically
        this will involve first decoding the serialized data objects,
        and then performing further processing necessary to construct
        a valid model input.

        Notes
        -----
        * Virtex places no restriction on the form of the `batch`, however
          it is required that running the ``run_inference()`` method on this
          batch produces a `model_output` that is iterable, and ordered with
          respect to the `data` list passed into this method.
        * The length of ``data`` **does not** correspond to the length of the
          ``Message.data`` field in the incoming requests.

        Parameters
        ----------
        data: ``List[Union[str, int, float]]``

        Returns
        -------
        model_input: ``Any``
            A valid model input
        """

    @abstractmethod
    def run_inference(self, model_input: Any) -> Iterable[Any]:
        """
        Executes model inference on the batched ``model_input`` (i.e., the
        output of ``process_request()``). This function Returns a batched
        ``model_output``.

        Parameters
        ----------
        model_input: ``Any``

        Returns
        -------
        model_output: ``Iterable[Any]``

        Notes
        -----
        * `model_output` must be iterable and ordered with respect to
          the items in the `data` argument in the ``process_request()``
          method.
        """

    @abstractmethod
    def process_response(self, model_output_item: Any) -> Union[str, int, float, bool]:
        """
        Response processing callback. The method accepts a single
        item from the batched model `output` of the ``run_inference()``
        callback, and performs the serialization necessary to
        convert it into a string. Virtex takes this response item
        and packs it into the ``Message.data``. Unlike the
        ``process_request()`` and ``run_inference()`` callback methods,
        this method operates on single data items, not a batch.

        Parameters
        ----------
        model_output_item: ``Any``

        Returns
        -------
        result: ``str``
        """

    def validate(self, message: HttpMessage):
        """
        Validates that the request handler is capable of processing a given
        `message`. For production systems, this can be called from unit tests
        to evaluate the compatibility of a given message with a custom request
        handler.

        Notes
        -----
        * Always validate on data of length equal to 1 and ``max_batch_size``.
        * For large language models with variable sized inputs along any
          feature dimension (as is common when processing batched LM inputs),
          make sure to run tests on text of maximum length in combination with
          the maximum batch size.
        * Always include a unit test that runs these validations in a loop to
          ensure that GPU memory behaves as expected over multiple model
          executions.

        Parameters
        ----------
        message: ``HttpMessage``
            Message to be evaluated

        Returns
        -------
        response: HttpMessage
        """
        # Validate the message
        if not message.validate():
            return

        # Validate the process_request() method
        try:
            inputs = self.process_request(message.data)
        except Exception as e:
            LOGGER.exception("Error caught in process_request callback: ", e)
            return

        # Validate the run_inference() method
        try:
            outputs = self.run_inference(inputs)
        except Exception as e:
            LOGGER.exception("Error caught in inference callback function: ", e)
            return

        # Validate the process_response() method
        try:
            results = [self.process_response(x) for x in outputs]
        except Exception as e:
            LOGGER.exception("Error caught in process_response callback: ", e)
            return

        # Validate http message creation from the response
        try:
            response = HttpMessage(data=results)
            status = response.validate()
            if not status:
                return
        except Exception as e:
            LOGGER.exception("Error caught while forming response: ", e)
            return

        LOGGER.debug("Server validation successfull.")

        return response
