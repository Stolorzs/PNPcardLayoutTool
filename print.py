from card_layout import batch_process
from card_layout_back import batch_process_back


# 调用函数

# batch_process("./Cards", "./pdf/正面.pdf")


batch_process("./Cards/index","./pdf/index.pdf")

batch_process_back("./Cards/index","./pdf/index_back.pdf")