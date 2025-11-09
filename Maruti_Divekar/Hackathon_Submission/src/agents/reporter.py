from __future__ import annotations
from typing import List, Dict, Any
import datetime
import json
import os
from src.utils.config import load_settings

SETTINGS = load_settings()

class ReporterAgent:
    def __init__(self, out_dir: str = './outputs'):
        os.makedirs(out_dir, exist_ok=True)
        self.out_dir = out_dir

    def build_report(self, query: str, plan: Dict[str,Any], analyses: Dict[str,Any], claims: List[Dict[str,Any]]):
        ts = datetime.datetime.now(datetime.UTC).isoformat()
        md_lines = [f"# Research Report", f"**Query:** {query}", f"**Generated:** {ts}", ""]
        md_lines.append("## Evidence")
        refs = {}
        for c in claims:
            for e in c.get('evidence',[]):
                if e.get('url'):
                    refs[e['id']] = e['url']
        for cid, url in refs.items():
            md_lines.append(f"- [{cid}] {url}")
        md_lines.append("")
        md_lines.append("## Claims & Evidence")
        for c in claims:
            v = f"[citation:{c['evidence'][0].get('url','unknown')}]" if c.get('evidence') else ""
            verified_mark = "✅" if c.get('verified') else "❌"
            md_lines.append(f"### {c['claim_id']} {verified_mark}")
            md_lines.append(f"{c['claim']} {v}")
            if c.get('notes'):
                md_lines.append(f"_Notes_: {'; '.join(c['notes'])}")
            md_lines.append("")
        md = '\n'.join(md_lines)
        json_artifact = {'query': query, 'plan': plan, 'claims': claims, 'meta': {'generated': ts}}
        md_path = os.path.join(self.out_dir, f"report_{int(datetime.datetime.now(datetime.UTC).timestamp())}.md")
        json_path = md_path.replace('.md', '.json')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_artifact, f, indent=2)
        return {'md_path': md_path, 'json_path': json_path, 'markdown': md}
