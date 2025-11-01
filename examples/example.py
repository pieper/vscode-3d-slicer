import SampleData

slicer.mrmlScene.Clear()
slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

SampleData.SampleDataLogic().downloadMRHead()

volumeNode = slicer.util.getNode('MRHead')
print(volumeNode)