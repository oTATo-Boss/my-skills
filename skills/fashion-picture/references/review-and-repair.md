# Garment and Character Asset Review and Repair

Read the rendered image itself. The prompt is not evidence that the requested design appeared.

## Four-view Garment Acceptance Checks

1. **Design fidelity:** every locked garment, shoe, accessory, color, material, closure, and prohibited-substitution rule is respected.
2. **View consistency:** front, back, left, and right depict the same design. Check repeated-element count, side placement, hem length, seams, hardware, shoes, and accessory quantity.
3. **Physical credibility:** projecting parts have supports; transparent parts have thickness and edges; fabric responds to gravity and body volume; shoes contact the floor.
4. **Air mannequin:** no face, skin, hair, neck, hands, legs, feet, or visible mannequin shell appears. Garments retain believable support.
5. **Capture realism:** the white wall has texture and natural light; materials look photographed rather than rendered; shadows and reflections are plausible.
6. **Framing:** the four views are complete, similarly scaled, ordered front/back/left/right, and not cropped.

Accept only when there is no major identity, structure, material, or mannequin failure. Minor camera or lighting variation is acceptable when it does not alter the garment.

## Single-variable Repair

Choose one primary failure category:

- `DESIGN_DRIFT`
- `VIEW_INCONSISTENCY`
- `MATERIAL_FAKE`
- `ATTACHMENT_IMPOSSIBLE`
- `VISIBLE_BODY`
- `CAPTURE_OR_LAYOUT`

Preserve every accepted part. Revise only the design sentence or generation constraint that controls the primary failure, then render a new version.

For `VIEW_INCONSISTENCY`, strengthen exact count and attachment landmarks inside `{{服装设计}}`. If the same repeated structure fails again, reduce or consolidate that structure. Do not inflate the universal template.

For `MATERIAL_FAKE`, replace metaphorical material words with named real materials, edge behavior, thickness, fastening, and photographed surface response.

For `VISIBLE_BODY`, restate that the support is fully invisible and that empty openings reveal the real wall behind the garment, not a white mannequin surface.

Report: status, visible evidence, preserved elements, one repair variable, and new version path.

## Character Styling Asset Acceptance Checks

1. **Identity:** every face remains the same identity as Image 1; bone structure, age, skin tone, body proportions, and selected hair state are unchanged.
2. **Image preservation:** panel count, viewpoint, pose, framing, background, lighting, and overall composition follow Image 1.
3. **Outfit fidelity:** Image 2's complete garments, shoes, accessories, materials, sides, quantities, layers, and wearing relationships appear consistently wherever visible.
4. **Controlled styling:** only the filled keep-list makeup/hair changes appear; every do-not-keep item is absent; real pores, lip texture, lash structure, and hair detail remain visible.
5. **Physical fit:** neckline, shoulders, chest, waist, hips, sleeves, hosiery, and footwear have credible contact, tension, folds, occlusion, support, and gravity.
6. **Human integrity:** inspect every hand, finger group, foot, arm, leg, ear, and facial feature in every panel. Nothing is missing, duplicated, fused, cropped unexpectedly, or anatomically impossible.
7. **Capture realism:** skin, cloth, leather, metal, transparent materials, shadows, and reflections look photographed rather than rendered or plastic.

## Decide Whether to Rerender or Revise

- If identity, garment logic, makeup scope, or composition is systematically wrong, revise the single controlling prompt variable and preserve everything already accepted.
- If one otherwise-correct result has an isolated missing hand, fused finger group, accidental crop, or similar stochastic defect, rerender once with the exact same prompt and references before changing the workflow.
- If the same defect repeats, classify its controlling category and make one targeted revision. Do not accumulate defensive prose in either universal template.
- Save every rerender as a new version; never overwrite an accepted or diagnostically useful prior result.

Report: status, visible evidence, whether it is a stochastic rerender or prompt repair, preserved elements, and the new version path.
