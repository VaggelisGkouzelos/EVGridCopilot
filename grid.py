"""
grid.py: Ο "πυρήνας" του project.
Φορτώνει το δίκτυο, προσθέτει φορτιστές και ελέγχει αν το δίκτυο αντέχει.
"""

import pandapower as pp
import pandapower.networks as pn

# Τα όρια που μάθαμε στο Task 1.2
MIN_VOLTAGE = 0.95   # κάτω από αυτό = υπόταση
MAX_LOADING = 100    # πάνω από αυτό = υπερφόρτιση (%)


def load_grid(load_level=0.6):
    """Φορτώνει το δίκτυο CIGRE με φορτίο 'τυπικής ώρας'.

    load_level=0.6 σημαίνει ότι όλα τα φορτία είναι στο 60% της αιχμής.
    Στο 100% (ώρα αιχμής) το δίκτυο ήταν ήδη εκτός ορίων (Task 1.3).
    """
    net = pn.create_cigre_network_mv(with_der=False)
    # Η στήλη "scaling" πολλαπλασιάζει κάθε φορτίο (0.6 = 60%)
    net.load["scaling"] = load_level
    return net


def add_chargers(net, bus, number, kw_each):
    """Προσθέτει 'number' φορτιστές των 'kw_each' kW στον κόμβο 'bus'."""
    total_mw = number * kw_each / 1000   # kW → MW (διαιρούμε με 1000)
    pp.create_load(net, bus=bus, p_mw=total_mw, name="EV chargers")


def check_grid(net):
    """Τρέχει power flow και επιστρέφει την 'υγεία' του δικτύου."""
    pp.runpp(net)

    min_v = net.res_bus.vm_pu.min()
    max_line = net.res_line.loading_percent.max()
    max_trafo = net.res_trafo.loading_percent.max()

    # Μαζεύουμε σε λίστα ό,τι παραβιάζει τα όρια
    problems = []
    if min_v < MIN_VOLTAGE:
        problems.append(f"υπόταση (κόμβος {net.res_bus.vm_pu.idxmin()}: {min_v:.3f} p.u.)")
    if max_line > MAX_LOADING:
        problems.append(f"υπερφόρτιση γραμμής ({max_line:.0f}%)")
    if max_trafo > MAX_LOADING:
        problems.append(f"υπερφόρτιση μετασχηματιστή ({max_trafo:.0f}%)")

    # Επιστρέφουμε ένα λεξικό (dictionary) με όλα τα αποτελέσματα
    return {
        "ok": len(problems) == 0,        # True αν δεν υπάρχει κανένα πρόβλημα
        "min_voltage": round(min_v, 4),
        "max_line_loading": round(max_line, 1),
        "max_trafo_loading": round(max_trafo, 1),
        "problems": problems,
    }


# Αυτό το κομμάτι τρέχει ΜΟΝΟ όταν γράφουμε "python grid.py".
# Αν άλλο αρχείο κάνει "import grid", δεν τρέχει.
if __name__ == "__main__":
    print("1) Δίκτυο χωρίς φορτιστές:")
    net = load_grid()
    print(check_grid(net))

    print("\n2) +4 φορτιστές 150 kW στον κόμβο 11 (μακρινός):")
    net = load_grid()
    add_chargers(net, bus=11, number=4, kw_each=150)
    print(check_grid(net))

    print("\n3) +4 φορτιστές 150 kW στον κόμβο 13 (άλλο κλαδί):")
    net = load_grid()
    add_chargers(net, bus=13, number=4, kw_each=150)
    print(check_grid(net))