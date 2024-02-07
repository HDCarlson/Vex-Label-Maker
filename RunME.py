import pandas as pd
import qrcode
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from io import BytesIO

def qrCreate(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=9,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    with Image(file=buf) as wand_img:
        return wand_img.clone()  # Return a clone of the image
def main():
    width, height = 900, 300
    w, h = width / 3, height
    db = pd.read_csv('Parts.csv')

    class Part:
        def __init__(self, name, url, sku):
            self.name = name
            self.url = url
            self.sku = sku
            self.fileName = name.replace(" ", "_")
            self.qr = qrCreate(self.url)
            self.label = Image(width=width, height=height, background=Color('white'))

    Parts = [Part(row['Name'], row['URL'], row['SKU']) for index, row in db.iterrows()]

    for part in Parts:
        x = (width - part.qr.width) // 2 + width // 3
        y = (height - part.qr.height) // 2
        part.label.composite(part.qr, left=x, top=y)
        left_space = width - part.qr.width
        with Drawing() as draw:
            draw.font = 'ComicSansMS3.ttf'  # Update with the correct path
            font_size = 60
            text = part.name
            metrics = draw.get_font_metrics(part.label, part.name, multiline=False)
            while font_size > 0:
                draw.font_size = font_size
                metrics = draw.get_font_metrics(part.label, part.name, multiline=False)
                text_width = metrics.text_width
                if text_width + 80 < left_space:  # If text fits in the available space
                    break
                font_size -= 1  # Decrease font size and try again
            text_width = metrics.text_width
            text_height = metrics.text_height
            x = (width - part.qr.width - text_width) / 2
            y = (text_height / 2) + 25 # Adjust y as needed, this places text vertically centered
            if x < 0:
                print(f'width: {width}, qrwidth: {part.qr.width}, text width: {text_width}')
            draw.text(int(x), int(y), text)
            draw(part.label)
        
        
        
        part.label.save(filename=f'Photos/Final_Labels/{part.fileName}.png')

if __name__ == "__main__":
    main()
