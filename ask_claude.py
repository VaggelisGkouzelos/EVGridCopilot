"""
ask_claude.py: Ρωτάμε το Claude πόσους φορτιστές χωράει ένας κόμβος.

Έκδοση A: ΧΩΡΙΣ εργαλείο. Το Claude απαντάει μόνο από τις γνώσεις του.
Έκδοση B: ΜΕ εργαλείο. Το Claude καλεί τη δική μας max_chargers() (pandapower).
"""

import json                      # για να μετατρέψουμε το αποτέλεσμα σε κείμενο JSON
from dotenv import load_dotenv
import anthropic

# Εισάγουμε τη δική μας συνάρτηση από το grid.py!
from grid import max_chargers

MODEL = "claude-sonnet-5-5"

load_dotenv()
client = anthropic.Anthropic()


# --- System Prompt: Έκδοση A (χωρίς εργαλείο) ---
SYSTEM_PROMPT = """Είσαι βοηθός μηχανικού δικτύων διανομής ηλεκτρικής ενέργειας.

Δουλεύουμε με το δίκτυο αναφοράς CIGRE μέσης τάσης (20 kV, 15 κόμβοι, 2 κλάδοι),
με τα φορτία στο 60% της αιχμής.

Όρια ασφαλούς λειτουργίας:
- τάση κάθε κόμβου τουλάχιστον 0.95 p.u.
- φόρτιση γραμμών και μετασχηματιστών το πολύ 100%

Όταν σε ρωτούν πόσους φορτιστές χωράει ένας κόμβος,
απάντησε ΜΟΝΟ με έναν ακέραιο αριθμό, χωρίς κανένα άλλο κείμενο."""


# --- System Prompt: Έκδοση B (με εργαλείο) ---
# Παίρνουμε το ίδιο κείμενο και προσθέτουμε οδηγία για το εργαλείο.
SYSTEM_PROMPT_WITH_TOOL = SYSTEM_PROMPT + """

Έχεις στη διάθεσή σου το εργαλείο max_chargers, που κάνει πραγματικό υπολογισμό
ροής φορτίου (power flow). Για κάθε ερώτηση σχετικά με το πόσους φορτιστές χωράει
ένας κόμβος, ΠΑΝΤΑ κάλεσε το εργαλείο. Μη μαντεύεις ποτέ."""


# --- Η περιγραφή του εργαλείου για το Claude ---
# Το Claude ΔΕΝ βλέπει τον κώδικα της max_chargers. Βλέπει ΜΟΝΟ αυτή την περιγραφή.
# Γι' αυτό πρέπει να είναι σαφής: τι κάνει, τι επιστρέφει, τι στοιχεία θέλει.
TOOLS = [
    {
        "name": "max_chargers",
        "description": (
            "Υπολογίζει με power flow (pandapower) πόσους φορτιστές ηλεκτρικών "
            "αυτοκινήτων συγκεκριμένης ισχύος χωράει ένας κόμβος του δικτύου "
            "CIGRE μέσης τάσης, χωρίς να παραβιαστούν τα όρια τάσης (0.95 p.u.) "
            "και φόρτισης (100%). Επιστρέφει τον μέγιστο αριθμό φορτιστών "
            "και τι 'σπάει' πρώτο αν προστεθεί ένας ακόμα."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "bus": {
                    "type": "integer",
                    "description": "Αριθμός κόμβου του δικτύου (από 1 έως 14)",
                },
                "kw_each": {
                    "type": "number",
                    "description": "Ισχύς κάθε φορτιστή σε kW, π.χ. 50 ή 150",
                },
            },
            "required": ["bus", "kw_each"],
        },
    }
]


def get_text(response):
    """Βρίσκει το κομμάτι της απάντησης που είναι ΚΕΙΜΕΝΟ."""
    for block in response.content:
        if block.type == "text":
            return block.text.strip()
    return ""


def ask_without_tool(question):
    """Έκδοση A: ρωτάει το Claude χωρίς να του δίνει εργαλείο υπολογισμού."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return get_text(response)


def ask_with_tool(question):
    """Έκδοση B: ρωτάει το Claude ΚΑΙ του δίνει το εργαλείο max_chargers.

    Επιστρέφει δύο πράγματα: (απάντηση, αν χρησιμοποιήθηκε το εργαλείο)
    """
    # Η "συζήτηση" ξεκινάει με την ερώτηση του χρήστη.
    # Θα της προσθέτουμε μηνύματα όσο προχωράει.
    messages = [{"role": "user", "content": question}]
    used_tool = False

    # Βρόχος: το πολύ 5 γύροι (για ασφάλεια, να μην κολλήσει για πάντα)
    for _ in range(5):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT_WITH_TOOL,
            tools=TOOLS,              # ← ΝΕΟ: του δίνουμε το εργαλείο
            messages=messages,
        )

        # Αν το Claude ΔΕΝ ζήτησε εργαλείο, έδωσε τελική απάντηση. Τέλος.
        if response.stop_reason != "tool_use":
            return get_text(response), used_tool

        # Αλλιώς, το Claude ζήτησε εργαλείο.
        # Κρατάμε στη συζήτηση ό,τι είπε (μαζί με το αίτημα για το εργαλείο).
        messages.append({"role": "assistant", "content": response.content})

        # Βρίσκουμε το αίτημα (tool_use block), τρέχουμε τη συνάρτηση,
        # και ετοιμάζουμε το αποτέλεσμα για να του το στείλουμε.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                used_tool = True
                print(f"   🔧 Το Claude ζητάει: {block.name}({block.input})")

                # block.input είναι λεξικό, π.χ. {"bus": 11, "kw_each": 150}
                # Το ** "ξεπακετάρει" το λεξικό σε ορίσματα: max_chargers(bus=11, kw_each=150)
                result = max_chargers(**block.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,   # σε ΠΟΙΟ αίτημα απαντάμε
                    "content": json.dumps(result, ensure_ascii=False),
                })

        # Στέλνουμε τα αποτελέσματα πίσω στο Claude (σαν μήνυμα "user")
        messages.append({"role": "user", "content": tool_results})

    # Αν φτάσαμε εδώ, πέρασαν 5 γύροι χωρίς τελική απάντηση
    return "", used_tool


if __name__ == "__main__":
    question = "Πόσους φορτιστές 150 kW χωράει ο κόμβος 11;"
    print("Ερώτηση:", question)
    print()

    answer_a = ask_without_tool(question)
    print("Έκδοση A (χωρίς εργαλείο):", answer_a)
    print()

    answer_b, used = ask_with_tool(question)
    print("Έκδοση B (με εργαλείο):   ", answer_b, "| χρησιμοποίησε εργαλείο:", used)
    print()

    print("Σωστή απάντηση:            9  (από το pandapower)")