import cv2 as cv
import numpy as np
import numpy.fft as npfft
import tkinter as tk
import os
class Char:
  def __init__(self, name, path, threshold, rep):
    self.name = name
    self.rep = rep
    self.pixel_pattern = image_to_array(path)
    self.locations = []
    self.threshold = threshold
  def __repr__(self):
    return self.rep
  def find_locations(self, data_path, rotate):
    data_pixels = image_to_array(data_path, rotate)
    pattern_shape = self.pixel_pattern.shape
    pattern_pixels = pad_pattern(data_pixels.shape, self.pixel_pattern)


    fft_data = npfft.fft2(data_pixels)
    fft_pattern = npfft.fft2(np.flipud(np.fliplr(pattern_pixels)))

    result = npfft.ifft2(fft_data * fft_pattern).real
    matches = np.where(result/np.max(result) >= self.threshold)
  
    pairs = tuple(zip(*matches))
    h, w = data_pixels.shape
    for y, x in pairs:
      x_center = x + int(pattern_shape[1] / 2)
      y_center = y + int(pattern_shape[0] / 2)
      if 0 <= y_center < h and 0 <= x_center < w:
          self.locations.append((x_center, y_center, result[y][x]))
    
  def draw(self, data_path, new_window = False):
    image = cv.imread(data_path)
    for x, y, _ in self.locations:
      image = cv.circle(image, (x, y), radius=3, color=(0, 0, 255), thickness=-1)
    cv.imwrite("utils/patterns/" + self.name + ".png", image)
    if new_window:
      cv.imshow("utils/patterns/" + self.name + ".png", image)
      cv.waitKey(0)
      cv.destroyWindow("utils/patterns/" + self.name + ".png")
    
 
def image_to_array(path, rotate=0, shift = True):
  """
  Make a grayscale array from the path to an image

  Args:
    path (str): path to an image
    shift (bool): should colors be inverted
  Returns:
    out (list[list[int]]): a 2D array that contains grayscale value of each pixel
  """
  img = cv.imread(path, cv.IMREAD_GRAYSCALE)
  img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv.THRESH_BINARY, blockSize=11, C=2)
  if shift:
      img = 255 - img
  img = img.astype(np.float64)
  
  if rotate != 0:
      angle = np.degrees(rotate)
      h, w = img.shape
      center = (w // 2, h // 2)
      rot_matrix = cv.getRotationMatrix2D(center, angle, 1.0)
      img = cv.warpAffine(img, rot_matrix, (w, h), flags=cv.INTER_LINEAR, borderValue=255)

  return img

def pad_pattern(shape, pattern):
  """
  Add 0 padding to pattern array to match shape of data

  Args:
    shape (tuple[int, int]): shape of data
    pattern (list[list[int]]): a 2D array that contains grayscale value of each pixel in pattern
  Returns:
    out (list[list[int]]): a 2D array that contains grayscale value of each pixel
  """
  ph, pw = pattern.shape
  sh, sw = shape

  # Resize pattern if it's too large
  if ph > sh or pw > sw:
      scale_y = min(1.0, sh / ph)
      scale_x = min(1.0, sw / pw)
      scale = min(scale_y, scale_x)
      new_size = (int(pw * scale), int(ph * scale))
      pattern = cv.resize(pattern, new_size, interpolation=cv.INTER_AREA)
      ph, pw = pattern.shape

  result = np.zeros(shape)
  result[:ph, :pw] = pattern
  return result

def count_chars(string):
  chars = {}
  for c in string:
    if c in list(chars.keys()):
      chars[c] += 1
    else:
      chars[c] = 1
  return chars

def main(path = "utils/tests/ewangelia.png", fontname="arial", chars = ["lower", "special"], rotate = 0): 
  lower_chars = {  
          'lower_a': (0.9, "a"),
          'lower_b': (0.9, "b"),
          'lower_c': (0.85, "c"),
          'lower_d': (0.9, "d"),
          'lower_e': (0.8, "e"),
          'lower_f': (0.9, "f"),
          'lower_g': (0.9, "g"),
          'lower_h': (0.99, "h"),
          'lower_i': (0.999, "i"),
          'lower_j': (0.9, "j"),
          'lower_k': (0.9, "k"),
          'lower_l': (0.999, "l"),
          'lower_m': (0.9, "m"),
          'lower_n': (0.95, "n"),
          'lower_o': (0.85, "o"),
          'lower_p': (0.9, "p"),
          'lower_q': (0.9, "q"),
          'lower_r': (0.999, "r"),
          'lower_s': (0.85, "s"),
          'lower_t': (0.87, "t"),
          'lower_u': (0.8, "u"),
          'lower_v': (0.9, "v"),
          'lower_w': (0.85, "w"),
          'lower_x': (0.9, "x"),
          'lower_y': (0.8, "y"),
          'lower_z': (0.9, "z")
  }
  
  if "polish" in chars:
    lower_chars.pop("lower_x")
    lower_chars.pop("lower_v")
    lower_chars.pop("lower_q")

  special = {
          "comma": (1, ","),
          "dot": (1, "."),
          "exclamation_mark": (1, "!"),
          "question_mark": (1, "?"),
          "0": (1, "0"),
          "1": (1, "1"),
          "2": (1, "2"),
          "3": (1, "3"),
          "4": (1, "4"),
          "5": (1, "5"),
          "6": (1, "6"),
          "7": (1, "7"),
          "8": (1, "8"),
          "9": (1, "9"),
  }

  def char_locations_to_string(
    char_locations,
    image_height,
    image_width,
    x_radius,
    y_radius,
    whitespace_width,
    alpha,
    ):
    # Making one line truly one line
    letters_in_line = [0]*image_height
    for x, y, *_ in char_locations:
        letters_in_line[y] += 1
    lines_by_letters = sorted(((i, num_of_letters) for i, num_of_letters in enumerate(letters_in_line)), key= lambda x: x[1], reverse=True)

    true_line = [i for i in range(image_height)]
    for y, _ in lines_by_letters:
        if true_line[y] != y or letters_in_line[y] < alpha * lines_by_letters[0][1]:
            continue
        for dy in range(-y_radius, y_radius + 1):
            if dy != 0 and 0 <= y + dy < image_height:
                letters_in_line[y] += letters_in_line[y + dy]
                letters_in_line[dy] = 0
                true_line[y + dy] = y

    old_locations = char_locations
    line_content = {}
    for (x, old_y, score, char) in old_locations:
        y = true_line[old_y]
        new_record = (y, x), (char, score)
        if y not in line_content:
            line_content[y] = [new_record]
        else:
            line_content[y].append(new_record)

    # Remove multiple characters
    chars_by_line = []
    for y in sorted(list(line_content.keys())):
        # line_content[y].sort(key=lambda x: x[1])
        is_free = [True for _ in range(image_width)]
        letters_by_score = sorted(line_content[y], key=lambda x: x[1][1], reverse=True)
        remaining_letters = []
        for (y, x), char_score in letters_by_score:
            if is_free[x]:
                remaining_letters.append(((y, x), char_score))
                for dx in range(-x_radius, x_radius + 1):
                    if 0 <= x + dx < image_width:
                        is_free[x + dx] = False
        chars_by_line.append(sorted(remaining_letters, key=lambda x: x[0][1]))

    result = ""
    for line in chars_by_line:
        prev_x = None
        for (_, x), (char, _) in line:
            if prev_x is not None:
                result += " " * (round((x - prev_x) / whitespace_width) - 1)
            result += char
            prev_x = x
        result += "\n"
    return result

  characters = []
  if "lower" in chars:
    for name, (a, rep) in list(lower_chars.items()):
      character = Char(name, f"utils/characters/{fontname}/{name}.png", a, rep)
      character.find_locations(path, rotate)
      characters.append(character)
      character.draw(path, False)

  if "special" in chars:
    for name, (a, rep) in list(special.items()):
      character = Char(name, f"utils/characters/{fontname}/{name}.png", a, rep)
      character.find_locations(path, rotate)
      characters.append(character)
      character.draw(path, False)
  

  all_locations = sorted(((*location, character.rep) for character in characters for location in character.locations), key= lambda x: x[2], reverse=True)
  res = char_locations_to_string(all_locations, *(image_to_array(path, rotate).shape), 5, 9, 9, 0.3)
  
  arr = path.split("/")
  name = arr[-1].removesuffix(".png")
  

  with open(f"utils/result/{font}/{name}.txt", "w+") as file:
    file.write(res + "\n" + str(count_chars(res)))

  print(res)
  print(count_chars(res))

font = "arial" # lub rockwell
name = "J1512"
main(f"utils/tests/{font}/{name}.png", font, ["lower", "special", "polish"], 0) #0.013 max ://


