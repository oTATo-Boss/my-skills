# Production and delivery records

Use the existing project schema when one exists. These fields illustrate the information necessary for resumption and evidence, not an additional required database.

```yaml
artifact_id: S03-04-render
version: 2
owner: cg
unit: {episode: E01, scene: S03, shot: S03-04}
inputs:
  - {id: camera, version: 3, path: source/camera-v03.json, sha256: ACTUAL_DIGEST}
  - {id: key, version: 2, path: assets/key-v02.glb, sha256: ACTUAL_DIGEST}
output: {path: work/S03-04/render-v02.mp4, sha256: ACTUAL_DIGEST}
media: {width: 1920, height: 1080, fps: "24000/1001", frames: 120}
runtime: {renderer: PROJECT_RENDERER, version: ACTUAL_VERSION, seed: 42}
reproduce: {project: source/scene-v04, command_record: work/S03-04/render-command.txt}
review: {mode: self, target_version: 2, target_sha256: ACTUAL_DIGEST}
evidence:
  decode: work/S03-04/decode.txt
  frames: work/S03-04/contact-sheet.png
  playback: not-verified
  listening: not-applicable-silent-shot
```

Replace uppercase example values with measured values; do not emit them as verified records. Frame count and duration must agree with the declared rational timebase within the encoder's documented behavior.

## External request lifecycle

```text
intent saved -> submitted with provider ID -> running -> downloaded -> inspected
                         |                         |
                         +-> outcome unknown ------+-> query/reconcile, not resubmit
```

Store the prompt/request version and non-secret asset identifiers. Some providers do not support idempotency or search by request key; label that limitation and ask for the missing external state when it prevents safe recovery.

## Delivery inventory

For each output, record purpose, path, exact version/hash, media specifications, source project path, dependency/license notes and verification state. A new render gets a new version even if its display filename is similar. Do not overwrite a prior delivery or copy an approval from a different hash.
