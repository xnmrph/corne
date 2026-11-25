"""Merge keymap-drawer's parsed layers into one urob-style picture.

The base layer stays in the middle of each key; other layers go in the corners
(see CORNERS). Combos are drawn on a second, empty keyboard below.

    python keymap-drawer/merge.py keymap-drawer/corne-layers.yaml > keymap-drawer/corne.yaml
"""
import sys

import yaml

BASE = "Base"
# corner -> layer (rename here if you rename a layer in the keymap)
CORNERS = {"tl": "System", "tr": "Symbols", "bl": "NavNum", "br": "Extra"}
# Thumb keys (Corne: the last six) are layer keys; corners there only add clutter.
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


def main(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    layers = data["layers"]
    base = layers[BASE]
    merged = []
    for i, key in enumerate(base):
        out = dict(key) if isinstance(key, dict) else {"t": key}
        own = tap(key)
        if i >= len(base) - THUMBS:
            merged.append(out)
            continue
        for corner, name in CORNERS.items():
            other = layers.get(name)
            if other is None or i >= len(other):
                continue
            legend = tap(other[i])
            if legend and legend != own:
                out[corner] = legend
        merged.append(out)
    blank = [{"t": "", "type": "blank"} for _ in base]
    data["layers"] = {"Layers": merged, "Combos": blank}
    # Explain the corners under the picture.
    marks = {"tl": "◤", "tr": "◥", "bl": "◣", "br": "◢"}
    key = "  ".join(f"{marks[c]} {n}" for c, n in CORNERS.items())
    data["draw_config"] = {"footer_text": f"xnmrph/corne · corners: {key} · drawn with keymap-drawer"}
    for combo in data.get("combos", []):
        combo["l"] = ["Combos"]
    yaml.safe_dump(data, sys.stdout, allow_unicode=True, sort_keys=False, width=1000)


if __name__ == "__main__":
    main(sys.argv[1])
