# 彼岸图网爬虫程序

## 使用说明

1. 运行 `main.py`，采集图片列表到 `bian_pic_all.db` 文件中
2. 如果 `main.py` 报错，请在 `config.py` 中更换最新的 `User-Agent` 和 `yjs_js_security_passport`

    - `User-Agent`：使用任意浏览器访问彼岸图网，查看请求头得到
    - `yjs_js_security_passport`：使用任意浏览器访问彼岸图网，查看 Cookie 得到
3. 自定义配置 `config.py`

    ```py
    paths = [  # 采集 path 列表
        '4kdongman',
        '4kfengjing',
        '4kmeinv',
        '4kyouxi',
        '4kyingshi',
        '4kqiche',
        '4kdongwu',
        '4krenwu',
        '4kzongjiao',
        '4kbeijing',
        'pingban',
        'shoujibizhi',
    ]
    headers = {
        'User-Agent': '',  # 从浏览器拿到的 UA
        'Cookie': 'yjs_js_security_passport=',  # 从浏览器拿到的 Cookie
    }
    ```
4. 运行 `download.py` 下载图片