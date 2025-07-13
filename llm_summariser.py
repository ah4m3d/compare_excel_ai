import requests, tomllib, textwrap, json

cfg = tomllib.load(open("settings.toml","rb"))["llm"]

def summarise(differences: list[dict]) -> str:
    prompt = textwrap.dedent(f"""
    You are an assistant summarising JSON diffs.

    <DIFFERENCES>
    {json.dumps(differences, indent=2)}
    </DIFFERENCES>

    Summarise in plain English, grouped by mbruid. Highlight which fields changed.
    """)
    resp = requests.post(
        cfg["endpoint"],
        json={"model": cfg["model"], "prompt": prompt, "stream": False},
        timeout=120,
    )
    return resp.json().get("response", "").strip()
