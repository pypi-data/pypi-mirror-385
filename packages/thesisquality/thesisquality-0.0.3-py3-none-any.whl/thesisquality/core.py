import re
from typing import Dict, List
import matplotlib.pyplot as plt

def _read_text(path:str)->str:
    if path.lower().endswith(".docx"):
        from docx import Document
        d=Document(path); return "\n".join(p.text for p in d.paragraphs)
    if path.lower().endswith(".pdf"):
        from PyPDF2 import PdfReader
        r=PdfReader(path); return "\n".join(p.extract_text() or "" for p in r.pages)
    return open(path,"r",encoding="utf-8",errors="ignore").read()

def _detect_lang(s:str)->str:
    s2=s.lower()
    id_hits=sum(k in s2 for k in ["bab i","pendahuluan","metode","hasil","pembahasan","kesimpulan","daftar pustaka"])
    en_hits=sum(k in s2 for k in ["chapter 1","introduction","methods","results","discussion","conclusion","references","abstract"])
    return "id" if id_hits>=en_hits else "en"

def _section_patterns(lang:str)->Dict[str,List[str]]:
    if lang=="id":
        return {
            "BAB I": [r"\bBAB\s*I\b", r"\bPendahuluan\b"],
            "BAB II": [r"\bBAB\s*II\b", r"\bTinjauan Pustaka\b", r"\bLandasan Teori\b", r"\bKerangka Teori\b"],
            "BAB III": [r"\bBAB\s*III\b", r"\bMetode\b", r"\bMetodologi\b", r"\bBahan dan Metode\b"],
            "BAB IV": [r"\bBAB\s*IV\b", r"\bHasil\b"],
            "BAB V": [r"\bBAB\s*V\b", r"\bPembahasan\b", r"\bDiskusi\b"],
            "BAB VI": [r"\bBAB\s*VI\b", r"\bKesimpulan\b", r"\bSimpulan\b"],
            "KESIMPULAN": [r"\bKesimpulan\b", r"\bSimpulan\b"],
            "ABSTRAK": [r"\bAbstrak\b"],
            "DAFTAR PUSTAKA": [r"\bDaftar Pustaka\b", r"\bReferensi\b", r"\bRujukan\b"]
        }
    else:
        return {
            "BAB I": [r"\bChapter\s*1\b", r"\bIntroduction\b"],
            "BAB II": [r"\bChapter\s*2\b", r"\bLiterature Review\b", r"\bBackground\b", r"\bRelated Work\b", r"\bTheoretical Framework\b"],
            "BAB III": [r"\bChapter\s*3\b", r"\bMethods\b", r"\bMethodology\b", r"\bMaterials and Methods\b"],
            "BAB IV": [r"\bChapter\s*4\b", r"\bResults\b"],
            "BAB V": [r"\bChapter\s*5\b", r"\bDiscussion\b"],
            "BAB VI": [r"\bChapter\s*6\b", r"\bConclusion\b"],
            "KESIMPULAN": [r"\bConclusion\b"],
            "ABSTRAK": [r"\bAbstract\b"],
            "DAFTAR PUSTAKA": [r"\bReferences\b", r"\bBibliography\b"]
        }

def _find_spans(text:str, patterns:Dict[str,List[str]]):
    idx=[]
    for sec, pats in patterns.items():
        for p in pats:
            for m in re.finditer(p, text, flags=re.IGNORECASE):
                idx.append((m.start(), sec))
    idx=sorted(idx)
    spans={}
    for i,(pos,sec) in enumerate(idx):
        start=pos
        end=len(text) if i==len(idx)-1 else idx[i+1][0]
        if sec not in spans or (end-start) > (spans[sec][1]-spans[sec][0]):
            spans[sec]=(start,end)
    return spans

def _kw_coverage(s:str, kws:List[str])->float:
    s2=s.lower()
    return sum(1 for k in kws if k in s2)/max(1,len(kws))

def _per_bab_keywords(lang:str)->Dict[str,List[str]]:
    if lang=="id":
        return {
            "BAB I": ["latar belakang","rumusan masalah","tujuan","manfaat","hipotesis","kebaruan"],
            "BAB II": ["tinjauan pustaka","kerangka","konsep","teori","gap riset","model"],
            "BAB III": ["desain","sampel","inklusi","eksklusi","instrumen","validitas","reliabilitas","analisis statistik","etik"],
            "BAB IV": ["karakteristik","tabel","gambar","uji","p","ci","median","rerata"],
            "BAB V": ["interpretasi","perbandingan","implikasi","keterbatasan","bias","generalizabilitas"],
            "BAB VI": ["jawab tujuan","ringkas","kontribusi","saran"],
            "KESIMPULAN": ["jawab tujuan","ringkas","kontribusi","saran"]
        }
    else:
        return {
            "BAB I": ["background","problem statement","aims","objectives","novelty","hypothesis"],
            "BAB II": ["literature review","framework","conceptual","theory","research gap","model"],
            "BAB III": ["design","sample","inclusion","exclusion","instrument","validity","reliability","statistical analysis","ethics"],
            "BAB IV": ["characteristics","table","figure","test","p-value","confidence interval","median","mean"],
            "BAB V": ["interpretation","comparison","implication","limitation","bias","generalizability"],
            "BAB VI": ["answer objectives","summary","contribution","recommendation"],
            "KESIMPULAN": ["answer objectives","summary","recommendation","contribution"]
        }

def _count_refs(s:str):
    s2=s.lower()
    bracket=len(re.findall(r"\[(\d+)\]", s2))
    doi=len(re.findall(r"doi\.org\/|10\.\d{4,9}\/[-._;()\/:A-Z0-9]+", s, flags=re.IGNORECASE))
    url=len(re.findall(r"https?://", s2))
    return bracket+url+doi, doi

def _fig_table_count(s:str)->int:
    return len(re.findall(r"\b(fig(ure)?|gambar|tabel|table)\b", s, flags=re.IGNORECASE))

def _objective_alignment(intro:str, concl:str)->float:
    goals=re.findall(r"(tujuan|objective|aim)s?:?\s*(.+)", intro, flags=re.IGNORECASE)
    if goals:
        goal_text=" ".join(g[1] for g in goals)
    else:
        gs=re.findall(r"(rumusan masalah|problem statement):?\s*(.+)", intro, flags=re.IGNORECASE)
        goal_text=" ".join(g[1] for g in gs) if gs else intro[:2000]
    kw=[w for w in re.split(r"[,;.\n]", goal_text) if len(w.split())>=2][:10] or ["tujuan","objective"]
    s2=concl.lower()
    return min(1.0, sum(1 for k in kw if k.lower() in s2)/max(1,len(kw)))

def _normalize(v:float)->float:
    return max(0.0, min(1.0, v))

def evaluate_document(text:str):
    lang=_detect_lang(text)
    pats=_section_patterns(lang)
    spans=_find_spans(text, pats)
    kws=_per_bab_keywords(lang)
    total_len=max(1,len(text))
    refs_total, doi_total=_count_refs(text)
    figs=_fig_table_count(text)
    words=len(re.findall(r"\w+", text))
    paras=[p for p in re.split(r"\n\s*\n", text) if p.strip()]
    avg_para_len=sum(len(p.split()) for p in paras)/max(1,len(paras))
    sec_names=["BAB I","BAB II","BAB III","BAB IV","BAB V","BAB VI","KESIMPULAN"]
    per_bab={}
    for s in sec_names:
        if s in spans:
            st,en=spans[s]
            seg=text[st:en]
            length_pct=(en-st)/total_len
            cov=_kw_coverage(seg, kws.get(s,[]))
            presence=1.0
        else:
            seg=""; length_pct=0.0; cov=0.0; presence=0.0
        per_bab[s]={"presence":presence,"length_pct":_normalize(length_pct*4),"keyword_coverage":cov,"words":len(seg.split())}
    intro_txt=text[spans["BAB I"][0]:spans["BAB I"][1]] if "BAB I" in spans else text[:min(total_len,5000)]
    concl_txt=text[spans["KESIMPULAN"][0]:spans["KESIMPULAN"][1]] if "KESIMPULAN" in spans else (text[spans["BAB VI"][0]:spans["BAB VI"][1]] if "BAB VI" in spans else text[-min(total_len,5000):])
    cites_per_1k=refs_total/max(1,words/1000)
    doi_ratio=_normalize(doi_total/max(1,refs_total))
    visual_density=_normalize(figs/max(1,words/1500))
    heading_consistency=_normalize(sum(1 for s in sec_names if s in spans)/len(sec_names))
    method_rigor=per_bab["BAB III"]["keyword_coverage"] if "BAB III" in per_bab else 0.0
    results_completeness=_normalize(per_bab["BAB IV"]["keyword_coverage"]*0.6 + visual_density*0.4)
    discussion_depth=per_bab["BAB V"]["keyword_coverage"] if "BAB V" in per_bab else 0.0
    conclusion_strength=_normalize(per_bab["KESIMPULAN"]["keyword_coverage"]*0.5 + _objective_alignment(intro_txt, concl_txt)*0.5)
    structure_balance=_normalize(sum(per_bab[s]["length_pct"] for s in sec_names)/len(sec_names))
    readability_proxy=_normalize(1.0/(1.0+abs(avg_para_len-120)/120))
    global_quality=_normalize(0.1*heading_consistency+0.15*method_rigor+0.15*results_completeness+0.15*discussion_depth+0.15*conclusion_strength+0.1*_normalize(cites_per_1k/10)+0.1*doi_ratio+0.1*readability_proxy)
    est_pub="Q2–Q1 (heuristik)" if (global_quality>=0.8 and doi_ratio>0.5 and cites_per_1k>=8) else ("Q3–Q2 (heuristik)" if (global_quality>=0.65 and doi_ratio>0.3 and cites_per_1k>=4) else ("Q4 / Sinta 1–2 (heuristik)" if global_quality>=0.5 else "Prosiding/Copernicus/Sinta 3–6 (heuristik)"))
    rec=[]
    if per_bab["BAB I"]["keyword_coverage"]<0.7: rec.append("Perkuat BAB I: latar belakang, rumusan masalah, tujuan, kebaruan.")
    if method_rigor<0.7: rec.append("Perjelas BAB III: desain, sampel, kriteria, instrumen, validitas/reliabilitas, analisis, etik.")
    if results_completeness<0.7: rec.append("Perkaya BAB IV: tabel/gambar, ukuran efek, p/CI, narasi hasil.")
    if discussion_depth<0.7: rec.append("Perdalam BAB V: komparasi literatur 2020–2025, implikasi, bias, generalisasi.")
    if cites_per_1k<5: rec.append("Tingkatkan kepadatan sitasi dan kualitas sumber (DOI, jurnal bereputasi).")
    metrics={
        "license_spdx":"MIT OR Apache-2.0 OR BSD-3-Clause",
        "licenses_detail":["MIT","Apache-2.0","BSD-3-Clause"],
        "licenses_approvals":["OSI Approved","DFSG approved"],
        "language":lang,
        "words":words,
        "paragraphs":len(paras),
        "refs_total":refs_total,
        "doi_total":doi_total,
        "fig_table_total":figs,
        "cites_per_1k":round(cites_per_1k,2),
        "doi_ratio":round(doi_ratio,2),
        "visual_density":round(visual_density,2),
        "heading_consistency":round(heading_consistency,2),
        "structure_balance":round(structure_balance,2),
        "readability_proxy":round(readability_proxy,2),
        "conclusion_strength":round(conclusion_strength,2),
        "global_quality":round(global_quality,2),
        "est_publication":est_pub
    }
    for s in ["BAB I","BAB II","BAB III","BAB IV","BAB V","BAB VI","KESIMPULAN"]:
        sb=per_bab.get(s,{"presence":0.0,"length_pct":0.0,"keyword_coverage":0.0,"words":0})
        metrics[f"{s}_presence"]=round(sb["presence"],2)
        metrics[f"{s}_length_pct"]=round(sb["length_pct"],2)
        metrics[f"{s}_kw_cov"]=round(sb["keyword_coverage"],2)
        metrics[f"{s}_words"]=sb["words"]
    return metrics, rec

def _plot(metrics:Dict):
    import io
    cats=["heading_consistency","structure_balance","readability_proxy","cites_per_1k","doi_ratio","visual_density","conclusion_strength","global_quality"]
    vals=[metrics[c] if c!="cites_per_1k" else min(1.0,metrics[c]/10) for c in cats]
    fig1=plt.figure(figsize=(8,4)); plt.bar(cats, vals); plt.ylim(0,1); plt.xticks(rotation=45, ha="right"); plt.title("Skor Global (0–1, cites_per_1k diskalakan)")
    b1=io.BytesIO(); plt.tight_layout(); fig1.savefig(b1,format="png"); b1.seek(0)
    secs=["BAB I","BAB II","BAB III","BAB IV","BAB V","BAB VI","KESIMPULAN"]
    pvals=[metrics.get(f"{s}_kw_cov",0.0) for s in secs]
    fig2=plt.figure(figsize=(8,4)); plt.plot(range(len(secs)), pvals, marker="o"); plt.xticks(range(len(secs)), secs); plt.ylim(0,1); plt.title("Cakupan Kata Kunci per Bab")
    b2=io.BytesIO(); plt.tight_layout(); fig2.savefig(b2,format="png"); b2.seek(0)
    return b1.read(), b2.read()
