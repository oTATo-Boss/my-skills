# 正常人体比例3D动画预设

- **标识**：`normal-human-proportions-3d-animation`
- **预设版本**：`1.0.1`
- **适用模式**：通用3D（`cg`）
- **适用模板**：`portrait`、`head-four`、`half`、`body-three`、`board`
- **控制范围**：自然人体结构与比例、动画化面部建模、皮肤与眼睛表现、立体发束及整体3D渲染。

## 风格提示词

```text
Use case: stylized-concept.
Create an original character in pure stylized 3D feature-animation art direction. For modeling and rendering calibration, use the clear animated-character stylization of KPop Demon Hunters: visibly designed geometry and an animated-feature face, not a photographic-looking person with softened skin. This is an art-direction anchor only; the separately supplied character design determines the person, age, gender, ethnicity, hairstyle, hair color, clothing and personality.

Normal human proportions apply to the BODY: plausible human anatomy, coherent head-to-body relationship, limbs, hands and feet appropriate to the specified age and body type. They do not require photorealistic facial proportions or a photographic head. Keep expressive, deliberately designed animation facial proportions, with eyes enlarged relative to real human eyes in a controlled, coherent way. Preserve an adult's specified age and facial individuality when the character is an adult; do not make a childlike doll or chibi figure. Do not impose one fixed head-to-body ratio on every character.

Clearly authored 3D facial sculpting: intentional clean cheek, jaw, nose and lip volumes; expressive, designed eyes and brows; clear, deliberately shaped eyelids; sculpted simplified nose and lip planes; art-directed facial proportions and clean dimensionally shaded surfaces. Retain the individual character's face silhouette, eye-shape character, ethnicity, skin tone and personality while translating them into this visibly animated 3D shape language. Facial stylization must be unmistakable, not merely subtle smoothing or beauty retouching on a realistic human face.

Skin has a smooth, subtly varied animation shader, soft restrained subsurface scattering, clean broad gradients and controlled highlights. Detail comes from modeled forms and art-directed shading, with very restrained surface microtexture. Eyes have a designed iris and controlled readable highlights integrated with the stylized face, not a photographic eye transplanted into a CG head. Avoid photographic human skin, dense pores, peach fuzz, photoreal digital doubles, AAA realistic game-head materials, waxy plastic dolls and oversized childlike toy eyes.

Hair uses coherent, dimensional modeled locks and layered sculpted strands, readable volume and art-directed highlights in the same feature-animation language. Keep the specified hairstyle and hair color; do not turn the render into a photorealistic groom-hair beauty portrait. Clothing and accessories have dimensional geometry and readable material differences within the same animated rendering language. Any separately requested exact product geometry or realistic product material is a local product requirement; it does not make the character's face, skin or hair photorealistic.

Deliver a visibly modeled, fully rendered 3D animated character with deliberate feature-animation stylization. Avoid flat 2D artwork, cel-shaded substitutes, photographic portraiture and a near-realistic digital human. The movie calibration controls ONLY modeling and rendering language: do not copy its protagonists' faces, purple hair, costumes, weapons or poses, and do not import its corridor or dramatic blue-magenta scene lighting. Use the background, lighting, framing, view count and layout specified by the chosen character-design template. Actual identity or product photos, if supplied for those purposes, do not override this selected animation style.
```

## 使用边界

“正常人体比例”约束身体结构与头身关系，不能解释成写实脸、真实皮肤或真人感CG。面部采用明确的动画化比例、设计过的眼睑与鼻唇块面；眼睛允许协调地大于真人比例。年龄感、具体脸型及体型按角色方案保持，不固定为年轻女性或某种族裔。已有角色身份按其确认资料继承，并转换到本预设的动画建模语言。

预设名称保持用户指定的通用名称。提示词内部保留原项目有效的动画电影造型/渲染校准锚点，作为质感与风格化强度参照，不绑定该电影的角色、发型、服装、场景或题材；不因改名而再次删除有效的风格描述。不要把本预设概括成“轻度风格化”“半写实”“真人质感3D”，也不要只注入预设名称而省略完整风格段。

本预设不包含人物设定、发型/发色、服装、品牌产品、背景、固定灯光、渲染器或宫格排版；这些由本次任务与原模板提供。用户未要求产品写实时，不自动为所有配饰添加写实例外。

## 来源与验证范围

由用户已确认的项目3D风格实际提示词提炼；用户于2026-11-11指定名称“正常人体比例3D动画预设”，要求作为可持续扩充的文字预设保存，不附确认图。`1.0.0`通用化时删除有效的电影造型锚点，又加入“Gently simplify”“subtle stylization”，其强度低于原项目明确的纯3D动画描述；用户随后反馈一次结果偏写实。该失败生成的完整实际输入未提供，不能据图片断言全部生成原因。`1.0.1`恢复原项目的造型/渲染锚点和较强风格化表述，分离身体比例与面部动画化要求，保留独立人物、产品和模板职责。

原项目效果曾获用户确认。`1.0.1`用完整预设与通用3D宫格模板做一次无参考纯文测试，相似酒红短发角色的面部动画化更明确；测试候选尚未获用户确认，半身取景偏长留档。[复测摘要](../evals/preset-style-fix-v1.7.1.json)只记录实际范围，图片留在工作项目，不在Skill内附确认图。单次测试不证明所有角色和模板稳定复现，不承诺仅凭预设即可保证人物或产品跨视图一致性。

## 后续测试确认（2026-11-11）

本次继续以完整预设与通用3D宫格模板纯文生成一位新的成年网红美女：摩卡棕长卷发、象牙白一字肩针织短裙、黑色及膝靴。用户查看后明确回复“OK，没问题，推送。”，确认本次视觉效果。头部四视、半身和完整全身三视齐全；左侧半身取景偏长及局部腰带遮挡/高度差异仍保留记录。该确认不扩展为其他人物、模板或跨视图稳定性的保证，详见[复测摘要](../evals/preset-style-fix-v1.7.1.json)。
