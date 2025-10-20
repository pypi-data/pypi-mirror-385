import argparse, json
from .core import _read_text, evaluate_document, _plot
def main():
    p=argparse.ArgumentParser()
    p.add_argument("file", help="Path ke .docx/.pdf/.txt skripsi")
    args=p.parse_args()
    text=_read_text(args.file)
    metrics, recs=evaluate_document(text)
    g1,g2=_plot(metrics)
    print(json.dumps({"report":metrics,"recommendations":recs}, ensure_ascii=False, indent=2))
    open("global_scores.png","wb").write(g1)
    open("per_bab_keywords.png","wb").write(g2)
    print("Tersimpan: global_scores.png, per_bab_keywords.png")
