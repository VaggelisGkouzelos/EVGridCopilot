"""
hello_claude.py: Ελέγχουμε ότι μπορούμε να μιλήσουμε με το Claude από την Python.
"""

# load_dotenv: διαβάζει το αρχείο .env και "φορτώνει" το API key
from dotenv import load_dotenv

# anthropic: η επίσημη βιβλιοθήκη για να μιλάμε με το Claude
import anthropic

# Ποιο μοντέλο Claude θα χρησιμοποιήσουμε
MODEL = "claude-sonnet-5-5"

# 1. Φορτώνουμε το API key από το .env
load_dotenv()

# 2. Φτιάχνουμε τον "πελάτη" (client), δηλαδή το αντικείμενο που μιλάει με το Claude.
#    Βρίσκει μόνο του το API key (ψάχνει τη μεταβλητή ANTHROPIC_API_KEY).
client = anthropic.Anthropic()

# 3. Στέλνουμε ένα μήνυμα
response = client.messages.create(
    model=MODEL,
    max_tokens=200,   # μέγιστο μήκος απάντησης (περίπου 150 λέξεις)
    messages=[
        # role="user" σημαίνει "αυτό το λέω εγώ, ο χρήστης"
        {"role": "user", "content": "Πες μου σε μία πρόταση τι είναι ένα δίκτυο διανομής ρεύματος."}
    ],
)

# 4. Τυπώνουμε την απάντηση.
#    Η απάντηση έρχεται σε "κομμάτια" (content blocks). Το πρώτο [0] έχει το κείμενο.
print(response.content[0].text)