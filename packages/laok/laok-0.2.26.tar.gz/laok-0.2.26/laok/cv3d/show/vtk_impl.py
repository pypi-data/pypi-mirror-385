#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/5/26 17:13:49

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
import vtk
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.util.numpy_support import numpy_to_vtk
#===============================================================================
'''     
'''
#===============================================================================

def _show_cld(*arr, data_fmt, color=(255,255,255)):
    win = VtkWin3d()
    for cld in arr:
        win.add_cld(array=cld, data_fmt=data_fmt, color=color)
    win.show()

class VtkWin3d:
    def __init__(self):
        ren = vtkRenderer()
        ren.SetBackground(0, 0, 0)

        renWin = vtkRenderWindow()
        renWin.AddRenderer(ren)
        renWin.SetSize(400, 400)
        renWin.SetWindowName('3D viewer')

        iren = vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)
        iren.SetInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera())

        self.ren_ = ren
        self.renWin_ = renWin
        self.iren_ = iren

    def add_cylinder(self):
        mapper = vtkPolyDataMapper()
        actor = vtkActor()
        actor.SetMapper(mapper)

        cylinder = vtkCylinderSource()
        cylinder.SetResolution(8)
        mapper.SetInputConnection(cylinder.GetOutputPort())

        self.ren_.AddActor(actor)
        return actor

    def add_cld(self, array, data_fmt="xyz", color=(255,255,255)):
        return self.add_xyz(array[:, 0:3], color)

    def add_xyz(self, array, color=(255,255,255)):
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(array))

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)

        vertex = vtk.vtkVertexGlyphFilter()
        vertex.SetInputData(polydata)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vertex.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0]/255, color[1]/255, color[2]/255)
        self.ren_.AddActor(actor)
        return actor

    def add_xyznormal(self, array, color=(255, 255, 255)):
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(array))

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)

        vertex = vtk.vtkVertexGlyphFilter()
        vertex.SetInputData(polydata)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vertex.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0] / 255, color[1] / 255, color[2] / 255)
        self.ren_.AddActor(actor)
        return actor

    def add_xyzrgb(self, array):
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(array))

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)

        vertex = vtk.vtkVertexGlyphFilter()
        vertex.SetInputData(polydata)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vertex.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # actor.GetProperty().SetColor(color[0]/255, color[1]/255, color[2]/255)
        self.ren_.AddActor(actor)
        return actor


    def show(self):
        self.iren_.Initialize()
        self.ren_.ResetCamera()
        self.renWin_.Render()
        self.iren_.Start()
