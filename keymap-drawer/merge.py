"""Merge keymap-drawer's parsed layers into one urob-style picture.

Each layer gets a place on the key and a colour (set in keymap_drawer.config.yaml):
the base layer in the middle, the others in the corners. The key that turns a layer on
is drawn in that layer's colour, so the keyboard explains itself. Layers reached by
holding two layer keys together are shown in a small panel between the halves.
Combos are drawn on an empty keyboard below.

    python keymap-drawer/merge.py keymap-drawer/corne-layers.yaml > keymap-drawer/corne.yaml
    keymap draw ... > keymap-drawer/corne.svg
    python keymap-drawer/merge.py panel keymap-drawer/corne.svg
"""
import re
import sys

import yaml

BASE = "Base"
# layer -> where its legend goes on each key (and so its colour)
PLACES = {"System": "tl", "Symbols": "tr", "NavNum": "bl", "Extra": "br"}
# Shown only in the layer-combo panel (its keys are in corne-layers.svg).
PANEL_ONLY = {"NOR": "å ø æ"}
# Layers you get by holding two layers together (mo 3 on both NavNum and Symbols; the
# conditional layer Symbols + Extra -> NOR). Update if the keymap changes.
LAYER_COMBOS = [(["NavNum", "Symbols"], "System"), (["Symbols", "Extra"], "NOR")]
# Thumb keys (Corne: the last six) are layer keys; corner legends there only add clutter.
THUMBS = 6


def tap(key):
    """The main legend of a parsed key ('' for transparent or empty keys)."""
    if key is None:
        return ""
    if isinstance(key, str):
        return key
    if key.get("type") in ("trans", "held"):
        return ""
    return str(key.get("t", ""))


def add_type(key, cls):
    key["type"] = f"{key['type']} {cls}" if key.get("type") else cls


def main(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    layers = data["layers"]
    base = layers[BASE]
    merged = []
    for i, key in enumerate(base):
        out = dict(key) if isinstance(key, dict) else {"t": key}
        own = tap(key)
        # The key that turns a layer on gets that layer's colour.
        if own in PLACES:
            add_type(out, f"lt-{PLACES[own]}")
        if out.get("h") in PLACES:
            add_type(out, f"lh-{PLACES[out['h']]}")
        if i < len(base) - THUMBS:
            for name, place in PLACES.items():
                other = layers.get(name)
                if other is None or i >= len(other):
                    continue
                legend = tap(other[i])
                if legend and legend != own:
                    out[place] = legend
        merged.append(out)
    blank = [{"t": "", "type": "blank"} for _ in base]
    data["layers"] = {"Layers": merged, "Combos": blank}
    for combo in data.get("combos", []):
        combo["l"] = ["Combos"]
    yaml.safe_dump(data, sys.stdout, allow_unicode=True, sort_keys=False, width=1000)


def panel(svg_path, w=176, top=58):
    """Draw the layer-combo panel between the halves (that gap is empty on a Corne)."""
    with open(svg_path, encoding="utf-8") as f:
        svg = f.read()
    width = float(re.search(r'<svg[^>]*width="([0-9.]+)"', svg).group(1))
    cx = width / 2
    line = 19
    rows = []
    for parts, result in LAYER_COMBOS:
        held = ' <tspan class="panel">+</tspan> '.join(
            f'<tspan class="c-{PLACES[p]}">{p}</tspan>' for p in parts
        )
        rows.append(f'<tspan class="panel">hold </tspan>{held}')
        if result in PLACES:
            res = f'<tspan class="c-{PLACES[result]}">{result}</tspan>'
        else:
            res = f'<tspan class="c-s">{result}</tspan><tspan class="panel"> ({PANEL_ONLY.get(result, "")})</tspan>'
        rows.append(f'<tspan class="panel">→ </tspan>{res}')
    h = 44 + line * len(rows) + 8 * (len(LAYER_COMBOS) - 1)
    out = [
        f'<rect rx="10" ry="10" x="{cx - w / 2}" y="{top}" width="{w}" height="{h}" class="panel"/>',
        f'<text x="{cx}" y="{top + 20}" class="panel-title">LAYER COMBOS</text>',
    ]
    y = top + 44
    for n, r in enumerate(rows):
        out.append(f'<text x="{cx}" y="{y}" class="panel">{r}</text>')
        y += line + (8 if n % 2 else 0)
    svg = svg.replace("</svg>", '<g class="layer-combos">' + "".join(out) + "</g>\n</svg>")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    if sys.argv[1] == "panel":
        panel(sys.argv[2])
    else:
        main(sys.argv[1])
