"""Install /crew into ~/.claude (Windows, macOS, Linux, WSL).

    python install.py              # skill + scout/builder/verifier agents
    python install.py --opusplan   # also set the default model to opusplan

Anything overwritten is backed up to ~/.claude/backups/crew-install/.
"""
import json, shutil, sys
from pathlib import Path

here = Path(__file__).resolve().parent
claude = Path.home() / ".claude"
backup = claude / "backups" / "crew-install"
backup.mkdir(parents=True, exist_ok=True)

dst = claude / "skills" / "crew"
if dst.exists():
    shutil.copytree(dst, backup / "crew", dirs_exist_ok=True)
shutil.copytree(here / "skills" / "crew", dst, dirs_exist_ok=True)
print("installed skill:", dst)

(claude / "agents").mkdir(parents=True, exist_ok=True)
for a in ("scout", "builder", "verifier"):
    d = claude / "agents" / f"{a}.md"
    if d.exists():
        shutil.copy2(d, backup / f"{a}.md")
    shutil.copy2(here / "agents" / f"{a}.md", d)
    print("installed agent:", d)

if "--opusplan" in sys.argv:
    p = claude / "settings.json"
    s = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if p.exists():
        shutil.copy2(p, backup / "settings.json")
    s["model"] = "opusplan"
    p.write_text(json.dumps(s, indent=2), encoding="utf-8")
    print("default model -> opusplan (Opus in plan mode, Sonnet otherwise)")

print("\nDone. Start a new session and type:  /crew <your request>")
