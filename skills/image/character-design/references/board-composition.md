# 确定性参考板排版

使用 [compose_board.py](../scripts/compose_board.py) 拼接已验收面板，不重绘脸、服装或状态。需要 Python 3.10+ 与 Pillow；先检查本机实际运行时，不自动安装或改变环境。

```text
python3 <skill-root>/scripts/compose_board.py --config <project>/board-layout.json --output <project>/C01-base-v001.png
```

## 配置

配置为JSON，`source`相对于配置文件所在目录解析。下例八个文件必须是实际面板；角色验收在调用前完成，脚本不识别人脸。

```json
{
  "style": "realistic",
  "output_size": [3072, 4096],
  "background": "#ffffff",
  "allow_upscale": false,
  "panels": [
    {"role": "head_front", "source": "panels/head-front.png"},
    {"role": "head_45", "source": "panels/head-45.png"},
    {"role": "head_side", "source": "panels/head-side.png"},
    {"role": "head_back", "source": "panels/head-back.png"},
    {"role": "half", "source": "panels/half.png"},
    {"role": "body_front", "source": "panels/body-front.png"},
    {"role": "body_side", "source": "panels/body-side.png"},
    {"role": "body_back", "source": "panels/body-back.png"}
  ]
}
```

`style`取 `realistic`、`cg`、`aaa`；AAA需增加唯一的`body_right`。AAA的`body_side`表示角色左侧；普通三视图表示所选90°侧面。每个角色、状态单独合成，不允许缺项、重复或未知角色面板。

源图是条带或宫格时，为每个面板明确填写`crop: [x, y, width, height]`，坐标为应用EXIF方向之后的像素。按真实图尺寸和已知布局确定分区；有留白和分隔线时先看图，不盲用等分。不会自动识别面部或生成缺失视角。

默认上方28%高度为头部四视图，下方左60%宽度为全身三/四视图，右侧为半身。面板等比缩放后居中留白，不拉伸、不自动裁掉内容。可按源图调整布局：所有面板都填写`box: [x, y, width, height]`，框必须在画布内且互不重叠。裂变复制基础板配置，只替换对应源图路径；画幅、框和裁切职责保留，除非新配件确实需要扩展空间并另记布局版本。

## 输出与限制

输出PNG与同名`.png.json`回执，包含实际尺寸、每个面板裁切框、布局框、放置区域、缩放、源文件摘要和警告。任一输出已存在即拒绝覆盖，使用新版本名。

默认不放大源图；信息不足时图像以原尺寸留白，回执提示改善源图。明确设置`allow_upscale: true`可放大，但回执记录上采样，不宣称新增细节。缩小后也需检查五官与衣物可读性，必要时调整分区或修源图。

检查完整头顶、手脚、服装外延；脚本只能保证所给裁切区域完整放入框，不能发现源图本就缺脚或裁切框切掉头发。排版回执不能替代视觉验收。
