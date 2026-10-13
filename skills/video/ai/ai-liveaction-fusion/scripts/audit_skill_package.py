#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

required=[
'SKILL.md','README.md','CHANGELOG.md','agents/openai.yaml',
'templates/video_editing_instruction_template.md','templates/material_lock_template.md','templates/film_texture_template.md','templates/shot_breakdown_template.md','templates/pure_ai_shot_template.md','templates/shot_fact_card_template.md','templates/storyboard_image_prompt_template.md','templates/storyboard_binding_manifest_template.md','templates/candidate_status_manifest_template.md',
'references/output_contract.md','references/source_authority_rules.md','references/camera_override_rules.md','references/reference_availability_rules.md','references/script_interpretation_rules.md','references/project_specific_overrides.md','references/project_workspace_rules.md','references/batch_execution_delivery_rules.md','references/shot_segmentation_rules.md','references/shot_breakdown_rules.md','references/spatial_lens_matching_rules.md','references/camera_scene_projection_rules.md','references/film_texture_rules.md','references/lighting_fusion_rules.md','references/platform_asset_binding_rules.md','references/platform_wording_rules.md','references/scene_continuity_rules.md','references/prompt_failure_diagnostics.md','references/storyboard_image_workflow.md','references/shot_fact_lineage_rules.md','references/storyboard_image_prompt_rules.md',
'checklists/intake_qc.md','checklists/material_lock_qc.md','checklists/film_texture_qc.md','checklists/shot_breakdown_qc.md','checklists/take_review_qc.md','checklists/repair_qc.md','checklists/storyboard_image_qc.md','checklists/storyboard_selection_qc.md',
'templates/project_agents_template.md','scripts/validate_skill_contract.py','scripts/test_validate_skill_contract.py','scripts/validate_storyboard_image_prompt.py','scripts/test_validate_storyboard_image_prompt.py','scripts/validate_camera_scene_projection_card.py','scripts/test_validate_camera_scene_projection_card.py','scripts/audit_skill_package.py']
for rel in required:
    if not (ROOT/rel).is_file(): errors.append(f'missing: {rel}')

skill=(ROOT/'SKILL.md').read_text()
readme=(ROOT/'README.md').read_text()
changelog=(ROOT/'CHANGELOG.md').read_text()
if '# AI Live-Action Fusion Skill v4.2.2' not in skill: errors.append('SKILL title version mismatch')
if '# AI Live-Action Fusion Skill v4.2.2' not in readme: errors.append('README version mismatch')
if '## 4.2.2 — 2026-09-03' not in changelog: errors.append('CHANGELOG missing 4.2.2')

front=skill.split('---',2)[1]
if 'name: ai-liveaction-fusion' not in front: errors.append('SKILL canonical name mismatch')
keys=[]
for line in front.splitlines():
    if ':' in line and not line.startswith(' '): keys.append(line.split(':',1)[0].strip())
for key in keys:
    if key not in {'name','description'}: errors.append(f'unsupported/extra SKILL frontmatter key: {key}')

openai_yaml=(ROOT/'agents/openai.yaml').read_text()
for token in ['display_name:', 'short_description:', 'default_prompt:', '$ai-liveaction-fusion', 'allow_implicit_invocation: true']:
    if token not in openai_yaml: errors.append(f'agents/openai.yaml missing: {token}')

for token in ['六栏逐镜','空间透视与镜头匹配','最终画面','VFX','空间锚点不得覆盖景别','项目要求与 Skill 核心分离原则','镜头—场景投影','主导可见表面','空间边界','可见人物状态锁定','@分镜图','镜头事实卡','/分镜图','候选图','project_workspace_rules.md','batch_execution_delivery_rules.md','candidate_status_manifest_template.md','project_agents_template.md']:
    if token not in skill: errors.append(f'SKILL missing: {token}')

for p in [ROOT/'SKILL.md', ROOT/'README.md', *(ROOT/'references').glob('*.md')]:
    txt=p.read_text()
    for forbidden in ['旧视频提示词','旧提示词','迁移证据']:
        if forbidden in txt: errors.append(f'active documentation contains obsolete input concept {forbidden}: {p.relative_to(ROOT)}')

shot_template=(ROOT/'templates/shot_breakdown_template.md').read_text()
shot_order=['### 构图与景别','### 背景与空间','### 空间透视与镜头匹配','### 光源与融合','### 最终画面','### VFX']
pos=[]
for t in shot_order:
    i=shot_template.find(t)
    if i<0: errors.append(f'shot template missing {t}')
    pos.append(i)
if all(i>=0 for i in pos) and pos!=sorted(pos): errors.append('shot template column order wrong')
for old in ['### 视频内容','### 画面内容']:
    if old in shot_template: errors.append(f'shot template contains old column {old}')

spatial=(ROOT/'references/spatial_lens_matching_rules.md').read_text()
for token in ['焦平面','景深','视差','环境动态','空间锚点','地墙交界','俯拍']:
    if token not in spatial: errors.append(f'spatial rules missing {token}')

projection=(ROOT/'references/camera_scene_projection_rules.md').read_text()
for token in ['人物屏幕空间姿态拓扑','主导可见表面','地墙交界','资产原视角','门、窗与空间边界拓扑','摄影机侧','人物侧','静态提示词编译','视频提示词编译','QC 硬失败']:
    if token not in projection: errors.append(f'projection rules missing {token}')

fact_template=(ROOT/'templates/shot_fact_card_template.md').read_text()
for token in ['## 镜头—场景投影','人物姿态拓扑','表面分布','资产原视角级别','空间边界','边界跨越时序','首 / 中 / 尾投影变化']:
    if token not in fact_template: errors.append(f'shot fact template missing {token}')

batch=(ROOT/'references/batch_execution_delivery_rules.md').read_text()
for token in ['参考图预算','部分成功','current_best','输出技术预检']:
    if token not in batch: errors.append(f'batch rules missing {token}')

candidate=(ROOT/'templates/candidate_status_manifest_template.md').read_text()
for token in ['current_best','superseded_by','正式 `/分镜图` 权威']:
    if token not in candidate: errors.append(f'candidate manifest missing {token}')

lighting=(ROOT/'references/lighting_fusion_rules.md').read_text()
for token in ['光比','禁止空话','接触阴影']:
    if token not in lighting: errors.append(f'lighting rules missing {token}')

contract=(ROOT/'references/output_contract.md').read_text()
for t in shot_order:
    if t not in contract: errors.append(f'output contract missing {t}')

# Every internal path referenced by SKILL / README must exist.
for doc in [skill,readme]:
    for rel in re.findall(r'`((?:templates|references|checklists|scripts)/[^`]+)`',doc):
        if not (ROOT/rel).exists(): errors.append(f'broken internal reference: {rel}')

# All templates are one markdown code block.
for p in (ROOT/'templates').glob('*.md'):
    txt=p.read_text().strip()
    if not (txt.startswith('```markdown\n') and txt.endswith('\n```')): errors.append(f'template not exact markdown block: {p.name}')

# Standard shot examples must use v3 columns and no old columns.
for p in (ROOT/'examples').rglob('*.md'):
    txt=p.read_text()
    if '# 逐镜分解' in txt:
        for t in shot_order:
            if t not in txt: errors.append(f'example missing v3 column {t}: {p.relative_to(ROOT)}')
        for old in ['### 视频内容','### 画面内容']:
            if old in txt: errors.append(f'example contains old column {old}: {p.relative_to(ROOT)}')

# No release junk.
for p in ROOT.rglob('*'):
    if p.name in {'.git','__pycache__','.DS_Store'} or p.suffix=='.pyc': errors.append(f'release junk: {p.relative_to(ROOT)}')

if errors:
    print('AUDIT FAIL')
    for e in sorted(set(errors)): print('-',e)
    sys.exit(1)
print('AUDIT PASS')
