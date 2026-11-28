# nice!view pictures

Made with mxKeys. Left half: a picture in the art area (left.gif). Right half: a picture in the art area (right.gif).

The originals are in `source/`, the settings in `mxkeys.json`. `src/frames.c` is generated —
change the pictures in mxKeys (or delete this folder and the `cmake`/`kconfig` lines in
`zephyr/module.yml` to go back to the stock screen). Turn the pictures off without
deleting anything with `CONFIG_MXKEYS_NICE_VIEW_ART=n` in your `.conf`.
