"""Frame 1 of the story as a 4:5 Instagram feed post (1080x1350)."""
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make.py')).read()
exec(src[:src.index('# 1 — photo + key line')])   # brand helpers + story constants
H = 1350


def post():
    ph = Image.open(PHOTO).convert('RGB').resize((W * S, 1920 * S), Image.LANCZOS)
    top = 250 * S                                      # keep heads in frame, crop mostly legs
    img = ph.crop((0, top, W * S, top + H * S))
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(H * S):
        t = y / (H * S)
        a = int(150 * max(0, 1 - t / 0.18)) + int(250 * min(1, max(0, (t - 0.42) / 0.24)) ** 1.2)
        od.line([(0, y), (W * S, y)], fill=DEEP + (min(a, 238),))
    img.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(img)
    logo(img, 180, W - M, 60, plate=True)
    y = quote_lines(d, '״זה לא מחבל בודד ולא פיגוע נקודתי, אלא איום רחב שהולך ומתעצם ועלול להסתיים באסון כבד.״', 86, 810)
    signature(d, y + 24)
    img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, 'yesha-post-gantz-1080x1350.png'))


post()
print('done')
