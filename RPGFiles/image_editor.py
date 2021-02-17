from PIL import Image


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


def createInventory(equipment, inventory, id):
    equipment = [Image.open(x) for x in equipment]
    inventory = [Image.open(x) for x in inventory]

    # Pack Equipment with size 128x128
    newequip = []
    for i in equipment:
        i = size128(i)
        newequip.append(i)
    if len(newequip) > 1:
        finalImage = append_images(newequip, direction='horizontal')
    elif len(newequip) == 1:
        finalImage = equipment[0]

    # Pack Inventory with size 64x64 in sets of 8
    invList = []
    loopSize = 8
    newinv = []
    for i in inventory:
        i = size64(i)
        newinv.append(i)
        if len(newinv) == loopSize:
            invList.append(append_images(newinv, direction='horizontal'))
            newinv = []
    if len(newinv) == 1:
        invList.append(newinv[0])
    elif len(newinv) > 1:
        invList.append(append_images(newinv, direction='horizontal'))

    # Combine Equipment and Inventory into one image to display
    for list in invList:
        finalImage = append_images([finalImage, list], direction='vertical', bg_color=(0, 0, 0), alignment='left')
    finalImage.save('temp_inv_%s.jpg' % id)
    return True


def createShop(lists, id):
    imagesToPack = []
    for list in lists:
        images = [Image.open(x) for x in list]
        sizedImages = []
        for i in images:
            i = size32(i)
            sizedImages.append(i)
        if len(list) == 1:
            imagesToPack.append(sizedImages[0])
        elif len(list) > 1:
            imagesToPack.append(append_images(sizedImages, direction='horizontal'))
    if len(imagesToPack) > 1:
        combo_3 = append_images(imagesToPack, direction='vertical', bg_color=(0, 0, 0), alignment='left')
    else:
        combo_3 = imagesToPack[0]
    combo_3.save('temp_shop_%s.jpg' % id)


def size32(image, string=False):
    if string is True:
        image = Image.open(image)
    if image.size != (32, 32):
        img = image.resize((32, 32), Image.ANTIALIAS)
        return img
    else:
        return image


def size64(image, string=False):
    if string is True:
        image = Image.open(image)
    if image.size != (32, 32):
        img = image.resize((64, 64), Image.ANTIALIAS)
        return img
    else:
        return image


def size128(image, string=False):
    if string is True:
        image = Image.open(image)
    if image.size != (32, 32):
        img = image.resize((128, 128), Image.ANTIALIAS)
        return img
    else:
        return image
