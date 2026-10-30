# Route-specific production and QA

Read only the route in use. Companion implementation skills are optional: discover their actual installed entrypoints and tools before using them. None is a mandatory dependency of this method package.

| Route | Verify before scaling | Keep for reproduction | Likely failure |
| --- | --- | --- | --- |
| AI generation | Identity, temporal stability, action completion, readable product/form | Prompt and references, model/service version, seed when supported, provider task IDs | Correct first frame but failed action; inconsistent later shots |
| Live action | Actual media, frame rate, audio sync, usable coverage and permissions | Original media, timecodes, select ranges, edit decisions | Missing reverse angle, variable-rate drift, unusable dialogue |
| 2D/code | Key poses and a real rendered interval, exact frame seek, font readiness | Source, dependency lock, seed, render command, assets | Browser preview differs from export; text shifts after font load |
| 3D CG | Camera framing, material/light at delivery size, motion and render cost | Scene, models/textures, camera, simulation caches, renderer/version | Unapplied transforms, missing texture, nondeterministic physics |
| Hybrid | Consistent perspective, light, grain, shutter/motion blur, edges and sound | Original plates, masks, transforms, intermediate comps | Compositing seam, contact shadow mismatch, occlusion error |

## Acceptance by format

- **Explainer:** each visual implies a defensible claim; labels/units agree; examples distinguish model assumptions; narration and demonstration align.
- **Ad/launch:** the actual product and claims match provided evidence; final frame and requested channel versions are usable; UI screens are accurate.
- **Film/series:** scene intention is legible; performances, spatial relationships and continuity survive editing; episode boundaries preserve the intended state.
- **MV:** musical phrases shape progression; motifs develop; intentional sync anchors land; sound is the supplied/approved master or documented edit.
- **Motion experiment:** visual mechanism is deliberate, repeatable and readable; loop seams and endpoint behavior match the brief.

## Evidence levels

1. Metadata and decode establish that the media is technically readable.
2. Selected frames establish composition at those timestamps only.
3. Continuous playback establishes motion/cut behavior over the played interval.
4. Listening establishes audible content and mix over the heard interval.
5. Creative review checks the brief against the actual film and records defects.

List the observed interval for partial playback/listening. Keep unavailable checks pending; do not average technical passes into a creative quality score. A review should identify concrete timestamped issues and repairs, not invent a numerical quality grade.
