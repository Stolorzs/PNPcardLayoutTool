import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader  # 加上这一行
from natsort import natsorted
from PIL import Image

# 参数
DPI = 300
CARD_W_MM, CARD_H_MM = 63, 88
BORDER_MM = 2     # 灰边
SPACING_MM = 1    # 卡牌间距
SCALE_MODE = 0    # !!!! 0非等比缩放 1 - 等比缩放并裁剪（纵向多余裁顶部，横向多余居中）!!!!

def mm_to_px(mm):
    return int(mm / 25.4 * DPI)

def add_gray_border(img):
    """
    给原始图片加灰边：
    scale_mode:
        0 - 非等比缩放，直接拉伸到目标尺寸
        1 - 等比缩放并裁剪（纵向多余裁顶部，横向多余居中）
    外围加2mm灰边
    """
    target_w_px = mm_to_px(CARD_W_MM)
    target_h_px = mm_to_px(CARD_H_MM)
    border_px = mm_to_px(BORDER_MM)

    img = img.convert("RGB")
    iw, ih = img.size

    if SCALE_MODE == 0:
        # 非等比缩放
        img = img.resize((target_w_px, target_h_px), Image.LANCZOS)
    else:
        # 等比缩放 + 裁剪
        target_ratio = target_w_px / target_h_px
        img_ratio = iw / ih

        # 等比缩放，保证短边覆盖目标尺寸
        if img_ratio > target_ratio:
            # 图片太宽 → 按高缩放
            new_h = target_h_px
            new_w = int(new_h * img_ratio)
        else:
            # 图片太高 → 按宽缩放
            new_w = target_w_px
            new_h = int(new_w / img_ratio)

        img = img.resize((new_w, new_h), Image.LANCZOS)

        # 裁剪
        if new_h > target_h_px:
            # 纵向多余 → 从顶部裁掉多余部分
            left = (new_w - target_w_px) // 2
            upper = new_h - target_h_px
            right = left + target_w_px
            lower = new_h
        elif new_w > target_w_px:
            # 横向多余 → 居中裁剪
            left = (new_w - target_w_px) // 2
            upper = (new_h - target_h_px) // 2
            right = left + target_w_px
            lower = upper + target_h_px
        else:
            left, upper, right, lower = 0, 0, new_w, new_h

        img = img.crop((left, upper, right, lower))

    # 添加灰边
    new_w = target_w_px + border_px*2
    new_h = target_h_px + border_px*2
    new_img = Image.new("RGB", (new_w, new_h), (200,200,200))  # 灰色背景
    new_img.paste(img, (border_px, border_px))

    return new_img



def create_pdf(images, pdf_path):
    """ 将处理后的卡牌排版到A4纸上，含四边裁剪线延伸整张A4 """
    page_w, page_h = A4
    c = canvas.Canvas(pdf_path, pagesize=A4)

    card_w = (CARD_W_MM + BORDER_MM*2) * mm
    card_h = (CARD_H_MM + BORDER_MM*2) * mm
    spacing_x = SPACING_MM * mm
    spacing_y = SPACING_MM * mm

    cols = 3
    rows = 3
    total_w = cols*card_w + (cols-1)*spacing_x
    total_h = rows*card_h + (rows-1)*spacing_y
    margin_x = (page_w - total_w) / 2
    margin_y = (page_h - total_h) / 2

    per_page = cols * rows
    page_count = (len(images) + per_page - 1) // per_page

    for page in range(page_count):
        start = page * per_page
        end = min(start + per_page, len(images))
        positions = []

        for idx, img in enumerate(images[start:end]):
            col = idx % cols
            row = idx // cols

            x = margin_x + col * (card_w + spacing_x)
            y = page_h - margin_y - (row+1) * card_h - row * spacing_y
            positions.append((x, y, card_w, card_h))

            # 直接用 Pillow Image 内嵌 PDF（PNG/RGB）
            c.drawImage(ImageReader(img), x, y, width=card_w, height=card_h, mask='auto')

        # 画裁剪线（四边延伸整张A4，位于灰边内侧）
        c.setLineWidth(0.25)
        c.setStrokeColorRGB(0, 0, 0)
        for x, y, w, h in positions:
            left = x + BORDER_MM * mm
            right = x + w - BORDER_MM * mm
            bottom = y + BORDER_MM * mm
            top = y + h - BORDER_MM * mm

            c.line(0, top, page_w, top)
            c.line(0, bottom, page_w, bottom)
            c.line(left, 0, left, page_h)
            c.line(right, 0, right, page_h)

        c.showPage()

    c.save()

def batch_process(input_dir, output_pdf="cards.pdf"):
    """ 自动处理文件夹内所有图片并生成排版PDF（无磁盘中间文件） """
    files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    files = natsorted(files) # 自然排序，保证顺序稳定

    images = []
    for fname in files:
        img_path = os.path.join(input_dir, fname)
        img = Image.open(img_path)
        img_with_border = add_gray_border(img)
        images.append(img_with_border)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    create_pdf(images, output_pdf)

# *****************************************************************************************

# 使用示例
# batch_process("./Cards", "./pdf/cards_with_full_cutlines.pdf")
