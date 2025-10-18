# from crosspt.third_party.models.t5 import T5LayerNorm
import os
import regex as re
import logging
from dataclasses import fields
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import hashlib
import sys
sys.path.append('..')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def str2int(s: str) -> int:
    # Encode the string to bytes
    encoded_string = s.encode()
    
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    
    # Update the hash object with the encoded string
    md5_hash.update(encoded_string)
    
    # Get the hexadecimal representation of the hash
    hex_digest = md5_hash.hexdigest()
    
    # Convert the hexadecimal digest to an integer
    unique_integer = int(hex_digest, 16)
    
    return unique_integer

##### My utils
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def isfloat(element: any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

def convert(val):
   if type(val) != str:
       return val 
   ret = val
   if val.lower() == "none": 
       ret= None 
   elif val.lower() == "false":
       ret = False
   elif val.lower() == "true":
       ret= True
   elif isfloat(val):
       if "." in val or "e" in val:
           ret = float(val)
       else:
           ret = int(val)
   elif val.isdigit():
       ret= int(val)
   return ret

def combine_x(images):
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height),(255, 255, 255))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    return new_im

def combine_y(images):
    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    max_height = sum(heights)

    new_im = Image.new('RGB', (total_width, max_height),(255, 255, 255) )

    y_offset = 0
    for im in images:
      new_im.paste(im, (0, y_offset))
      y_offset += im.size[1]

    return new_im

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

from itertools import chain, combinations, combinations_with_replacement

def all_nonempty_subsets_upto_l(iterable, l):
    return chain.from_iterable(combinations(iterable, r) for r in range(1, l+1))

def all_multisets_upto_l(iterable, l):
    return chain.from_iterable(combinations_with_replacement(iterable, r) for r in range(1, l+1))


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def strval(inp):
   if type(inp) != str:
      return inp
   if inp.startswith("%"): 
      return inp[1:]
   arr = []
   inp = str(inp)
   sep = "@" if "@" in inp else "+"
   vals = inp.split(sep)
   for val in vals:
       if not val:
           continue
       ret = convert(val)
       arr.append(ret)
   if len(arr) == 1 and not sep in inp:
       return arr[0]
   return arr

##### My utils end

def create_dir(output_dir):
    """
    Checks whether to the output_dir already exists and creates it if not.
    Args:
      output_dir: path to the output_dir
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def save_json(filepath, dictionary):
    with open(filepath, "w") as outfile:
        json.dump(dictionary, outfile)

def read_json(filepath):
    f = open(filepath,)
    return json.load(f)


def save_training_config(config_file, output_dir):
    json_data = read_json(config_file)
    save_json(os.path.join(output_dir, "training_config.json"), json_data)

