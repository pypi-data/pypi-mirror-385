
def show_cld_xyz(*arr, color=(255,255,255)):
    from .vtk_impl import _show_cld
    _show_cld(*arr, data_fmt="xyz", color=color)

def show_cld_xyznormal(*arr, color=(255,255,255)):
    from .vtk_impl import _show_cld
    _show_cld(*arr, data_fmt="xyzn", color=color)

def show_cld_xyzrgb(arr):
    from .vtk_impl import _show_cld
    _show_cld(*arr, data_fmt="xyzrgb")