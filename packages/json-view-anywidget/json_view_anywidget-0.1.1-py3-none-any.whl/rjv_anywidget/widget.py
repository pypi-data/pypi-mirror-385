import anywidget
import traitlets
import importlib.resources


class JsonWidget(anywidget.AnyWidget):
    """
    A simple JSON viewer widget using React JSON View for Jupyter notebooks.

    This widget provides an interactive JSON tree view with support for multiple themes,
    expand/collapse functionality, and data synchronization between Python and JavaScript.

    Parameters
    ----------
    data : dict, list, or JSON-serializable object
        The JSON data to display in the widget
    theme : str, optional
        The theme for the JSON viewer. Default is "rjv-default".
        For available themes, see: https://github.com/mac-s-g/react-json-view
    **kwargs : dict
        Additional keyword arguments passed to the parent class

    Examples
    --------
    >>> from rjv_anywidget import JsonWidget
    >>> widget = JsonWidget({"name": "John", "age": 30})
    >>> widget  # Display in Jupyter notebook

    >>> # With custom theme
    >>> widget = JsonWidget({"data": [1, 2, 3]}, theme="monokai")

    >>> # Update data dynamically
    >>> widget.json_data = {"new": "data"}
    >>> widget.theme = "solarized"
    """

    # Widget paths - using importlib.resources to access package resources
    _esm = importlib.resources.files(__package__).joinpath("static/widget.js")
    _css = importlib.resources.files(__package__).joinpath("static/widget.css")

    # JSON data
    json_data = traitlets.Any({}).tag(sync=True)
    theme = traitlets.Any("rjv-default").tag(sync=True)

    def __init__(self, data=None, theme: str="rjv-default", **kwargs):
        """
        Initialize the JsonWidget with data and theme.

        Parameters
        ----------
        data : dict, list, or JSON-serializable object, optional
            The JSON data to display. If None, defaults to empty dict.
        theme : str, optional
            The theme for the JSON viewer. Default is "rjv-default".
            For available themes, see: https://github.com/mac-s-g/react-json-view
        **kwargs : dict
            Additional keyword arguments passed to the parent class.
        """
        if data is None:
            data = {}
        super().__init__(json_data=data, theme=theme, **kwargs)