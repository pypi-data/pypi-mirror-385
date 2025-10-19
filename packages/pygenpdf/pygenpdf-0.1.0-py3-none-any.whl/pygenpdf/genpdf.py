#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pygenpdf

"""
__author__ = ['numael.garay']

import json
import subprocess
import os
import tempfile

import pygenpdf_json

timeout=5 * 60
DIR_GENPDF_JSON_BIN = "genpdf-json-bin"


__all__ = ["Document", "VerticalLayout","TableLayout", "HorizontalLayout", "UnorderedList", "OrderedList",
           "Paragraph", "Text", "Image",  "PageBreak", "Break",
           "FramedElement","PaddedElement", "StyledElement" ,
           "Color", "LineStyle", "Margins", "Size", "StyledString", "FrameCellDecorator", "Alignment", "Style"]
            

class Document:
    def __init__(self):
        self.genpdf_library = "lib" # lib or console genpdf-json-bin
        self.dict_doc = {
            "config":{
                "title":"", 
                "style":{}, 
                "page_size": "A4", 
                "fonts" : [],
                "default_font":{"font_family_name":"LiberationSans",  "dir":"/usr/share/fonts/truetype/liberation"}
            },        
            "elements": [],
            
        }
        
    def set_default_font(self, _dir, font_name):
        if type(_dir) is not str or type(font_name) is not str:
            raise ValueError("expected a str")        
        self.dict_doc["config"]["default_font"] = {"font_family_name":font_name,  "dir":_dir}
    
    def add_font(self, _dir, font_name):
        if type(_dir) is not str or type(font_name) is not str:
            raise ValueError("expected a str")
        self.dict_doc["config"]["fonts"].append({"font_family_name":font_name,  "dir":_dir})
        
    def set_margins(self, margins):
        if type(margins) is not Margins:
            raise ValueError("expected a Margins")
        self.dict_doc["config"]["margins"] = margins.get_data()
    
    def set_head_page(self, head_page):
        if type(head_page) is not Paragraph:
            raise ValueError("expected a Paragraph")
        self.dict_doc["config"]["head_page"] = head_page.get_data()
    
    def set_head_page_count(self, head_page_count):
        if type(head_page_count) is not Paragraph:
            raise ValueError("expected a Paragraph")
        self.dict_doc["config"]["head_page_count"] = head_page_count.get_data()
    
    def set_title(self, title):
        if type(title) is not str:
            raise ValueError("expected a str")
        self.dict_doc["config"]["title"] = title
    
    def set_paper_size(self, size):
        if type(size) is not Size:
            raise ValueError("expected a Size")
        self.dict_doc["config"]["page_size"] = size.get_data()
    
    def set_line_spacing(self, line_spacing):
        if type(line_spacing) not in [float, int]:
            raise ValueError("expected a float or int")
        self.dict_doc["config"]["line_spacing"] = float(line_spacing)
    
    def set_font_size(self, font_size):
        if type(font_size) is not int:
            raise ValueError("expected a int")
        self.dict_doc["config"]["deafault_font_size"] = font_size
    
    def set_creation_date(self, date):
        pass
    
    def set_modification_date(self, date):
        pass
       
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_doc["elements"].append(element.get_data())
    
    def use_genpdf_json_bin(self, path = ""):
        if path:
            global DIR_GENPDF_JSON_BIN
            DIR_GENPDF_JSON_BIN = path
        self.genpdf_library = "console"
        
    def render_json_file(self, out_path):
        sjson = json.dumps(self.dict_doc)
        dtemp = tempfile.mkdtemp(prefix='genpdf_')
        path_json = os.path.join(dtemp, "_json_.json")
        with open(path_json, "w") as archivo:
            archivo.write(sjson)
            
        if self.genpdf_library == "lib":                
            pygenpdf_json.render_json_file(path_json, out_path)            
        else:            
            cmd = [DIR_GENPDF_JSON_BIN, path_json, out_path] 
            subprocess.check_call(cmd, timeout=timeout)
    
    def render_json_base64(self):
        if self.genpdf_library == "console":
            raise ValueError("not implemented console base64")
        else:
            return pygenpdf_json.render_json_base64(json.dumps(self.dict_doc))
        
        
class BaseElement:
    def __init__(self):
        self.dict_element = {}
    
    def set_frame(self, line_style):
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        self.dict_element["frame"] = line_style.get_data()
        
    def framed(self, line_style):
        self.set_frame(line_style)
        return self
    
    def set_style(self, style):
        if type(style) is not Style:
            raise ValueError("expected a Style")
        self.dict_element["style"] = style.get_data()
        
    def styled(self, style):
        self.set_style(style)
        return self
        
    def set_padding(self, padding):
        self.dict_element["padding"] = padding.get_data()
    
    def padded(self, padding):
        if type(padding) not in [float, int, Margins]:
            raise ValueError("expected a float, int or Margins")
        if type(padding) in [float, int]:
            self.set_padding(Margins(top=padding, right=padding, bottom=padding, left=padding))
        elif type(padding) is Margins:
            self.set_padding(padding)
        return self
    
    def get_data(self):
        return self.dict_element
    
    
class Break:
    def __init__(self, value):
        if type(value) not in [float, int]:
            raise ValueError("expected a float or int")
        self.dict_element = {"type" : "break", "value": value}
        
    def get_data(self):
        return self.dict_element


class PageBreak:
    def __init__(self):
        self.dict_element = {"type" : "page_break"}
        
    def get_data(self):
        return self.dict_element
        
        
class Image(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "image"}
        
    def from_path(self, path):
        if type(path) is not str:
            raise ValueError("expected str")
        self.dict_element["path"] = path
        return self
        
    def from_base64(self, str_base64):
        if type(str_base64) is not str:
            raise ValueError("expected str")
        self.dict_element["base64"] = str_base64
        return self
        
    def set_position(self, pos_x, pos_y):
        if type(pos_x) not in [float, int] or type(pos_y) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["position"] = [float(pos_x), float(pos_y)]
    
    def with_position(self, pos_x, pos_y):
        self.set_position(pos_x, pos_y)
        return self
    
    def set_scale(self, scale):
        if type(scale) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["scale"] = abs(float(scale))
    
    def set_style(self, style):
        pass
    
    def with_scale(self, scale):
        self.set_scale(scale)
        return self
        
    def set_alignment(self, alignment):
        if type(alignment) is not str:
            raise ValueError("expected str")
        if alignment not in Alignment.get_values():
            raise ValueError("expected Alignment values")
        self.dict_element["alignment"] = alignment
    
    def aligned(self, alignment):
        self.set_alignment(alignment)
        return self
    
    def set_clockwise_rotation(self, rotation):
        if type(rotation) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["rotation"] = rotation        
    
    def with_clockwise_rotation(self, rotation):
        self.set_clockwise_rotation(rotation)
        return self
    
    def set_dpi(self, dpi):
        if type(dpi) not in [float, int]:
            raise ValueError("expected float or int")
        self.dict_element["dpi"] = dpi    
    
    def with_dpi(self, dpi):
        self.set_dpi(dpi)
        return self

    
class VerticalLayout(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "layout", "orientation":"vertical", "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())    
    
    def element(self, element):
        self.push(element)
        return self

class FrameCellDecorator:
    def __init__(self, inner=False, outer=False, cont=False):
        if type(inner) is not bool or type(outer) is not bool or type(cont) is not bool:
            raise ValueError("expected a bool" )
        self.list_fcell = [inner, outer, cont]
        self.line_style = None
    
    def with_line_style(self, inner, outer, cont, line_style):
        if type(inner) is not bool or type(outer) is not bool or type(cont) is not bool:
            raise ValueError("expected a bool" )
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        self.list_fcell = [inner, outer, cont]
        self.line_style = line_style
        return self
    
    def get_data(self):
        return [self.list_fcell, self.line_style]


class TableLayout(BaseElement):
    def __init__(self, column_weights):
        if type(column_weights) is not list:
            raise ValueError("expected a list")
        self.column_weights = column_weights
        self.dict_element = {"type" : "table_layout", "rows":[], "column_weights": column_weights}
    
    def push_row(self, row):
        if type(row) is not list:
            raise ValueError("expected a list the elements")
        row_data = [x.get_data() for x in row]        
        if len(row_data) != len(self.column_weights):
            raise ValueError("The row count is different from the column count" )
        self.dict_element["rows"].append(row_data)
        
    def set_cell_decorator(self, cell_decorator):
        if type(cell_decorator) is not FrameCellDecorator:
            raise ValueError("expected a FrameCellDecorator")
        list_fcell, line_style = cell_decorator.get_data()
        self.dict_element["frame_decorator"] = list_fcell
        if line_style:
            self.set_frame(line_style)

## HorizontalLayout adaptacion de TableLayout con un solo row, por conveniencia de nombre, en genpdf-js no existe
class HorizontalLayout(BaseElement):
    def __init__(self, column_weights):
        if type(column_weights) is not list:
            raise ValueError("expected a list column weights")
        self.column_weights = column_weights
        self.dict_element = {"type" : "layout", "orientation":"horizontal", 
                             "column_weights": column_weights, "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if len(self.column_weights) == len(self.dict_element["elements"]):
            raise ValueError("element cannot be added, because it exceeds column_weights")
        self.dict_element["elements"].append(element.get_data())   
    
    def get_data(self):
        d = len(self.column_weights) - len(self.dict_element["elements"])
        if d > 0:
            fix_row = self.dict_element["elements"] + [{"type":"paragraph", "value":[{"text":""}]} for x in range(d)]
            self.dict_element["elements"] = fix_row   
        return self.dict_element
    
class UnorderedList(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "unordered_list", "elements":[]}
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())
    
    def with_bullet(self, bullet):
        if type(bullet) not in [str]:
            raise ValueError("expected str")
        self.dict_element["bullet"] = bullet
    
    def element(self, element):
        self.push(element)
        return self
        
class OrderedList(BaseElement):
    def __init__(self):
        self.dict_element = {"type" : "ordered_list", "elements":[]}
        # self.with_start(1)
    
    def push(self, element):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        self.dict_element["elements"].append(element.get_data())   
    
    def with_start(self, start):
        if type(start) not in [int]:
            raise ValueError("expected int")
        self.dict_element["start"] = start
    
    def element(self, element):
        self.push(element)
        return self
        
# Wrappers
class FramedElement:
    def __init__(self, element, line_style):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(line_style) is not LineStyle:
            raise ValueError("expected a LineStyle" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
        
        element.set_frame(line_style)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()
    
class PaddedElement:
    def __init__(self, element, margins):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(margins) is not Margins:
            raise ValueError("expected a margins" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
        
        element.set_padding(margins)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()

class StyledElement:
    def __init__(self, element, style):
        if type(element) not in ELEMENTS:
            raise ValueError("unknown element")
        if type(style) is not Style:
            raise ValueError("expected a Style" )
        if type(element) in [FramedElement, PaddedElement, StyledElement]:
            element = element.element
            
        element.set_style(style)
        self.element = element
        
    def get_data(self):
        return self.element.get_data()

class Paragraph(BaseElement):
    def __init__(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style, Style())            
        self.dict_element = {"type": "paragraph", "value":[string_style.get_data()]}                
    
    def set_alignment(self, alignment):
        if type(alignment) is not str:
            raise ValueError("expected str")
        if alignment not in Alignment.get_values():
            raise ValueError("expected Alignment values")
        self.dict_element["alignment"] = alignment
    
    def aligned(self, alignment):
        self.set_alignment(alignment)
        return self
    
    def push(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style)
        if not "value" in self.dict_element:
            self.dict_element["value"] = []
        self.dict_element["value"].append(string_style.get_data())
    
    def string(self, string_style):
        self.push(string_style)
        return self
    
    def push_styled(self, s, style):
        if type(s) is not StyledString:
            raise ValueError("expected a StyledString")
        if type(s) is not str:
            raise ValueError("expected a str")
        self.push(StyledString(s, style))        
    
    def styled_string(self, s, style):
        self.push_styled(s, style)
        return self
    
    def set_style(self, style):
        if type(style) is not Style:
            raise ValueError("expected a Style")
        if not "value" in self.dict_element:
            self.dict_element["value"] = [StyledString("",style).get_data()]
        else:
            last_index = len(self.dict_element["value"])-1
            last_value = self.dict_element["value"][last_index]
            self.dict_element["value"][last_index] = StyledString(last_value["text"], style).get_data()
    
    def set_bullet(self, bullet):
        if type(bullet) is not str:
            raise ValueError("expected a str")
        self.dict_element["bullet"] = bullet
    
    def with_bullet(self, bullet):
        self.set_bullet(bullet);
        return self
    
    def get_data(self):
        return self.dict_element

# a single line of text, not alignment
class Text(BaseElement):
    def __init__(self, string_style):
        if type(string_style) not in [str, StyledString]:
            raise ValueError("expected a str o StyledString")
        if type(string_style) is str:
            string_style = StyledString(string_style, Style()) 
        text = string_style.text
        style = string_style.style
        self.dict_element = {"type": "text", "value": text, "style":style}                
            
    def set_bullet(self, bullet):
        if type(bullet) is not str:
            raise ValueError("expected a str")
        self.dict_element["bullet"] = bullet
    
    def with_bullet(self, bullet):
        self.set_bullet(bullet);
        return self

    
class Margins:
    def __init__(self, top=0.1, right=0.1, bottom=0.1, left=0.1):
        self.list_padding = [top, right, bottom, left]            
    
    def trbl(self, top, right, bottom, left):
        self.list_padding = [top, right, bottom, left]
        return self
    
    def vh(self, vertical, horizontal):
        self.list_padding = [vertical, horizontal, vertical, horizontal]
        return self
    
    def all(self, padding):
        if type(padding) not in [float, int]:
            raise ValueError("expected a float or int")
        padding = float(padding)
        self.list_padding = [padding, padding, padding, padding]     
        return self
    
    def get_data(self):
        return self.list_padding


class Style:
    def __init__(self):
        self._bold = None
        self._size = None
        self._italic = None
        self._font_family = None
        self._color = None
        self._line_spacing = None
        self.dict_style={}
    
    def set_italic(self):
        self._italic = True
        
    def italic(self):
        self.set_italic()
        return self
    
    def set_bold(self):
        self._bold = True
        
    def bold(self):
        self.set_bold()
        return self
    
    def set_line_spacing(self, line_spacing):
        if type(line_spacing) not in [float, int]:
            raise ValueError("expected a float or int")
        self._line_spacing = float(line_spacing)
        
    def with_line_spacing(self, line_spacing):
        self.set_line_spacing(line_spacing)
        return self
    
    def set_font_size(self, font_size):
        if type(font_size) is not int:
            raise ValueError("expected a int")
        self._size = font_size
    
    def with_font_size(self, font_size):
        self.set_font_size(font_size)
        return self
    
    def set_font_family(self, font_family):
        if type(font_family) is not str:
            raise ValueError("expected a str")
        self._font_family = font_family
        
    def with_font_family(self, font_family):
        self.set_font_family(font_family)
        return self
    
    def set_color(self, color):
        if type(color) is not Color:
            raise ValueError("expected a Color")
        self._color = color.get_data()
        
    def with_color(self, color):
        self.set_color(color)
        return self
    
    def update_style(self):
        if self._bold:
            self.dict_style["bold"]=self._bold
        if self._size:
            self.dict_style["size"]=self._size
        if self._italic:
            self.dict_style["italic"]=self._italic
        if self._font_family:
            self.dict_style["font_family"]=self._font_family
        if self._color:
            self.dict_style["color"]=self._color
        if self._line_spacing:
            self.dict_style["line_spacing"]=self._line_spacing
            
    def get_data(self):
        self.update_style()
        return self.dict_style


class Color:
    def __init__(self):
        self._rgb = None
        self._cmyk = None
        self._greyscale = None        
        
    def min_max(self, x):
        if x < 0:
            return 0
        if x > 255:
            return 255
        return x
        
    #An RGB color with red, green and blue values between 0 and 255.
    def rgb(self, r, g, b):
        if type(r) is not int or type(g) is not int or type(b) is not int:
            raise ValueError("expected a int")
        self._rgb = [self.min_max(r), self.min_max(g), self.min_max(b)]
        return self
    
    #An CMYK color with cyan, magenta, yellow and key values between 0 and 255.
    def cmyk(self, c, m, y, k):
        if type(c) is not int or type(m) is not int or type(y) is not int or type(k) is not int:
            raise ValueError("expected a int")
        self._cmyk = [self.min_max(c), self.min_max(m), self.min_max(y), self.min_max(k)]
        return self
    
    #A greyscale color with a value between 0 and 255.
    def greyscale(self, g):
        if type(g) is not int:
            raise ValueError("expected a int")
        self._greyscale = self.min_max(g)
        return self
    
    def get_data(self):
        if self._rgb:
            return {"type":"rgb", "value":self._rgb}
        if self._cmyk:
            return {"type":"cmyk", "value":self._cmyk}
        if self._greyscale:
            return {"type":"greyscale", "value":self._greyscale}
        return {}


class StyledString:
    __name__ = "StyledString"
    def __init__(self, s="", style=Style()):
        self.text = {"text": s}
        try:
            self.style = style.get_data()
        except:
            self.style = {}
        self.dict_styled_string = {**self.text, **self.style}
    
    def get_data(self):
        return self.dict_styled_string


class Alignment:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    
    @classmethod
    def get_values(self):
        return ["left", "center", "right"]
    
    # @classmethod
    # def get_value(cls, name):
    #     return getattr(cls, name, None)       
class LineStyle:
    def __init__(self):
        self._thickness = 0.1
        self._color = None
        self.dict_line_style = {"thickness": self._thickness}
        
    def set_thickness(self, thickness):
        if type(thickness) not in [float, int]:
            raise ValueError("expected a float or int")
        self._thickness = float(thickness)
        self.dict_line_style["thickness"] = self._thickness
        
    def with_thickness(self, thickness):
        self.set_thickness(thickness)
        return self
    
    def set_color(self, color):
        if type(color) is not Color:
            raise ValueError("expected a type Color")
        self._color = color.get_data()
        self.dict_line_style["color"] = self._color
    
    def with_color(self, color):
        self.set_color(color)
        return self
    
    def get_data(self):
        return self.dict_line_style
    
class Size:
    def __init__(self, w = None, h = None):
        if w == None and h == None:
            self.size = "A4"
        else:
            if type(w) is not [int, float] or type(h) is not [int, float]:
                raise ValueError("expected a int or float")
            self.size = [abs(w), abs(h)]
    
    def A4(self):
        self.size = "A4"
        return self
    
    def Legal(self):
        self.size = "Legal"
        return self
        
    def Letter(self):
        self.size = "Letter"
        return self
        
    def get_data(self):
        return self.size
    
ELEMENTS = [VerticalLayout, HorizontalLayout, TableLayout, OrderedList, UnorderedList, 
            Paragraph, Image, Text, StyledElement, PaddedElement, FramedElement,
            PageBreak, Break]
