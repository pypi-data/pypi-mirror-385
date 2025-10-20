---
name: alfred:2-build
description: "[DEPRECATED] /alfred:2-run 을 사용하세요 - 하위 호환성을 위한 별칭"
argument-hint: "SPEC-ID"
allowed-tools:
  - SlashCommand
---

# ⚠️ 명령어 변경 안내

`/alfred:2-build` 명령어는 `/alfred:2-run`으로 변경되었습니다.

## 🔄 변경 이유

- **"build"**는 코드 빌드만을 의미하지만, 실제로는 **계획 수행 전반**을 지원합니다
- **새로운 워크플로우**: 계획(Plan) → **실행(Run)** → 동기화(Sync)
- TDD 구현, 프로토타입 제작, 문서화 작업 등 **다양한 실행 시나리오** 지원

## ✅ 새로운 명령어로 자동 전환

아래 명령어를 자동으로 실행합니다:

```bash
/alfred:2-run $ARGUMENTS
```

---

**이 별칭은 하위 호환성을 위해 제공되며, 향후 제거될 예정입니다.**
**가능한 빨리 `/alfred:2-run`을 사용해주세요.**
