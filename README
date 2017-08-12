# diagram-script

This is an experimental system for creating illustrations from Python script. For example, the following script:

```
setstyle(stroke="black", fill="blue",stroke_width=1)
plate=Polygon([[[0,0], [60,0], [60,60], [0,60]], [[10,10], [50,10], [50,30], [30,30], [30,50], [10,50]]])
plate2=copy(plate, 61,0)
setstyle(fill="red")
a=Circle(20,20,5)
b=Circle(81,20,5)
setstyle(fill="green")
_pusher=Polygon([[[0,0], [50,0], [50,20], [0,20]]])
_hole1 = Circle(10,10,5)
pusher = subtract(_pusher, _hole1)
move(pusher, 61+61, 20)
```

... will produce this diagram:

![Example diagram output](example-output.svg)

# Intended use

This is intended to be used for people who need to make simple diagrams but prefer to write scripts rather than use a graphical user interface.

diagram-script is meant for illustrative diagrams. If you want to make CAD files, the excellent [OpenSCAD][http://www.openscad.org/] is better suited.

# Usage

This software is very experimental and not suitable for production use. All the input is run through python's 'exec' keyword, which means unknown input is a security risk, so please don't use it on input script which you didn't create yourself.

The following functions are implemented at the moment:

* Circle
* Polygon
* subtract
* setstyle
* copy
* move

Elements are written to the SVG output in the same order as they are listed in the script, so the first shape described in the script will be at the back, and the last shape described on top, the same way z-ordering worksin SVG.

# Requirements

This uses the [PyClipper][https://pypi.python.org/pypi/pyclipper] library to perform binary geometry, for example subtracting one shape from another.