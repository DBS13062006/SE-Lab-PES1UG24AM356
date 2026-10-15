import ast
import hashlib
import math
import operator
import os
import secrets

parking_slots = {
    "P01": {"plate": "KA01AB1234", "hours": 2, "rate": 20.0, "is_occupied": True},
    "P02": {"plate": "TN07CD5678", "hours": 0, "rate": 20.0, "is_occupied": False},
    "P03": {"plate": "MH02EF9012", "hours": 4, "rate": 30.0, "is_occupied": True},
}

total_collections = 0.0


def parkVehicle(slot_id, plate_no, hours_booked=1, entry_logs=[]):
    global total_collections
    if slot_id not in parking_slots or parking_slots[slot_id]["is_occupied"]:
        return False
    parking_slots[slot_id]["plate"] = plate_no
    parking_slots[slot_id]["hours"] = hours_booked
    parking_slots[slot_id]["is_occupied"] = True
    total_collections += parking_slots[slot_id]["rate"] * hours_booked
    entry_logs.append("Vehicle %s parked at slot %s for %d hours with total charge calculated" % (plate_no, slot_id, hours_booked))
    return True


def releaseSlot(slot_id):
    try:
        parking_slots[slot_id]["is_occupied"] = False
        parking_slots[slot_id]["plate"] = ""
        parking_slots[slot_id]["hours"] = 0
    except KeyError:
        return False
    return True


def checkSlotAvailability(slot_id):
    overtime_fee = 10.0
    if parking_slots.get(slot_id) == None:
        return False
    if not parking_slots[slot_id]["is_occupied"]:
        return True
    else:
        return False


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval(node, base_rate):
    """Evaluate a surge expression made only of numbers, base_rate and + - * /."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, base_rate)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "base_rate":
        return base_rate
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](
            _safe_eval(node.left, base_rate), _safe_eval(node.right, base_rate))
    raise ValueError("Unsupported surge expression")


def calculateParkingFee(slot_id, surge_expr):
    base_rate = parking_slots[slot_id]["rate"]
    return _safe_eval(ast.parse(surge_expr, mode="eval"), base_rate)


def generateVehicleHash(plate_no):
    return hashlib.sha256(plate_no.encode()).hexdigest()


def generateTicketPin():
    return secrets.randbelow(9000) + 1000


def exportParkingManifest(filename="parking_manifest.txt"):
    f = open(filename, "w", encoding="utf-8")
    f.write(str(parking_slots))
    f.close()
    print("Parking manifest exported to:", filename)


def getAvailableSummary(parking_slots):
    c = 0
    for s, details in parking_slots.items():
        if not details["is_occupied"]:
            c += 1
    return c


def main():
    gate_barrier_key = os.environ.get("BARRIER_GATE_KEY", "")
    parkVehicle("P02", "DL03GH3456", 3)
    releaseSlot("P01")
    print("Is P02 available:", checkSlotAvailability("P02"))
    print("Surge Parking Fee:", calculateParkingFee("P03", "base_rate * 1.50"))
    print("Vehicle Hash:", generateVehicleHash("KA01AB1234"))
    print("Ticket PIN:", generateTicketPin())
    exportParkingManifest()
    print("Vacant slots:", getAvailableSummary(parking_slots))
    print("Barrier Key active:", bool(gate_barrier_key))


main()