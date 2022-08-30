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
from .operators.base import Base_OT_Op
from .operators.mesh import Insert_OT_Op
from .operators.stylize import Stylize_OT_Op
from .operators.segment import Segment_OT_Op
from .panels.stylize import SmartStyle3D_PT_Panel
from bpy.props import StringProperty, EnumProperty

classes = (Stylize_OT_Op, Insert_OT_Op, SmartStyle3D_PT_Panel, Base_OT_Op, Segment_OT_Op)
props = {
    'prompt': StringProperty(
        name = "", 
        default = 'A vase made of wood'
    ),

    'selected_mesh': EnumProperty(
        name = "",
        items = [
            ('0', "Vase", "Add a vase to the scene"),
            ('1', "Cup Holder", "Add a cup holder to the scene"),
            ('2', "Lamp", "Add a lamp to the scene") 
        ]
    )
}

def register():
    """ """
    for class_ in classes: bpy.utils.register_class(class_)
    for prop_name, prop_value in props.items(): setattr(bpy.types.Scene, prop_name, prop_value)

def unregister():
    """ """
    for class_ in classes: bpy.utils.unregister_class(class_)

if __name__ == "__main__":
    register()