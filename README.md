# novelSprider
爬取国内某些小说网站指定的小说

目前支持的小说网站如下：
1、奇奇小说网  https://www.477zw3.com
2、TXT小说网  https://www.shuangliusc.com
3、笔趣阁    https://www.bqbi.cc

执行结果文件是TXT格式，记录章节名称和每章内容

由于网站存在反爬虫机制，程序运行一段时间会异常退出，所以增加如何特性：
1、创建临时文件保存爬取过章节URL，重新运行爬取会跳过已经爬取的
2、结果文件会按照顺序保存已经爬取的，重新运行爬取会跳过已经爬取的
