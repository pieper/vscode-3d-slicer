import SampleData
import slicer
import vtk
import numpy as np

# Clear the scene
slicer.mrmlScene.Clear()

# Set the layout to show 3D and slice views
slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

# Download the MRHead sample data
SampleData.SampleDataLogic().downloadMRHead()

# Get the volume node from the scene
volumeNode = slicer.util.getNode('MRHead')

# Enable volume rendering for the node
slicer.modules.volumerendering.logic().CreateDefaultVolumeRenderingNodes(volumeNode)
slicer.app.layoutManager().threeDWidget(0).threeDView().resetFocalPoint()

# Create a smoothed version of the volume for more stable gradient calculation
gaussian = vtk.vtkImageGaussianSmooth()
gaussian.SetInputData(volumeNode.GetImageData())
gaussian.SetStandardDeviations(2.0, 2.0, 2.0)
gaussian.Update()

# Create a new volume node for the smoothed data
smoothedVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "SmoothedMRHead")
smoothedImageData = vtk.vtkImageData()
smoothedImageData.DeepCopy(gaussian.GetOutput())
smoothedVolumeNode.SetAndObserveImageData(smoothedImageData)
smoothedVolumeNode.CopyOrientation(volumeNode)
smoothedVolumeNode.CreateDefaultDisplayNodes()
smoothedVolumeNode.GetDisplayNode().SetVisibility(False) # Hide from slice views

# Create a transform node that will follow the fiducial
transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLinearTransformNode", "ToolTransform")

# This function will be called every time the fiducial is moved
def updateTransform(caller, event):
    # Get the last placed fiducial's position in world coordinates
    lastFiducialIndex = caller.GetNumberOfControlPoints() - 1
    if lastFiducialIndex < 0:
        return
    p_ras = np.array([0,0,0])
    caller.GetNthControlPointPositionWorld(lastFiducialIndex, p_ras)

    # Get the volume's image data and coordinate transforms
    imageData = smoothedVolumeNode.GetImageData()
    rasToIjk = vtk.vtkMatrix4x4()
    volumeNode.GetRASToIJKMatrix(rasToIjk)
    ijkToRas = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASMatrix(ijkToRas)

    # Convert fiducial position to IJK (voxel) coordinates
    p_ijk_homogeneous = rasToIjk.MultiplyPoint(np.append(p_ras, 1.0))
    p_ijk = np.array(p_ijk_homogeneous[:3])

    # Calculate the gradient in IJK space (central differences)
    i, j, k = int(round(p_ijk[0])), int(round(p_ijk[1])), int(round(p_ijk[2]))
    gx = (imageData.GetScalarComponentAsDouble(i + 1, j, k, 0) - imageData.GetScalarComponentAsDouble(i - 1, j, k, 0)) / 2.0
    gy = (imageData.GetScalarComponentAsDouble(i, j + 1, k, 0) - imageData.GetScalarComponentAsDouble(i, j - 1, k, 0)) / 2.0
    gz = (imageData.GetScalarComponentAsDouble(i, j, k + 1, 0) - imageData.GetScalarComponentAsDouble(i, j, k - 1, 0)) / 2.0
    gradient_ijk = np.array([gx, gy, gz])

    # The gradient is a vector, so we use the direction matrix part of the IJK-to-RAS transform
    # to get the gradient in world coordinates. This is our surface normal.
    directionMatrix = np.array([[ijkToRas.GetElement(row, col) for col in range(3)] for row in range(3)])
    vecZ = directionMatrix.dot(gradient_ijk)
    vecZ = vecZ / np.linalg.norm(vecZ) # Normalize

    # Calculate the origin of the transform, 10mm away from the surface along the normal
    origin = p_ras - 10.0 * vecZ

    # Define the superior direction vector
    vecSuperior = np.array([0, 0, 1.0])

    # Handle the edge case where the normal is parallel to the superior direction
    if np.allclose(np.abs(vecZ), vecSuperior):
        # Ambiguity: normal is pointing straight up/down. Make X point left.
        vecX = np.array([1.0, 0, 0])
    else:
        # Calculate X by crossing superior with the normal
        vecX = np.cross(vecSuperior, vecZ)
        vecX = vecX / np.linalg.norm(vecX) # Normalize

    # Calculate Y as the cross product of Z and X
    vecY = np.cross(vecZ, vecX)
    # vecY is already normalized because vecZ and vecX are orthonormal

    # Create the 4x4 transformation matrix
    matrix = vtk.vtkMatrix4x4()
    for i in range(3):
        matrix.SetElement(i, 0, vecX[i])
        matrix.SetElement(i, 1, vecY[i])
        matrix.SetElement(i, 2, vecZ[i])
        matrix.SetElement(i, 3, origin[i])
    transformNode.SetMatrixTransformToParent(matrix)

# Create a simple figure-8 TMS coil model using VTK primitives
def createCoilModel():
    # Use vtkAppendPolyData to combine two tori into a figure-8
    appendPolyData = vtk.vtkAppendPolyData()

    # Create two torus sources
    for i in [-1, 1]:
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetRadius(15)
        cylinder.SetHeight(6)
        cylinder.SetResolution(50)

        # Position the tori side-by-side to make a figure-8
        transform = vtk.vtkTransform()
        transform.RotateX(90) # Lay the cylinder flat
        transform.Translate(i * 20, 0, 0)
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(cylinder.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        appendPolyData.AddInputData(transformFilter.GetOutput())

    appendPolyData.Update()
    return appendPolyData.GetOutput()

coilPolyData = createCoilModel()
coilModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "TMSCoil")
coilModelNode.SetAndObservePolyData(coilPolyData)
coilModelNode.CreateDefaultDisplayNodes()
displayNode = coilModelNode.GetDisplayNode()
displayNode.SetColor(1.0, 1.0, 0.0) # Yellow
coilModelNode.SetAndObserveTransformNodeID(transformNode.GetID())
coilModelNode.SetSelectable(0) # Make the coil model not pickable

# Create a new fiducial markups node and set the mouse to place points
markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "ToolTarget")
markupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, updateTransform)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
# interactionNode.Place is a constant for place mode
interactionNode.SetCurrentInteractionMode(interactionNode.Place)