import cv2 as cv
import numpy as np
import numpy.fft as npfft
class Char:
  """
  A class that represents a character

  Attributes
  ----------
  name: str
    name of the corresponding file in /utils/chars/{fontname}/
  path: str
    path to said file
  pixel_pattern: list[list[int]]
    values of pixels in the image
  locations: list[list[int, int, float]]
    coordinates and score of found pattern
  threshold: float
    threshold under it can be said pattern was found

  Methods
  -------
  find_locations(self, data_path, rotate)
    prepares self.locations

  draw(self, data_path, new_window = False)
    saves image of found locations to /utils/found_locations, can be shown in a pop-up window
  """
  def __init__(self, name, path, threshold, rep):
    self.name = name
    self.rep = rep
    self.pixel_pattern = image_to_array(path)
    self.locations = []
    self.threshold = threshold
  def __repr__(self):
    return self.rep
  def find_locations(self, data_path, rotate):
    """
    Loads data image and then uses DFT to assign found locations of a character

    Args:
      data_path (str): path to an image
      rotate (float): how much should the image be rotated
    Returns:
      out (list[list[int, int, float]]]): coordinates and score of found pattern
    """
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
    cv.imwrite("utils/found_locations/" + self.name + ".png", image)
    if new_window:
      cv.imshow("utils/found_locations/" + self.name + ".png", image)
      cv.waitKey(0)
      cv.destroyWindow("utils/found_locations/" + self.name + ".png")
    
 
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
  
  #noise removal
  img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv.THRESH_BINARY, blockSize=11, C=2)
  
  #background to black
  if shift:
      img = 255 - img
  
  img = img.astype(np.float64)
  
  #rotation
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

def main(path, fontname="arial", chars = ["lower", "special"], rotate = 0): 
  def init_chars(path = path, chars = chars, rotate = rotate):
    """
    Prepare an array of class Char elements

    Args:
      
    Returns:
      out (list[Char]): an array of class Char elements with found locations ready
    """
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
    
    # for scanning polish text its better to exclude these
    if "polish" in chars:
      lower_chars.pop("lower_x")
      lower_chars.pop("lower_v")
      lower_chars.pop("lower_q")

    special = {
      "comma": (1, ","),
      "dot": (1, "."),
      "exclamation_mark": (0.9, "!"),
      "question_mark": (0.9, "?"),
      "0": (0.9, "0"),
      "1": (0.9, "1"),
      "2": (0.9, "2"),
      "3": (0.9, "3"),
      "4": (0.9, "4"),
      "5": (0.9, "5"),
      "6": (0.9, "6"),
      "7": (0.9, "7"),
      "8": (0.9, "8"),
      "9": (0.9, "9"),
    }

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
    
    return characters

  def char_locations_to_string(
    char_locations,
    image_height,
    image_width,
    x_radius,
    y_radius,
    whitespace_width,
    alpha,
    ):

    # scan for found locations
    number_of_letters_on_pixel_height = [0]*image_height
    for _, y, *_ in char_locations:
      number_of_letters_on_pixel_height[y] += 1
    sorted_lines = sorted(((y, num_of_letters) for y, num_of_letters in enumerate(number_of_letters_on_pixel_height)), key= lambda x: x[1], reverse=True)

    many_pixel_row = [i for i in range(image_height)]
    for y, _ in sorted_lines:
        #check if the line was already parsed and is dense enough - another noise filterring 
        if many_pixel_row[y] != y or number_of_letters_on_pixel_height[y] < alpha * sorted_lines[0][1]:
            continue
        
        for dy in range(-y_radius, y_radius + 1):
            if dy != 0 and 0 <= y + dy < image_height:
                number_of_letters_on_pixel_height[y] += number_of_letters_on_pixel_height[y + dy]
                number_of_letters_on_pixel_height[dy] = 0
                many_pixel_row[y + dy] = y

    # making row of various pixels
    old_locations = char_locations
    line_content = {}
    for (x, old_y, score, char) in old_locations:
        y = many_pixel_row[old_y]
        new_record = (y, x), (char, score)
        if y not in line_content:
            line_content[y] = [new_record]
        else:
            line_content[y].append(new_record)

    # remove multiple characters
    chars_by_line = []
    for y in sorted(list(line_content.keys())):
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

  def write_results_to_file(path, font, res):
    arr = path.split("/")
    name = arr[-1].removesuffix(".png")
  
    with open(f"utils/results/{font}/{name}.txt", "w+") as file:
      file.write(res + "\n" + str(count_chars(res)))

  characters = init_chars()
  all_locations = sorted(((*location, character.rep) for character in characters for location in character.locations), key= lambda x: x[2], reverse=True)
  res = char_locations_to_string(all_locations, *(image_to_array(path, rotate).shape), 5, 9, 9, 0.1)  
  write_results_to_file(path, fontname, res)






