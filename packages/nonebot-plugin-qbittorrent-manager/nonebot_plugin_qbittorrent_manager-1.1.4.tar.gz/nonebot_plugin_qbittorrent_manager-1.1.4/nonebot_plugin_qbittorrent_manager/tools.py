# coding=utf-8
import io
import json
import re
import shutil
import httpx
from PIL.Image import Image as PIL_Image
from PIL import Image, ImageDraw, ImageFont
import random
import os
import time
import matplotlib.font_manager as fm
from nonebot import logger
from pathlib import Path
from .config import plugin_cache_dir

qbm_cache = {
    "font_path": {}
}
system_font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
for font_path in system_font_list:
    font_path = font_path.replace("\\", "/")
    qbm_cache["font_path"][font_path.split("/")[-1]] = font_path


def save_image(
        image,
        image_path: str = None,
        image_name: int | str = None,
        to_bytes: bool = False,
        mode: str = "jpg"):
    """
    保存图片文件到缓存文件夹
    :param image:要保存的图片
    :param image_path: 指定的图片所在文件夹路径，默认为缓存
    :param image_name:图片名称，不填为随机数字
    :param to_bytes: 是否转为bytes
    :param mode: 保存的图片格式
    :return:保存的路径
    """
    if mode == "jpg":
        image = image.convert("RGB")
    if to_bytes is True and type(image) is PIL_Image:
        # 将Pillow图像数据保存到内存中
        image_stream = io.BytesIO()
        image.save(image_stream, format='JPEG')
        image_stream.seek(0)
        return image_stream.read()

    d_y, d_m, d_d = time.strftime("%Y/%m/%d", time.localtime()).split("/")
    time_now = int(time.time())

    if image_path is None:
        image_path = plugin_cache_dir / "cache" / d_y / d_m / d_d
    os.makedirs(image_path, exist_ok=True)

    if image_name is None:
        image_name = f"{time_now}_{random.randint(1000, 9999)}"
        num = 50
        while True and num > 0:
            num -= 1
            random_num = str(random.randint(1000, 9999))
            if os.path.exists(image_path / f"{image_name}_{random_num}.{mode}"):
                continue
            image_name = f"{image_name}_{random_num}.{mode}"
            break

    logger.debug(f"保存图片文件：{image_path}/{image_name}")
    image.save(image_path / image_name)

    if to_bytes is True:
        image_file = open(image_path / image_name, "rb")
        image = image_file.read()
        image_file.close()
        return image
    return image_path / image_name


def circle_corner(img, radii: int):
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


def image_resize2(image, size: [int, int], overturn=False):
    """
    重缩放图像
    :param image: 要缩放的图像
    :param size: 缩放后的大小
    :param overturn: 是否放大到全屏
    :return: 缩放后的图像
    """
    x, y = image.size
    if size[0] is None:
        size = (int(size[1] * x / y), size[1])
    if size[1] is None:
        size = (size[0], int(size[0] * y / x))

    image_background = Image.new("RGBA", size=size, color=(0, 0, 0, 0))
    image = image.convert("RGBA")
    w, h = image_background.size
    x, y = image.size
    if overturn:
        if w / h >= x / y:
            rex = w
            rey = int(rex * y / x)
            paste_image = image.resize((rex, rey))
            image_background.alpha_composite(paste_image, (0, 0))
        else:
            rey = h
            rex = int(rey * x / y)
            paste_image = image.resize((rex, rey))
            x = int((w - rex) / 2)
            image_background.alpha_composite(paste_image, (x, 0))
    else:
        if w / h >= x / y:
            rey = h
            rex = int(rey * x / y)
            paste_image = image.resize((rex, rey))
            x = int((w - rex) / 2)
            y = 0
            image_background.alpha_composite(paste_image, (x, y))
        else:
            rex = w
            rey = int(rex * y / x)
            paste_image = image.resize((rex, rey))
            x = 0
            y = int((h - rey) / 2)
            image_background.alpha_composite(paste_image, (x, y))

    return image_background


async def draw_text(
        texts: str,
        size: int,
        textlen: int = 20,
        fontfile: str = "",
        text_color=None,
        calculate=False
):
    """
    - 文字转图片
    :param texts: 输入的字符串
    :param size: 文字尺寸
    :param textlen: 一行的文字数量
    :param fontfile: 字体文字
    :param text_color: 字体颜色，例："#FFFFFF"、(10, 10, 10)
    :param calculate: 计算长度。True时只返回空白图，不用粘贴文字，加快速度。

    :return: 图片文件（RGBA）
    """
    if texts is None:
        texts = "None"
    if text_color is None:
        text_color = "#000000"

    def get_font_render_w(text):
        if text == " ":
            return 20
        none = ["\n", ""]
        if text in none:
            return 1
        canvas = Image.new('RGB', (500, 500))
        draw = ImageDraw.Draw(canvas)
        draw.text((0, 0), text, font=font, fill=(255, 255, 255))
        bbox = canvas.getbbox()
        # 宽高
        # size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
        if bbox is None:
            return 0
        return bbox[2]

    def sequence_generator(sequence):
        for value in sequence:
            yield value

    default_font = ["msyh.ttc", "DejaVuSans.ttf", "msjh.ttc", "msjhl.ttc", "msjhb.ttc", "YuGothR.ttc"]
    if fontfile is None or fontfile == "":
        fontfile = "msyh.ttc"
    if not fontfile.startswith("/") or ":/" in fontfile:
        # 获取字体绝对路径

        font_list = [fontfile] + default_font + ["no_font"]
        for font in font_list:
            if font == "no_font":
                # logger.error(f"字体加载失败，请安装字体{font_list[0]}")
                # raise f"字体加载失败，请安装字体"
                fontfile = font_list[0]
                break

            if font in qbm_cache["font_path"].keys():
                fontfile = qbm_cache["font_path"][font]
                break

            if os.path.exists(fontfile):
                break

    font = ImageFont.truetype(font=fontfile, size=size)

    # 计算图片尺寸
    print_x = 0
    print_y = 0
    jump_num = 0
    text_num = -1
    max_text_y = 0
    max_text_y_list = []
    texts_len = len(texts)
    for text in texts:
        text_num += 1
        if jump_num > 0:
            jump_num -= 1
        else:
            if (textlen * size) < print_x or text == "\n":
                print_x = 0
                print_y += 1.3 * max_text_y
                max_text_y_list.append(max_text_y)
                max_text_y = 0
                if text == "\n":
                    continue
            if text == " ":
                print_x += get_font_render_w(text) + 2
                if size > max_text_y:
                    max_text_y = size
                continue
            if text == "<":
                while text_num + jump_num < texts_len and texts[text_num + jump_num] != ">":
                    jump_num += 1
                jump_num += 0

                text = texts[text_num:text_num + jump_num]
                pattern = r'src="([^"]+)"'
                urls = re.findall(pattern, text)
                if urls:
                    pattern = r'width="(\d+)"'
                    image_size_x = re.findall(pattern, text)

                    paste_image = await load_image(urls[0])
                    if image_size_x:
                        paste_image = image_resize2(paste_image, (int(image_size_x[0]), None))
                    print_x += paste_image.size[0] + 2
                    if paste_image.size[1] > max_text_y:
                        max_text_y = paste_image.size[1]
                    continue
            print_x += get_font_render_w(text) + 2
            if size > max_text_y:
                max_text_y = size
    max_text_y_list.append(max_text_y)
    text_y_list = sequence_generator(max_text_y_list)

    x = int((textlen + 1.5) * size)
    y = int(print_y + 1.2 * size)

    image = Image.new("RGBA", size=(x, y), color=(0, 0, 0, 0))  # 生成透明图片
    draw_image = ImageDraw.Draw(image)

    # 绘制文字
    if calculate is False:
        print_x = 0
        print_y = 0
        jump_num = 0
        text_num = -1
        draw_max_text_y = next(text_y_list)
        for text in texts:
            text_num += 1
            if jump_num > 0:
                jump_num -= 1
            else:
                if (textlen * size) < print_x or text == "\n":
                    print_x = 0
                    print_y += draw_max_text_y
                    draw_max_text_y = next(text_y_list, None)
                    if text == "\n":
                        continue
                if text in ["\n", " "]:
                    if text == " ":
                        print_x += get_font_render_w(text) + 2
                    continue
                if text == "<":
                    while text_num + jump_num < texts_len and texts[text_num + jump_num] != ">":
                        jump_num += 1
                    jump_num += 0

                    text = texts[text_num:text_num + jump_num]
                    pattern = r'src="([^"]+)"'
                    urls = re.findall(pattern, text)
                    if urls:
                        pattern = r'width="(\d+)"'
                        image_size_x = re.findall(pattern, text)

                        paste_image = await load_image(urls[0])
                        if image_size_x:
                            paste_image = image_resize2(paste_image, (int(image_size_x[0]), None))
                        image.alpha_composite(paste_image, (int(print_x), int(print_y)))
                        print_x += paste_image.size[0] + 2
                        continue

                draw_image.text(xy=(int(print_x), int(print_y)),
                                text=text,
                                fill=text_color,
                                font=font)
                print_x += get_font_render_w(text) + 2
        # 把输出的图片裁剪为只有内容的部分
        bbox = image.getbbox()
        if bbox is None:
            box_image = Image.new("RGBA", (2, size), (0, 0, 0, 0))
        else:
            box_image = Image.new("RGBA", (bbox[2] - bbox[0], bbox[3] - bbox[1]), (0, 0, 0, 0))
            box_image.paste(image, (0 - int(bbox[0]), 0 - int(bbox[1])), mask=image)
        image = box_image
    return image


async def load_image(path: str, size=None, mode=None, cache_image=True):
    """
    读取图片或请求网络图片
    :param path: 图片路径/图片url
    :param size: 出错时候返回的图片尺寸
    :param mode: 图片读取模式
    :param cache_image: 焕缓存获取的图片
    :return:image
    """
    if type(path) is Image.Image:
        return path
    if mode is None:
        mode = "r"
    try:
        if path.startswith("http"):
            if cache_image is False:
                image = await connect_api("image", path)
            else:
                cache_path = Path(path.removeprefix("http://").removeprefix("https://").split("?")[0])

                if os.path.exists(plugin_cache_dir / "web_cache" / cache_path):
                    return Image.open(plugin_cache_dir / "web_cache" / cache_path)
                file_name = cache_path.name
                file_path = plugin_cache_dir / "web_cache" / cache_path.parent
                os.makedirs(file_path, exist_ok=True)
                image = await connect_api("image", path)
                image.save(file_path / file_name)

            return image
        else:
            if path.startswith("{cache_dir}"):
                image_path = plugin_cache_dir / Path(path.removeprefix("{cache_dir}"))
                if not os.path.exists(image_path):
                    raise "图片不存在"
                image = Image.open(image_path, mode)
                if mode == "rb":
                    return save_image(image, to_bytes=True)
                return image
            return Image.open(path, mode)
    except Exception as e:
        logger.error(f"读取图片错误：{path}")
        logger.error(e)
        if size is not None:
            return Image.new("RGBA", size, (0, 0, 0, 0))
        raise "图片读取错误"


def draw_gradient_color(
        color_a: tuple | str,
        color_b: tuple | str,
        size: tuple[int, int] | list[int, int],
):
    """
    绘制一张从左到右的渐变
    :param size: 图片的尺寸
    :param color_a: 图片读取模式
    :param color_b: 图片读取模式
    :return:image
    """

    def covert_color(c: tuple | str) -> tuple:
        """
        转换str颜色到tuple颜色
        """
        if type(c) is str:
            c = (
                int(c[1:3], 16),
                int(c[3:5], 16),
                int(c[5:7], 16),
                255 if len(c) == 7 else int(c[7:9], 16)
            )
        return c

    color_a = covert_color(color_a)
    color_b = covert_color(color_b)

    image = Image.new("RGBA", (size[0], 1), (0, 0, 0, 0))
    img_array = image.load()
    for i in range(size[0]):
        color = (
            int(color_a + ((color_b[0] - color_a[0]) / size[0] * i)),
            int(color_a + ((color_b[1] - color_a[1]) / size[0] * i)),
            int(color_a + ((color_b[2] - color_a[2]) / size[0] * i)),
            int(color_a + ((color_b[3] - color_a[3]) / size[0] * i)),
        )
        img_array[i, 0] = color
    image = image.resize(size)
    return image


async def connect_api(
        connect_type: str,
        url: str,
        post_json=None,
        file_path: str = None,
        timeout: int = 10
):
    """
    请求网络资源
    :param connect_type: json, image, file
    :param url: url
    :param post_json: 要post的内容
    :param file_path: 文件的保存路径
    :param timeout: 超时时间
    :return:
    """
    logger.debug(f"connect_api请求URL：{url}")
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"}
    if connect_type == "json":
        if post_json is None:
            async with httpx.AsyncClient() as client:
                data = await client.get(url, headers=h, timeout=timeout)
            return json.loads(data.text)
        else:
            async with httpx.AsyncClient() as client:
                data = await client.post(url, json=post_json, headers=h, timeout=timeout)
            return json.loads(data.text)
    elif connect_type == "image":
        if url is None or url in ["none", "None", "", " "]:
            image = await draw_text("获取图片出错", 50, 10)
        else:
            try:
                async with httpx.AsyncClient() as client:
                    data = await client.get(url, timeout=timeout)
                image = Image.open(io.BytesIO(data.content))
            except Exception as e:
                logger.error(e)
                logger.error(url)
                raise "获取图片出错"
        return image
    elif connect_type == "file":
        cache_file_path = file_path + "cache"
        f = open(cache_file_path, "wb")
        try:
            res = httpx.get(url, headers=h, timeout=timeout).content
            f.write(res)
            logger.debug(f"下载完成-{file_path}")
        except Exception as e:
            logger.error(e)
            raise Exception
        finally:
            f.close()
        shutil.copyfile(cache_file_path, file_path)
        os.remove(cache_file_path)
    return


async def draw_form(
        form_data: list[list[dict]],
        size_x: int,
        uniform_size: bool = True,
        calculate: bool = False,
        out_of_form: bool = True,
        font_file_path: str = None
) -> Image.Image:
    """
    绘制表格
    :param form_data: 表格数据
    :param size_x: x的尺寸
    :param uniform_size: 统一尺寸（使用每行最大的尺寸）
    :param calculate: 是否仅计算不绘制
    :param out_of_form: 在右边为空时，文字允许超出格子范围
    :param font_file_path: 字体文件
    :return:保存的路径
    """
    """
    sample_from_data = [
        [
            {"type": "text", "size": 40, "color": "#000000", "text": "文字内容"},
            {"type": "image", "size": (30, 30), "image": "./sample.png"}
        ]
    ]
    """

    size_y = 0
    size_y += 16
    add_size_y_list = []
    for num_x, form_x in enumerate(form_data):
        add_size_y = 0
        for num_y, form_y in enumerate(form_x):
            if form_y.get("type") is None and form_y.get("text") is None:
                continue
            elif form_y.get("type") == "image" and form_y.get("image") is None:
                continue

            if form_y.get("draw_size") is not None:
                draw_size = form_y.get("draw_size")
            elif form_y.get("type") is None or form_y.get("type") == "text":
                textlen = int(size_x / len(form_x) / form_y["size"])
                if out_of_form is True:
                    if num_y < len(form_x) - 1 and form_x[num_y + 1] == {}:
                        textlen += textlen * 0.8
                        if num_y < len(form_x) - 2 and form_x[num_y + 2] == {}:
                            textlen += textlen * 0.8
                draw_size = await draw_text(
                    form_y.get("text"),
                    size=form_y["size"],
                    textlen=textlen,
                    fontfile=font_file_path if form_y.get("font") is None else form_y.get("font"),
                    text_color=form_y.get("color"),
                    calculate=True
                )
                draw_size = draw_size.size
            elif form_y.get("type") == "image":
                if form_y.get("size") is not None and form_y.get("size")[1] is not None:
                    draw_size = form_y.get("size")
                else:
                    image = await load_image(form_y.get("image"))
                    draw_size = image.size
            else:
                continue

            form_data[num_x][num_y]["draw_size"] = draw_size
            if draw_size[1] > add_size_y:
                add_size_y = draw_size[1]
        add_size_y_list.append(add_size_y)
        size_y += int(size_x * 0.01)  # 间隔
    if uniform_size is True:
        max_size = max(add_size_y_list)
        for i in range(len(add_size_y_list)):
            add_size_y_list[i] = max_size
    for s in add_size_y_list:
        size_y += s

    image = Image.new("RGBA", (size_x, size_y), (0, 0, 0, 0))
    if calculate is True:
        return image

    paste_line = Image.new("RGBA", (int(size_x * 0.95), 3), "#000000")
    draw_y = 0
    for num_x, form_x in enumerate(form_data):
        if num_x != 0:
            image.alpha_composite(paste_line, (int(size_x * 0.025), int(draw_y)))

        add_size_y = add_size_y_list[num_x]

        add_size_y += int(size_x * 0.01)  # 间隔

        for num_y, form_y in enumerate(form_x):
            if form_y.get("type") is None and form_y.get("text") is None:
                continue
            elif form_y.get("type") == "image" and form_y.get("image") is None:
                continue

            if form_y.get("type") is None or form_y.get("type") == "text":
                textlen = int(size_x / len(form_x) / form_y["size"])
                if out_of_form is True:
                    if num_y < len(form_x) - 1 and form_x[num_y + 1] == {}:
                        textlen += textlen * 0.8
                        if num_y < len(form_x) - 2 and form_x[num_y + 2] == {}:
                            textlen += textlen * 0.8
                paste_image = await draw_text(
                    form_y.get("text"),
                    size=form_y["size"],
                    textlen=textlen,
                    fontfile=font_file_path if form_y.get("font") is None else form_y.get("font"),
                    text_color=form_y.get("color"),
                    calculate=False
                )
            elif form_y.get("type") == "image":
                paste_image = await load_image(form_y.get("image"))
                image_size = form_y.get("size")
                if image_size is not None:
                    paste_image = image_resize2(paste_image, image_size)
                else:
                    image_size = paste_image.size
                if form_y.get("color") is not None:
                    paste_card = Image.new("RGBA", image_size, (0, 0, 0, 0))
                    paste_color = Image.new("RGBA", image_size, form_y.get("color"))
                    paste_card.paste(paste_color, (0, 0), paste_image)
                    paste_image = paste_card
            else:
                continue
            image.alpha_composite(paste_image, (
                int(num_y * size_x / len(form_x) + (size_x * 0.01)),
                int(draw_y + ((add_size_y - paste_image.size[1]) / 2))
            ))

        draw_y += add_size_y
    return image


async def mix_image(image_1, image_2, mix_type=1):
    """
    将两张图合并为1张
    :param image_1: 要合并的图像1
    :param image_2: 要合并的图像2
    :param mix_type: 合成方式。1：竖向
    :return:
    """
    if type(image_1) is str:
        image_1 = await load_image(image_1)
    if type(image_2) is str:
        image_2 = await load_image(image_2)
    if mix_type == 1:
        x1, y1 = image_1.size
        x2, y2 = image_2.size
        if image_1.mode == "RGB":
            image_1 = image_1.convert("RGBA")
        if image_2.mode == "RGB":
            image_2 = image_2.convert("RGBA")

        if x1 > x2:
            x2_m = x1
            y2_m = int(x2_m / x2 * y2)
            images = Image.new("RGBA", (x2_m, y2_m + y1), (0, 0, 0, 0))
            image_2_m = image_2.resize((x2_m, y2_m))
            images.alpha_composite(image_1, (0, 0))
            images.alpha_composite(image_2_m, (0, y1))
            return images
        else:  # x1 < x2
            x1_m = x2
            y1_m = int(x1_m / x1 * y1)
            images = Image.new("RGBA", (x1_m, y1_m + y2), (0, 0, 0, 0))
            image_1_m = image_1.resize((x1_m, y1_m))
            images.alpha_composite(image_1_m, (0, 0))
            images.alpha_composite(image_2, (0, y1_m))
            return images
    raise "未知的合并图像方式"


def get_parameters(text: str | list) -> dict:
    """
    解析文字包含的参数，以空格切割
    :param text:
    :return:
    """
    if type(text) is str:
        texts = text.split(" ")
    else:
        texts = text

    parameters_list = {
        "tag": ["-tag", "-t"],
        "savepath": ["-savepath", "-path", "-p"],
        "category": ["-category", "-c"],
    }
    return_data = {
        "tag": None,
        "savepath": None,
        "category": None,
        "texts": "",
    }

    # 解析
    jump_num = 0
    for text in texts:
        if jump_num > 0:
            jump_num -= 1
            continue
        for i, parameters in enumerate(parameters_list):
            if text in parameters_list[parameters]:
                return_data[parameters] = parameters_list[i + 1]
                jump_num += 1
            else:
                return_data["texts"] += " " + text
    return_data["texts"].removeprefix(" ")
    return return_data
