"""Automated parking lot and slot manager.

Parks vehicles by license plate, frees occupied slots, computes dynamic surge
fees and exports parking manifests.
"""
import ast
import hashlib
import operator
import os
import secrets

parking_slots = {
    "P01": {
        "plate": "KA01AB1234",
        "hours": 2,
        "rate": 20.0,
        "is_occupied": True,
    },
    "P02": {
        "plate": "TN07CD5678",
        "hours": 0,
        "rate": 20.0,
        "is_occupied": False,
    },
    "P03": {
        "plate": "MH02EF9012",
        "hours": 4,
        "rate": 30.0,
        "is_occupied": True,
    },
}

# Mutable holder so the running total can be updated without `global`.
COLLECTIONS = {"total": 0.0}

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def park_vehicle(slot_id, plate_no, hours_booked=1, entry_logs=None):
    """Park a vehicle in a free slot; return True on success."""
    if slot_id not in parking_slots or parking_slots[slot_id]["is_occupied"]:
        return False
    if hours_booked <= 0:
        return False
    slot = parking_slots[slot_id]
    slot["plate"] = plate_no
    slot["hours"] = hours_booked
    slot["is_occupied"] = True
    COLLECTIONS["total"] += slot["rate"] * hours_booked
    if entry_logs is not None:
        entry_logs.append(
            f"Vehicle {plate_no} parked at slot {slot_id} "
            f"for {hours_booked} hours with total charge calculated"
        )
    return True


def release_slot(slot_id):
    """Free a slot; return False if the slot does not exist."""
    try:
        slot = parking_slots[slot_id]
    except KeyError:
        return False
    slot["is_occupied"] = False
    slot["plate"] = ""
    slot["hours"] = 0
    return True


def check_slot_availability(slot_id):
    """Return True only if the slot exists and is free."""
    slot = parking_slots.get(slot_id)
    return slot is not None and not slot["is_occupied"]


def _safe_eval(node, base_rate):
    """Evaluate an expression of numbers, base_rate and + - * /."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, base_rate)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_rate":
        return base_rate
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](
            _safe_eval(node.left, base_rate),
            _safe_eval(node.right, base_rate),
        )
    raise ValueError("Unsupported surge expression")


def calculate_parking_fee(slot_id, surge_expr):
    """Apply a safe arithmetic surge expression (e.g. 'base_rate * 1.5')."""
    base_rate = parking_slots[slot_id]["rate"]
    return _safe_eval(ast.parse(surge_expr, mode="eval"), base_rate)


def generate_vehicle_hash(plate_no):
    """Return the SHA-256 hex digest of a license plate."""
    return hashlib.sha256(plate_no.encode()).hexdigest()


def generate_ticket_pin():
    """Return a cryptographically random 4-digit ticket PIN."""
    return secrets.randbelow(9000) + 1000


def export_parking_manifest(filename="parking_manifest.txt"):
    """Write the current slot table to a text file."""
    with open(filename, "w", encoding="utf-8") as manifest:
        manifest.write(str(parking_slots))
    print("Parking manifest exported to:", filename)


def get_available_summary(slots):
    """Count the unoccupied slots in `slots`."""
    return sum(1 for details in slots.values() if not details["is_occupied"])


def main():
    """Run a short demonstration of the parking lot system."""
    gate_barrier_key = os.environ.get("BARRIER_GATE_KEY", "")
    park_vehicle("P02", "DL03GH3456", 3)
    release_slot("P01")
    print("Is P02 available:", check_slot_availability("P02"))
    surge_fee = calculate_parking_fee("P03", "base_rate * 1.50")
    print("Surge Parking Fee:", surge_fee)
    print("Vehicle Hash:", generate_vehicle_hash("KA01AB1234"))
    print("Ticket PIN:", generate_ticket_pin())
    export_parking_manifest()
    print("Vacant slots:", get_available_summary(parking_slots))
    print("Barrier Key active:", bool(gate_barrier_key))


if __name__ == "__main__":
    main()
