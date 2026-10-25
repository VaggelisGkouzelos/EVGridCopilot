"""
evaluate.py: Αξιολόγηση (evaluation) των δύο εκδόσεων σε 10 ερωτήσεις.

Για κάθε ερώτηση:
  1. υπολογίζουμε τη ΣΩΣΤΗ απάντηση με pandapower (ground truth)
  2. ρωτάμε την Έκδοση A (χωρίς εργαλείο) και την Έκδοση B (με εργαλείο)
  3. βαθμολογούμε: σωστό / λάθος / χωρίς αριθμό
"""

import csv     # για να γράψουμε τα αποτελέσματα σε αρχείο CSV (ανοίγει στο Excel)
import os      # για να φτιάξουμε τον φάκελο results/
import re      # regular expressions: έλεγχος μορφής κειμένου

from grid import max_chargers
from ask_claude import ask_without_tool, ask_with_tool


# --- Οι 10 ερωτήσεις ---
# Κάθε ερώτηση έχει: το κείμενο, τον κόμβο και την ισχύ φορτιστή.
# Τον κόμβο και την ισχύ τα χρειαζόμαστε ΜΟΝΟ για να υπολογίσουμε τη σωστή απάντηση.
# Το Claude βλέπει ΜΟΝΟ το κείμενο.
QUESTIONS = [
    {"text": "Πόσους φορτιστές 150 kW χωράει ο κόμβος 11;", "bus": 11, "kw": 150},
    {"text": "Θέλω να βάλω ταχυφορτιστές των 50 kW στον κόμβο 11. Πόσοι το πολύ χωράνε;", "bus": 11, "kw": 50},
    {"text": "Πόσα wallbox των 22 kW αντέχει ο κόμβος 11;", "bus": 11, "kw": 22},
    {"text": "Ποιος είναι ο μέγιστος αριθμός φορτιστών 150 kW στον κόμβο 5;", "bus": 5, "kw": 150},
    {"text": "Σε ένα πάρκινγκ στον κόμβο 5 θέλουμε φορτιστές 50 kW. Πόσους μπορούμε να εγκαταστήσουμε;", "bus": 5, "kw": 50},
    {"text": "Πόσους φορτιστές 150 kW σηκώνει ο κόμβος 3;", "bus": 3, "kw": 150},
    {"text": "Πόσους φορτιστές 150 kW χωράει ο κόμβος 8;", "bus": 8, "kw": 150},
    {"text": "Πόσους υπερταχυφορτιστές 350 kW χωράει ο κόμβος 13;", "bus": 13, "kw": 350},
    {"text": "Πόσους φορτιστές 150 kW χωράει ο κόμβος 14;", "bus": 14, "kw": 150},
    {"text": "Ένας σταθμός φόρτισης στον κόμβο 12 έχει μονάδες των 150 kW. Μέχρι πόσες μονάδες χωράνε;", "bus": 12, "kw": 150},
]


def to_number(answer):
    """Μετατρέπει την απάντηση σε ακέραιο, ΜΟΝΟ αν είναι σκέτος αριθμός.

    "9"            → 9
    "Δεν μπορώ..." → None  (δεν ακολούθησε την οδηγία "μόνο αριθμό")
    """
    # re.fullmatch(r"\d+", ...) σημαίνει: "όλο το κείμενο είναι ένα ή περισσότερα ψηφία;"
    if re.fullmatch(r"\d+", answer.strip()):
        return int(answer)
    return None


def grade(number, truth):
    """Βαθμολογεί μία απάντηση: 'σωστό', 'λάθος' ή 'χωρίς αριθμό'."""
    if number is None:
        return "χωρίς αριθμό"
    if number == truth:
        return "σωστό"
    return "λάθος"


def summarize(name, rows, key):
    """Τυπώνει σύνοψη για μία έκδοση (A ή B)."""
    grades = [r[f"{key}_grade"] for r in rows]
    correct = grades.count("σωστό")
    wrong = grades.count("λάθος")
    no_num = grades.count("χωρίς αριθμό")

    # Μέσο απόλυτο σφάλμα (MAE): μόνο για τις απαντήσεις που ήταν αριθμοί
    errors = [abs(r[f"{key}_number"] - r["truth"]) for r in rows if r[f"{key}_number"] is not None]
    mae = sum(errors) / len(errors) if errors else None

    print(f"\n{name}")
    print(f"  ✅ Σωστά:         {correct}/{len(rows)}")
    print(f"  ❌ Λάθος:         {wrong}/{len(rows)}")
    print(f"  ⚪ Χωρίς αριθμό:  {no_num}/{len(rows)}")
    if mae is not None:
        print(f"  📏 Μέσο σφάλμα:   {mae:.1f} φορτιστές")


if __name__ == "__main__":
    rows = []

    # enumerate δίνει και αρίθμηση: 1, 2, 3, ...
    for i, q in enumerate(QUESTIONS, start=1):
        print(f"\n[{i}/{len(QUESTIONS)}] {q['text']}")

        # 1. Σωστή απάντηση (ground truth) από το pandapower
        truth = max_chargers(bus=q["bus"], kw_each=q["kw"])["max_chargers"]

        # 2. Έκδοση A: χωρίς εργαλείο
        answer_a = ask_without_tool(q["text"])
        number_a = to_number(answer_a)

        # 3. Έκδοση B: με εργαλείο
        answer_b, used_tool = ask_with_tool(q["text"])
        number_b = to_number(answer_b)

        row = {
            "question": q["text"],
            "bus": q["bus"],
            "kw": q["kw"],
            "truth": truth,
            "A_number": number_a,
            "A_grade": grade(number_a, truth),
            "B_number": number_b,
            "B_grade": grade(number_b, truth),
            "B_used_tool": used_tool,
        }
        rows.append(row)

        print(f"   Σωστό: {truth} | A: {number_a} ({row['A_grade']}) | B: {number_b} ({row['B_grade']})")

    # --- Σύνοψη ---
    print("\n" + "=" * 50)
    print("ΣΥΝΟΨΗ")
    print("=" * 50)
    summarize("Έκδοση A (χωρίς εργαλείο)", rows, "A")
    summarize("Έκδοση B (με εργαλείο)", rows, "B")
    tool_uses = sum(r["B_used_tool"] for r in rows)
    print(f"  🔧 Χρήση εργαλείου: {tool_uses}/{len(rows)}")

    # --- Αποθήκευση σε CSV ---
    os.makedirs("results", exist_ok=True)   # φτιάχνει τον φάκελο αν δεν υπάρχει
    with open("results/results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("\n💾 Τα αποτελέσματα αποθηκεύτηκαν στο results/results.csv")