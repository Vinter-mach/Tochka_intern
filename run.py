import json
from datetime import datetime


def make_input():
    while True:
        line = input()
        if line.strip():
            return line


def parse_time(current_time: str) -> datetime:
    return datetime.strptime(current_time, "%Y-%m-%d")


def check_capacity(max_capacity: int, guests: list) -> bool:
    points = set()
    for element in guests:
        check_in = parse_time(element["check-in"])
        check_out = parse_time(element["check-out"])
        name = element["name"]

        points.add((check_in, 1, name))
        points.add((check_out, -1, name))

    points = sorted(points)

    actual_guests = set()
    actual_guests_count = 0

    for guest in points:
        current_time = guest[0]
        current_type = guest[1]
        current_name = guest[2]

        if current_type == 1:
            if current_name in actual_guests:
                continue

            actual_guests.add(current_name)
            actual_guests_count += 1

            if actual_guests_count > max_capacity:
                return False
        else:
            if current_name not in actual_guests:
                continue

            actual_guests_count -= 1
            actual_guests.remove(current_name)

    return True


if __name__ == "__main__":
    max_capacity = int(make_input().strip())
    n = int(make_input().strip())

    guests = []
    for _ in range(n):
        guest_json = make_input().strip()
        guest_data = json.loads(guest_json)
        guests.append(guest_data)

    result = check_capacity(max_capacity, guests)
    print(result)
