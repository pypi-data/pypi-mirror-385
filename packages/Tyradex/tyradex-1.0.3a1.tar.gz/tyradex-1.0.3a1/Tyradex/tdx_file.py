import datetime
import inspect
import json
import os
import pathlib
import time
import warnings

_DELAY = 604800 # 1 week


def _get_tdx_path(endpoint):
    """ Get the path of TDX file of endpoint.

    Args:
        endpoint (str | pathlib.Path): The endpoint.

    Returns:
        pathlib.Path: Path of TDX file.
    """
    return pathlib.Path(os.path.join(os.path.expanduser("~"), ".TyraDex")) / endpoint


class TDXFile:
    """A class to manage TDX files related to endpoints.

    This class handles the creation, loading, updating, and saving of TDX files,
    as well as checking if they are valid based on their expiration time.

    Attributes:
        exists (bool): Check if the TDX file exists.
        is_valid (bool): Check if the TDX file is valid (not expired).
        endpoint (str): Get the endpoint associated with the TDX file.
        limit (datetime.datetime): Get the expiration date of the TDX file as a datetime object.
        data (dict): Get the data from the TDX file, with expiration check.
    """

    @classmethod
    def create(cls, endpoint, data):
        """Create a new TDX file for the given endpoint with the provided data.

        Args:
            endpoint (str): The endpoint associated with the TDX file.
            data (dict | list): The data to be saved in the TDX file.

        Returns:
            TDXFile: The created TDXFile instance.
        """
        path = _get_tdx_path(endpoint + '.tdx')
        if path.exists():
            os.remove(path)
        tdx = cls(path)
        tdx._data = data
        tdx._limit = int(time.time()) + _DELAY
        tdx.save()
        return tdx

    @classmethod
    def get(cls, endpoint):
        """Retrieve an existing TDX file for the given endpoint.

        Args:
            endpoint (str): The endpoint associated with the TDX file.

        Returns:
            TDXFile: The TDXFile instance for the endpoint.
        """
        path = _get_tdx_path(endpoint)
        return cls(path)

    def __init__(self, path):
        """Initialize a TDXFile instance.

        Args:
            path (str | pathlib.Path): The path to the TDX file.
        """
        self._path = pathlib.Path(str(path) + ('' if str(path).endswith('.tdx') else '.tdx'))
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

        self._endpoint: str = str(self._path).removeprefix(str(_get_tdx_path('')))[1:].removesuffix('.tdx')
        self._limit: int = 0
        self._data = {}

        self.load()

    def __repr__(self):
        """Return a string representation of the TDXFile instance.

        Returns:
            str: The string representation of the TDXFile instance.
        """
        return (
            "<data:{data}, limit: {limit}, endpoint: {endpoint}>"
            .format(
                data=str(self._data).replace('\n', ' '),
                limit=self._limit,
                endpoint=self._endpoint
            )
        )

    def __str__(self):
        """Return a JSON string representation of the TDXFile data.

        Returns:
            str: The JSON representation of the TDXFile data.
        """
        return json.dumps(self._data, ensure_ascii=False, indent=4)

    @property
    def exists(self):
        """Check if the TDX file exists.

        Returns:
            bool: True if the TDX file exists, False otherwise.
        """
        return self._path.exists()

    @property
    def is_valid(self):
        """Check if the TDX file is valid (not expired).

        Returns:
            bool: True if the TDX file is valid, False if expired.
        """
        return self._limit > time.time()

    @property
    def endpoint(self):
        """Get the endpoint associated with the TDX file.

        Returns:
            str: The endpoint associated with the TDX file.
        """
        return self._endpoint

    @property
    def limit(self):
        """Get the expiration date of the TDX file as a datetime object.

        Returns:
            datetime.datetime: The expiration date of the TDX file.
        """
        return datetime.datetime.fromtimestamp(int(self._limit))

    @property
    def data(self):
        """Get the data from the TDX file, with expiration check.

        If the data is expired, a warning is issued.

        Returns:
            dict: The data contained in the TDX file.
        """
        if self._limit < time.time():
            stacks = [s.function for s in inspect.stack()]
            if 'create' not in stacks:
                sl = 2
                if stacks[1] == "save":
                    sl = 3
                    if stacks[2] == '__init__':
                        sl = 4
                warnings.warn('Data is out of date.', UserWarning, stacklevel=sl)
        return self._data

    def update(self, data):
        """Update the data in the TDX file with new data.

        Args:
            data (dict | list | iterable): The new data to be stored in the TDX file.

        Raises:
            TypeError: If the data is not iterable (neither a dict, list, nor iterable object).
        """
        if isinstance(data, dict) or isinstance(data, list):
            self._data = data
            self._limit = int(time.time()) + _DELAY
            self.save()
        else:
            try:
                self.update(list(iter(data)))
            except TypeError:
                raise TypeError("Data must be iterable.")

    def load(self):
        """Load the data from the TDX file into memory.

        This includes the endpoint, expiration limit, and the data. If any part
        of the file is malformed, warnings are issued and defaults are set.
        """
        if self._path.exists():
            with open(self._path, "r", encoding='utf-8') as f:
                data = ""
                for line in f.readlines():
                    if line.startswith("$") or line.isspace() or line == "\n":
                        pass
                    else:
                        data += line

                try:
                    self._endpoint = data.splitlines()[0]
                except TypeError:
                    raise TypeError("Critical error, the endpoint is bad.")

                try:
                    self._limit = int(data.splitlines()[1])
                    if self._limit < time.time():
                        if inspect.stack()[1].function != "__init__":
                            warnings.warn('The data is out of date.', UserWarning, stacklevel=2)
                except (ValueError, TypeError):
                    warnings.warn('Limit must be an int. The data will be considered outdated.', RuntimeWarning, stacklevel=2)
                    self._limit = 0

                try:
                    self._data = json.loads('\n'.join(data.splitlines()[2:]))
                except (json.decoder.JSONDecodeError, TypeError):
                    self._limit = 0
                    self._data = {}

    def save(self):
        """Load the data from the TDX file into memory.

        This includes the endpoint, expiration limit, and the data. If any part
        of the file is malformed, warnings are issued and defaults are set.
        """
        with open(self._path, "w", encoding='utf-8') as f:
            f.write(
                "{endpoint}\n{limit}\n{data}"
                .format(
                    endpoint=self._endpoint,
                    limit=self._limit,
                    data=json.dumps(self.data, ensure_ascii=False, indent=4)
                )
            )