import aiohttp
from cvtxtclient.models.motor import Motor
from cvtxtclient.models.servomotor import Servomotor
from cvtxtclient.api.config import APIConfig
from cvtxtclient.api.exceptions import APIError, BadRequestError, NotFoundError, InternalServerError, UnexpectedError
from cvtxtclient.models import (
    Controller as ControllerModel,
    Counter as CounterModel,
    Input as InputModel,
    ImageRecognitionConfig,
    CameraConfig,
    Enabled,
    DebuggerArguments,
    DebuggerResponse,
)
from typing import AsyncIterator, List, Optional


class ControllerAPI:
    def __init__(self,
                 config: APIConfig,
                 session: Optional[aiohttp.ClientSession] = None):
        """Api client for the controller.

        Parameters
        ----------
        config : APIConfig
            Configuration for the API client.

        session : Optional[aiohttp.ClientSession], optional
            An optional aiohttp session to use for requests. If not provided, a new session will be created.

        """
        self.config = config
        self._session = session
        self.headers = {}

    @property
    def session(self) -> aiohttp.ClientSession:
        """Returns the aiohttp session for making requests."""
        if self._session is None:
            connector = aiohttp.TCPConnector(force_close=True)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    def get_headers(self) -> dict:
        """Returns the headers for the API requests."""
        headers = self.headers.copy()
        if self.config.api_key:
            headers['X-API-KEY'] = self.config.api_key
        return headers

    async def add_camera_image_recognition_config(self, image_recognition_config: ImageRecognitionConfig):
        """
        Defines the image recognition configuration of the controller camera.
        Todo: Untested

        Parameters
        ----------
        image_recognition_config : ImageRecognitionConfig
            The image recognition configuration to be set.
        """
        url = f"{self.config.base_url}/controller/camera/image-recognition"
        async with self.session.post(url, headers=self.headers, json=image_recognition_config.model_dump(by_alias=True)) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def camera_message_stream(self, x_api_key: Optional[str] = None) -> AsyncIterator[str]:
        """Retrieves the current state of the image recognition."""
        headers = self.headers.copy()
        params = {}
        if x_api_key:
            params['X-API-KEY'] = x_api_key
        url = f"{self.config.base_url}/controller/camera/message-stream"
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                async for line in response.content.iter_any():
                    if line:
                        yield line.decode('utf-8').strip()
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def start_camera(self, camera_config: CameraConfig):
        """Starts the video stream of the camera."""
        url = f"{self.config.base_url}/controller/camera/start"
        async with self.session.post(url, headers=self.get_headers(), json=camera_config.model_dump(by_alias=True)) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def camera_image_stream(self) -> AsyncIterator[bytes]:
        """Retrieves a stream of images from the controller camera."""
        headers = self.headers.copy()
        params = dict()
        params['X-API-KEY'] = self.config.api_key if self.config.api_key else None
        url = f"{self.config.base_url}/controller/camera/image-stream"
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    boundary = response.headers.get(
                        'Content-Type', '').split('boundary=')[-1].strip('"')
                    if not boundary:
                        raise ValueError(
                            "Boundary not found in Content-Type header")

                    async for chunk, ok in response.content.iter_chunks():
                        if ok:
                            # Basic splitting, might need more robust handling for partial boundaries
                            parts = chunk.split(b'--' + boundary.encode())
                            for part in parts:
                                if part.startswith(b'\r\nContent-Type: image/jpeg\r\n\r\n') and part.endswith(b'\r\n'):
                                    image_data = part[len(
                                        b'\r\nContent-Type: image/jpeg\r\n\r\n'):-len(b'\r\n')]
                                    if image_data:
                                        yield image_data
                elif response.status == 400:
                    raise BadRequestError(f"Bad Request: {await response.text()}")
                elif response.status == 404:
                    raise NotFoundError(f"Not Found: {await response.text()}")
                elif response.status == 500:
                    raise InternalServerError(f"Internal Server Error: {await response.text()}")
                else:
                    raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())
        except aiohttp.ClientError as e:
            print(f"Error during camera stream: {e}")
        except ValueError as e:
            print(f"Error processing camera stream: {e}")

    async def stop_camera(self):
        """Stops the video stream of the camera."""
        url = f"{self.config.base_url}/controller/camera/stop"
        async with self.session.delete(url, headers=self.get_headers()) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controllers(self) -> List[ControllerModel]:
        """Returns information about controller and controllers connected to it."""
        url = f"{self.config.base_url}/controller/discovery"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                data = await response.json()
                return [ControllerModel(**item) for item in data]
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_message_stream(self, x_api_key: Optional[str] = None) -> AsyncIterator[str]:
        """Retrieves all console outputs for a running program."""
        headers = self.get_headers().copy()
        params = {}
        if x_api_key:
            params['X-API-KEY'] = x_api_key
        url = f"{self.config.base_url}/controller/message-stream"
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                async for line in response.content.iter_any():
                    if line:
                        yield line.decode('utf-8').strip()
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_by_id(self, controller_id: int) -> ControllerModel:
        """Returns a controller with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                data = await response.json()
                return ControllerModel(**data)
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def init_controller_by_id(self, controller_id: int):
        """Initializes a controller with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}"
        async with self.session.post(url, headers=self.get_headers()) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_counters(self, controller_id: int) -> List[CounterModel]:
        """Returns a list of all initialized counters."""
        url = f"{self.config.base_url}/controller/{controller_id}/counters"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                data = await response.json()
                return [CounterModel(**item) for item in data]
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def add_controller_counters(self, controller_id: int, counters: List[CounterModel]):
        """Initializes a list of counters."""
        url = f"{self.config.base_url}/controller/{controller_id}/counters"
        payload = [counter.model_dump(by_alias=True) for counter in counters]
        async with self.session.post(url, headers=self.get_headers(), json=payload) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_counters_message_stream(self, controller_id: int, x_api_key: Optional[str] = None) -> AsyncIterator[str]:
        """Retrieves current state of controller counters (updating every 100 ms)."""
        headers = self.headers.copy()
        params = {}
        if x_api_key:
            params['X-API-KEY'] = x_api_key
        url = f"{self.config.base_url}/controller/{controller_id}/counters/message-stream"
        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                async for line in response.content.iter_any():
                    if line:
                        yield line.decode('utf-8').strip()
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_counter_by_id(self, controller_id: int, counter_id: int) -> CounterModel:
        """Returns a counter with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}/counters/{counter_id}"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                data = await response.json()
                return CounterModel(**data)
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def update_controller_counter_by_id(self, controller_id: int, counter_id: int):
        """Resets a counter with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}/counters/{counter_id}"
        async with self.session.patch(url, headers=self.get_headers()) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def get_controller_inputs(self, controller_id: int) -> List[InputModel]:
        """Returns a list of all initialized inputs."""
        url = f"{self.config.base_url}/controller/{controller_id}/inputs"
        async with self.session.get(url, headers=self.get_headers()) as response:
            if response.status == 200:
                data = await response.json()
                return [InputModel(**item) for item in data]
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def add_controller_inputs(self, controller_id: int, inputs: List[InputModel]):
        """Initializes a list of inputs."""
        url = f"{self.config.base_url}/controller/{controller_id}/inputs"
        payload = [input.model_dump(by_alias=True) for input in inputs]
        async with self.session.post(url, headers=self.get_headers(), json=payload) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())

    async def update_controller_motor_by_id(self, controller_id: int, motor_id: int, motor: Motor):
        """Sets the configuration of a motor with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}/motors/{motor_id}"
        async with self.session.post(url, headers=self.get_headers(), json=motor.model_dump(by_alias=True)) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())
            

    async def update_controller_servomotor_by_id(self, controller_id: int, servomotor_id: int, servomotor: Servomotor):
        """Sets the configuration of a servomotor with the specified ID."""
        url = f"{self.config.base_url}/controller/{controller_id}/servomotors/{servomotor_id}"
        async with self.session.post(url, headers=self.get_headers(), json=servomotor.model_dump(by_alias=True)) as response:
            if response.status == 200:
                return  # OK
            elif response.status == 400:
                raise BadRequestError(f"Bad Request: {await response.text()}")
            elif response.status == 404:
                raise NotFoundError(f"Not Found: {await response.text()}")
            elif response.status == 500:
                raise InternalServerError(f"Internal Server Error: {await response.text()}")
            else:
                raise UnexpectedError(f"Unexpected Error: {response.status}", response.status, await response.text())
