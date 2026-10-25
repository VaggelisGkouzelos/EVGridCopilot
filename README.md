# EV Grid Copilot

Ένας AI agent που υπολογίζει πόσους φορτιστές ηλεκτρικών αυτοκινήτων αντέχει ένας κόμβος του ηλεκτρικού δικτύου.
Φτιαγμένος με Python, pandapower και το Claude API (tool use).

## Πώς λειτουργεί

- Το δίκτυο είναι το δίκτυο αναφοράς μέσης τάσης της CIGRE (20 kV, 15 κόμβοι).
- Προστίθενται φορτιστές σε έναν κόμβο έναν-έναν, μέχρι η τάση να πέσει κάτω από 0,95 p.u. ή μια γραμμή ή ο μετασχηματιστής να ξεπεράσει το 100% φόρτιση.
- Ο AI agent καταλαβαίνει την ερώτηση σε φυσική γλώσσα και καλεί μόνος του τον υπολογισμό δικτύου.

## Αποτελέσματα (10 ερωτήσεις)

- LLM χωρίς υπολογισμό δικτύου: 0/10 σωστές, μέσο σφάλμα 27 φορτιστές
- AI agent με υπολογισμό δικτύου: 10/10 σωστές

Χωρίς τον υπολογισμό, το μοντέλο έδινε διαφορετικές απαντήσεις στην ίδια ερώτηση. Με τον υπολογισμό, οι απαντήσεις ήταν πάντα σωστές.

## Βασικό εύρημα

Η θέση μετράει. Στο ίδιο δίκτυο, ο κόμβος 11 αντέχει 9 ταχυφορτιστές των 150 kW, ενώ ο κόμβος 13 αντέχει 41.

## Περιορισμοί

Δίκτυο αναφοράς (όχι πραγματικό δίκτυο), σενάριο φορτίου 60%, 10 ερωτήσεις ελέγχου.

---

## 🇬🇧 English

An AI agent that calculates how many EV chargers a node of the electricity grid can handle.
Built with Python, pandapower and the Claude API (tool use).

### How it works

- The grid is the CIGRE medium voltage benchmark network (20 kV, 15 nodes).
- Chargers are added to a node one by one, until the voltage drops below 0.95 p.u. or a line or transformer goes above 100% loading.
- The AI agent understands the question in natural language and calls this calculation as a tool.

### Results (10 questions)

- LLM without tool: 0/10 correct, average error 27 chargers
- LLM agent with tool: 10/10 correct

Without the tool, the model gave different answers to the same question. With the tool, the answers were always correct.

### Key finding

Location matters. On the same network, node 11 can handle 9 fast chargers of 150 kW, while node 13 can handle 41.

### Limitations

Benchmark network (not a real grid), 60% load scenario, 10 test questions.