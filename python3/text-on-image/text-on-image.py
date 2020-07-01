from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def center(image_size, block_size):
    return (image_size - block_size) / 2


def right(image_size, block_size):
    return image_size - block_size


_POSITIONS = {
    'center': center,
    'left': lambda _, __: 0,
    'right': right,
    'top': lambda _, __: 0,
    'bottom': right
}


def calc_position(position):
    if isinstance(position, str):
        return _POSITIONS[position]
    return lambda _, __: position


def draw_outline_text(image: Image,
                      text: str,
                      font: str,
                      color: list = (255, 255, 255, 255),
                      spacing: int = 1,
                      outline_color: list = (0, 0, 0, 200),
                      outline_border: int = (5, 3),
                      position: str = ('center', 'center'),
                      font_size: int = 8):
    """
    Draw text with outline on image.
    
    :param image: object
    :param text: string of text
    :param color: list of integer values from 0 to 255
    :param spacing: text lines spacing. percent of image size
    :param outline_color: list of integer values from 0 to 255
    :param outline_border: outline border size. percent of image size
    :param position: (x, y) or combination of 'center', 'left', 'right' and 'center', 'top', 'bottom'
    :param font: font file
    :param font_size: percent of image size
    :return: image object
    """

    position_x, position_y = position
    position_x, position_y = calc_position(position_x), calc_position(position_y)

    draw = ImageDraw.Draw(image, 'RGBA')

    width, height = image.size
    font_size = width * font_size / 100
    font = ImageFont.truetype(font, int(font_size))

    spacing = width * spacing / 100
    t_width, t_height = draw.multiline_textsize(text, font=font, spacing=spacing)
    x, y = position_x(width, t_width), position_y(height, t_height)

    outline_border_x, outline_border_y = outline_border
    outline_border_x = width * outline_border_x / 100
    outline_border_y = width * outline_border_y / 100
    draw.rectangle((x - outline_border_x,
                    y - outline_border_y + outline_border_y / 2,
                    x + t_width + outline_border_x,
                    y + t_height + outline_border_y,
                    ),
                   fill=outline_color)
    draw.multiline_text((x, y), text, fill=color, font=font, align='center', spacing=spacing)

    return image 
