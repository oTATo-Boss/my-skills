---
name: web-visual-effects
description: "Implement a selected web visual effect such as glass, gradient borders, blur, dithering, particles, globes, WebGL or Three.js objects. Use for concrete effect requests; Chinese triggers include 玻璃效果、渐变边框、粒子、地球、三维背景、激光。"
---

# 视觉效果与 3D

## 使用边界

用户要求和项目已有设计系统优先。沿用现有组件、样式和依赖；修改限定在本次目标内。下方参考文件是按需使用的配方，其固定数值、字体、色彩、版式和输出格式均可依项目调整。
只读取当前任务需要的参考；不默认加载整个库或全部总技能。额外工具、素材生成和新依赖由实际需要决定。
库中的版本、外部链接和代码片段来自旧合集；涉及实际安装或 API 时，先核对项目现有版本和对应官方资料。静态设计或素材示例不代表已实现的数据、交互或持久化。
已有专用技能、工具或组件能完成目标时复用它们，避免重复启动另一套流程。

## 执行方法

确定用户要的效果及其服务的内容，再选择最低复杂度的实现。先查现有 CSS 和依赖，装饰性效果通常可用 CSS 或 SVG，实际三维空间再使用 WebGL。

1. 保留文字、表单和主要操作的清晰度。把背景放在独立层，装饰层避免拦截点击；需要跟随鼠标时考虑触屏降级。
2. 配置可调整的颜色、强度、密度、尺寸和速度，不把效果参考里的配色强制应用到项目。
3. 画布尺寸随容器更新，像素比考虑设备性能。实例和监听器应在卸载时清理；不可见或后台的持续动画按需要暂停。
4. 对 WebGL 不可用、减少动态效果与较弱设备提供静态图、渐变或静止帧。控制透视、滤镜、粒子数量和纹理尺寸。
5. 图表保留 HTML 标题、单位、摘要或表格；canvas 中的文字不能作为唯一可访问的数据内容。
6. 在实际内容和容器中检查层级、裁切、交互和持续运行。只验证本次选定效果，不默认搭建重型 3D 场景。

## 按需参考

- 表面：`beautiful-shadows`、`css-border-gradient`、`progressive-blur`、`skeuomorphic-ui`。
- 结构和纹理：container / corner / masking / dither 系列。
- 三维对象：`threejs`、`webgl-3d-object`；地球：cobe / globe 系列。
- 激光与氛围：webgl / atmosphere 系列；物理：`matterjs`；嵌入效果：`unicorn-studio`、`vantajs`。
- `dither-charts` 附带图表引擎，采用它需保留数据的可访问表达；图标风格由项目已有库决定。

## 参考索引

仅当需要具体配方时查看 [index.md](references/index.md)，从中选择当前问题对应的参考文件。
