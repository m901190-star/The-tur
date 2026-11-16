"""C14 article screenshot (status bar removed) + the signing photo embedded below like the article's lead image."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
a = Image.open(HERE + '/source-article.jpg').convert('RGB'); p = Image.open(HERE + '/photo.jpg').convert('RGB')
top = a.crop((0, 95, a.width, a.height)); d = ImageDraw.Draw(top); d.rectangle((0, 112, 24, 150), fill=(255, 255, 255))   # stray edge pixels
W = a.width; M = 0
ph = p.crop((0, 540, p.width, 1640)); ph = ph.resize((W - 2 * M, int((W - 2 * M) * ph.height / ph.width)), Image.LANCZOS)
out = Image.new('RGB', (W, top.height + 26 + ph.height), (255, 255, 255)); out.paste(top, (0, 0)); out.paste(ph, (M, top.height + 26))
out.save(HERE + '/article-with-photo.jpg', quality=95); print(out.size)
