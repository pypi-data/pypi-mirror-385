# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class TiledViewer(Component):
    """A TiledViewer component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- apiKey (string; optional):
    The API key for the Tiled viewer.

- backgroundClassName (string; optional):
    The class name for the background.

- bearerToken (string; optional):
    The bearer token for the Tiled viewer.

- buttonModeText (string; optional):
    The text for the button mode.

- closeOnSelect (boolean; optional):
    Whether to close the viewer on select.

- contentClassName (string; optional):
    The class name for the content.

- enableStartupScreen (boolean; optional):
    Whether to enable the startup screen.

- inButtonModeShowApiKeyInput (boolean; optional):
    Whether to show the API key input in button mode.

- inButtonModeShowReverseSortInput (boolean; optional):
    Whether to show the reverse sort input in button mode.

- inButtonModeShowSelectedData (boolean; optional):
    Whether to show the selected data in button mode.

- initialPath (string; optional):
    The initial path for the Tiled viewer.

- isButtonMode (boolean; optional):
    Whether to use button mode.

- isFullWidth (boolean; optional):
    Whether to use full width of the parent element.

- isPopup (boolean; optional):
    Whether the viewer is a popup.

- reverseSort (boolean; optional):
    Whether to reverse the sort order.

- selectedLinks (boolean | number | string | dict | list; optional):
    The content sent into the callback function from Tiled.

- singleColumnMode (boolean; optional):
    Whether to use single column mode.

- size (string; optional):
    The size of the viewer. 'small', 'medium', 'large'.

- tiledBaseUrl (string; optional):
    The base URL for the tiled viewer."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'tiled_viewer'
    _type = 'TiledViewer'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, backgroundClassName=Component.UNDEFINED, closeOnSelect=Component.UNDEFINED, apiKey=Component.UNDEFINED, bearerToken=Component.UNDEFINED, isButtonMode=Component.UNDEFINED, buttonModeText=Component.UNDEFINED, contentClassName=Component.UNDEFINED, enableStartupScreen=Component.UNDEFINED, isPopup=Component.UNDEFINED, selectedLinks=Component.UNDEFINED, singleColumnMode=Component.UNDEFINED, tiledBaseUrl=Component.UNDEFINED, size=Component.UNDEFINED, isFullWidth=Component.UNDEFINED, inButtonModeShowApiKeyInput=Component.UNDEFINED, inButtonModeShowReverseSortInput=Component.UNDEFINED, inButtonModeShowSelectedData=Component.UNDEFINED, reverseSort=Component.UNDEFINED, initialPath=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'apiKey', 'backgroundClassName', 'bearerToken', 'buttonModeText', 'closeOnSelect', 'contentClassName', 'enableStartupScreen', 'inButtonModeShowApiKeyInput', 'inButtonModeShowReverseSortInput', 'inButtonModeShowSelectedData', 'initialPath', 'isButtonMode', 'isFullWidth', 'isPopup', 'reverseSort', 'selectedLinks', 'singleColumnMode', 'size', 'tiledBaseUrl']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'apiKey', 'backgroundClassName', 'bearerToken', 'buttonModeText', 'closeOnSelect', 'contentClassName', 'enableStartupScreen', 'inButtonModeShowApiKeyInput', 'inButtonModeShowReverseSortInput', 'inButtonModeShowSelectedData', 'initialPath', 'isButtonMode', 'isFullWidth', 'isPopup', 'reverseSort', 'selectedLinks', 'singleColumnMode', 'size', 'tiledBaseUrl']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(TiledViewer, self).__init__(**args)
