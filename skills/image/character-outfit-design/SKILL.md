---
name: character-outfit-design
description: "Design photorealistic fashion pictures for a user-selected person or character: original outfits, four-view garment samples, outfit try-on, and controlled makeup and hair styling. Use for 服装图片设计, 四视图样衣, 人物换装, 妆造图片, and garment image review or repair; do not use to extract an existing outfit unchanged."
metadata:
  version: "1.0.1"
---

# 角色的服装设计

Build one approved character look through two linked stages: first make the outfit physically credible as a four-view sample, then transfer it to the user-selected person or character reference while designing only the requested makeup and hair styling. Keep both reusable templates unchanged; put current-look detail only inside their placeholders.

## Authority

Apply this order when information conflicts:

1. The user's explicit garment, coverage, color, material, accessory, makeup, hair, and keep/remove decisions.
2. Image 1, the user-selected person or character reference, for identity, body, hair state, pose, layout, scene, lighting, and image expression.
3. Image 2, the approved outfit, for the complete garment, accessory, footwear, construction, and wearing logic.
4. Images 3–N only for the corresponding details they were supplied to clarify.
5. The filled `{{服装设计}}` block and the two `{{用户输入}}` styling fields under “保留的妆造 / 不保留的妆造” for the current look.

Garment references cannot change the selected subject's identity. Identity references cannot replace, simplify, or restyle an approved garment. Makeup styling can change only the explicitly controlled cosmetic and hair variables, never facial identity, bone structure, age, body, or skin identity.

## Route the Request

- **Design or prompt only:** read [references/design-brief.md](references/design-brief.md), write the design inside the braces of [assets/four-view-template.txt](assets/four-view-template.txt), and return or save the filled prompt.
- **Generate a four-view image:** create the filled prompt as above, then use the available image-generation capability. Save both the prompt and final image in the project workspace.
- **Review or repair a garment or character asset:** read [references/review-and-repair.md](references/review-and-repair.md). Diagnose the visible result before deciding whether to rerender unchanged or revise one primary variable.
- **Put an approved look on the selected person or character and design makeup/hair:** only after the user approves the design or four-view sample, read [references/character-try-on.md](references/character-try-on.md) and [references/makeup-styling.md](references/makeup-styling.md), then fill [assets/character-styling-template.txt](assets/character-styling-template.txt).
- **Need structural calibration:** read the single example in [references/example-filled-design.md](references/example-filled-design.md); do not copy its aesthetic by default.

## Workflow

1. Convert the user's concept into one coherent outfit with explicit pieces, silhouette, layer order, real materials, construction, closures, attachment points, footwear, accessories, and fixed view-consistency anchors.
2. Copy the four-view template verbatim and replace only `{{填写具体服装设计与款式}}`.
3. Render one 16:9 horizontal four-view air-mannequin sheet on a real white-wall background with phone-photo realism; inspect and repair it until the outfit identity is stable.
4. Wait for explicit approval of the design or four-view sample before putting it on the selected person or character.
5. Use the base image supplied or selected by the user; do not assume a particular character, project, or local filename. Treat it as Image 1 and the approved outfit as Image 2; add Images 3–N only when they clarify named details.
6. Copy the character-styling template verbatim. Fill only the keep and do-not-keep styling fields with the requested or newly designed makeup/hair decisions. Do not rewrite the shared template around them.
7. Generate the character styling asset while preserving Image 1's person and complete image structure and Image 2's complete outfit identity.
8. Inspect the actual result for identity, outfit fidelity, makeup control, consistent panels, complete hands and feet, realistic contact, and real texture. Version every accepted rerender instead of overwriting prior results.

## Non-negotiable Invariants

- The universal four-view and character-styling templates stay concise and unchanged.
- All abstract concepts must become visible garment decisions inside `{{服装设计}}`; visual effects are not substitutes for materials or construction.
- The air mannequin is fully invisible. Only clothing and non-body worn objects appear.
- Four views show one frozen design, not four variations.
- A photorealistic sample needs real thickness, seams, folds, reflections, support, gravity, contact, and floor shadows.
- Do not default to game armor, generic metallic bodysuits, floating fantasy objects, or concept-art environments.
- Do not put the design on the selected person or character before explicit design approval.
- In a character asset, Image 1 remains the same person and image; Image 2 remains the same outfit. Never mix their identity authority.
- Makeup must preserve recognizable identity, bone structure, age, skin tone, and real skin texture. Do not add unrequested fantasy markings, colored contacts, heavy retouching, or hair changes.
- Check every visible hand, foot, arm, leg, face, and repeated panel. A single isolated anatomy or cropping defect is a render bug candidate, not automatic evidence that the prompt or workflow is wrong.
- Nude base-model sheets may inform body structure but never make the output nude by default.

## Deliverables

- **Filled prompt:** the complete universal template with the current design inside `{{ }}`.
- **Rendered sample:** the saved four-view image plus its filled prompt path.
- **Review:** acceptance status, visible evidence, and the single next repair variable.
- **Character styling prompt:** the complete reusable try-on template with explicit keep/do-not-keep makeup and hair controls.
- **Character styling asset:** the saved look image for the selected person or character, the exact base image, approved garment source, final prompt, and version.
