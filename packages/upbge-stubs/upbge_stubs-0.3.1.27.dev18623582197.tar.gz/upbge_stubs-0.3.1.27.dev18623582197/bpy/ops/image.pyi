"""


Image Operators
***************

:func:`add_render_slot`

:func:`change_frame`

:func:`clear_render_border`

:func:`clear_render_slot`

:func:`clipboard_copy`

:func:`clipboard_paste`

:func:`convert_to_mesh_plane`

:func:`curves_point_set`

:func:`cycle_render_slot`

:func:`external_edit`

:func:`file_browse`

:func:`flip`

:func:`import_as_mesh_planes`

:func:`invert`

:func:`match_movie_length`

:func:`new`

:func:`open`

:func:`open_images`

:func:`pack`

:func:`project_apply`

:func:`project_edit`

:func:`read_viewlayers`

:func:`reload`

:func:`remove_render_slot`

:func:`render_border`

:func:`replace`

:func:`resize`

:func:`rotate_orthogonal`

:func:`sample`

:func:`sample_line`

:func:`save`

:func:`save_all_modified`

:func:`save_as`

:func:`save_sequence`

:func:`tile_add`

:func:`tile_fill`

:func:`tile_remove`

:func:`unpack`

:func:`view_all`

:func:`view_center_cursor`

:func:`view_cursor_center`

:func:`view_ndof`

:func:`view_pan`

:func:`view_selected`

:func:`view_zoom`

:func:`view_zoom_border`

:func:`view_zoom_in`

:func:`view_zoom_out`

:func:`view_zoom_ratio`

"""

import typing

import mathutils

def add_render_slot() -> None:

  """

  Add a new render slot

  """

  ...

def change_frame(*args, frame: int = 0) -> None:

  """

  Interactively change the current frame number

  """

  ...

def clear_render_border() -> None:

  """

  Clear the boundaries of the render region and disable render region

  """

  ...

def clear_render_slot() -> None:

  """

  Clear the currently selected render slot

  """

  ...

def clipboard_copy() -> None:

  """

  Copy the image to the clipboard

  """

  ...

def clipboard_paste() -> None:

  """

  Paste new image from the clipboard

  """

  ...

def convert_to_mesh_plane(*args, interpolation: str = 'Linear', extension: str = 'CLIP', use_auto_refresh: bool = True, relative: bool = True, shader: str = 'PRINCIPLED', emit_strength: float = 1.0, use_transparency: bool = True, render_method: str = 'DITHERED', use_backface_culling: bool = False, show_transparent_back: bool = True, overwrite_material: bool = True, name_from: str = 'OBJECT', delete_ref: bool = True) -> None:

  """

  Convert selected reference images to textured mesh plane

  """

  ...

def curves_point_set(*args, point: str = 'BLACK_POINT', size: int = 1) -> None:

  """

  Set black point or white point for curves

  """

  ...

def cycle_render_slot(*args, reverse: bool = False) -> None:

  """

  Cycle through all non-void render slots

  """

  ...

def external_edit(*args, filepath: str = '') -> None:

  """

  Edit image in an external application

  """

  ...

def file_browse(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Open an image file browser, hold Shift to open the file, Alt to browse containing directory

  """

  ...

def flip(*args, use_flip_x: bool = False, use_flip_y: bool = False) -> None:

  """

  Flip the image

  """

  ...

def import_as_mesh_planes(*args, interpolation: str = 'Linear', extension: str = 'CLIP', use_auto_refresh: bool = True, relative: bool = True, shader: str = 'PRINCIPLED', emit_strength: float = 1.0, use_transparency: bool = True, render_method: str = 'DITHERED', use_backface_culling: bool = False, show_transparent_back: bool = True, overwrite_material: bool = True, filepath: str = '', align: str = 'WORLD', location: mathutils.Vector = (0.0, 0.0, 0.0), rotation: mathutils.Euler = (0.0, 0.0, 0.0), files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, directory: str = '', filter_image: bool = True, filter_movie: bool = True, filter_folder: bool = True, force_reload: bool = False, image_sequence: bool = False, offset: bool = True, offset_axis: str = '+X', offset_amount: float = 0.1, align_axis: str = 'CAM_AX', prev_align_axis: str = 'NONE', align_track: bool = False, size_mode: str = 'ABSOLUTE', fill_mode: str = 'FILL', height: float = 1.0, factor: float = 600.0) -> None:

  """

  Create mesh plane(s) from image files with the appropriate aspect ratio

  """

  ...

def invert(*args, invert_r: bool = False, invert_g: bool = False, invert_b: bool = False, invert_a: bool = False) -> None:

  """

  Invert image's channels

  """

  ...

def match_movie_length() -> None:

  """

  Set image's user's length to the one of this video

  """

  ...

def new(*args, name: str = 'Untitled', width: int = 1024, height: int = 1024, color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0), alpha: bool = True, generated_type: str = 'BLANK', float: bool = False, use_stereo_3d: bool = False, tiled: bool = False) -> None:

  """

  Create a new image

  """

  ...

def open(*args, allow_path_tokens: bool = True, filepath: str = '', directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '', use_sequence_detection: bool = True, use_udim_detecting: bool = True) -> None:

  """

  Open image

  """

  ...

def open_images(*args, directory: str = '', files: typing.Union[typing.Sequence[OperatorFileListElement], typing.Mapping[str, OperatorFileListElement], bpy.types.bpy_prop_collection] = None, relative_path: bool = True, use_sequence_detection: bool = True, use_udim_detection: bool = True) -> None:

  """

  Undocumented, consider `contributing <https://developer.blender.org/>`_.

  """

  ...

def pack() -> None:

  """

  Pack an image as embedded data into the .blend file

  """

  ...

def project_apply() -> None:

  """

  Project edited image back onto the object

  """

  ...

def project_edit() -> None:

  """

  Edit a snapshot of the 3D Viewport in an external image editor

  """

  ...

def read_viewlayers() -> None:

  """

  Read all the current scene's view layers from cache, as needed

  """

  ...

def reload() -> None:

  """

  Reload current image from disk

  """

  ...

def remove_render_slot() -> None:

  """

  Remove the current render slot

  """

  ...

def render_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True) -> None:

  """

  Set the boundaries of the render region and enable render region

  """

  ...

def replace(*args, filepath: str = '', hide_props_region: bool = True, check_existing: bool = False, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Replace current image by another one from disk

  """

  ...

def resize(*args, size: typing.Tuple[int, int] = (0, 0), all_udims: bool = False) -> None:

  """

  Resize the image

  """

  ...

def rotate_orthogonal(*args, degrees: str = '90') -> None:

  """

  Rotate the image

  """

  ...

def sample(*args, size: int = 1) -> None:

  """

  Use mouse to sample a color in current image

  """

  ...

def sample_line(*args, xstart: int = 0, xend: int = 0, ystart: int = 0, yend: int = 0, flip: bool = False, cursor: int = 5) -> None:

  """

  Sample a line and show it in Scope panels

  """

  ...

def save() -> None:

  """

  Save the image with current name and settings

  """

  ...

def save_all_modified() -> None:

  """

  Save all modified images

  """

  ...

def save_as(*args, save_as_render: bool = False, copy: bool = False, allow_path_tokens: bool = True, filepath: str = '', check_existing: bool = True, filter_blender: bool = False, filter_backup: bool = False, filter_image: bool = True, filter_movie: bool = True, filter_python: bool = False, filter_font: bool = False, filter_sound: bool = False, filter_text: bool = False, filter_archive: bool = False, filter_btx: bool = False, filter_alembic: bool = False, filter_usd: bool = False, filter_obj: bool = False, filter_volume: bool = False, filter_folder: bool = True, filter_blenlib: bool = False, filemode: int = 9, relative_path: bool = True, show_multiview: bool = False, use_multiview: bool = False, display_type: str = 'DEFAULT', sort_method: str = '') -> None:

  """

  Save the image with another name and/or settings

  """

  ...

def save_sequence() -> None:

  """

  Save a sequence of images

  """

  ...

def tile_add(*args, number: int = 1002, count: int = 1, label: str = '', fill: bool = True, color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0), generated_type: str = 'BLANK', width: int = 1024, height: int = 1024, float: bool = False, alpha: bool = True) -> None:

  """

  Adds a tile to the image

  """

  ...

def tile_fill(*args, color: typing.Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0), generated_type: str = 'BLANK', width: int = 1024, height: int = 1024, float: bool = False, alpha: bool = True) -> None:

  """

  Fill the current tile with a generated image

  """

  ...

def tile_remove() -> None:

  """

  Removes a tile from the image

  """

  ...

def unpack(*args, method: str = 'USE_LOCAL', id: str = '') -> None:

  """

  Save an image packed in the .blend file to disk

  """

  ...

def view_all(*args, fit_view: bool = False) -> None:

  """

  View the entire image

  """

  ...

def view_center_cursor() -> None:

  """

  Center the view so that the cursor is in the middle of the view

  """

  ...

def view_cursor_center(*args, fit_view: bool = False) -> None:

  """

  Set 2D Cursor To Center View location

  """

  ...

def view_ndof() -> None:

  """

  Use a 3D mouse device to pan/zoom the view

  """

  ...

def view_pan(*args, offset: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Pan the view

  """

  ...

def view_selected() -> None:

  """

  View all selected UVs

  """

  ...

def view_zoom(*args, factor: float = 0.0, use_cursor_init: bool = True) -> None:

  """

  Zoom in/out the image

  """

  ...

def view_zoom_border(*args, xmin: int = 0, xmax: int = 0, ymin: int = 0, ymax: int = 0, wait_for_input: bool = True, zoom_out: bool = False) -> None:

  """

  Zoom in the view to the nearest item contained in the border

  """

  ...

def view_zoom_in(*args, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Zoom in the image (centered around 2D cursor)

  """

  ...

def view_zoom_out(*args, location: mathutils.Vector = (0.0, 0.0)) -> None:

  """

  Zoom out the image (centered around 2D cursor)

  """

  ...

def view_zoom_ratio(*args, ratio: float = 0.0) -> None:

  """

  Set zoom ratio of the view

  """

  ...
