# Validation receipt

- Standard skill frontmatter/structure validator passed.
- CLI test coverage: init/overwrite rejection, portable prompt loading, artifact parsing and gate results, rejected/ordered approval, invalidation and history, stale revisions, adaptation onboarding, UTF-8/DOCX/PDF extraction, editable ZIP, import consent reset/credential exclusion, write lock and skill-directory protection; added Chinese/general vs BL/English episode continuation cases.
- Independent forward test: a fresh evaluator read the runtime Skill only and created a recoverable Chinese mystery project, completed STAGE 1, persisted 3 artifacts, obtained 3/3 structural items, and left approval at 0. Workspace `/tmp/gleam-screenwriter-forward-test`; no live App or network calls. It reported App-specific sidebar wording, which was then adapted in static source instructions.
- Trigger query labels and additional content comparison scenarios are in the maintainer design directory. No with/without-skill ablation or measured trigger-accuracy benchmark has been run; do not claim those passed.
- No creative quality guarantee, global installation, commits or pushes.

Relocation initially exposed a /var vs /private/var path-alias boundary defect. Output checks now canonicalize physical paths before comparing against the Skill root. Final source and relocated archive reruns: all 16 tests passed in each location. The extracted Skill passed structure validation, and all archive hashes matched.
