```json
{
  "status": "blocked",
  "gate": "<mode_arbitration | start_image | missing_source | task_input>",
  "code": "<E_错误码，取 SKILL.md / 对应 references 错误码表中的一个>",
  "message": "<一句话说明为什么被阻断>",
  "missing_fields": ["<缺失/冲突的字段路径，逐个列出；没有则为 []>"],
  "resume_hint": "<用户需补齐什么后本轮即可继续>"
}
```