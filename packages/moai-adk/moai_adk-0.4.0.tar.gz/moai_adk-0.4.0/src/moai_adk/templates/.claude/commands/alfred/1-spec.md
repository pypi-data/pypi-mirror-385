---
name: alfred:1-spec
description: "[DEPRECATED] /alfred:1-plan 을 사용하세요 - 하위 호환성을 위한 별칭"
argument-hint: "제목1 제목2 ... | SPEC-ID 수정내용"
allowed-tools:
  - SlashCommand
---

# ⚠️ 명령어 변경 안내

`/alfred:1-spec` 명령어는 `/alfred:1-plan`으로 변경되었습니다.

## 🔄 변경 이유

- **"spec"**은 명세 작성만을 의미하지만, 실제로는 **계획 수립 전반**을 지원합니다
- **새로운 워크플로우**: **계획(Plan)** → 실행(Run) → 동기화(Sync)
- **철학**: "항상 계획을 먼저 세우고 진행한다"
- SPEC 작성, 브레인스토밍, 설계 논의 등 **계획 수립 전반** 지원

## ✅ 새로운 명령어로 자동 전환

아래 명령어를 자동으로 실행합니다:

```bash
/alfred:1-plan $ARGUMENTS
```

---

**이 별칭은 하위 호환성을 위해 제공되며, 향후 제거될 예정입니다.**
**가능한 빨리 `/alfred:1-plan`을 사용해주세요.**
