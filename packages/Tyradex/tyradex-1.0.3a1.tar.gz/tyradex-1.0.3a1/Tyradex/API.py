import ctypes
import json
import os
import pathlib
import platform
import subprocess

import requests

try:
    import TyradexErrors as TyradexErrors
except ModuleNotFoundError:
    import Tyradex.TyradexErrors as TyradexErrors
try:
    from tdx_file import TDXFile
except ModuleNotFoundError:
    from Tyradex.tdx_file import TDXFile

try:
    with open(pathlib.Path(__file__).parent / 'metadata.json', 'r') as f:
        _METADATA = json.load(f)
        VERSION = 'Tyradex for Python version {version} on {os} {os_release} ({os_version})'.format(
            version=_METADATA['version'],
            os=platform.system(),
            os_release=platform.release(),
            os_version=platform.version(),
        )
except FileNotFoundError:
    with open(pathlib.Path(__file__).parent.parent / 'metadata.json', 'r') as f:
        _METADATA = json.load(f)
        VERSION = 'Tyradex for Python version {version} on {os} {os_release} ({os_version})'.format(
            version=_METADATA['version'],
            os=platform.system(),
            os_release=platform.release(),
            os_version=platform.version(),
        )

_CACHE_FOLDER = pathlib.Path(os.path.join(os.path.expanduser("~"), ".TyraDex"))
if not os.path.exists(_CACHE_FOLDER):
    os.makedirs(_CACHE_FOLDER)
    if platform.system() == "Windows":  # Windows
        ctypes.windll.kernel32.SetFileAttributesW(_CACHE_FOLDER, 0x02)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["chflags", "hidden", _CACHE_FOLDER])


class Tyradex:
    _URL = "https://tyradex.app/api/v1/"

    _HEADER = {
        "User-Agent": "Tyradex For Python Version {version}".format(version=_METADATA["version"]),
        "From": "https://github.com/LassaInora/TyraDex",
        'Content-type': 'application/json'
    }

    @classmethod
    def call(cls, endpoint):
        """
                Sends a request to the Tyradex API with local cache handling.

                If the requested endpoint data is available and valid in the cache,
                it is returned directly without performing an HTTP request.
                Otherwise, a GET request is made to the API. On success, the data is
                cached and returned. If an error occurs (e.g., 404), a custom error
                message is displayed and `None` is returned.

                Args:
                    endpoint (str): The API endpoint to query (e.g., "pokemon/1").

                Returns:
                    dict | None: The data returned as a dictionary, or `None` if an
                    error occurred (e.g., page not found).
                """
        cache = TDXFile.get(endpoint)
        if not cache.exists or not cache.is_valid:
            request = requests.get(cls._URL + endpoint, headers=cls._HEADER)
            try:
                rjson = request.json()
            except requests.exceptions.JSONDecodeError:
                rjson = {
                    "status": request.status_code,
                    "message": request.reason
                }
            if isinstance(rjson, dict) and rjson.get('status') == 404:
                TyradexErrors.PageNotFound(endpoint).print()
                return None
            else:
                cache.update(request.json())
        return cache.data
