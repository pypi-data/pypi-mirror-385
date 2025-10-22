from io import BytesIO
import httpx
try:
    import pandas as pd
except ImportError:
    pd = None

import functools
import inspect
import warnings

def json_to_csv_bytes(json_data):
    """
    Converts JSON data to CSV byte array.

    Args:
        json_data (list[dict]): A list of dictionaries representing JSON data.

    Returns:
        bytes: CSV formatted data as a byte array.
    """
    # Convert JSON to DataFrame
    df = pd.DataFrame(json_data)
    
    # Create a buffer
    buffer = BytesIO()
    
    # Convert DataFrame to CSV and save it to buffer
    df.to_csv(buffer, index=False)
    buffer.seek(0)  # Rewind the buffer to the beginning
    
    # Return bytes
    return buffer.getvalue()
        
def handle_response_data(response, object_class=None, export_csv=False, export_df=False):
    """
    Processes API response data dynamically, converting it to the requested format (CSV, DataFrame, or object list/raw data).
    Returns an empty list, empty DataFrame, or empty CSV byte string when the response payload is empty.

    Args:
        response (list[dict]): The raw response data from the API.
        object_class (type, optional): The class to instantiate for each item in the response. If None, raw data will be returned.
        export_csv (bool): If True, exports data as CSV.
        export_df (bool): If True, exports data as pandas DataFrame.

    Returns:
        list[object_class] | list[dict] | bytes | pd.DataFrame: List of object instances, raw data (list of dictionaries), CSV data, 
                                                               or DataFrame depending on the export flag.
    """
    if isinstance(response, httpx.Response):
        response = response.json()

    if not response:
        # Return empty objects based on export format
        if export_csv:
            return b''
        elif export_df:
            if pd:
                return pd.DataFrame()
            else:
                raise ImportError("Pandas is required for exporting data as a DataFrame.")
        else:
            return []

    if export_csv:
        return json_to_csv_bytes(response)
    elif export_df:
        if pd:
            return pd.DataFrame(response)
        else:
            raise ImportError("Pandas is required for exporting data as a DataFrame.")
    elif object_class:
        # Convert response to a list of object instances if an object class is provided
        return [object_class(**item) for item in response]
    else:
        # Return the raw data (list of dictionaries) if no object class is provided
        return response

string_types = (type(b''), type(u''))

def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter('always', DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2
                )
                warnings.simplefilter('default', DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))