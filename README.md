# 3d-slicer README

A basic VSCode extension to work with code for 3D Slicer

## Features

Currently you can execute a buffer from code in the 3D Slicer Python environment and modify things like the current scene, the GUI, etc.  This is powerful for developing and testing new functionality.  Instead of embedding the AI tools in Slicer, this allows you to use any of the existing VSCode AI extensions on your Slicer code easily.

In the future we may want to add additional features, like an interactive explorer for the data loaded in Slicer, the current variables in the Python environment, etc.


## Requirements

A recent [3D Slicer](https://download.slicer.org/), like 5.8.1 or greater.  Enable the [Web Server exec endpoint](https://slicer.readthedocs.io/en/latest/user_guide/modules/webserver.html) and you should be good to go.

## Extension Settings

The defaults on both sides should be working.

## Known Issues

The features are very limited currently.  We might want to enhance the Web Server to support more functionality for this plugin.

## Release Notes

### 1.0.0

Initial release with minimal features

