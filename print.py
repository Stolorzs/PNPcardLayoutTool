from card_layout import batch_process
from card_layout_back import batch_process_back


# 调用函数

batch_process("./Cards", "./pdf/正面.pdf")

batch_process_back("./Cards", "./pdf/背面测试1.pdf")

batch_process_back("./Cards/1e47a6f5-5a53-426a-b38d-9723fe391c7d.png",
                   "./pdf/背面.pdf")

batch_process("./Cards/long", "./pdf/正面拉长.pdf")