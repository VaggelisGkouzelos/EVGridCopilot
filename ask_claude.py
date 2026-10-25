"""
ask_claude.py: Ρωτάμε το Claude πόσους φορτιστές χωράει ένας κόμβος.

Έκδοση A: ΧΩΡΙΣ εργαλείο. Το Claude απαντάει μόνο από τις γνώσεις του.
(Στο επόμενο βήμα θα προσθέσουμε την Έκδοση B, ΜΕ εργαλείο.)
"""

from dotenv import load_dotenv
import anthropic

MODEL = "claude-sonnet-5-5"

load_dotenv()
client = anthropic.Anthropic()


# --- Το System Prompt (οδηγίες συστήματος) ---
SYSTEM_PROMPT = """Είσαι βοηθός μηχανικού δικτύων διανομής ηλεκτρικής ενέργειας.

Δουλεύουμε με το δίκτυο αναφοράς CIGRE μέσης τάσης (20 kV, 15 κόμβοι, 2 κλάδοι),
με τα φορτία στο 60% της αιχμής.

Όρια ασφαλούς λειτουργίας:
- τάση κάθε κόμβου τουλάχιστον 0.95 p.u.
- φόρτιση γραμμών και μετασχηματιστών το πολύ 100%

Όταν σε ρωτούν πόσους φορτιστές χωράει ένας κόμβος,
απάντησε ΜΟΝΟ με έναν ακέραιο αριθμό, χωρίς κανένα άλλο κείμενο."""


def get_text(response):
    """Βρίσκει το κομμάτι της απάντησης που είναι ΚΕΙΜΕΝΟ.

    Η απάντηση του Claude μπορεί να έχει πολλά κομμάτια (content blocks):
    π.χ. πρώτα τη "σκέψη" (thinking) και μετά το κείμενο (text).
    Εμείς θέλουμε μόνο το κείμενο.
    """
    for block in response.content:     # για κάθε κομμάτι της απάντησης...
        if block.type == "text":        # ...αν είναι κείμενο...
            return block.text.strip()   # ...το επιστρέφουμε
    return ""                           # αν δεν βρέθηκε κείμενο, επιστρέφουμε κενό


def ask_without_tool(question):
    """Έκδοση A: ρωτάει το Claude χωρίς να του δίνει εργαλείο υπολογισμού."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,        # αρκετό χώρο και για τη "σκέψη" και για την απάντηση
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return get_text(response)   # ← ΑΛΛΑΓΗ: ψάχνουμε το κείμενο, όχι "το πρώτο κομμάτι"


if __name__ == "__main__":
    question = "Πόσους φορτιστές 150 kW χωράει ο κόμβος 11;"
    answer = ask_without_tool(question)

    print("Ερώτηση:                 ", question)
    print("Claude (χωρίς εργαλείο): ", answer)
    print("Σωστή απάντηση:           9  (από το pandapower)")