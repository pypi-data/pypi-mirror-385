import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Union, Tuple, List, Union, Callable, Optional
import toml
from pydantic import BaseModel, Field

# Define a reusable type for color input:
# Either a fixed RGB list, a callable that computes color dynamically,
# or None (default color)
ColorType = Union[
    List[int],
    Callable[[Image.Image, int, int], List[int]],
    None
]


class TextDrawParams(BaseModel):
    """Pydantic model representing parameters for text drawing."""
    
    text: str = Field(..., description="Text string to be drawn")
    x: int = Field(..., description="X coordinate of the text position")
    y: int = Field(..., description="Y coordinate of the text position")
    height: int = Field(..., description="Font size (height in pixels)")
    font_path: Optional[str] = Field(default=None, description="Path to the font file")
    color: ColorType = Field(
        default=None,
        description="Either a fixed RGB list, a callable function, or None"
    )

# Model representing a list of multiple text draw parameters
class MultiTextDrawParams(BaseModel):
    """Container model that holds multiple TextDrawParams items."""
    
    texts: List[TextDrawParams] = Field(
        ...,
        description="A list of text drawing parameter objects"
    )

def hsv_to_opencv(h: float, s: float, v: float) -> np.ndarray:
    """
    Convert standard HSV (H:0–360°, S,V:0–100%) 
    into OpenCV HSV (H:0–179, S,V:0–255).
    """
    h_cv = np.clip(h / 2, 0, 179)
    s_cv = np.clip(s * 255 / 100, 0, 255)
    v_cv = np.clip(v * 255 / 100, 0, 255)
    return np.array([int(h_cv), int(s_cv), int(v_cv)], dtype=np.uint8)

def load_image_cv2(img_or_path: Union[str, np.ndarray]) -> np.ndarray:
    """Accepts either a file path or an already loaded image."""
    if isinstance(img_or_path, np.ndarray):
        return img_or_path
    elif isinstance(img_or_path, str) and os.path.exists(img_or_path):
        img = cv2.imread(img_or_path)
        if img is None:
            raise ValueError(f"Failed to load image from {img_or_path}")
        return img
    else:
        raise TypeError("Expected either a valid file path or a NumPy image array.")

def load_pil_image(img_or_path: Union[str, Image.Image]) -> Image.Image:
    """
    Accepts either a file path or a PIL.Image object.
    If a path is given, it loads the image using PIL.Image.open().
    """
    if isinstance(img_or_path, Image.Image):
        return img_or_path
    elif isinstance(img_or_path, str):
        if not os.path.exists(img_or_path):
            raise FileNotFoundError(f"Image not found: {img_or_path}")
        return Image.open(img_or_path)
    else:
        raise TypeError("Expected either a file path (str) or a PIL.Image.Image object.")

def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """
    Convert a PIL.Image to an OpenCV (BGR) numpy array.
    """
    cv_image = np.array(pil_image.convert("RGB"))  # Pillow → NumPy
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    return cv_image

def paste_image_with_height(
    base_img: Union[str, Image.Image],
    overlay_img: Union[str, Image.Image],
    x: int,
    y: int,
    height: int
) -> Image.Image:
    """
    Paste `overlay_img` onto `base_img` at (x, y) with the given height,
    preserving aspect ratio and alpha transparency (RGBA).

    - Supports both file paths and Image.Image objects.
    - Converts both images to RGBA to ensure safe compositing.
    - If the overlay has no transparency, it will still blend properly.
    """
    # --- Load both images ---
    base = load_pil_image(base_img)
    overlay = load_pil_image(overlay_img)

    # --- Ensure both are in RGBA mode (so alpha transparency is handled correctly) ---
    if base.mode != "RGBA":
        base = base.convert("RGBA")
    if overlay.mode != "RGBA":
        overlay = overlay.convert("RGBA")

    # --- Resize overlay proportionally by height ---
    w, h = overlay.size
    if h == 0:
        raise ValueError("Overlay image height cannot be zero.")
    aspect_ratio = w / h
    new_w = int(height * aspect_ratio)
    new_h = height
    overlay_resized = overlay.resize((new_w, new_h), Image.LANCZOS)

    # --- Create a copy of the base image for output ---
    result = base.copy()

    # --- Paste overlay respecting alpha transparency ---
    result.paste(overlay_resized, (x, y), overlay_resized)

    return result

def draw_sample_img(
    size=(512, 700),
    boxes=[(50, 50, 100, 100), (400, 670, 430, 700)],
    line_color=(0, 255, 0),
    line_width=2
):
    w, h = size
    gradient = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            val = int(255 * (1 - (x + y) / (w + h)))
            gradient[y, x] = (val, val, val)
    img = Image.fromarray(gradient)
    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.rectangle(box, outline=line_color, width=line_width)
    return img

class GreenPoster():
  def __init__(self,
              lower_green_hsv:list = [110, 90, 90], 
              upper_green_hsv:list = [160, 100, 100],
              default_font:str = "/content/NotoSansJP-Black.otf"
              ):
    self.lower_green = np.array(lower_green_hsv)  
    self.upper_green = np.array(upper_green_hsv)
    self.default_font = default_font
    self.default_color = [0,0,0]

  def read_green(self, img_or_path: Union[str, np.ndarray, Image.Image]) -> List[dict]:
    if isinstance(img_or_path, Image.Image):
      img = pil_to_cv2(img_or_path)
    else:
      img = load_image_cv2(img_or_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = hsv_to_opencv(*self.lower_green)
    upper = hsv_to_opencv(*self.upper_green)
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        results.append({
            "x": x,
            "y": y,
            "h": h
        })
    return results

  def read_green_to_toml(self, img_or_path: Union[str, np.ndarray, Image.Image],
                         toml_path:str="format.toml"):
      res=self.read_green(img_or_path)
      di={}
      for i, v in enumerate(res):
        di[f"input_{i}"]=v
      toml_str = toml.dumps(di)
      with open(toml_path, "w", encoding="utf-8") as f:
          f.write(toml_str)

  def write_chars(
      self,
      img_or_path: Union[str, Image.Image],
      text:str,
      x:int,
      y:int,
      height:int,
      font_path:str=None,
      color: Union[List[int], Callable[[Image.Image, int, int], List[int]], None] = None,
      ) -> Image.Image:
    img=load_pil_image(img_or_path)
    draw = ImageDraw.Draw(img)
    if font_path is None:
      font_path = self.default_font
    if callable(color):
      color = color(img, x, y)
    elif isinstance(color, list):
      color = color
    else:
      color = self.default_color
    font=ImageFont.truetype(font_path, height)

    dummy = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))
    ddraw = ImageDraw.Draw(dummy)
    ddraw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    arr = np.array(dummy.split()[-1])  
    rows = np.any(arr > 0, axis=1)
    if not np.any(rows):
        return img 
    top_idx = np.argmax(rows) 
    y_offset = top_idx - y
    y_corrected = y - y_offset

    draw.text((x, y_corrected), text, font=font, fill=tuple(color))
    return img

  def paste_image_with_height(self,
        base_img: Union[str, Image.Image],
        overlay_img: Union[str, Image.Image],
        x: int,
        y: int,
        height: int):
    return paste_image_with_height(base_img, overlay_img, x, y, height)

  def apply_text_draw_params(self,
      img_or_path: Union[str, Image.Image],
      params: MultiTextDrawParams
  ) -> Image.Image:
      """Apply each TextDrawParams item to the image sequentially."""
      img = load_pil_image(img_or_path)
      for p in params.texts:
          img = self.write_chars(
              img_or_path=img,
              text=p.text,
              x=p.x,
              y=p.y,
              height=p.height,
              font_path=p.font_path,
              color=p.color
          )
      return img

  def test(self):
      img=draw_sample_img()
      res=green_poster.read_green(img)
      for r in res:
        img=self.write_chars(img, "あア亜１A", r["x"], r["y"], r["h"])
      return img  

  def test2(self):
      img=draw_sample_img()
      multiple_texts=MultiTextDrawParams(texts=[
          TextDrawParams(text="主題タイトルABC",x=50,y=50,height=51),
          TextDrawParams(text="文字abc",x=400,y=670,height=30, color=[100,100,100])
      ])
      img=self.apply_text_draw_params(img, multiple_texts)
      return img
