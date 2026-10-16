# Anime.js 官方创意示例目录

来源：juliangarnier/anime；版本 4.5.0；固定快照 01b81be1df6843ccfe0a71c0699a746bf740dd77。共 36 个示例入口，原始源码与共享素材一起保存。

检索英文关键词或中文用途，再读取当前案例的源码。依赖与集成信息见 [catalog.json](catalog.json) 和 [integration.md](integration.md)。

## 按创意目标快速选择

- 品牌开场：Logo 分层揭示、SVG 描边。
- 动态文字：乱码揭示、字词拆分、悬停反馈、非均匀打字。
- 数据与网格：中心扩散、周期表重排、SVG 图形。
- 交互：跟随鼠标、无限拖拽轮播、滚动吸附。
- 氛围与群体：萤火虫、程序化生物、星点、鸟群。
- 布局与叙事：卡片、导航、列表、固定滚动区块、无缝循环。
- 渲染结合：Canvas 2D 或 Three.js 对象变换。

## 生成与群体运动

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `additive-creature` | 叠加动画组成程序化生物；creature, additive, procedural | [本地代码](../assets/upstream/examples/additive-creature/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/additive-creature) | 按案例运行环境接入 |
| `additive-fireflies` | 萤火虫式光点与叠加运动；fireflies, particles, additive | [本地代码](../assets/upstream/examples/additive-fireflies/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/additive-fireflies) | 按案例运行环境接入 |
| `timeline-50K-stars` | 大量星点的事件与时间线编排；stars, particles, timeline | [本地代码](../assets/upstream/examples/timeline-50K-stars/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/timeline-50K-stars) | 按案例运行环境接入 |
| `timeline-refresh-starlings` | 鸟群式运动与可刷新的时间线；starlings, flock, timeline, refresh | [本地代码](../assets/upstream/examples/timeline-refresh-starlings/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/timeline-refresh-starlings) | 按案例运行环境接入 |

## 网格与几何

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `advanced-grid-staggering` | 二维网格分布、中心扩散与交错编排；grid, stagger, center | [本地代码](../assets/upstream/examples/advanced-grid-staggering/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/advanced-grid-staggering) | 按案例运行环境接入 |
| `stagger` | 多个目标的延迟和数值分布；stagger, distribution | [本地代码](../assets/upstream/examples/stagger/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/stagger) | 按案例运行环境接入 |

## 指针与拖拽

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `animatable-follow-cursor` | 可连续响应的跟随鼠标运动；cursor, follow, animatable | [本地代码](../assets/upstream/examples/animatable-follow-cursor/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/animatable-follow-cursor) | 按案例运行环境接入 |
| `draggable-infinite-auto-carousel` | 可拖拽且自动运行的无限轮播；draggable, infinite, carousel, loop | [本地代码](../assets/upstream/examples/draggable-infinite-auto-carousel/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/draggable-infinite-auto-carousel) | 按案例运行环境接入 |
| `draggable-mouse-scroll-snap-carousel` | 鼠标拖拽、滚动吸附与轮播联动；draggable, scroll, snap, carousel | [本地代码](../assets/upstream/examples/draggable-mouse-scroll-snap-carousel/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/draggable-mouse-scroll-snap-carousel) | 按案例运行环境接入 |
| `draggable-playground` | 拖拽参数与手感调试；draggable, interaction, debug | [本地代码](../assets/upstream/examples/draggable-playground/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/draggable-playground) | 按案例运行环境接入 |

## Logo 与 SVG

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `animejs-v4-logo-animation` | 分层 Logo 路径和文字的多阶段揭示；logo, svg, reveal, branding | [本地代码](../assets/upstream/examples/animejs-v4-logo-animation/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/animejs-v4-logo-animation) | 按案例运行环境接入 |
| `svg-graph` | SVG 图形中的线条与数据表现；svg, graph, data | [本地代码](../assets/upstream/examples/svg-graph/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/svg-graph) | 按案例运行环境接入 |
| `svg-line-drawing` | 沿 SVG 路径进行描边绘制；svg, draw, stroke, path | [本地代码](../assets/upstream/examples/svg-line-drawing/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/svg-line-drawing) | 按案例运行环境接入 |

## 布局过渡

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `auto-layout/accordion` | 折叠内容的布局变化；layout, accordion, collapse | [本地代码](../assets/upstream/examples/auto-layout/accordion/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/accordion) | 按案例运行环境接入 |
| `auto-layout/cards` | 卡片重排与布局连续性；layout, cards, reorder | [本地代码](../assets/upstream/examples/auto-layout/cards/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/cards) | 按案例运行环境接入 |
| `auto-layout/code` | 代码展示区域的布局变化；layout, code | [本地代码](../assets/upstream/examples/auto-layout/code/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/code) | 按案例运行环境接入 |
| `auto-layout/grid-columns` | 网格列数变化的连续过渡；layout, grid, columns | [本地代码](../assets/upstream/examples/auto-layout/grid-columns/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/grid-columns) | 按案例运行环境接入 |
| `auto-layout/nav` | 导航项状态与布局转场；layout, navigation | [本地代码](../assets/upstream/examples/auto-layout/nav/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/nav) | 按案例运行环境接入 |
| `auto-layout/onscroll` | 由滚动状态驱动的布局变化；layout, scroll | [本地代码](../assets/upstream/examples/auto-layout/onscroll/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/onscroll) | 按案例运行环境接入 |
| `auto-layout/periodic-table` | 大量数据单元的有序布局变化；layout, periodic, table, data | [本地代码](../assets/upstream/examples/auto-layout/periodic-table/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/periodic-table) | 按案例运行环境接入 |
| `auto-layout/planets` | 行星主题的元素布局转场；layout, planets | [本地代码](../assets/upstream/examples/auto-layout/planets/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/planets) | 按案例运行环境接入 |
| `auto-layout/todo-list` | 任务列表增删与重排；layout, todo, list | [本地代码](../assets/upstream/examples/auto-layout/todo-list/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/auto-layout/todo-list) | 按案例运行环境接入 |

## Canvas 与 Three.js

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `canvas-2d` | 在 Canvas 上绘制由参数驱动的动画；canvas, 2d, renderer | [本地代码](../assets/upstream/examples/canvas-2d/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/canvas-2d) | 按案例运行环境接入 |
| `threejs/transforms` | Anime.js 与 Three.js 对象变换联动；threejs, 3d, transforms, adapter | [本地代码](../assets/upstream/examples/threejs/transforms/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/threejs/transforms) | three, three/addons/controls/OrbitControls.js, tweaks, tweaks/gui |

## 时间线与循环

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `clock-playback-controls` | 带播放控制的时钟与同步动画；clock, timeline, playback, controls | [本地代码](../assets/upstream/examples/clock-playback-controls/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/clock-playback-controls) | 按案例运行环境接入 |
| `layered-css-transforms` | 多个动画叠加在同一 CSS 变换上；transforms, layered, additive | [本地代码](../assets/upstream/examples/layered-css-transforms/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/layered-css-transforms) | 按案例运行环境接入 |
| `timeline-seamless-loop` | 无缝循环的时间线构造；seamless, loop, timeline | [本地代码](../assets/upstream/examples/timeline-seamless-loop/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/timeline-seamless-loop) | 按案例运行环境接入 |

## 文字动效

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `irregular-playback-typewriter` | 非均匀节奏的打字播放；text, typewriter, irregular | [本地代码](../assets/upstream/examples/irregular-playback-typewriter/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/irregular-playback-typewriter) | 按案例运行环境接入 |
| `text/hover-effects` | 对悬停作出反馈的文字变化；text, hover, interaction | [本地代码](../assets/upstream/examples/text/hover-effects/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/text/hover-effects) | 按案例运行环境接入 |
| `text/scramble` | 可配置的文字扰动与逐渐稳定；text, scramble, reveal | [本地代码](../assets/upstream/examples/text/scramble/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/text/scramble) | tweaks, tweaks/gui |
| `text/scramble-tl` | 乱码揭示与时间线组合；text, scramble, timeline | [本地代码](../assets/upstream/examples/text/scramble-tl/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/text/scramble-tl) | 按案例运行环境接入 |
| `text/split-effects` | 按字、词、行拆分后的文字编排；text, split, characters, words, lines | [本地代码](../assets/upstream/examples/text/split-effects/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/text/split-effects) | tweaks/gui |
| `text/split-playground` | 文字拆分及参数调试；text, split, debug | [本地代码](../assets/upstream/examples/text/split-playground/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/text/split-playground) | tweaks, tweaks/gui |

## 滚动与响应式

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `onscroll-responsive-scope` | 滚动触发结合响应式作用域；scroll, responsive, scope | [本地代码](../assets/upstream/examples/onscroll-responsive-scope/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/onscroll-responsive-scope) | 按案例运行环境接入 |
| `onscroll-sticky` | 固定区块中的滚动动画；scroll, sticky, scrub | [本地代码](../assets/upstream/examples/onscroll-sticky/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/onscroll-sticky) | 按案例运行环境接入 |

## 性能与机制参考

| 示例 | 可复用思路 | 源码 | 额外依赖 |
|---|---|---|---|
| `timeline-stress-test` | 用于理解时间线负载的压力示例；stress, test, benchmark, timeline | [本地代码](../assets/upstream/examples/timeline-stress-test/index.js) · [上游](https://github.com/juliangarnier/anime/tree/01b81be1df6843ccfe0a71c0699a746bf740dd77/examples/timeline-stress-test) | 按案例运行环境接入 |
