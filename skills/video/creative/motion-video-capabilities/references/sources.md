# 证据索引

资料核验日期：2026-10-19。按条目中的 S 编号查找原始来源和适用范围；在线文档和分支内容可能更新，具体实现承诺以对应版本与输入条件为准。

## 证据含义

- **文档**：支持来源明确说明的能力、输入、输出与条件。
- **源码或源码入口**：提供可定位的实现或工程入口；运行结果由实际执行记录证明。
- **作品说明**：提供作者或官方描述的效果实例及已披露的输入。
- **推导**：将已知操作、输入或信息范围组合得到的判断；能力条目按需标明。
- **实际验证**：由具体输入、环境版本、输出与观察记录构成；与文档和作品证据分别记录。

把环境是否接入某个框架、模型或编码器，与技术能力是否存在分别说明。来源名称用于追溯相应实现，能力正文保持框架中立。

## 来源目录

| 编号 | 来源 | 类型 |
| --- | --- | --- |
| [S01](#s01) | Agent Skills specification | 规范 |
| [S02](#s02) | Remotion：remotion-best-practices/SKILL.md | 官方 Skill |
| [S03](#s03) | Remotion：remotion-markup/SKILL.md | 官方 Skill |
| [S04](#s04) | HyperFrames：capability-menu.md | 官方能力菜单 |
| [S05](#s05) | video-shotcraft | 社区 Skill |
| [S06](#s06) | knowledge-explainer-skill | 社区 Skill |
| [S07](#s07) | ai-video-editing-skill | 社区 Skill |
| [S08](#s08) | chapter-progress-bar | 社区 Skill |
| [S09](#s09) | lower-thirds-skills | 社区 Skill |
| [S10](#s10) | website-to-hyperframes-demo | 官方项目案例 |
| [S11](#s11) | News article headline highlight | 官方案例说明 |
| [S12](#s12) | Transparent call-to-action overlay | 官方案例说明 |
| [S13](#s13) | Travel route on map with 3D landmarks | 官方案例说明 |
| [S14](#s14) | Product demo for Presscut | 官方案例说明 |
| [S15](#s15) | Three.js top 20 games sold ranking | 官方案例说明 |
| [S16](#s16) | Jonny Burger：Remotion Skills 制作记录 | 作者实现记录 |
| [S17](#s17) | Motion Canvas examples | 官方示例仓库 |
| [S18](#s18) | Manim example gallery | 官方文档与源码示例 |
| [S19](#s19) | MoviePy quick presentation | 官方文档 |
| [S20](#s20) | FFmpeg 滤镜与命令文档 | 官方文档 |
| [S21](#s21) | OpenCV homography tutorial | 官方文档 |
| [S22](#s22) | OpenCV optical flow tutorial | 官方文档 |
| [S23](#s23) | SAM 2 | 原始项目 |
| [S24](#s24) | SAM 2 paper，Appendix C | 原始论文 |
| [S25](#s25) | Robust Video Matting | 原始项目 |
| [S26](#s26) | Video Depth Anything | 原始项目 |
| [S27](#s27) | ProPainter | 原始项目 |
| [S28](#s28) | Three.js Points | 官方文档 |
| [S29](#s29) | Three.js post-processing | 官方文档 |
| [S30](#s30) | COLMAP tutorial | 官方文档 |
| [S31](#s31) | Editing Motion Graphics Video via Motion Vectorization and Transformation | 原始论文 |
| [S32](#s32) | Remotion：Rendering transparent videos | 官方文档 |
| [S33](#s33) | librosa beat_track（0.11.0） | 官方文档 |

## S01

**Agent Skills specification**

[原始来源](https://agentskills.io/specification) · 证据：文档。

- **关联能力**：格式与参考文件组织。
- **支持内容**：SKILL.md、元信息与 references 的格式和渐进加载依据。
- **适用范围**：适用于 Skill 的结构；视频技术能力由相应技术来源支持。

## S02

**Remotion：remotion-best-practices/SKILL.md**

[原始来源](https://github.com/remotion-dev/remotion/blob/main/packages/skills/skills/remotion-best-practices/SKILL.md) · 证据：文档。

- **关联能力**：能力索引与实现主题。
- **支持内容**：Remotion 官方 Skill 的画面、媒体、字幕、地图和渲染主题入口。
- **适用范围**：具体能力以相应主题和组件条件为准。

## S03

**Remotion：remotion-markup/SKILL.md**

[原始来源](https://github.com/remotion-dev/remotion/blob/main/packages/skills/skills/remotion-markup/SKILL.md) · 证据：文档。

- **关联能力**：G01–G05、V01–V04、U02、O01。
- **支持内容**：帧驱动图形、路径、文字、媒体和像素效果的实现类型。
- **适用范围**：组件与依赖存在版本差异；本文抽取能力语义，具体 API 以采用的版本为准。

## S04

**HyperFrames：capability-menu.md**

[原始来源](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/capability-menu.md) · 证据：文档。

- **关联能力**：图形、媒体与渲染能力范围。
- **支持内容**：HyperFrames 官方能力参考中列出的可见结果、模块和依赖。
- **适用范围**：条目涉及的素材、分析或生成服务各有成立条件。

## S05

**video-shotcraft**

[原始来源](https://github.com/Vincentwei1021/video-shotcraft/blob/main/SKILL.md) · 证据：文档、源码入口。

- **关联能力**：G03–G04、V02–V04。
- **支持内容**：镜头卡、图层运动和对应演示源码入口。
- **适用范围**：效果实例与其素材结构相关；本文使用效果及输入信息。

## S06

**knowledge-explainer-skill**

[原始来源](https://github.com/znyupup/knowledge-explainer-skill/blob/main/SKILL.md) · 证据：文档、源码入口。

- **关联能力**：G05–G06、D04。
- **支持内容**：双摆、量级变化和离散算法状态等自定义动画实例。
- **适用范围**：表现方式与科学计算正确性分别验证；示例参数属于该实现。

## S07

**ai-video-editing-skill**

[原始来源](https://github.com/znyupup/ai-video-editing-skill/blob/main/SKILL.md) · 证据：文档、源码示例。

- **关联能力**：M01–M04、C01、U01、U03。
- **支持内容**：素材剪辑、标题叠加、混音以及 ASR/视觉分析实例。
- **适用范围**：社区记录支持操作实例；性能、默认参数和平台兼容性以各原始工具资料或环境验证为准。

## S08

**chapter-progress-bar**

[原始来源](https://github.com/serenawangCU/chapter-progress-bar/blob/main/SKILL.md) · 证据：文档、源码入口。

- **关联能力**：G05、U03、O02–O03。
- **支持内容**：章节时间数据驱动独立进度图层。
- **适用范围**：核验时正文采用 HyperFrames；透明输出的具体链路有平台条件。

## S09

**lower-thirds-skills**

[原始来源](https://github.com/iart-ai/lower-thirds-skills/blob/main/skills/lower-thirds/SKILL.md) · 证据：文档、源码示例。

- **关联能力**：G01、C01、O02–O03。
- **支持内容**：Canvas 图文条、名称标识与透明输出实例。
- **适用范围**：文字、字体、动画和编码配置共同决定可交付范围。

## S10

**website-to-hyperframes-demo**

[原始来源](https://github.com/heygen-com/website-to-hyperframes-demo) · 证据：文档、源码。

- **关联能力**：G03–G04、C01。
- **支持内容**：页面捕获素材与代码动画、音频组成产品演示工程。
- **适用范围**：支持既有媒体进入代码时间轴的实例；页面组件化与截图输入分别说明。

## S11

**News article headline highlight**

[原始来源](https://www.remotion.dev/prompts/news-article-headline-highlight) · 证据：作品说明。

- **关联能力**：G01、G03、A01。
- **支持内容**：新闻截图的文字位置识别、标注和画面运动案例。
- **适用范围**：案例使用的文字位置与画面处理可作为依据；对象分离和原文字替换另有输入条件。

## S12

**Transparent call-to-action overlay**

[原始来源](https://www.remotion.dev/prompts/transparent-call-to-action-overlay) · 证据：作品说明。

- **关联能力**：G01、C01、O02。
- **支持内容**：独立订阅提示层、按钮状态和弹性动画案例。
- **适用范围**：透明目标需结合实际编码与接收端条件。

## S13

**Travel route on map with 3D landmarks**

[原始来源](https://www.remotion.dev/prompts/travel-route-on-map-with-3d-landmarks) · 证据：作品说明。

- **关联能力**：G07、D01。
- **支持内容**：地图路线、摄像机运动与三维地标的案例。
- **适用范围**：坐标、地图和地标资产是该类表现的输入。

## S14

**Product demo for Presscut**

[原始来源](https://www.remotion.dev/prompts/product-demo-for-presscut) · 证据：作品说明。

- **关联能力**：G04、O03。
- **支持内容**：用 React 重建可动画化 UI 的案例。
- **适用范围**：界面重建提供所创建元素的控制；真实产品逻辑和隐藏状态需要对应信息。

## S15

**Three.js top 20 games sold ranking**

[原始来源](https://www.remotion.dev/prompts/threejs-top-20-games-sold-ranking-1) · 证据：作品说明。

- **关联能力**：G05、D01–D02。
- **支持内容**：数据驱动三维高度、标签与摄像机运动的案例。
- **适用范围**：数据表达方式与源数据真实性是分别成立的条件。

## S16

**Jonny Burger：Remotion Skills 制作记录**

[原始来源](https://gist.github.com/JonnyBurger/5b801182176f1b76447901fbeb5a84ac) · 证据：作者源码与日志。

- **关联能力**：G03、O01、O03。
- **支持内容**：作者公开的界面动画、标志、转场与渲染迭代记录。
- **适用范围**：记录表明作者的实施过程；实际环境复现应有独立运行记录。

## S17

**Motion Canvas examples**

[原始来源](https://github.com/motion-canvas/examples) · 证据：源码、文档。

- **关联能力**：G03、D02。
- **支持内容**：视差、标志动画与光照的官方代码示例。
- **适用范围**：示例实现范围与其输入和渲染方式相关。

## S18

**Manim example gallery**

[原始来源](https://docs.manim.community/en/stable/examples.html) · 证据：文档、源码示例。

- **关联能力**：G02、G05–G06、D01–D02、D04。
- **支持内容**：数学、几何、三维曲面、摄像机与光照示例。
- **适用范围**：动画表达与所表达模型的正确性分别说明。

## S19

**MoviePy quick presentation**

[原始来源](https://zulko.github.io/moviepy/getting_started/quick_presentation.html) · 证据：文档。

- **关联能力**：M01–M04、C01、O01–O03。
- **支持内容**：从媒体、图像、文字或帧函数创建片段，并进行编辑、合成和效果处理。
- **适用范围**：具体媒体解码、像素处理与输出配置依赖实现环境。

## S20

**FFmpeg 滤镜与命令文档**

[滤镜文档](https://ffmpeg.org/ffmpeg-filters.html) · [命令文档](https://ffmpeg.org/ffmpeg.html) · 证据：文档。

- **关联能力**：M01–M04、C01–C04、V01–V04、A01、A04、A06、U01–U03、O01。
- **支持内容**：视频与音频滤镜、时间处理、合成、alpha 与像素处理；命令文档补充流复制、时间定位和准确寻址条件。
- **适用范围**：不同滤镜、编译依赖和输入约束分别成立；局部插值类处理保留其信息范围。

## S21

**OpenCV homography tutorial**

[原始来源](https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html) · 证据：文档。

- **关联能力**：C04、A07。
- **支持内容**：单应映射、平面对应关系及摄像机几何条件。
- **适用范围**：平面或满足特殊几何假设时的对应关系；曲面与复杂空间运动需要更多模型和数据。

## S22

**OpenCV optical flow tutorial**

[原始来源](https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html) · 证据：文档。

- **关联能力**：A02。
- **支持内容**：二维稀疏/稠密光流及运动估计假设。
- **适用范围**：二维位移提供运动线索，目标身份与三维姿态需相应信息。

## S23

**SAM 2**

[原始来源](https://github.com/facebookresearch/sam2) · 证据：原始项目文档、源码。

- **关联能力**：A03、C02–C03。
- **支持内容**：提示驱动的对象分割与视频遮罩传播。
- **适用范围**：输入提示、对象和模型条件影响结果；细节范围结合 S24。

## S24

**SAM 2 paper，Appendix C**

[原始来源](https://arxiv.org/html/2408.00714v2) · 证据：原始论文。

- **关联能力**：A02–A03。
- **支持内容**：SAM 2 在切镜、长遮挡、拥挤、相似对象和快速细小目标上的局限。
- **适用范围**：以论文对应模型和任务为范围描述质量条件。

## S25

**Robust Video Matting**

[原始来源](https://github.com/PeterL1n/RobustVideoMatting) · 证据：原始项目文档、源码。

- **关联能力**：A04、C02–C03、O02。
- **支持内容**：人像视频抠像，以及分别输出前景颜色和 alpha。
- **适用范围**：任务范围是人像视频；其他对象的精细抠像需相应依据。

## S26

**Video Depth Anything**

[原始来源](https://github.com/DepthAnything/Video-Depth-Anything) · 证据：原始项目文档、源码。

- **关联能力**：A05、D03。
- **支持内容**：视频相对/度量深度估计及深度数据输出。
- **适用范围**：深度模型类型、尺度与摄像机信息影响空间解释；可见表面信息与完整几何有区别。

## S27

**ProPainter**

[原始来源](https://github.com/sczhou/ProPainter) · 证据：原始项目文档、源码。

- **关联能力**：A06。
- **支持内容**：以视频、逐帧遮罩和模型进行内容修补。
- **适用范围**：修补根据已有信息与模型推断补充区域；隐藏场景的真实内容需额外观测或依据。

## S28

**Three.js Points**

[原始来源](https://threejs.org/docs/pages/Points.html) · 证据：文档。

- **关联能力**：D03、V04。
- **支持内容**：用几何点集和材质渲染点集合。
- **适用范围**：点数据来源另行成立；图像采样点状外观属于基于渲染与采样关系的实现推导。

## S29

**Three.js post-processing**

[原始来源](https://threejs.org/manual/pages/how-to-use-post-processing.html) · 证据：文档。

- **关联能力**：V01–V04、D02。
- **支持内容**：对已渲染图像执行景深、泛光、噪声等后处理。
- **适用范围**：处理对象是图像缓冲；真实光照和空间关系还需场景信息。

## S30

**COLMAP tutorial**

[原始来源](https://colmap.github.io/tutorial.html) · 证据：文档。

- **关联能力**：A07、D01、D03。
- **支持内容**：从重叠多视角图像恢复摄像机与几何，及纹理、光照和采集条件。
- **适用范围**：可重建范围依赖观测覆盖与场景条件；动态物体和未见表面需相应处理。

## S31

**Editing Motion Graphics Video via Motion Vectorization and Transformation**

[原始来源](https://arxiv.org/abs/2309.14642) · 证据：原始论文。

- **关联能力**：G01、G04、A06、O03。
- **支持内容**：从栅格动态图形恢复矢量运动表示的专门研究。
- **适用范围**：该研究对应动态图形及其方法假设；压平成片的对象级编辑需建立可编辑表示。

## S32

**Remotion：Rendering transparent videos**

[原始来源](https://www.remotion.dev/docs/transparent-videos) · 证据：文档。

- **关联能力**：O02。
- **支持内容**：透明视频输出中的编码、像素格式和配置要求。
- **适用范围**：内部 alpha、输出链路和接收端支持分别成立。

## S33

**librosa beat_track（0.11.0）**

[原始来源](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html) · 证据：官方文档：0.11.0。

- **关联能力**：U02。
- **支持内容**：拍点与速度估计、音频或起音强度输入、事件时间单位。
- **适用范围**：返回位置属于估计结果；分析帧、采样点和秒需正确换算到视频时间。
