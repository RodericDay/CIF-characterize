import vtk

class Scene:

    def __init__(self):
        render_window = vtk.vtkRenderWindow()

        self.renderer = vtk.vtkRenderer()
        render_window.AddRenderer(self.renderer)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(render_window)

        camera = vtk.vtkInteractorStyleTrackballCamera()
        camera.SetCurrentRenderer(self.renderer)
        self.interactor.SetInteractorStyle(camera)

    def render_object(self, nodes, edges, radii, color):
        polydata = vtk.vtkPolyData()

        points = vtk.vtkPoints()
        for x, y, z in nodes:
            points.InsertNextPoint(x, y, z)
        polydata.SetPoints(points)

        lines = vtk.vtkCellArray()
        for a, b in edges:
            id_list = vtk.vtkIdList()
            id_list.InsertNextId(a)
            id_list.InsertNextId(b)
            lines.InsertNextCell(id_list)
        polydata.SetLines(lines)

        data = vtk.vtkFloatArray()
        try:
            iter(radii)
        except TypeError:
            radii = [radii for _ in range(len(nodes))]
        for r in radii:
            data.InsertNextValue(r)
        polydata.GetPointData().SetScalars(data)

        # wires
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        self.renderer.AddActor(actor)

        # sphere
        sphere_source = vtk.vtkSphereSource()
        sphere_filter = vtk.vtkGlyph3D()
        sphere_filter.SetSourceConnection(sphere_source.GetOutputPort())
        sphere_filter.SetInput(polydata)
        sphere_filter.GeneratePointIdsOn()
        sphere_filter.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere_filter.GetOutputPort())
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        self.renderer.AddActor(actor)

        # tube
        tube_filter = vtk.vtkTubeFilter()
        tube_filter.SetInput(polydata)
        tube_filter.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
        tube_filter.SetNumberOfSides(10)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube_filter.GetOutputPort())
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        self.renderer.AddActor(actor)

    def play(self):
        self.interactor.Start()


def visualize(solid_nodes, solid_edges, pore_centers, pore_radii):
    scene = Scene()
    scene.render_object(solid_nodes, solid_edges, 1, (1,0,0))
    scene.render_object(pore_centers, [], pore_radii, (0,0,1))
    scene.play()


if __name__ == '__main__':
    visualize([(0,0,0),(1,1,1)], [(0,1)], [(20,20,20)], [5])