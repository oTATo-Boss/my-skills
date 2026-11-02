---
name: json-prompt-system
description: Generate or restore social-photo action-variable-layer JSON prompts for mirror selfies, front-camera selfies, third-person lifestyle photos, ecommerce clothing, and ecommerce try-on. Use when the user asks Codex to create, infer, translate, or repair JSON prompt actions from text or reference images, especially for pose, expression, composition, clothing-boundary interaction, phone-camera realism, and mode routing.
metadata:
  version: "2.1.0"
---

# JSON Prompt System

Use this skill to generate or restore pure action-variable-layer JSON for image prompts. It is standalone and does not depend on the original project backend, API wrapper, database, or UI.

## Workflow

1. Read `references/json-prompt-system/soul.md`, `flowchart.md`, `core/Role.txt`, `core/rule.txt`, and `core/workflow.txt`.
2. Judge the three inputs before writing: character reference, clothing reference, scene reference. Each one independently decides whether its block says "use reference N" or is written out in full (see `core/rule.txt` §12).
3. Determine the mode:
   - `mirror-selfie` for mirror/self-shot actions.
   - `front-camera-selfie` for front-camera/self-screen actions where the capture device stays out of frame.
   - `third-person` for external-photographer/third-person actions.
   - `ecommerce-clothing` for standalone clothing/product effect JSON.
   - `ecommerce-tryon` for upper-body try-on/ecommerce model effect JSON.
4. Read only the relevant mode folder under `references/json-prompt-system/modes/<mode>/`.
5. For lifestyle modes, also use the relevant core rules for image restore, women selfie presentation, expression intensity, pose invention, expressive pose translation, anatomy sanity, visual-anchor abstraction, and output density.
6. Output only the final JSON that matches the selected mode template. Do not output analysis, markdown fences, wrapper objects, `reply`, or `draft`.

## Mode Boundaries

- If the user locks a mode, keep that mode even when the image or text suggests another mode. Translate the reference into the locked mode instead of switching.
- Use `AUTO` behavior only when the user did not lock a mode: if an image is provided, judge by the image first; if no image is provided, judge by the user instruction.
- Do not mix view semantics. Mirror mode may use mirror/capture-in-frame logic; front-camera mode must not; third-person mode must use an external camera relationship.
- Ecommerce modes should not inherit lifestyle selfie aesthetics unless their own rules allow it.

## Product Boundaries

- Work with social-photo action variables first; character, clothing, and environment are filled only as far as the input requires (see `core/rule.txt` §12).
- Output only executable photo variables. Requests outside the action-variable layer do not enter the JSON.
- Treat these as product constraints, not wording tasks.
- This JSON is one part of a larger prompt stack: it does not reproduce the site-side markdown prompt, reference-image orchestration, or backend logic. It only fills what the JSON itself needs to stand alone.

## Output Boundaries

- Output hygiene: final JSON must not contain file paths, rule names, developer notes, or non-executable internal metadata.
- Do not output the original project wrapper format. The standalone skill output is pure JSON.
- When reference images exist for character, clothing, or scene: do not restate their concrete details. Write consistency requirements, boundary/fit relationships, and spatial or light direction only.
- When a reference is missing: fill the `角色与服装` and `环境与光线` blocks completely, including outfit categories, colors, materials, fit, scene, furnishings, lived-in traces, light source and time. Never leave those fields empty in that case.
- Never invent identity, a real person, a brand, or marketing copy in those blocks; describe what can be seen and executed.
- Keep output compact: preserve view composition, main action motif, expression intensity, body structure, hand/boundary mechanics, crop, and camera-relative direction without repeating the same anchor across fields.
- Hands placed on the chest, crotch, inner thigh, or pressing fabric are the highest-risk area: write finger separation, knuckle direction, contact surface, and both hands' positions, or move that hand to a safer spot.

## Reference Loading

- Entry and shared rules: `references/json-prompt-system/core/`
- Mode rules, templates, examples, and quality gates: `references/json-prompt-system/modes/`
- Use examples as calibration references, not as project output to copy.
