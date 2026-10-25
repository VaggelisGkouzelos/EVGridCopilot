"""
Task 1.3: Το πρώτο μας power flow (ροή φορτίου).

Φορτώνουμε το δίκτυο αναφοράς μέσης τάσης της CIGRE,
τρέχουμε power flow και βλέπουμε την "υγεία" του δικτύου
ΠΡΙΝ βάλουμε φορτιστές (το λέμε base case / βασικό σενάριο).
"""

# --- Εισαγωγή βιβλιοθηκών ---
# Το pandapower είναι η βιβλιοθήκη που κάνει τους υπολογισμούς δικτύου.
# Το γράφουμε "pp" για συντομία (σύμβαση που χρησιμοποιούν όλοι).
import pandapower as pp

# Το pandapower.networks περιέχει έτοιμα δίκτυα αναφοράς (benchmark networks).
import pandapower.networks as pn


# --- 1. Φόρτωση του δικτύου ---
# with_der=False σημαίνει "χωρίς φωτοβολταϊκά και ανεμογεννήτριες".
# DER = Distributed Energy Resources (διεσπαρμένη παραγωγή).
# Θέλουμε μόνο καταναλωτές, γιατί το project μας αφορά φορτίο (φορτιστές).
# Το "net" είναι ένα αντικείμενο που περιέχει ΟΛΟ το δίκτυο σε πίνακες
# (σαν φύλλα Excel): net.bus, net.line, net.load, net.trafo κ.λπ.
net = pn.create_cigre_network_mv(with_der=False)

print("=" * 55)
print("ΤΙ ΠΕΡΙΕΧΕΙ ΤΟ ΔΙΚΤΥΟ")
print("=" * 55)
# len() μετράει πόσες γραμμές έχει κάθε πίνακας, δηλαδή πόσα στοιχεία.
print(f"Κόμβοι (buses):            {len(net.bus)}")
print(f"Γραμμές (lines):           {len(net.line)}")
print(f"Μετασχηματιστές (trafos):  {len(net.trafo)}")
print(f"Φορτία (loads):            {len(net.load)}")
# .sum() αθροίζει όλη τη στήλη p_mw (ενεργός ισχύς σε MW).
# :.2f σημαίνει "τύπωσε με 2 δεκαδικά".
print(f"Συνολικό φορτίο:           {net.load.p_mw.sum():.2f} MW")


# --- 2. Power flow ---
# Εδώ γίνεται όλη η "μαγεία": το pandapower λύνει τις εξισώσεις
# του δικτύου με τη μέθοδο Newton-Raphson και γεμίζει τους πίνακες
# αποτελεσμάτων: net.res_bus, net.res_line, net.res_trafo.
# (res = results / αποτελέσματα)
pp.runpp(net)


# --- 3. Τάσεις κόμβων ---
print("\n" + "=" * 55)
print("ΤΑΣΕΙΣ ΚΟΜΒΩΝ (p.u.)   όρια: 0.95 - 1.05")
print("=" * 55)
# Ενώνουμε δύο πίνακες με .join():
#  - από το net.bus παίρνουμε το όνομα και την ονομαστική τάση (vn_kv)
#  - από το net.res_bus παίρνουμε την υπολογισμένη τάση (vm_pu)
# Ενώνονται "δίπλα-δίπλα" επειδή έχουν τον ίδιο αριθμό κόμβου (index).
voltages = net.bus[["name", "vn_kv"]].join(net.res_bus[["vm_pu"]])
print(voltages.round(4).to_string())


# --- 4. Φόρτιση γραμμών ---
print("\n" + "=" * 55)
print("ΦΟΡΤΙΣΗ ΓΡΑΜΜΩΝ (%)   όριο: 100%")
print("=" * 55)
# from_bus / to_bus: από ποιον κόμβο σε ποιον πάει η γραμμή.
# length_km: μήκος γραμμής (μεγαλύτερο μήκος = μεγαλύτερη πτώση τάσης).
lines = net.line[["name", "from_bus", "to_bus", "length_km"]].join(
    net.res_line[["loading_percent"]]
)
print(lines.round(2).to_string())


# --- 5. Φόρτιση μετασχηματιστών ---
print("\n" + "=" * 55)
print("ΦΟΡΤΙΣΗ ΜΕΤΑΣΧΗΜΑΤΙΣΤΩΝ (%)   όριο: 100%")
print("=" * 55)
trafos = net.trafo[["name", "hv_bus", "lv_bus"]].join(
    net.res_trafo[["loading_percent"]]
)
print(trafos.round(2).to_string())


# --- 6. Σύνοψη: η "υγεία" του δικτύου σε 3 νούμερα ---
print("\n" + "=" * 55)
print("ΣΥΝΟΨΗ BASE CASE")
print("=" * 55)
# .min() / .max() βρίσκουν τη μικρότερη / μεγαλύτερη τιμή της στήλης.
# .idxmin() / .idxmax() βρίσκουν ΣΕ ΠΟΙΟΝ κόμβο/γραμμή είναι.
min_v = net.res_bus.vm_pu.min()
min_v_bus = net.res_bus.vm_pu.idxmin()
max_line = net.res_line.loading_percent.max()
max_line_id = net.res_line.loading_percent.idxmax()
max_trafo = net.res_trafo.loading_percent.max()

print(f"Χαμηλότερη τάση:         {min_v:.4f} p.u. (κόμβος {min_v_bus})")
print(f"Πιο φορτωμένη γραμμή:    {max_line:.1f}% (γραμμή {max_line_id})")
print(f"Πιο φορτωμένος μετασχ.:  {max_trafo:.1f}%")

# Ελέγχουμε αν το δίκτυο είναι "υγιές" με βάση τα όρια του Task 1.2.
healthy = (min_v >= 0.95) and (max_line <= 100) and (max_trafo <= 100)
print(f"\nΔίκτυο εντός ορίων:      {'ΝΑΙ ✅' if healthy else 'ΟΧΙ ⚠️'}")