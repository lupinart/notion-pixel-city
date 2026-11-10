"""Original pixel skyline. Python standard library only; no remote assets."""
import argparse
from datetime import datetime
from pathlib import Path
from random import Random
from zoneinfo import ZoneInfo
from heading_bitmap import ROWS as HEADING, YEAR_ROWS, FONT_FAMILY

TAIPEI = ZoneInfo('Asia/Taipei')
PALETTES = {
    'day': dict(sky=['#629dd8', '#72ace1', '#84bae7', '#9ccbeb', '#b7dbee', '#d1e9ee'],
                far='#8baac4', mid='#547b9c', front='#304f70', side='#233f5e',
                edge='#729ab8', off='#759ab4', on='#d6edf2', cloud='#f5f5e8', shade='#cfdfdf', text='#fff9e9'),
    'dusk': dict(sky=['#565d91', '#887297', '#b6869e', '#d49b9d', '#edb49e', '#f5c9a6'],
                 far='#aa8f9e', mid='#736c87', front='#494966', side='#383952',
                 edge='#968095', off='#696783', on='#ffd994', cloud='#f8d3be', shade='#ce9da6', text='#fff2d5'),
    'night': dict(sky=['#101d38', '#162644', '#1c304e', '#233a58', '#2c4562', '#38536c'],
                  far='#354c66', mid='#2c405b', front='#192e47', side='#12233b',
                  edge='#45607b', off='#29445f', on='#ffe0a0', cloud='#70879b', shade='#4d657d', text='#fff0cb'),
}
DIGITS = {
    '0': ['01110','11011','11011','11011','11011','11011','01110'],
    '1': ['00110','01110','00110','00110','00110','00110','01111'],
    '2': ['01110','11011','00011','00110','01100','11000','11111'],
    '3': ['11110','00011','00011','01110','00011','00011','11110'],
    '4': ['00011','00111','01111','11011','11111','00011','00011'],
    '5': ['11111','11000','11000','11110','00011','00011','11110'],
    '6': ['01110','11000','11000','11110','11011','11011','01110'],
    '7': ['11111','00011','00110','00110','01100','01100','01100'],
    '8': ['01110','11011','11011','01110','11011','11011','01110'],
    '9': ['01110','11011','11011','01111','00011','00011','01110'],
    '.': ['00000','00000','00000','00000','00000','00110','00110'],
    '-': ['00000','00000','00000','11111','00000','00000','00000'],
}


def taipei_time(stamp=None):
    if stamp is None:
        return datetime.now(TAIPEI)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=TAIPEI)
    return stamp.astimezone(TAIPEI)


def scene_for(stamp):
    hour = taipei_time(stamp).hour
    return 'day' if 6 <= hour < 17 else 'dusk' if 17 <= hour < 19 else 'night'


def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def pixel_text(text, size, y, fill, shadow):
    rows = ['0'.join(DIGITS[char][row] for char in text) for row in range(7)]
    return pixel_art(rows, size, y, fill, shadow)


def pixel_art(rows, size, y, fill, shadow):
    width = len(rows[0]) * size
    x = (1500 - width) // 2
    paths = []
    for row, cells in enumerate(rows):
        for col, cell in enumerate(cells):
            if cell == '1':
                px, py = x + col * size, y + row * size
                paths.append(f'M{px} {py}h{size}v{size}h-{size}z')
    path = ''.join(paths)
    return (f'<path d="{path}" fill="{shadow}" transform="translate({size} {size})"/>'
            f'<path d="{path}" fill="{fill}"/>')


def render(stamp=None, scene=None, *, cover=False):
    stamp = taipei_time(stamp)
    scene = scene or scene_for(stamp)
    if scene not in PALETTES:
        raise ValueError('Scene must be day, dusk or night')
    p = PALETTES[scene]
    width = 3600 if cover else 1500
    offset = (width - 1500) // 2
    rng = Random(2873)
    stars = Random(1110)
    lights = Random(stamp.date().toordinal())
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 600" '
         f'preserveAspectRatio="xMidYMid slice" shape-rendering="crispEdges" role="img" '
         f'aria-labelledby="title desc" data-scene="{scene}">',
         f'<title id="title">PAI任務管理 · 2026 · {scene} · generated {stamp:%Y-%m-%d}</title>',
         '<desc id="desc">PAI任務管理，2026。下方是台北101、北門與台北車站意象，雲與飛機緩慢移動。</desc>',
         f'<style>@keyframes drift{{from{{transform:translateX({-380-offset}px)}}to{{transform:translateX({1600+offset}px)}}}}'
         f'@keyframes flight{{from{{transform:translateX({1640+offset}px)}}to{{transform:translateX({-200-offset}px)}}}}'
         '@keyframes blink{0%,65%,100%{opacity:1}75%,85%{opacity:.15}}'
         '.cloud{animation:drift linear infinite}.plane{animation:flight 85s linear infinite;animation-delay:-31s}'
         '.beacon{animation:blink 5s steps(1) infinite}'
         '@media(prefers-reduced-motion:reduce){.cloud,.plane,.beacon{animation:none!important}}'
         '</style><defs><pattern id="dither" width="12" height="12" patternUnits="userSpaceOnUse">'
         '<path d="M0 0h6v6H0zM6 6h6v6H6z" fill="#ffffff" opacity=".12"/>'
         '</pattern></defs>']
    s.append(f'<g transform="translate({offset} 0)">')
    for i, color in enumerate(p['sky']):
        s.append(rect(-offset, i * 100, width, 100, color))
        if i:
            s.append(rect(-offset, i * 100 - 12, width, 24, 'url(#dither)'))
    if scene == 'night':
        for _ in range(65):
            x, y = stars.randrange(12-offset, 1490+offset, 6), stars.randrange(12, 325, 6)
            s.append(rect(x, y, 3, 3, '#d3e3eb', 'opacity=".65"'))
        s.append('<path d="M1170 48h36v12h12v48h-12v12h-36v-12h-12V60h12z" fill="#fff0c8"/>')
        s.append('<path d="M1194 42h24v18h12v36h-12v12h-24V96h-12V60h12z" fill="'+p['sky'][0]+'"/>')
    else:
        sun = '#fff0bd' if scene == 'day' else '#ffcf9d'
        sy = 70 if scene == 'day' else 245
        s.append(rect(1134, sy-12, 108, 108, sun, 'opacity=".12"'))
        s.append(f'<path d="M1158 {sy}h60v12h12v60h-12v12h-60v-12h-12v-60h12z" fill="{sun}"/>')
    cloud_path = 'M0 36h24V24h24V12h48V0h48v12h24v12h36v12h36v24H0z'
    for y, scale, speed, delay in [(92, 1, 170, -30), (108, .7, 230, -145), (45, .5, 290, -215)]:
        s.append(f'<g class="cloud" style="animation-duration:{speed}s;animation-delay:{delay}s" transform="translate(220 0)">'
                 f'<g transform="translate(0 {y}) scale({scale})"><path d="{cloud_path}" fill="{p["cloud"]}"/>'
                 f'<path d="M0 48h240v12H0zM24 36h24v12H24zM168 24h36v12h-36z" fill="{p["shade"]}"/></g></g>')
    s.append('<g class="plane" transform="translate(310 0)"><g transform="translate(0 105)">'
             '<path d="M0 12h30L48 0h12L48 12h42l12-12h12l-6 24H48l18 18H54L30 24H0z" fill="'+p['cloud']+'"/>'
             '<rect class="beacon" x="72" y="12" width="6" height="6" fill="#ef7f78"/></g></g>')
    # Keep ordinary buildings low; the taller 101 sits beside the date.
    s.append('<g id="city"><g id="skyline">')
    for layer, floor, start, color in [('far', 500, -24, p['far']), ('mid', 566, -40, p['mid']), ('front', 600, -54, p['front'])]:
        x = start - offset
        while x < 1500 + offset:
            w = rng.choice([60, 78, 96, 114])
            height = rng.randrange(48, 102, 6) if layer == 'far' else rng.randrange(72, 132, 6)
            if layer == 'front':
                height = rng.randrange(42, 90, 6)
            y = floor - height
            s.append(rect(x, y, w, height, color))
            s.append(rect(x+12, y-12, w-24, 12, color))
            if layer != 'far':
                s.append(rect(x+w-18, y, 18, height, p['side']))
                s.append(rect(x, y, w-18, 6, p['edge']))
                if rng.random() < .35:
                    s.append(rect(x+24, y-42, 6, 30, color))
                    s.append(rect(x+24, y-48, 6, 6, '#ef9b89', 'class="beacon"'))
                for wy in range(y+24, floor-12, 24):
                    for wx in range(x+12, x+w-24, 18):
                        lit = lights.random() < (.64 if scene == 'night' else .3 if scene == 'dusk' else 0)
                        s.append(rect(wx, wy, 6, 12, p['on'] if lit else p['off']))
            x += w + rng.choice([6, 12, 18])
    s.append('</g>')
    # A stylized Taipei montage, not a geographically accurate panorama.
    teal = {'day': '#3b7c86', 'dusk': '#526c7d', 'night': '#245260'}[scene]
    roof = {'day': '#746864', 'dusk': '#805f68', 'night': '#55566a'}[scene]
    brick = {'day': '#af7567', 'dusk': '#ac736e', 'night': '#755862'}[scene]
    warm = p['on'] if scene != 'day' else '#c8d8d4'
    # Taipei 101: narrow spire, eight stacked tapering sections, wide podium.
    s.append('<g id="taipei-101"><title>台北101意象</title>')
    s.append(rect(1167, 210, 6, 30, teal))
    s.append(rect(1158, 240, 24, 24, teal))
    for tier in range(8):
        y = 264 + tier * 36
        half = 24 + tier * 2
        s.append(f'<path d="M{1170-half} {y}h{half*2}l-6 28h-{half*2-12}z" fill="{teal}"/>')
        s.append(rect(1170-half, y, half*2, 3, p['edge']))
        for wx in range(1170-half+12, 1170+half-6, 12):
            s.append(rect(wx, y+7, 3, 14, warm))
    s.append(rect(1122, 552, 96, 48, teal))
    s.append(rect(1104, 576, 132, 24, teal))
    s.append('</g>')
    # North Gate: red masonry, raised swallowtail roof and a dark arched passage.
    s.append('<g id="north-gate"><title>北門意象</title>')
    s.append(rect(264, 546, 156, 54, brick))
    s.append(rect(288, 516, 108, 30, brick))
    s.append(f'<path d="M270 498h12v12h24v-6h72v6h24v-12h12v24H270z" fill="{roof}"/>')
    s.append(rect(276, 540, 132, 6, roof))
    s.append(f'<path d="M324 600v-30h6v-6h24v6h6v30z" fill="{p["side"]}"/>')
    for wx in [300, 324, 348, 372]:
        s.append(rect(wx, 525, 6, 9, warm))
    s.append('</g>')
    # Taipei Main Station: broad hall, layered hipped roof and repeated columns.
    s.append('<g id="taipei-station"><title>台北車站意象</title>')
    s.append(rect(612, 552, 300, 48, p['edge']))
    s.append(rect(660, 528, 204, 24, p['edge']))
    s.append(f'<path d="M678 504h168v6h12v6h18v12H648v-12h18v-6h12z" fill="{roof}"/>')
    s.append(f'<path d="M630 534h264v6h12v6h18v12H600v-12h18v-6h12z" fill="{roof}"/>')
    s.append(rect(624, 564, 276, 24, p['side']))
    for wx in range(636, 900, 24):
        s.append(rect(wx, 564, 12, 24, warm))
        s.append(rect(wx-6, 558, 6, 42, p['edge']))
    s.append('</g></g>')
    # Fixed pixel artwork: every lit cell is an SVG square, with no text/font nodes.
    s.append('<g id="date">')
    s.append(f'<g id="heading-text" role="img" aria-label="PAI任務管理" data-font="{FONT_FAMILY}">')
    s.append(pixel_art(HEADING, 10, 175, p['text'], p['side']))
    s.append('</g>')
    s.append('<g id="year" role="img" aria-label="2026">')
    s.append(pixel_art(YEAR_ROWS, 5, 298, p['text'], p['side']))
    s.append('</g>')
    s.append('</g></g></svg>')
    return '\n'.join(s)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--at', help='ISO date/time; no offset means Asia/Taipei')
    parser.add_argument('--out', type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    try:
        stamp = taipei_time(datetime.fromisoformat(args.at)) if args.at else taipei_time()
    except ValueError:
        parser.error('--at must be an ISO date/time, e.g. 2026-11-10T18:00:00+08:00')
    args.out.mkdir(parents=True, exist_ok=True)
    for scene in PALETTES:
        (args.out / f'{scene}.svg').write_text(render(stamp, scene), encoding='utf-8')
    (args.out / 'today.svg').write_text(render(stamp), encoding='utf-8')
    (args.out / 'cover.svg').write_text(render(stamp, cover=True), encoding='utf-8')
    print(f'{stamp.isoformat()}: generated day.svg, dusk.svg, night.svg, today.svg, cover.svg')


if __name__ == '__main__':
    main()
