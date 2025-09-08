import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from natsort import natsorted


# 卡牌尺寸（mm）
CARD_W_MM = 67
CARD_H_MM = 92
SPACING_MM = 1 # 间距
DPI = 300  # 输出目标 DPI

# ---------- 工具函数 ----------
def mm_to_px(mm_value):
    """毫米转像素"""
    return int(mm_value / 25.4 * DPI)

def mm_to_pt(mm_value):
    """毫米转 PDF pt"""
    return mm_value * mm  # reportlab 已经有 mm 单位

# ---------- 牌背排版 ----------
def layout_card_back(img, output_size_mm=(CARD_W_MM, CARD_H_MM)):
    """牌背排版：等比缩放并裁剪到指定尺寸，保证300DPI"""
    target_w_px = mm_to_px(output_size_mm[0])
    target_h_px = mm_to_px(output_size_mm[1])

    w, h = img.size
    scale = max(target_w_px / w, target_h_px / h)
    new_w, new_h = int(w*scale), int(h*scale)
    img_scaled = img.resize((new_w, new_h), Image.LANCZOS)

    # 裁剪中心区域
    left = (new_w - target_w_px) // 2
    top = (new_h - target_h_px) // 2
    img_cropped = img_scaled.crop((left, top, left + target_w_px, top + target_h_px))

    # 设置 DPI 信息
    img_cropped.info['dpi'] = (DPI, DPI)
    return img_cropped

# ---------- PDF 排版 ----------
def create_pdf_with_back(input_data, pdf_path):
    """生成 PDF，可输入单张 Pillow Image 或图片路径列表，牌背不加灰边"""
    page_w_pt, page_h_pt = A4
    c = canvas.Canvas(pdf_path, pagesize=A4)

    card_w_pt = mm_to_pt(CARD_W_MM)
    card_h_pt = mm_to_pt(CARD_H_MM)
    spacing_x = mm_to_pt(SPACING_MM)
    spacing_y = mm_to_pt(SPACING_MM)

    cols, rows = 3, 3
    per_page = cols * rows

    total_w = cols*card_w_pt + (cols-1)*spacing_x
    total_h = rows*card_h_pt + (rows-1)*spacing_y
    margin_x = (page_w_pt - total_w)/2
    margin_y = (page_h_pt - total_h)/2

    # 生成图片列表
    images = []
    if isinstance(input_data, Image.Image):
        # 单张图片复制9次
        images = [input_data]*9
    elif isinstance(input_data, list):
        # 图片路径列表，按牌背排版
        for path in input_data:
            img = Image.open(path)
            img_back = layout_card_back(img)
            images.append(img_back)
    else:
        raise ValueError("输入必须是 Pillow Image 对象或图片路径列表")

    # PDF 排版
    page_count = (len(images) + per_page - 1) // per_page
    for page in range(page_count):
        start = page * per_page
        end = min(start + per_page, len(images))

        for idx, img_item in enumerate(images[start:end]):
            # col = idx % cols
            row = idx // cols
            col = cols -1 -(idx % cols) # 左右翻转
            x = margin_x + col*(card_w_pt + spacing_x)
            y = page_h_pt - margin_y - (row+1)*card_h_pt - row*spacing_y

            # Pillow Image 直接用 ImageReader
            img_reader = ImageReader(img_item)
            c.drawImage(img_reader, x, y, width=card_w_pt, height=card_h_pt, mask='auto')

        c.showPage()

    c.save()

# ---------- 输入处理 ----------
def batch_process_back(input_path, pdf_path):
    """
    支持输入单个图片文件或图片目录
    - 单个文件 → 复制9次排版
    - 目录 → 按牌背排版生成 PDF
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    if os.path.isfile(input_path):
        img = Image.open(input_path)
        # 保证高像素
        img = layout_card_back(img)
        create_pdf_with_back(img, pdf_path)
    elif os.path.isdir(input_path):
        image_files = [os.path.join(input_path, f) for f in os.listdir(input_path)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))] 
        image_files = natsorted(image_files)# 按自然排序，保证顺序

        create_pdf_with_back(image_files, pdf_path)
    else:
        raise ValueError("输入必须是有效的图片文件或目录路径")

# *****************************************************************************************


# 目录
# batch_process_back("./Cards", "./pdf/card_back_all.pdf")
