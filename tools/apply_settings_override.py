"""Troca a proteção da pasta do jogo em .claude/settings.json: libera só data/dmc3/GData.afs/ e Crimson/.
Rodado pelo LG (o agente não pode alterar as próprias permissões)."""
import json
from pathlib import Path

p = Path(__file__).resolve().parent.parent / ".claude" / "settings.json"
cfg = json.loads(p.read_text(encoding="utf-8"))
game = str(p.parent.parent / "Devil May Cry HD Collection")
protected = ["*", "data/*", "data/dmc1/**", "data/dmc2/**", "data/dmclauncher/**",
             "data/dmc3/*", "data/dmc3/Video/**", "data/dmc3/afs/**"]
deny = [d for d in cfg["permissions"]["deny"] if game not in d]
deny += [f"{tool}({game}/{pat})" for pat in protected for tool in ("Edit", "Write")]
cfg["permissions"]["deny"] = deny
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("deny atualizado:", *deny, sep="\n  ")
