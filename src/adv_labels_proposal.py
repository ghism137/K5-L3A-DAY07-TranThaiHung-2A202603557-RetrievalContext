"""Writes results/advanced/test/review/labels.json: one hand label (pass/fail) with its reason for each of the 30 test questions.

Each label was set by reading the system answer against the reference answer and the ORIGINAL page image / text layer, after the
single test run. Three labels differ from the first-pass automatic grade (t13, t21, t29); they are listed in the report so they
can be checked first. Nothing here changes the pipeline or any frozen file.
"""
import json

from . import config

P, F = "pass", "fail"
L = {
    "t01": (P, "15.2 US$ billion, Table 1.2 IMF 2020; unit given; citation = visual chunk of p63."),
    "t02": (P, "Fall of 21.9 US$ billion (66.3 to 44.4), sign and operands shown; cites p63."),
    "t03": (P, "2021 and 85.9 US$ billion; cites p63."),
    "t04": (P, "Increase of 1.5 US$ billion (13.3 to 14.8); cites p63."),
    "t05": (P, "16 countries; cites the Country Groups text chunk on p269; the p138 header also says 16."),
    "t06": (P, "(P), preliminary; cites p269."),
    "t07": (P, "3,762 at End-2024 (printed label); cites Figure 3.3 chunk on p113."),
    "t08": (P, "61.8 US$ billion at End-2023 (printed label); cites p113."),
    "t09": (P, "2025, about 56 percent, as in the reference; cites Figure 3.2 chunk on p111."),
    "t10": (P, "2025, about 6 percent (p110 text: 5.8); cites p111."),
    "t11": (P, "About 24, inside the accepted 23-25 range; cites Figure 3.1 chunk on p110."),
    "t12": (P, "Tier 2 = IDS (International Debt Statistics), 'trusted, transparent statistics'; cites p132."),
    "t13": (P, "Exact arrow text 'Gaps and findings strengthen reporting'. The first-pass grade failed it only because the reference "
               "answer carries an unrequested parenthesis about the arrow's direction; the question asks for the text. Changed from auto fail."),
    "t14": (P, "Tier 3, IDR = International Debt Report; cites p132."),
    "t15": (P, "Belize, 1,609 US$ million, +2.6% from 2024; cites the sample on p136."),
    "t16": (F, "Refused. The values (24 years, 3.6%) are in the index (vis:p0136:e05) but retrieval returned Figure 4 chunks of other "
               "country pages (p251, p186, p137...) because over 120 profile pages have an almost identical Figure 4 card; "
               "a genuine retrieval failure."),
    "t17": (P, "Peru, by 43,751 US$ million (94,270 - 50,519); cites both profile pages (p230, p200)."),
    "t18": (P, "84,917 US$ million (28,633 + 56,284); cites p262 and p175."),
    "t19": (P, "About 10.8 percent (1,020 / 9,445, US$ billion); cites p143 and p137."),
    "t20": (P, "2,358 US$ billion (3,313 - 955); cites p138 and p142."),
    "t21": (P, "8.9 percent to $262.4 billion, which is the whole of what is asked. Cites p30 (chapter 1), which states the same figures "
               "(checked in the chunk); the reference page is the Key Takeaways page 19. Changed from auto fail (gold lists one page; the fact is on two)."),
    "t22": (P, "$294.5 billion and FDI down 25.5 percent 2011-2025; cites p21."),
    "t23": (P, "Fell from 42.1 to 41.2 percent; growth outpaced debt accumulation and restructuring helped; cites p21."),
    "t24": (P, "IMF (supplemented by UNCTAD and country data); sixth edition of the Balance of Payments Manual; cites p267."),
    "t25": (P, "Abstained; no claim about Switzerland."),
    "t26": (P, "Abstained and correctly said Figure 3.3 has end-2021, end-2023 and end-2024 only."),
    "t27": (P, "Abstained; said Figure 3.7 is not in the material."),
    "t28": (P, "Abstained; said no 2027 projection exists in the material."),
    "t29": (P, "Judgement call. The system did not invent a rate: it said none was reported because Azerbaijan had no new private commitments "
               "in 2025, citing the Figure 4 chunk of p150, and the original note says exactly that ('..' and the note). That is a clear statement "
               "that the value is missing, with no unsupported claim. The first-pass grade failed it because the status was 'answered'. "
               "Changed from auto fail; if counted as fail the result is 28/30."),
    "t30": (P, "Abstained; no claim about Norway."),
}


def main() -> None:
    out = config.RESULTS_DIR / "advanced" / "test" / "review"
    out.mkdir(parents=True, exist_ok=True)
    rows = [{"id": k, "label": v[0], "reason": v[1]} for k, v in sorted(L.items())]
    (out / "labels.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(rows), "labels written to", out / "labels.json")


if __name__ == "__main__":
    main()
