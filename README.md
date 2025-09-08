# PNP素材制作工具

## 用法

1、安装python  

2、安装reportlab，Image  

3、在脚本中调用call_layout.py/call_layout_back.py的 batch_process/ batch_process_back函数

## 注意事项
1、正面卡牌+灰边后需要与背面卡牌(灰边为出血区域)的尺寸相等

2、SPACING_MM为排版间距，正面卡牌和背面卡牌的的卡牌间距要一致

3、batch_process_back()参数1若为目录，则会依次将目录下所有的卡牌进行排版，若为图片文件，则会将该图片排作一张pdf；此功能用于牌背不同/牌背相同的卡牌的排版