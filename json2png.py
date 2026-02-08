import os
import sys
import json
from PIL import Image

CHAR_SIZE = 8
BORDER_SIZE = 1
CHAR_INDEX = {
    "A":  0, "B":  1, "C":  2, "D":  3, "E":  4, "F":  5, "G":  6, "H":  7, "I":  8, "J":  9,
    "K": 10, "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17, "S": 18, "T": 19,
    "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25, ">": 26, "@": 42, "-": 28, " ": 29,
    "0": 30, "1": 31, "2": 32, "3": 33, "4": 34, "5": 35, "6": 36, "7": 37, "8": 38, "9": 39,
    "?": 40, ".": 41
}


class Char:
    def __init__(self, png_path):
        self.char_image = Image.open(png_path).convert("RGBA")
        width, _ = self.char_image.size
        self.row_count = (width - BORDER_SIZE) // (BORDER_SIZE + CHAR_SIZE)

    def put_text(self, background, text, ini, x, y, scale):
        put_x = x
        text_len = len(text)
        print("text :", text)
        for char in text:
            index = CHAR_INDEX[char.upper()]
            sx = (index % self.row_count) * (CHAR_SIZE + BORDER_SIZE) + BORDER_SIZE
            sy = (index // self.row_count) * (CHAR_SIZE + BORDER_SIZE) + BORDER_SIZE
            char_surf = self.char_image.crop((sx, sy, sx+CHAR_SIZE, sy+CHAR_SIZE))
            new_size = (char_surf.width * scale, char_surf.height * scale)
            char_surf = char_surf.resize(new_size, Image.NEAREST)

            offset_x, offset_y = get_ini_offset(ini, char_surf, text_len)
            background.paste(char_surf, (put_x+offset_x, y+offset_y), char_surf)
            put_x += CHAR_SIZE*scale


def get_ini_offset(ini, image, text_len=1):
    offset_x, offset_y = 0, 0

    # vertical
    if "top_" in ini:
        # デフォルトのまま
        pass
    elif "bottom_" in ini:
        offset_y = -image.height
    elif "center_" in ini:
        offset_y = -image.height // 2

    # horizontal
    if "_left" in ini:
        # デフォルトのまま
        pass
    elif "_right" in ini:
        offset_x = -image.width*text_len
    elif "_center" in ini:
        offset_x = -image.width*text_len // 2

    return offset_x, offset_y


def put_image(background, png_path, ini, x, y, scale, flip_x, flip_y):
    image = Image.open(png_path).convert("RGBA")
    new_size = (image.width * scale, image.height * scale)
    output_img = image.resize(new_size, Image.NEAREST)
    if flip_x:
        output_img = output_img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_y:
        output_img = output_img.transpose(Image.FLIP_TOP_BOTTOM)

    offset_x, offset_y = get_ini_offset(ini, output_img)
    background.paste(output_img, (x+offset_x, y+offset_y), output_img)


# JSONファイル読み込み
json_path = sys.argv[1]
if not os.path.exists(json_path):
    raise FileNotFoundError(f"JSON file not found: {json_path}")

with open(json_path, "r") as f:
    json_data = json.load(f)

# 背景画像を開く
background = Image.open(json_data["bg"]).convert("RGBA")

# キャラクタ画像を開く
char = Char(json_data["character"])

# テキストを描く
for info in json_data["texts"]:
    char.put_text(background, info["text"], info["ini"], info["x"], info["y"], info["scale"])

# キャラの位置（左上の座標）
for info in json_data["images"]:
    put_image(background, info["png_path"], info["ini"], info["x"], info["y"], info["scale"], info["flip_x"], info["flip_y"])

# 合成結果を保存
background.save("result.png")

print("合成画像を result.png として保存しました！")

