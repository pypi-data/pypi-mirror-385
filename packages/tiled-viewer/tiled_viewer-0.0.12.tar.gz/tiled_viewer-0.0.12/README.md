# Tiled Viewer

Tiled Viewer is a Dash component that can be embedded in a Dash application to visually browse Tiled data and select data for use with your own custom callbacks.

[Github](https://github.com/bluesky/tiled-viewer-dash)

[React Source Code](https://github.com/bluesky/tiled-viewer-react)

The main source code is written in React, then converted into a Dash component.
## User Setup
Console
```
pip install tiled-viewer
```
Dash App Example
```python
import tiled_viewer
from dash import Dash, callback, html, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    tiled_viewer.TiledViewer(
        id='input',
        tiledBaseUrl='http://127.0.0.1:8000/api/v1',
    ),
    html.Div(id='output')
])


@callback(Output('output', 'children'), Input('input', 'selectedLinks'))
def display_output(links):
    return f"Selected: {links}"


if __name__ == '__main__':
    app.run(debug=True)
```

Get started with:
1. Install Dash and its dependencies: https://dash.plotly.com/installation
2. Run `python usage.py`
3. Visit http://localhost:8050 in your web browser

# Developer Instructions

### Install dependencies

If you have selected install_dependencies during the prompt, you can skip this part.

1. Install npm packages
    ```
    $ npm install
    ```
2. Create a virtual env and activate.
    ```
    $ virtualenv venv
    $ . venv/bin/activate
    ```
    _Note: venv\Scripts\activate for windows_

3. Install python packages required to build components.
    ```
    $ pip install -r requirements.txt
    ```
4. Install the python packages for testing (optional)
    ```
    $ pip install -r tests/requirements.txt
    ```

### Write your component code in `src/lib/components/TiledViewer.react.js`.

- The demo app is in `src/demo` and you will import your example component code into your demo app.
- Test your code in a Python environment:
    1. Build your code
        ```
        $ npm run build
        ```
    2. Run and modify the `usage.py` sample dash app:
        ```
        $ python usage.py
        ```
- Write tests for your component.
    - A sample test is available in `tests/test_usage.py`, it will load `usage.py` and you can then automate interactions with selenium.
    - Run the tests with `$ pytest tests`.
    - The Dash team uses these types of integration tests extensively. Browse the Dash component code on GitHub for more examples of testing (e.g. https://github.com/plotly/dash-core-components)
- Add custom styles to your component by putting your custom CSS files into your distribution folder (`tiled_viewer`).
    - Make sure that they are referenced in `MANIFEST.in` so that they get properly included when you're ready to publish your component.
    - Make sure the stylesheets are added to the `_css_dist` dict in `tiled_viewer/__init__.py` so dash will serve them automatically when the component suite is requested.
- [Review your code](./review_checklist.md)

### Create a production build and publish:

1. Build your code:
    ```
    $ npm run build
    ```
2. Create a Python distribution
    ```
    $ python setup.py sdist bdist_wheel
    ```
    This will create source and wheel distribution in the generated the `dist/` folder.
    See [PyPA](https://packaging.python.org/guides/distributing-packages-using-setuptools/#packaging-your-project)
    for more information.

3. Test your tarball by copying it into a new environment and installing it locally:
    ```
    $ pip install tiled_viewer-0.0.1.tar.gz
    ```

4. If it works, then you can publish the component to NPM and PyPI:
    1. Publish on PyPI
        ```
        $ twine upload dist/*
        ```
    2. Cleanup the dist folder (optional)
        ```
        $ rm -rf dist
        ```
    3. Publish on NPM (Optional if chosen False in `publish_on_npm`)
        ```
        $ npm publish
        ```
        _Publishing your component to NPM will make the JavaScript bundles available on the unpkg CDN. By default, Dash serves the component library's CSS and JS locally, but if you choose to publish the package to NPM you can set `serve_locally` to `False` and you may see faster load times._

5. Share your component with the community! https://community.plotly.com/c/dash
    1. Publish this repository to GitHub
    2. Tag your GitHub repository with the plotly-dash tag so that it appears here: https://github.com/topics/plotly-dash
    3. Create a post in the Dash community forum: https://community.plotly.com/c/dash

6. Making a revision
    Make sure you're in the tiled_viewer folder, not the root project
    1. npm uninstall @blueskyproject/tiled
    2. npm install @blueskyproject/tiled
    3. npm version patch
    4. npm run build
    3. Verify it works with python usage.py
    4. rm -rf dist 
    5. python setup.py sdist bdist_wheel
    6. twine upload dist/* 