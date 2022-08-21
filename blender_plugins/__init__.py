# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "imad",
    "author" : "imad",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy 
from bpy.props import StringProperty
from .operators.stylize import Stylize_OT_Op
from .panels.stylize import SmartStyle3D_PT_Panel

classes = (Stylize_OT_Op, SmartStyle3D_PT_Panel)

def register():
    """"""
    for class_ in classes: bpy.utils.register_class(class_)
    bpy.types.Scene.directory = StringProperty(subtype='DIR_PATH')

def unregister():
    """"""
    for class_ in classes: bpy.utils.unregister_class(class_)
    del(bpy.types.Scene.directory)
