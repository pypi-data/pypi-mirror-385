# Flask-Leaflet

Flask-Leaflet provides a simple interface to use LeafletJS API with Flask.

```{warning}
🚧 This package is under heavy development..
```

## Installation

Install the extension with pip:

```bash
pip install flask-leaflet
```

Install with uv:

```bash
uv add flask-leaflet
```

## Configuration

This are some of the settings available

| Config                                   | Description                          | Type | Default |
| ---------------------------------------- | ------------------------------------ | ---- | ------- |
| LEAFLET_CSS_LOCAL_PATH                   | Leaflet CSS Path relative to static  | str  | `None`  |
| LEAFLET_JS_LOCAL_PATH                    | Leaflet JS Path relative to static   | str  | `None`  |
| LEAFLET_MARKER_ICON_URL                  | Defaul marker Icon URL image         | str  | `None`  |
| LEAFLET_MARKER_ICON_SHADOW_URL           | Defaul marker Icon Shadow URL image  | str  | `None`  |
| LEAFLET_DEFAULT_RASTER_TILE_URL_TEMPLATE | RasterTile URL default for every map | str  | `None`  |
| LEAFLET_DEFAULT_RASTER_TILE_OPTIONS      | RasterTile default options           | dict | `{}`    |

## Usage

Once installed Flask-Leaflet is easy to use. Let's walk through setting up a basic application. Also please note that this is a very basic guide: we will be taking shortcuts here that you should never take in a real application.

To begin we'll set up a Flask app:

```python
from flask import Flask
from flask_leaflet import Leaflet

app = Flask(__name__)

leaflet = Leaflet()
leaflet.init_app(app)
```

### Load resources

Once the extension is set up, this will make available the `leaflet` object into the templates context so you could load the javascript and css package easily, like this.

```html
<head>
  {{ leaflet.load() }}
</head>
```

### Constructing a Map

Once the resources are loaded into the head, then we need to constructo our first map.

```python
from flask import render_template
from flask_leaflet import Map

@app.get('/my-map')
def my_map():
    # You got every option available in the original LeafletJS
    # Using snake_case for the options.
    my_map = Map('my-map', center=[-41.139416, -73.025431], zoom=16)
    return render('my_map.html', my_map=my_map)
```

### Rendering the map

Now that we have a Map instance we can render it in a template. **IMPORTANT:** The map container **Must have a Height** given the special `class_` argument. Also you got access to `nonce_` in case you need to add a nonce token to the script tag.
in the next example we use `tailwindcss` class for a 200px height

```html
<body>
  <!-- You can add custom options at this instance that will overwrite any defaults coming from the view. Note that using class_='h-200px' we stablish a minimum height otherwise the map wouldnt be visible. -->
  {{ leaflet.render_map(my_map, class_='h-[200px]', zoom=10) }}
</body>
```

### What about RasterLayers

If you need to use a RasterTile style for every map you could stablish in your configuration the url_template and options for the default raster. Doing this will automatically be seted up for every map rendered.

You can also do it programatically in python as follows.

```python
# ...
my_map = Map('my-map', center=[-41.139416, -73.025431], zoom=16)
my_map.new_tile_layer(r"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", max_zoom=15, min_zoom=10)
```

or

```python
from flask_leaflet.layers.raster import TileLayer
# ...
my_map = Map('my-map', center=[-41.139416, -73.025431], zoom=16)
tile_layer = TileLayer(r"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", max_zoom=15, min_zoom=10)
my_map.layers.append(tile_layer)
```

### What about Markers and Polys

If you want to add a marker to your map, you could do it like so.

```python
# ...
my_map = Map('my-map', center=[-41.139416, -73.025431], zoom=16)
my_marker = my_map.new_marker([-41.139416, -73.025431], opacity=0.8)

# if you want to add a tooltip to your marker
my_marker.new_tooltip('My Marker Tooltip')

# To add a popup associated with the marker
my_marker.new_popup('<b>This is the popup content</b>')

# Adding Polys
circle = my_map.new_circle([-41.139416, -73.025431], radius=15)
# You can add popups and tooltips as well
circle.new_tooltip('This is a circle tooltip')

rectangle = my_map.new_rectangle([[-41.139416, -73.025431],[-41.139446, -73.025451]])
rectangle.new_popup('This is a rectangle popup')

```

I will be adding more functionallity in the future to extend the capabilities and customization options. Help is always welcomed.
