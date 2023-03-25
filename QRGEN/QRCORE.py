# _*_ coding:utf-8 _*_

'''
创建时间：2020-12-07
文件说明：生成个性的带背景图的二维码
'''
import colorsys
import math
import os
import sys
from pathlib import Path

import PIL.ImageShow
import qrcode
from PIL import Image, ImageDraw, ImageEnhance
import matplotlib.pyplot as plt

# from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

Base_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Base_DIR)

whiteRGB = (255, 255, 255, 255)  # 白色RGB值
blackRGB = (0, 0, 0, 255)  # 黑色RGB值


class GenerateQRCode(object):
    '''
        生成透明带背景图的二维码
        返回图片
    '''

    # 初始化参数
    def __init__(self, background_map, version=None, error_correction=qrcode.ERROR_CORRECT_L, box_size=8, border=2):
        self.version = version  # 版本信息
        self.error_correction = error_correction  # 容错率
        self.box_size = box_size  # 点阵粗细
        self.border = border  # 边框
        self.background_map = background_map

    # 白色背景透明设置
    def __transparent_back(self, image):
        img = image.convert('RGBA')
        L, H = img.size
        color_0 = whiteRGB  # 要替换的颜色
        for h in range(H):
            for l in range(L):
                dot = (l, h)
                color_1 = img.getpixel(dot)
                if color_1 == color_0:
                    color_1 = color_1[:-1] + (0,)
                    img.putpixel(dot, color_1)
        # img.save(f"{1}.png", quality=100)
        return img

    # 计算二维码黑点白点位置
    def __position(self, coordinate):
        Tlist = list()  # 黑块列表
        Flist = list()  # 白块列表
        rnum = int(self.box_size / (self.box_size / 2))
        clen = len(coordinate)
        numy = 0
        for y in coordinate:
            if self.border - 1 < numy < self.box_size + self.border:  # 头
                numx = 0
                for x in y:
                    if self.box_size + self.border <= numx < clen - (self.box_size + self.border):  # 避开左右空白和两个头对齐
                        if x == True:
                            # 计算出坐标位置
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Tlist.append((wx, hy))
                        elif x == False:
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Flist.append((wx, hy))
                    # 加入装饰用白块
                    else:
                        if self.border - 1 < numx < clen - self.border:
                            if x == False:
                                wx = int(numx * self.box_size) + rnum
                                hy = int(numy * self.box_size) + rnum
                                Flist.append((wx, hy))
                    numx += 1
            elif self.box_size + self.border <= numy < clen - (self.box_size + self.border):  # 腰
                numx = 0
                for x in y:
                    if self.border - 1 < numx < clen - self.border:  # 避开左右空白
                        if x == True:
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Tlist.append((wx, hy))
                        else:
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Flist.append((wx, hy))
                    numx += 1
            elif clen - (self.box_size + self.border) <= numy < clen - self.border:  # 尾
                numx = 0
                for x in y:
                    if self.box_size + self.border <= numx < clen - self.border:  # 避开左右空白和一个尾对齐
                        if x == True:
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Tlist.append((wx, hy))
                        elif x == False:
                            wx = int(numx * self.box_size) + rnum
                            hy = int(numy * self.box_size) + rnum
                            Flist.append((wx, hy))
                    # 加入装饰用白块
                    else:
                        if self.border - 1 < numx < clen - self.border:
                            if x == False:
                                wx = int(numx * self.box_size) + rnum
                                hy = int(numy * self.box_size) + rnum
                                Flist.append((wx, hy))
                    numx += 1
            numy += 1
        return Tlist, Flist

    # 生成二维码
    def Qrcode(self, txt):
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(txt)
        qr.make(fit=True)
        # 获取二维码矩阵
        coordinate = qr.get_matrix()
        # 获取生成的二维码大小
        qrimg = qr.make_image()
        qrimg = self.__transparent_back(qrimg)
        w, h = qrimg.size
        # 打开背景图
        b_map = Image.open(self.background_map)
        # 设置背景图大小
        b_map_image = b_map.resize((w, h), Image.ANTIALIAS)
        # 获取黑点和白点的列表
        (Tlist, Flist) = self.__position(coordinate)

        # 颜色确定，rgb转hsv，提升s降低v以染色
        def rgb2hsv(r, g, b):
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            mx = max(r, g, b)
            mn = min(r, g, b)
            df = mx - mn
            if mx == mn:
                h = 0
            elif mx == r:
                h = (60 * ((g - b) / df) + 360) % 360
            elif mx == g:
                h = (60 * ((b - r) / df) + 120) % 360
            elif mx == b:
                h = (60 * ((r - g) / df) + 240) % 360
            if mx == 0:
                s = 0
            else:
                s = df / mx
            v = mx
            return h, s, v

        def hsv2rgb(h, s, v):
            h = float(h)
            s = float(s)
            v = float(v)
            h60 = h / 60.0
            h60f = math.floor(h60)
            hi = int(h60f) % 6
            f = h60 - h60f
            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)
            r, g, b = 0, 0, 0
            if hi == 0:
                r, g, b = v, t, p
            elif hi == 1:
                r, g, b = q, v, p
            elif hi == 2:
                r, g, b = p, v, t
            elif hi == 3:
                r, g, b = p, q, v
            elif hi == 4:
                r, g, b = t, p, v
            elif hi == 5:
                r, g, b = v, p, q
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            return r, g, b

        max_score = 0
        dominant_color = 0, 0, 0

        # 取得主要颜色
        try:
            for count, (r, g, b, a) in b_map.getcolors(b_map.size[0] * b_map.size[1]):
                # 跳过纯黑色
                if a == 0:
                    continue
                saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
                y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
                y = (y - 16.0) / (235 - 16)
                # 忽略高亮色
                if y > 0.9:
                    continue
                score = (saturation + 0.1) * count
                if score > max_score:
                    max_score = score
                    dominant_color = (r, g, b)
        except ValueError:
            for count, (r, g, b) in b_map.getcolors(b_map.size[0] * b_map.size[1]):
                saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
                y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
                y = (y - 16.0) / (235 - 16)
                # 忽略高亮色
                if y > 0.9:
                    continue
                score = (saturation + 0.1) * count
                if score > max_score:
                    max_score = score
                    dominant_color = (r, g, b)

        print(dominant_color)

        # 此处添加通过s判断是否颜色过于深，如过深则整成灰色，防止被整成深红色
        h, s, v = rgb2hsv(dominant_color[0], dominant_color[1], dominant_color[2])
        if s <= 0.0001:
            s = 0
        else:
            s = 1  # 饱和度拉满

        # v = 0.32  # 明度固定防止过暗过亮
        # 加入亮度控制，v等于原本颜色减去0.2,v恒大于0.1且小于0.4
        v = v - 0.25
        if v <= 0.1:
            v = 0.1
        if v >= 0.4:
            v = 0.4
        r, g, b = hsv2rgb(h, s, v)

        dark = (r, g, b, 255)
        white = (255, 255, 255, 255)

        # 重绘以取得彩色对齐块
        qrimg = qr.make_image(fill_color=dark, back_color="white")
        qrimg = self.__transparent_back(qrimg)

        '''
        1、把需要缩小的黑色块变成白色
        2、画出黑色的小块
        3、把图片白色透明
        4、二维码图和背景图合并
        5、画出白色的小方块
        '''

        rnum = int(self.box_size / (self.box_size / 2))
        for n in Tlist:
            for m in range(self.box_size + 1):
                for m1 in range(self.box_size + 1):
                    qrimg.putpixel((n[0] - rnum + m1, n[1] - rnum + m), white)

            for p in range(rnum + 2):
                for p1 in range(rnum + 2):
                    qrimg.putpixel((n[0] + p1, n[1] + p), dark)

        image = self.__transparent_back(qrimg)
        for n1 in Flist:
            for p in range(rnum + 2):
                for p1 in range(rnum + 2):
                    image.putpixel((n1[0] + p1, n1[1] + p), white)

        # 透明度

        r, g, b, a = image.split()

        opacity = 0.95
        alpha = ImageEnhance.Brightness(a).enhance(opacity)
        image.putalpha(alpha)

        # 使用alpha_composite叠加，两者需相同size
        final = Image.new("RGBA", b_map_image.size)
        final = Image.alpha_composite(final, b_map_image)
        final = Image.alpha_composite(final, image)

        # 缩放图片以保持原图大小
        final = final.resize((b_map.width, b_map.height))

        # 保存图片

        save_file = f'{self.background_map}'
        path_str = Path(save_file)
        path_parent_path = path_str.parent
        path_file_name = path_str.stem
        # 输出结果图
        final.save(f'{path_parent_path}/web/{path_file_name}.png', quality=100)
        # 输出独立二维码图
        image.save(f'{path_parent_path}/qr/{path_file_name}_qr.png', quality=100)


def single(img_org_path, text):
    gqrc = GenerateQRCode(background_map=img_org_path)
    gqrc.Qrcode(text)


if __name__ == "__main__":
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=8,
        border=2,
        image_factory=None,
        mask_pattern=None
    )
    qr.add_data('1')
    qr.make(fit=True)

    # 获取生成的二维码大小
    qrimg = qr.make_image(

    )
    qrimg.save('qrt8.png', quality=100)
