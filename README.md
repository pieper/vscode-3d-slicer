# 3d-slicer README

A basic VSCode extension to work with code for 3D Slicer

## Features

Currently you can execute a buffer from code in the 3D Slicer Python environment and modify things like the current scene, the GUI, etc.  This is powerful for developing and testing new functionality.  Instead of embedding the AI tools in Slicer, this allows you to use any of the existing VSCode AI extensions on your Slicer code easily.

In the future we may want to add additional features, like an interactive explorer for the data loaded in Slicer, the current variables in the Python environment, etc.


## Requirements

A recent [3D Slicer](https://download.slicer.org/), like 5.8.1 or greater.  Enable the [Web Server exec endpoint](https://slicer.readthedocs.io/en/latest/user_guide/modules/webserver.html) and you should be good to go.

## Installation

Download the latest `.vslx` file from the releases for this repository.  In VSCode, pick the settings gear icon in the lower left, and pick Extensions from the menu.  In the upper right of the Extensions pane, pick "Install from VSLX" and browse to the downloaded file.

<img width="698" height="307" alt="image" src="https://github.com/user-attachments/assets/8b29baa2-994c-4163-9c72-5bcda5da6691" />

## Example usage

Be sure to enable exec in the advanced mode of Slicer's Web Server and click Start.

Open a New File in VSCode.

Add some Slicer code, such as this:
```
import slicer
import SampleData

# 1. Close the current scene
slicer.mrmlScene.Clear(0)

# 2. Download the MRHead dataset
print("Downloading MRHead dataset...")
volumeNode = SampleData.SampleDataLogic().downloadMRHead()
if not volumeNode:
  print("Failed to download MRHead dataset.")
else:
  print("MRHead dataset downloaded successfully.")

  # 3. Set the layout to 4-up view
  slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

  # 4. Enable volume rendering
  volRenLogic = slicer.modules.volumerendering.logic()
  displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
  displayNode.SetVisibility(True)

  print("Volume rendering enabled in 4-up view.")
```

Use the Command Palette shortcut (`control-shift-P` or `command-shift-P` for mac) and type `Slicer` to find the `Slicer: Execute script` command and select it to execute.  This will become the default, so that later you can just do `control-shift-P return` to execute the script.

## Troubleshooting

Any script errors are currently only shown in the Web Server log in Slicer.

## Extension Settings

The defaults on both sides should be working.

## Known Issues

The features are very limited currently.  We might want to enhance the Web Server to support more functionality for this plugin.

Only one instance of the Slicer Web Server can currently be used becuase the server port is fixed as 2016.

## Release Notes

### 1.0.0

Initial release with minimal features

