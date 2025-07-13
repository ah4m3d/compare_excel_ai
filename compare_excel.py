import argparse, json, tomllib, pandas as pd
from llm_summariser import summarise

def compare_rows(row, col_left, col_right):
    left = json.loads(row[col_left])
    right = json.loads(row[col_right])
    diffs = {
        k: [left.get(k), right.get(k)]
        for k in set(left) | set(right)
        if left.get(k) != right.get(k)
    }
    return diffs

def run(path, anchor, left, right, out):
    df = pd.read_excel(path, dtype=str)
    diff_rows = []

    for _, row in df.iterrows():
        changes = compare_rows(row, left, right)
        if changes:
            diff_rows.append({"mbruid": row[anchor], "changes": changes})

    if not diff_rows:
        print("No differences found 🎉")
        return

    diff_df = pd.json_normalize(diff_rows, sep=".")
    summary = summarise(diff_rows)
    print("LLM summary:\n", summary)

    with pd.ExcelWriter(out, engine="openpyxl") as xl:
        diff_df.to_excel(xl, sheet_name="Mismatches", index=False)
        pd.DataFrame([{"summary": summary}]).to_excel(xl, sheet_name="Summary", index=False)

    print(f"Done. Results written to {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Compare two JSON columns in Excel")
    ap.add_argument("file", help="Path to Excel file")
    ap.add_argument("--anchor", default="mbruid")
    ap.add_argument("--left", default="json_1_col_name")
    ap.add_argument("--right", default="json_2_col_name")
    ap.add_argument("--out", default="comparison_output.xlsx")
    args = ap.parse_args()
    run(args.file, args.anchor, args.left, args.right, args.out)
