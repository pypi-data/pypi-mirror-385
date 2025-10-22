import fsspec.implementations.http
from aiohttp import ClientResponseError

from ngio.utils import NgioValueError


def fractal_fsspec_store(
    url: str, fractal_token: str | None = None, client_kwargs: dict | None = None
) -> fsspec.mapping.FSMap:
    """Simple function to get an http fsspec store from a url."""
    client_kwargs = {} if client_kwargs is None else client_kwargs
    if fractal_token is not None:
        client_kwargs["headers"] = {"Authorization": f"Bearer {fractal_token}"}
    fs = fsspec.implementations.http.HTTPFileSystem(client_kwargs=client_kwargs)

    store = fs.get_mapper(url)

    possible_keys = [".zgroup", ".zarray"]
    for key in possible_keys:
        try:
            value = store.get(key)
            if value is not None:
                break
        except ClientResponseError as e:
            if e.status == 401 and fractal_token is None:
                raise NgioValueError(
                    "No auto token is provided. You need a valid "
                    f"'fractal_token' to access: {url}."
                ) from e
            elif e.status == 401 and fractal_token is not None:
                raise NgioValueError(
                    f"The 'fractal_token' provided is invalid for: {url}."
                ) from e
            else:
                raise e
    else:
        raise NgioValueError(
            f"Store {url} can not be read. Possible problems are: \n"
            "- The url does not exist. \n"
            "- The url is not a valid .zarr. \n"
        )
    return store
