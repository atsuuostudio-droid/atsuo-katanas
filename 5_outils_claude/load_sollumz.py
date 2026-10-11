import bpy, addon_utils
def load():
    m=addon_utils.enable('sollumz', default_set=True, persistent=True)
    return m
