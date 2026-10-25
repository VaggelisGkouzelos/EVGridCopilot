"""
grid.py: Ο "πυρήνας" του project.
Φορτώνει το δίκτυο, προσθέτει φορτιστές, ελέγχει αν το δίκτυο αντέχει
και βρίσκει πόσους φορτιστές χωράει κάθε κόμβος.
"""

import pandapower as pp
import pandapower.networks as pn

# Τα όρια που μάθαμε στο Task 1.2
MIN_VOLTAGE = 0.95   # κάτω από αυτό = υπόταση
MAX_LOADING = 100    # πάνω από αυτό = υπερφόρτιση (%)


def load_grid(load_level=0.6):
    """Φορτώνει το δίκτυο CIGRE με φορτίο 'τυπικής ώρας' (60% της αιχμής)."""
    net = pn.create_cigre_network_mv(with_der=False)
    net.load["scaling"] = load_level
    return net


def add_chargers(net, bus, number, kw_each):
    """Προσθέτει 'number' φορτιστές των 'kw_each' kW στον κόμβο 'bus'."""
    total_mw = number * kw_each / 1000   # kW → MW
    pp.create_load(net, bus=bus, p_mw=total_mw, name="EV chargers")


def check_grid(net):
    """Τρέχει power flow και επιστρέφει την 'υγεία' του δικτύου."""

    # try / except = "δοκίμασε, κι αν βγει error, κάνε κάτι άλλο αντί να σταματήσεις".
    # Με πάρα πολύ φορτίο ο υπολογισμός μπορεί να μη βρει λύση.
    # Τότε λέμε απλώς ότι το δίκτυο "έσπασε".
    try:
          pp.runpp(net, numba=False)
    except Exception:
        return {
            "ok": False,
            "min_voltage": None,
            "max_line_loading": None,
            "max_trafo_loading": None,
            "problems": ["ο υπολογισμός δεν βρήκε λύση (πάρα πολύ φορτίο)"],
        }

    # float() μετατρέπει το np.float64 σε απλό αριθμό Python (καθαρότερο print)
    min_v = float(net.res_bus.vm_pu.min())
    max_line = float(net.res_line.loading_percent.max())
    max_trafo = float(net.res_trafo.loading_percent.max())

    problems = []
    if min_v < MIN_VOLTAGE:
        weak_bus = int(net.res_bus.vm_pu.idxmin())
        problems.append(f"υπόταση (κόμβος {weak_bus}: {min_v:.3f} p.u.)")
    if max_line > MAX_LOADING:
        problems.append(f"υπερφόρτιση γραμμής ({max_line:.0f}%)")
    if max_trafo > MAX_LOADING:
        problems.append(f"υπερφόρτιση μετασχηματιστή ({max_trafo:.0f}%)")

    return {
        "ok": len(problems) == 0,
        "min_voltage": round(min_v, 4),
        "max_line_loading": round(max_line, 1),
        "max_trafo_loading": round(max_trafo, 1),
        "problems": problems,
    }


def max_chargers(bus, kw_each, limit=100):
    """Βρίσκει πόσους φορτιστές των 'kw_each' kW χωράει ο κόμβος 'bus'.

    Βάζει 1, 2, 3, ... φορτιστές (κάθε φορά σε "καθαρό" δίκτυο)
    μέχρι κάτι να σπάσει. Η απάντηση είναι ο τελευταίος αριθμός που ήταν ok.
    """
    # range(1, limit + 1) δίνει τους αριθμούς 1, 2, 3, ..., limit
    for n in range(1, limit + 1):
        net = load_grid()                    # καθαρό δίκτυο κάθε φορά
        add_chargers(net, bus, n, kw_each)   # βάζουμε n φορτιστές
        result = check_grid(net)             # ελέγχουμε

        if not result["ok"]:                 # αν κάτι έσπασε...
            return {
                "bus": bus,
                "kw_each": kw_each,
                "max_chargers": n - 1,        # ...ο προηγούμενος αριθμός ήταν το όριο
                "what_breaks_first": result["problems"],
            }

    # Αν φτάσαμε ως το limit χωρίς να σπάσει τίποτα
    return {
        "bus": bus,
        "kw_each": kw_each,
        "max_chargers": limit,
        "what_breaks_first": ["τίποτα μέχρι το όριο αναζήτησης"],
    }


if __name__ == "__main__":
    print("Δίκτυο χωρίς φορτιστές:")
    print(check_grid(load_grid()))

    print("\nΠόσους ταχυφορτιστές 150 kW χωράει...")
    for bus in [11, 5, 13]:
        print(max_chargers(bus=bus, kw_each=150))