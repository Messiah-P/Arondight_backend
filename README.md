<div align="center">

# Arondight

<img src="public/Arondight.png" height="180" width="180" alt="Arondight">

</div>


## 1、功能

- 主要功能
  - [x] 使用FastAPI提供接口服务
  - [x] 使用线程池和数据库进行任务并发控制
  - [x] 数据库事务管理
  - [x] Bark消息推送
- Pixiv相关功能
  - [x] 通过Cookie获得用户的关注画师信息
  - [x] 支持收集关注画师作品
  - [x] 支持收集日榜作品
  - [x] 支持单图、多图、动图的原图下载
  - [x] 文件整理
    - [x] 文件重命名
    - [x] 修改作品上传日期
    - [x] 按作者名归类

TODO

- [ ] 用户收藏作品的下载
- [ ] Docker安装部署
- [ ] 前端

## 2、基本使用
1. 配置数据库：/controller/config/config.yml
2. 安装依赖后执行
```bash
python /controller/main.py
```
## 许可证

本项目采用 **Apache-2.0 license** 进行许可。您可以根据许可证的条款自由地使用、修改和分发本项目。

## 版权声明

本工具仅用于个人学习和非商业用途。所有通过本工具下载的Pixiv作品的版权归原作者所有。

## 感谢

衷心感谢所有在 **[PIXIV](https://www.pixiv.net/)** 上分享精彩作品的艺术家们。