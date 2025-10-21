######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.268671                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.cards.card_modules.card
    import metaflow.plugins.cards.card_modules.components
    import typing
    import metaflow.plugins.cards.card_modules.json_viewer

from .basic import LogComponent as LogComponent
from .basic import ErrorComponent as ErrorComponent
from .basic import ArtifactsComponent as ArtifactsComponent
from .basic import TableComponent as TableComponent
from .basic import ImageComponent as ImageComponent
from .basic import SectionComponent as SectionComponent
from .basic import MarkdownComponent as MarkdownComponent
from .basic import PythonCodeComponent as PythonCodeComponent
from .card import MetaflowCardComponent as MetaflowCardComponent
from .card import with_default_component_id as with_default_component_id
from .convert_to_native_type import TaskToDict as TaskToDict
from .renderer_tools import render_safely as render_safely

class UserComponent(metaflow.plugins.cards.card_modules.card.MetaflowCardComponent, metaclass=type):
    def update(self, *args, **kwargs):
        ...
    ...

class StubComponent(UserComponent, metaclass=type):
    def __init__(self, component_id):
        ...
    def update(self, *args, **kwargs):
        ...
    ...

class Artifact(UserComponent, metaclass=type):
    """
    A pretty-printed version of any Python object.
    
    Large objects are truncated using Python's built-in [`reprlib`](https://docs.python.org/3/library/reprlib.html).
    
    Example:
    ```
    from datetime import datetime
    current.card.append(Artifact({'now': datetime.utcnow()}))
    ```
    
    Parameters
    ----------
    artifact : object
        Any Python object.
    name : str, optional
        Optional label for the object.
    compressed : bool, default: True
        Use a truncated representation.
    """
    def update(self, artifact):
        ...
    def __init__(self, artifact: typing.Any, name: typing.Optional[str] = None, compressed: bool = True):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Table(UserComponent, metaclass=type):
    """
    A table.
    
    The contents of the table can be text or numerical data, a Pandas dataframe,
    or other card components: `Artifact`, `Image`, `Markdown` objects.
    
    Example: Text and artifacts
    ```
    from metaflow.cards import Table, Artifact
    current.card.append(
        Table([
            ['first row', Artifact({'a': 2})],
            ['second row', Artifact(3)]
        ])
    )
    ```
    
    Example: Table from a Pandas dataframe
    ```
    from metaflow.cards import Table
    import pandas as pd
    import numpy as np
    current.card.append(
        Table.from_dataframe(
            pd.DataFrame(
                np.random.randint(0, 100, size=(15, 4)),
                columns=list("ABCD")
            )
        )
    )
    ```
    
    Parameters
    ----------
    data : List[List[str or MetaflowCardComponent]], optional
        List (rows) of lists (columns). Each item can be a string or a `MetaflowCardComponent`.
    headers : List[str], optional
        Optional header row for the table.
    """
    def update(self, *args, **kwargs):
        ...
    def __init__(self, data: typing.Optional[typing.List[typing.List[typing.Union[str, metaflow.plugins.cards.card_modules.card.MetaflowCardComponent]]]] = None, headers: typing.Optional[typing.List[str]] = None, disable_updates: bool = False):
        ...
    @classmethod
    def from_dataframe(cls, dataframe = None, truncate: bool = True):
        """
        Create a `Table` based on a Pandas dataframe.
        
        Parameters
        ----------
        dataframe : Optional[pandas.DataFrame]
            Pandas dataframe.
        truncate : bool, default: True
            Truncate large dataframe instead of showing all rows (default: True).
        """
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Image(UserComponent, metaclass=type):
    """
    An image.
    
    `Images can be created directly from PNG/JPG/GIF `bytes`, `PIL.Image`s,
    or Matplotlib figures. Note that the image data is embedded in the card,
    so no external files are required to show the image.
    
    Example: Create an `Image` from bytes:
    ```
    current.card.append(
        Image(
            requests.get("https://www.gif-vif.com/hacker-cat.gif").content,
            "Image From Bytes"
        )
    )
    ```
    
    Example: Create an `Image` from a Matplotlib figure
    ```
    import pandas as pd
    import numpy as np
    current.card.append(
        Image.from_matplotlib(
            pandas.DataFrame(
                np.random.randint(0, 100, size=(15, 4)),
                columns=list("ABCD"),
            ).plot()
        )
    )
    ```
    
    Example: Create an `Image` from a [PIL](https://pillow.readthedocs.io/) Image
    ```
    from PIL import Image as PILImage
    current.card.append(
        Image.from_pil_image(
            PILImage.fromarray(np.random.randn(1024, 768), "RGB"),
            "From PIL Image"
        )
    )
    ```
    
    Parameters
    ----------
    src : bytes
        The image data in `bytes`.
    label : str
        Optional label for the image.
    """
    @staticmethod
    def render_fail_headline(msg):
        ...
    def __init__(self, src = None, label = None, disable_updates: bool = True):
        ...
    @classmethod
    def from_pil_image(cls, pilimage, label: typing.Optional[str] = None, disable_updates: bool = False):
        """
        Create an `Image` from a PIL image.
        
        Parameters
        ----------
        pilimage : PIL.Image
            a PIL image object.
        label : str, optional
            Optional label for the image.
        """
        ...
    @classmethod
    def from_matplotlib(cls, plot, label: typing.Optional[str] = None, disable_updates: bool = False):
        """
        Create an `Image` from a Matplotlib plot.
        
        Parameters
        ----------
        plot :  matplotlib.figure.Figure or matplotlib.axes.Axes or matplotlib.axes._subplots.AxesSubplot
            a PIL axes (plot) object.
        label : str, optional
            Optional label for the image.
        """
        ...
    def render(self, *args, **kwargs):
        ...
    def update(self, image, label = None):
        """
        Update the image.
        
        Parameters
        ----------
        image : PIL.Image or matplotlib.figure.Figure or matplotlib.axes.Axes or matplotlib.axes._subplots.AxesSubplot or bytes or str
            The updated image object
        label : str, optional
            Optional label for the image.
        """
        ...
    ...

class Error(UserComponent, metaclass=type):
    """
    This class helps visualize Error's on the `MetaflowCard`. It can help catch and print stack traces to errors that happen in `@step` code.
    
    ### Parameters
    - `exception` (Exception) : The `Exception` to visualize. This value will be `repr`'d before passed down to `MetaflowCard`
    - `title` (str) : The title that will appear over the visualized  `Exception`.
    
    ### Usage
    ```python
    @card
    @step
    def my_step(self):
        from metaflow.cards import Error
        from metaflow import current
        try:
            ...
            ...
        except Exception as e:
            current.card.append(
                Error(e,"Something misbehaved")
            )
        ...
    ```
    """
    def __init__(self, exception, title = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class Markdown(UserComponent, metaclass=type):
    """
    A block of text formatted in Markdown.
    
    Example:
    ```
    current.card.append(
        Markdown("# This is a header appended from `@step` code")
    )
    ```
    
    Multi-line strings with indentation are automatically dedented:
    ```
    current.card.append(
        Markdown(f'''
            # Header
            - Item 1
            - Item 2
        ''')
    )
    ```
    
    Parameters
    ----------
    text : str
        Text formatted in Markdown. Leading whitespace common to all lines
        is automatically removed to support indented multi-line strings.
    """
    def update(self, text = None):
        ...
    def __init__(self, text = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class ProgressBar(UserComponent, metaclass=type):
    """
    A Progress bar for tracking progress of any task.
    
    Example:
    ```
    progress_bar = ProgressBar(
        max=100,
        label="Progress Bar",
        value=0,
        unit="%",
        metadata="0.1 items/s"
    )
    current.card.append(
        progress_bar
    )
    for i in range(100):
        progress_bar.update(i, metadata="%s items/s" % i)
    
    ```
    
    Parameters
    ----------
    max : int, default 100
        The maximum value of the progress bar.
    label : str, optional, default None
        Optional label for the progress bar.
    value : int, default 0
        Optional initial value of the progress bar.
    unit : str, optional, default None
        Optional unit for the progress bar.
    metadata : str, optional, default None
        Optional additional information to show on the progress bar.
    """
    def __init__(self, max: int = 100, label: typing.Optional[str] = None, value: int = 0, unit: typing.Optional[str] = None, metadata: typing.Optional[str] = None):
        ...
    def update(self, new_value: int, metadata: typing.Optional[str] = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class ValueBox(UserComponent, metaclass=type):
    """
    A Value Box component for displaying key metrics with styling and change indicators.
    
    Inspired by Shiny's value box component, this displays a primary value with optional
    title, subtitle, theme, and change indicators.
    
    Example:
    ```
    # Basic value box
    value_box = ValueBox(
        title="Revenue",
        value="$1.2M",
        subtitle="Monthly Revenue",
        change_indicator="Up 15% from last month"
    )
    current.card.append(value_box)
    
    # Themed value box
    value_box = ValueBox(
        title="Total Savings",
        value=50000,
        theme="success",
        change_indicator="Up 30% from last month"
    )
    current.card.append(value_box)
    
    # Updatable value box for real-time metrics
    metrics_box = ValueBox(
        title="Processing Progress",
        value=0,
        subtitle="Items processed"
    )
    current.card.append(metrics_box)
    
    for i in range(1000):
        metrics_box.update(value=i, change_indicator=f"Rate: {i*2}/sec")
    ```
    
    Parameters
    ----------
    title : str, optional
        The title/label for the value box (usually displayed above the value).
        Must be 200 characters or less.
    value : Union[str, int, float]
        The main value to display prominently. Required parameter.
    subtitle : str, optional
        Additional descriptive text displayed below the title.
        Must be 300 characters or less.
    theme : str, optional
        CSS class name for styling the value box. Supported themes: 'default', 'success',
        'warning', 'danger', 'bg-gradient-indigo-purple'. Custom themes must be valid CSS class names.
    change_indicator : str, optional
        Text indicating change or additional context (e.g., "Up 30% VS PREVIOUS 30 DAYS").
        Must be 200 characters or less.
    """
    def __init__(self, title: typing.Optional[str] = None, value: typing.Union[str, int, float] = '', subtitle: typing.Optional[str] = None, theme: typing.Optional[str] = None, change_indicator: typing.Optional[str] = None):
        ...
    def update(self, title: typing.Optional[str] = None, value: typing.Union[str, int, float, None] = None, subtitle: typing.Optional[str] = None, theme: typing.Optional[str] = None, change_indicator: typing.Optional[str] = None):
        """
        Update the value box with new data.
        
        Parameters
        ----------
        title : str, optional
            New title for the value box.
        value : Union[str, int, float], optional
            New value to display.
        subtitle : str, optional
            New subtitle text.
        theme : str, optional
            New theme/styling class.
        change_indicator : str, optional
            New change indicator text.
        """
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class VegaChart(UserComponent, metaclass=type):
    def __init__(self, spec: dict, show_controls: bool = False):
        ...
    def update(self, spec = None):
        """
        Update the chart.
        
        Parameters
        ----------
        spec : dict or altair.Chart
            The updated chart spec or an altair Chart Object.
        """
        ...
    @classmethod
    def from_altair_chart(cls, altair_chart):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class PythonCode(UserComponent, metaclass=type):
    """
    A component to display Python code with syntax highlighting.
    
    Example:
    ```python
    @card
    @step
    def my_step(self):
        # Using code_func
        def my_function():
            x = 1
            y = 2
            return x + y
        current.card.append(
            PythonCode(my_function)
        )
    
        # Using code_string
        code = '''
        def another_function():
            return "Hello World"
        '''
        current.card.append(
            PythonCode(code_string=code)
        )
    ```
    
    Parameters
    ----------
    code_func : Callable[..., Any], optional, default None
        The function whose source code should be displayed.
    code_string : str, optional, default None
        A string containing Python code to display.
        Either code_func or code_string must be provided.
    """
    def __init__(self, code_func: typing.Optional[typing.Callable[..., typing.Any]] = None, code_string: typing.Optional[str] = None):
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class EventsTimeline(UserComponent, metaclass=type):
    """
    An events timeline component for displaying structured log messages in real-time.
    
    This component displays events in a timeline format with the latest events at the top.
    Each event can contain structured data including other UserComponents for rich display.
    
    Example: Basic usage
    ```python
    @card
    @step
    def my_step(self):
        from metaflow.cards import EventsTimeline
        from metaflow import current
    
        # Create an events component
        events = EventsTimeline(title="Processing Events")
        current.card.append(events)
    
        # Add events during processing
        for i in range(10):
            events.update(
                event_data={
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "processing",
                    "item_id": i,
                    "status": "completed",
                    "duration_ms": random.randint(100, 500)
                }
            )
            time.sleep(1)
    ```
    
    Example: With styling and rich components
    ```python
    from metaflow.cards import EventsTimeline, Markdown, PythonCode
    
    events = EventsTimeline(title="Agent Actions")
    current.card.append(events)
    
    # Event with styling
    events.update(
        event_data={
            "action": "tool_call",
            "function": "get_weather",
            "result": "Success"
        },
        style_theme="success"
    )
    
    # Event with rich components
    events.update(
        event_data={
            "action": "code_execution",
            "status": "completed"
        },
        payloads={
            "code": PythonCode(code_string="print('Hello World')"),
            "notes": Markdown("**Important**: This ran successfully")
        },
        style_theme="info"
    )
    ```
    
    Parameters
    ----------
    title : str, optional
        Title for the events timeline.
    max_events : int, default 100
        Maximum number of events to display. Older events are removed from display
        but total count is still tracked. Stats and relative time display are always enabled.
    """
    def __init__(self, title: typing.Optional[str] = None, max_events: int = 100):
        ...
    def update(self, event_data: dict, style_theme: typing.Optional[str] = None, priority: typing.Optional[str] = None, payloads: typing.Optional[dict] = None, finished: typing.Optional[bool] = None):
        """
        Add a new event to the timeline.
        
        Parameters
        ----------
        event_data : dict
            Basic event metadata (strings, numbers, simple values only).
            This appears in the main event display area.
        style_theme : str, optional
            Visual theme for this event. Valid values: 'default', 'success', 'warning',
            'error', 'info', 'primary', 'secondary', 'tool_call', 'ai_response'.
        priority : str, optional
            Priority level for the event ('low', 'normal', 'high', 'critical').
            Affects visual prominence.
        payloads : dict, optional
            Rich payload components that will be displayed in collapsible sections.
            Values must be UserComponent instances: ValueBox, Image, Markdown,
            Artifact, JSONViewer, YAMLViewer. VegaChart is not supported inside EventsTimeline.
        finished : bool, optional
            Mark the timeline as finished. When True, the status indicator will show
            "Finished" in the header.
        """
        ...
    def get_stats(self) -> dict:
        """
        Get timeline statistics.
        
        Returns
        -------
        dict
            Statistics including total events, display count, timing info, etc.
        """
        ...
    def render(self, *args, **kwargs):
        ...
    ...

class JSONViewer(metaflow.plugins.cards.card_modules.json_viewer.JSONViewer, UserComponent, metaclass=type):
    """
    A component for displaying JSON data with syntax highlighting and collapsible sections.
    
    This component provides a rich view of JSON data with proper formatting, syntax highlighting,
    and the ability to collapse/expand sections for better readability.
    
    Example:
    ```python
    from metaflow.cards import JSONViewer, EventsTimeline
    from metaflow import current
    
    # Use in events timeline
    events = EventsTimeline(title="API Calls")
    events.update({
        "action": "api_request",
        "endpoint": "/users",
        "payload": JSONViewer({"user_id": 123, "fields": ["name", "email"]})
    })
    
    # Use standalone
    data = {"config": {"debug": True, "timeout": 30}}
    current.card.append(JSONViewer(data, collapsible=True))
    ```
    """
    ...

class YAMLViewer(metaflow.plugins.cards.card_modules.json_viewer.YAMLViewer, UserComponent, metaclass=type):
    """
    A component for displaying YAML data with syntax highlighting and collapsible sections.
    
    This component provides a rich view of YAML data with proper formatting and syntax highlighting.
    
    Example:
    ```python
    from metaflow.cards import YAMLViewer, EventsTimeline
    from metaflow import current
    
    # Use in events timeline
    events = EventsTimeline(title="Configuration Changes")
    events.update({
        "action": "config_update",
        "config": YAMLViewer({
            "database": {"host": "localhost", "port": 5432},
            "features": ["auth", "logging"]
        })
    })
    ```
    """
    ...

