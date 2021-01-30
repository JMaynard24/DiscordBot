from PIL import Image
from math import floor


def append_images(images, direction='horizontal',
                  bg_color=(255, 255, 255), alignment='center'):
    """
    Appends images in horizontal/vertical direction.

    Args:
        images: List of PIL images
        direction: direction of concatenation, 'horizontal' or 'vertical'
        bg_color: Background color (default: white)
        aligment: alignment mode if images need padding;
           'left', 'right', 'top', 'bottom', or 'center'

    Returns:
        Concatenated image as a new PIL image object.
    """
    widths, heights = zip(*(i.size for i in images))

    if direction == 'horizontal':
        new_width = sum(widths)
        new_height = max(heights)
    else:
        new_width = max(widths)
        new_height = sum(heights)

    new_im = Image.new('RGB', (new_width, new_height), color=bg_color)


    offset = 0
    for im in images:
        if direction == 'horizontal':
            y = 0
            if alignment == 'center':
                y = int((new_height - im.size[1]) / 2)
            elif alignment == 'bottom':
                y = new_height - im.size[1]
            new_im.paste(im, (offset, y))
            offset += im.size[0]
        else:
            x = 0
            if alignment == 'center':
                x = int((new_width - im.size[0]) / 2)
            elif alignment == 'right':
                x = new_width - im.size[0]
            new_im.paste(im, (x, offset))
            offset += im.size[1]

    return new_im


def createInventory(equipment, inventory):
    combo_1 = None
    combo_2 = None
    equipment = [Image.open(x) for x in equipment]
    inventory = [Image.open(x) for x in inventory]
    newinv = []
    newequip = []
    for i in equipment:
        i = size128(i)
        newequip.append(i)
    for i in inventory:
        i = size64(i)
        newinv.append(i)
    if len(newequip) + len(newinv) == 0:
        return None
    if len(newequip) > 1:
        combo_1 = append_images(newequip, direction='horizontal')
    elif len(newequip) == 1:
        combo_1 = equipment[0]
    if len(newinv) > 1:
        combo_2 = append_images(newinv, direction='horizontal')
    elif len(newinv) == 1:
        combo_2 == newinv[0]
    if combo_1 is not None and combo_2 is not None:
        combo_3 = append_images([combo_1, combo_2], direction='vertical', bg_color=(0, 0, 0), alignment='left')
        combo_3.save('temp.jpg')
    elif combo_1 is None and combo_2 is not None:
        combo_2.save('temp.jpg')
    elif combo_2 is None and combo_1 is not None:
        combo_1.save('temp.jpg')
    return True


def size64(image, string=False):
    if string is True:
        image = Image.open(image)
    img = image.resize((64, 64), Image.ANTIALIAS)
    return img


def size128(image, string=False):
    if string is True:
        image = Image.open(image)
    img = image.resize((128, 128), Image.ANTIALIAS)
    return img
