#!/usr/bin/env python

import math
import pyclipper
import sys
from copy import deepcopy as objcopy

# Set some initial and default settings
style = {"stroke":"black", "fill":"green", "fill-opacity":"1", "stroke-opacity":"1"}
z = 0
clipper_scale = 1000


def convert_style(style_dict):
    """ Converts a dictionary which contains style settings into a string suitable for use in SVG. """
    style_text = ""
    for d in style_dict:
        style_text += "%s=\"%s\" "%(d,style_dict[d])
    return style_text

def zorder():
    """ Increments then returns the global variable z, for use in z-ordering shapes. """
    global z
    z += 1
    return z

class Drawable(object):
    def svg(self):
        return "<!--- unimplemented shape --->"
    def copy_style(self, other_shape):
        self.style = other_shape.style
        self.z = other_shape.z
    def copy_attributes(self, other_shape):
        self.ref_x = other_shape.ref_x
        self.ref_y = other_shape.ref_y
        self.copy_style(other_shape)

class Polygon(Drawable):
    def __init__(self, pointsets):
        self.pointsets = pointsets
        self.ref_x = 0
        self.ref_y = 0
        self.z = zorder()
        self.style = objcopy(style)
    def svg(self):
        path = "<path d=\""
        for paths in self.pointsets:
            c = paths[0]
            path += "M %f %f "%(c[0]+self.ref_x,c[1]+self.ref_y)
            for c in paths[1:]:
                path += "L %f %f "%(c[0]+self.ref_x,c[1]+self.ref_y)
            path += "z "
        path += "\" fill-rule=\"evenodd\" "+convert_style(self.style)+ "/>"
        return path

class Circle(Drawable):
    def __init__(self, x, y, radius):
        self.ref_x = x;
        self.ref_y = y;
        self.radius = radius;
        self.z = zorder()
        self.style = objcopy(style)
    def svg(self):
        circle = '<circle cx="%d" cy="%d" r="%d" %s />'%(self.ref_x, self.ref_y, self.radius, convert_style(self.style))
        return circle
    def to_polygon(self):
        fn = 20
        points = []
        for step in range(0,fn):
            angle = step*math.pi*2.0/(fn)
            points.append([self.ref_x + self.radius*math.cos(angle), self.ref_y+self.radius*math.sin(angle)])
        p = Polygon([points])
        p.copy_style(self)
        return p

class Rect(Polygon):
    def __init__(self, x, y, width, height):
        self.pointsets = [[[x,y],[x+width,y],[x+width,y+height],[x,y+height]]]
        self.ref_x = x;
        self.ref_y = y;
        self.z = zorder()
        self.style = objcopy(style)

Rectangle = Rect

def translation(obj, x, y):
    """ Returns a copy of the original object translated by (x,y) """
    d = objcopy(obj)
    d.ref_x += x
    d.ref_y += y
    return d

def copy(obj, x, y):
    """ Returns a copy of the original object translated by (x,y) """
    return translation(obj, x,y)

def move(obj, x, y):
    """ Moves an object by (x,y) without making a copy. """
    obj.ref_x += x
    obj.ref_y += y

def deep_tuple(l):
    """ Convert lists of lists of lists (...) into tuples of tuples of tuples, and so on. """
    if type(l) != list: return l
    return tuple(deep_tuple(a) for a in l)

def scale_poly(poly, scale):
    """Converts polygons and lists of polygons by scaling their
       coordinates. Works recursively on lists of polygons."""
    if type(poly) != list: return poly*scale
    return list(scale_poly(p, scale) for p in poly)

def subtract(x, y):
    """ Binary geometry - cuts out the object y from the polygon object x.
        If y is not a polygon, it will attempt to convert it to a
        polygon which approximates it, using that object's to_polygon
        method.
    """
    if isinstance(y,Drawable) and not isinstance(y,Polygon):
        y = y.to_polygon()
    pc = pyclipper.Pyclipper()
    a = deep_tuple(scale_poly(x.pointsets, clipper_scale))
    b = deep_tuple(scale_poly(y.pointsets, clipper_scale))

    print"<!--Clipping %s -->"%(repr(a))
    print"<!--Clipping %s -->"%(repr(b))


    pc.AddPath(a[0], pyclipper.PT_SUBJECT, True)
    pc.AddPath(b[0], pyclipper.PT_CLIP, True)
    result = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    new_p = Polygon(scale_poly(result, 1.0/clipper_scale))
    new_p.copy_attributes(x)
    return new_p

def add(start, *args):
    """ Binary geometry - union all shapes together.
        If any shape is not a polygon, it will attempt to convert it to a
        polygon which approximates it, using that object's to_polygon
        method.
    """
    if isinstance(start,Drawable) and not isinstance(start,Polygon):
        start = start.to_polygon()
    print("<!-- starting object is %s -->"%(repr(start)))
    a = deep_tuple(scale_poly(start.pointsets, clipper_scale))
    for addition in args:
        if isinstance(addition,Drawable) and not isinstance(addition,Polygon):
            addition = addition.to_polygon()
        pc = pyclipper.Pyclipper()
        b = deep_tuple(scale_poly(addition.pointsets, clipper_scale))

        print"<!--Clipping %s -->"%(repr(a))
        print"<!--Clipping %s -->"%(repr(b))
        print("<!-- addding is %s -->"%(repr(b)))


        pc.AddPath(a[0], pyclipper.PT_SUBJECT, True)
        pc.AddPath(b[0], pyclipper.PT_CLIP, True)
        a = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    new_p = Polygon(scale_poly(a, 1.0/clipper_scale))
    new_p.copy_attributes(start)
    return new_p

def setstyle(**kwargs):
    """ Set any number of style arguments in the global style variable.
        Because 'fill-opacity' cannot be an argument name, underscores
        will be converted to hyphens here. """
    global style
    for x in kwargs:
        style[x.replace('_','-')] = kwargs[x]

def usage():
    print("Usage: %s <script file>"%sys.argv[0])

def main():
    if len(sys.argv) != 2:
        usage()
        return

    input_filename = sys.argv[1]
    with open(input_filename, "rt") as f:
        code = "\n".join(f.readlines())
    locals = dict()
    globs = globals()
    exec(code, globs, locals)
    print "<svg width=\"297\" height=\"210\" viewPort=\"0 0 297 210\" >"
    for l in locals:
        print "<!-- %s -->"%l
        if l[0] != "_" and isinstance(locals[l], Drawable):
            print locals[l].svg()
    print "</svg>"

if __name__=="__main__": main()
