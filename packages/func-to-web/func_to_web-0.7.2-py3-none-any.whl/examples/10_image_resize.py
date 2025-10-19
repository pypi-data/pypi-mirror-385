from PIL import Image

from func_to_web import Annotated, Field, Literal, run
from func_to_web.types import ImageFile


def resize_image(
    image: ImageFile,
    width: Annotated[int, Field(ge=10, le=4000)] = 800,
    height: Annotated[int, Field(ge=10, le=4000)] = 600,
    mode: Literal['stretch', 'fit', 'fill'] = 'fit'
):
    """Resize image with different modes"""
    img = Image.open(image)
    
    if mode == 'stretch':
        return img.resize((width, height))
    elif mode == 'fit':
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        return img
    else:  # fill
        return img.resize((width, height), Image.Resampling.LANCZOS)

run(resize_image)