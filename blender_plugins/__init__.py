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
from .operators.mesh import Insert_OT_Op
from .operators.stylize import Stylize_OT_Op
from .operators.segment import Segment_OT_Op
from .panels.panel import SmartStyle3D_PT_Panel
from .operators.utils.select_segment import SelectSegment_OT_Op
from bpy.props import StringProperty, EnumProperty, CollectionProperty, BoolProperty, IntProperty

class CustomPropertiesGroup(bpy.types.PropertyGroup):
    i: IntProperty()
    label: StringProperty()
    faces: StringProperty()
    color: StringProperty()
    selected: BoolProperty(default = False)

classes = (Stylize_OT_Op, Insert_OT_Op, SmartStyle3D_PT_Panel, Segment_OT_Op, CustomPropertiesGroup, SelectSegment_OT_Op)
props = {
    'prompt': StringProperty(
        name = "", 
        default = 'A vase made of wood'
    ),

    'selected_mesh': EnumProperty(
        name = "",
        items = [
            ('0', "Vase", "Add a vase to the scene"),
            ('1', "Pencil Holder", "Add a cup holder to the scene"),
            ('2', "Lamp", "Add a lamp to the scene"),
            ('3', "Can Holder", "Add a can holder to the scene"),
            ('4', "Phone Holder", "Add a phone holder to the scene"),
            ('5', "Phone Holder Decimated", "Add a decimated phone holder to the scene (for performance purposes)"),
            ('6', 'Wrist Thing', "A wrist thing for broken wrists"),
            ('7', 'Ring', "The ring of your dreams")
        ]
    ),

    'segments': CollectionProperty(
        type = CustomPropertiesGroup
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