import os

from PIL import Image, ImageOps

from viggocore.subsystem.image.resource import Image as ImageViggocore, \
    QualityImage


class ImageHandler:

    def __init__(self, sizes=None):
        self.target_extension = '.jpg'
        if sizes is None:
            self.sizes = {
                QualityImage.min.value: (170, 150),
                QualityImage.med.value: (350, 310),
                QualityImage.max.value: (1500, 1300)
            }
        else:
            self.sizes = sizes

    def process(self, folder, filename):
        try:
            image_path = os.path.join(folder, filename)
            with Image.open(image_path) as image:
                image.load()
                normalized = self.normalize(image)
                file, extension = os.path.splitext(filename)
                self.create_thumbnails(normalized, os.path.join(folder, file))
        except IOError:
            raise

    def _remove_transparency(self, image):
        fill_color = (255, 255, 255)
        image = image.convert('RGBA')
        try:
            mask = image.split()[-1]
        except IndexError:
            mask = None
        background = Image.new('RGBA', image.size, fill_color)
        background.paste(image, mask=mask)
        image = background
        return image

    def normalize(self, image):
        if image.mode in ['RGBA', 'P', 'LA']:
            image = self._remove_transparency(image)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image

    def create_thumbnails(self, image, file):
        for size in self.sizes:
            name = '{}.{}{}'.format(file, size, self.target_extension)
            self.create_thumbnail(image, self.sizes[size], name)

    def create_thumbnail(self, image, size, name):
        width, height = size
        if image.width < width:
            width = image.width
        if image.height < height:
            height = image.height
        thumb = image.copy()
        thumb.thumbnail((width, height))
        try:
            thumb = ImageOps.exif_transpose(thumb)
        except Exception:
            pass
        thumb.save(name, 'JPEG')

    @staticmethod
    def verify_size_resolution_image(folder, filename):
        messageError = None
        try:
            image_path = os.path.join(folder, filename)
            with Image.open(image_path) as img:
                if img.height > ImageViggocore.MAX_ALLOWED_SIZE[0] or \
                   img.width > ImageViggocore.MAX_ALLOWED_SIZE[1]:
                    messageError = 'Image must be less than {}px and less\
                        than {}px high!'.format(
                            ImageViggocore.MAX_ALLOWED_SIZE[0],
                            ImageViggocore.MAX_ALLOWED_SIZE[1])
        except Exception:
            messageError = 'ERROR: image resolution check failed'
        finally:
            return messageError
