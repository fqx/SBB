

**SBB**( **S**ina **B**log **B**ook) 是一个用于下载指定新浪博客作者全部文章的脚本。

基于这些下载来的 HTML 文件，您可以借助 [Kindlegen](http://www.amazon.com/gp/feature.html?docId=1000765211) 来生成电子书，或者当作存档。

请在 Python 2.7.8 下使用。

## 用法
1. SBB.py (新浪博客地址) (desc|asc)
2. kindlegen package.opf 

排序开关是可选的，默认为按发表时间顺序排列（即 asc）。

例子：

- SBB.py http://blog.sina.com.cn/gongmin desc
- SBB.py http://blog.sina.com.cn/u/1239657051
	
## Roadmap
- [x] 首页增加时间戳
- [x] 'SELECT * FROM AllBlogPosts ORDER BY DatePosted DESC / ASC'
- [x] 生成package.opf，支持kindlegen打包
- [x] 支持目录和章节
- [ ] 增加下载图片选项

## 授权
Licensed under the Apache License, Version 2.0

##升级日志

###2015年2月15日

- [增加] 索引页面和文章页面增加时间戳。
- [增加] 文章排序选项，默认按发表时间顺序排列。
- [增加] 生成opf文件，支持kindlegen。
