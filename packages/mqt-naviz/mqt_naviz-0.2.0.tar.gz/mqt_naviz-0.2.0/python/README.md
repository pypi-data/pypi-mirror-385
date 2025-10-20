# Python Package for NAViz

## Building the wheel

This package uses [`maturin`](https://github.com/PyO3/maturin) to export the [`bindings`](./../bindings/) crate as a Python wheel.
The wheel can be built using `maturin build` or alternatively `maturin develop` for faster development builds.
For more information on [`maturin`](https://github.com/PyO3/maturin) and the difference between the build commands, see [`maturin`'s README](https://github.com/PyO3/maturin?tab=readme-ov-file#maturin).

## Usage

The Python library currently only exports a simple functionality to export a visualization as a video.
An example can be seen below:

```python
from naviz import *

# Get machine and style from repository
machine = Repository.machines().get("example")
style = Repository.machines().get("tum")

# Alternatively, you can also use manual configurations
machine = "<...>"
style = "<...>"

# Render NAViz instructions to `out.mp4` at 1080p60
export_video("<NAViz instructions>", "out.mp4", (1920, 1080), 60, machine, style)

# Render MQT NA instructions to `out.mp4` at 1080p60 with the default import options
# Alternatively, substitute the call to `default_import_settings` with your custom import settings
export_video(
    "<MQT NA instructions>",
    "out.mp4",
    (1920, 1080),
    60,
    machine,
    style,
    default_import_settings("MqtNa"),
)
```

## License

The NAViz Python package is licensed under the terms of the [MIT](./LICENSE) license.
