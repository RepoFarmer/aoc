import itertools as it
import numpy
import re
import string
import copy
import math
from enum import Enum


def fix_expense_report(expenses, num_entries=2):
    for i in list(it.permutations(expenses, num_entries)):
        if sum(i) == 2020:
            return numpy.prod(i)
    return 0


def check_password(min, max, letter, password):
    min = int(min)
    max = int(max)
    occurrences = password.count(letter)
    return occurrences >= min and occurrences <= max


def check_toboggan_corporate_password(indexes, letter, password):
    count = 0
    for index in indexes:
        index = int(index)
        if password[index - 1] == letter:
            count = count + 1
    return count == 1


def toboggan_map_count_trees(map, slope):
    tree_count = 0
    tree = "#"
    width = len(map[0])

    # start in top left corner of map (0,0)
    x = 0
    y = 0

    while y < len(map):
        if map[y][x % width] == tree:
            tree_count = tree_count + 1
        x = (x + slope[0]) % width  # map repeats indefinitely to the right
        y = y + slope[1]
    return tree_count


def is_valid_passport(passport):
    required_keys = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]
    for key in required_keys:
        if key not in passport:
            return False
    return True


def is_valid_num(num, **kwargs):
    length = kwargs.get("length", None)
    min = kwargs.get("min", None)
    max = kwargs.get("max", None)

    if length is not None:
        if len(str(num)) != length:
            return False
    if min is not None:
        if num < min:
            return False
    if max is not None:
        if num > max:
            return False
    return True


def is_valid_birth_year(year):
    return is_valid_num(year, length=4, min=1920, max=2002)


def is_valid_issue_year(year):
    return is_valid_num(year, length=4, min=2010, max=2020)


def is_valid_expiration_year(year):
    return is_valid_num(year, length=4, min=2020, max=2030)


def is_valid_height(height):
    pattern = "^([0-9]+)(cm|in)$"
    result = re.search(pattern, height)
    if result is None:
        return False
    if result.group(2) == "cm":
        if not is_valid_num(int(result.group(1)), min=150, max=193):
            return False
    elif result.group(2) == "in":
        if not is_valid_num(int(result.group(1)), min=59, max=76):
            return False
    else:
        return False

    return True


def is_valid_hair_color(hair_color):
    pattern = "^#[0-9a-f]{6}$"
    result = re.search(pattern, hair_color)
    if result is None:
        return False
    return True


def is_valid_eye_color(eye_color):
    eye_colors = ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]
    return eye_color in eye_colors


def is_valid_passport_id(passport_id):
    pattern = "^[0-9]{9}$"
    result = re.search(pattern, passport_id)
    if result is None:
        return False
    return True


def is_valid_passport2(passport):
    if not is_valid_passport(passport):
        return False

    if not is_valid_birth_year(int(passport["byr"])):
        return False
    if not is_valid_issue_year(int(passport["iyr"])):
        return False
    if not is_valid_expiration_year(int(passport["eyr"])):
        return False
    if not is_valid_height(passport["hgt"]):
        return False
    if not is_valid_hair_color(passport["hcl"]):
        return False
    if not is_valid_eye_color(passport["ecl"]):
        return False
    if not is_valid_passport_id(passport["pid"]):
        return False

    return True


def decode_seat(seat_code):
    seat_code = seat_code.replace("F", "0")
    seat_code = seat_code.replace("B", "1")
    seat_code = seat_code.replace("L", "0")
    seat_code = seat_code.replace("R", "1")
    row = seat_code[0:7]
    column = seat_code[-3:]
    # convert from binary to int
    row = int(row, 2)
    column = int(column, 2)
    return (row, column)


def seat_id(seat):
    return seat[0] * 8 + seat[1]


def count_customs_forms(forms):
    answers = {}
    for form in forms:
        for question in form:
            if question.isalpha():
                answers[question] = answers.get(question, 0) + 1
    return answers


def parse_bag_line(line):
    line = line.translate(str.maketrans("", "", string.punctuation))
    line = line.replace(" bags", "")
    line = line.replace(" bag", "")
    line = line.split(" contain ")
    bag_color = line[0]
    bag_contents = line[1].split(" ")
    bag_contents = [
        " ".join(bag_contents[i : i + 3]) for i in range(0, len(bag_contents), 3)
    ]
    return (bag_color, bag_contents)


def check_bag_color(target_color, bag_color, bag_rules):
    if bag_color == "no other":
        return False
    if bag_color == target_color:
        return True
    for color in bag_rules.get(bag_color, []):
        color = color.split(" ", 1)[1]  # remove leading number
        if check_bag_color(target_color, color, bag_rules):
            return True
    return False


def count_bags(bag_color, bag_rules):
    num_bags = 1
    for color in bag_rules.get(bag_color, ["no other"]):
        if color == "no other":
            num_bags = num_bags
            continue
        number = int(color.split(" ", 1)[0])
        color = color.split(" ", 1)[1]
        num_bags = num_bags + (number * count_bags(color, bag_rules))
    return num_bags


class OpCode(Enum):
    acc = 0
    jmp = 1
    nop = 2


class Instruction:
    def __init__(self, opcode, value):
        self.opcode = opcode
        self.value = value

    def __eq__(self, other):
        if self.opcode != other.opcode:
            return False
        if self.value != other.value:
            return False
        return True

    def __repr__(self):
        return "%s %s" % (self.opcode, self.value)


def flip_instruction(instruction):
    if instruction.opcode == OpCode.nop:
        instruction.opcode = OpCode.jmp
    elif instruction.opcode == OpCode.jmp:
        instruction.opcode = OpCode.nop
    return instruction


def run_program(program, ptr=0):
    accumulator = 0
    ptr_history = []
    while ptr < len(program):
        if ptr in ptr_history:
            return (accumulator, ptr_history)
        else:
            ptr_history.append(ptr)
        instruction = program[ptr]
        if instruction.opcode == OpCode.acc:
            accumulator = accumulator + instruction.value
            ptr = ptr + 1
        elif instruction.opcode == OpCode.jmp:
            ptr = ptr + instruction.value
        elif instruction.opcode == OpCode.nop:
            ptr = ptr + 1
    return (accumulator, ptr_history)


def parse_instruction(line):
    line = line.split()
    return Instruction(OpCode[line[0]], int(line[1]))


def find_sum_pair(target, xmas_list):
    for pair in it.permutations(xmas_list, 2):
        if pair[0] + pair[1] == target:
            return pair
    return None


def find_contiguous_sum(target, xmas_list, window_size):
    for index in range(0, len(xmas_list)):
        slice = xmas_list[index : index + window_size]
        contiguous_sum = sum(slice)
        if contiguous_sum == target:
            return slice


def xmas_find_non_sum(xmas_list, preamble_length=25):
    index = preamble_length
    for index in range(preamble_length, len(xmas_list)):
        preamble = xmas_list[index - preamble_length : index]
        number = xmas_list[index]
        if find_sum_pair(number, preamble) is None:
            return number


def xmas_find_weakness(target, xmas_list):
    for window_size in range(2, len(xmas_list)):
        slice = find_contiguous_sum(target, xmas_list, window_size)
        if slice:
            return min(slice) + max(slice)


def count_jolt_differences(adapters):
    jolt_array = {}
    for index in range(len(adapters) - 1):
        difference = adapters[index + 1] - adapters[index]
        jolt_array[difference] = jolt_array.get(difference, 0) + 1
    return jolt_array


def find_next_adapter(index, adapters, max_difference):
    next_adapter = []
    current_joltage = adapters[index]
    index = index + 1
    while index < len(adapters):
        joltage = adapters[index]
        if joltage - current_joltage <= max_difference:
            next_adapter.append(index)
        else:
            break
        index = index + 1
    return next_adapter


def count_adapter_combinations(adapters, lookup={}):
    # counting adapter combinations can be split into sub-probrems that are
    # uniquely identifable by the first adapter in the list
    combo_id = adapters[0]
    if combo_id in lookup:
        return lookup[combo_id]

    if len(adapters) == 1:
        return 1

    next_adapters = find_next_adapter(0, adapters, 3)
    count = 0
    for adapter in next_adapters:
        count = count + count_adapter_combinations(adapters[adapter:], lookup)
    lookup[combo_id] = count
    return count


class WaitingArea:
    def __init__(self, seats, max_depth=1, neighbor_threshold=4):
        self.seats = seats
        self.empty = "L"
        self.occupied = "#"
        self.floor = "."
        self.default_directions = [
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
            (-1, 0),
        ]
        self.max_depth = max_depth
        self.neighbor_threshold = neighbor_threshold
        self.width = len(seats[0])
        self.height = len(seats)

    def get_seat(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]
        if x < 0 or y < 0:
            return None
        try:
            status = self.seats[y][x]
        except:
            return None
        return status

    def count_occupied(self):
        total = 0
        for row in range(self.height):
            for col in range(self.width):
                if self.get_seat((col, row)) == self.occupied:
                    total = total + 1
        return total

    def find_occupied_neighbors(
        self,
        x,
        y,
        directions,
        depth=1,
        occupied_neighbors=[],
    ):
        if len(directions) == 0:
            return occupied_neighbors
        elif self.max_depth and depth > self.max_depth:
            return occupied_neighbors
        search_directions = copy.deepcopy(directions)
        for direction in search_directions:
            direction_depth = tuple(d * depth for d in direction)
            coordinates = (x + direction_depth[0], y + direction_depth[1])
            seat = self.get_seat(coordinates)
            if seat == None:  # out of bounds
                directions.remove(direction)
            elif seat == self.empty:
                directions.remove(direction)
            elif seat == self.occupied:
                occupied_neighbors.append(coordinates)
                directions.remove(direction)
        return self.find_occupied_neighbors(
            x, y, directions, depth + 1, occupied_neighbors
        )

    def count_occupied_neighbors(self, x, y):
        neighbors = self.find_occupied_neighbors(
            x,
            y,
            directions=copy.deepcopy(self.default_directions),
            depth=1,
            occupied_neighbors=[],
        )
        return len(neighbors)

    def __str__(self):
        string = ""
        for row in self.seats:
            string = string + "".join(row) + "\n"
        return string

    def step(self):
        changed = False
        updated_seats = copy.deepcopy(self.seats)
        for row in range(self.height):
            for col in range(self.width):
                seat = self.get_seat((col, row))
                if seat == self.floor:
                    updated_seats[row][col] = self.floor
                    continue
                occupied_neighbors = self.count_occupied_neighbors(col, row)
                if seat == self.empty and occupied_neighbors == 0:
                    updated_seats[row][col] = self.occupied
                    changed = True
                elif (
                    seat == self.occupied
                    and occupied_neighbors >= self.neighbor_threshold
                ):
                    updated_seats[row][col] = self.empty
                    changed = True
        self.seats = updated_seats
        return changed

    def run(self):
        counter = 0
        while self.step():
            counter = counter + 1
        return counter


class Ferry:
    def __init__(self):
        self.coordinates = (0, 0)
        self.bearing = 0  # due east

    def move_north(self, distance):
        self.coordinates = (self.coordinates[0], self.coordinates[1] + distance)

    def move_east(self, distance):
        self.coordinates = (self.coordinates[0] + distance, self.coordinates[1])

    def move_south(self, distance):
        self.coordinates = (self.coordinates[0], self.coordinates[1] - distance)

    def move_west(self, distance):
        self.coordinates = (self.coordinates[0] - distance, self.coordinates[1])

    def turn_left(self, degrees):
        self.bearing = (self.bearing - degrees) % 360

    def turn_right(self, degrees):
        self.bearing = (self.bearing + degrees) % 360

    def move_forward(self, distance):
        if self.bearing == 270:  # north
            self.move_north(distance)
        elif self.bearing == 0:  # east
            self.move_east(distance)
        elif self.bearing == 90:  # south
            self.move_south(distance)
        elif self.bearing == 180:  # west
            self.move_west(distance)

    def move(self, instruction):
        action = instruction[0:1]
        scalar = int(instruction[1:])
        if action == "N":
            self.move_north(scalar)
        elif action == "S":
            self.move_south(scalar)
        elif action == "E":
            self.move_east(scalar)
        elif action == "W":
            self.move_west(scalar)
        elif action == "L":
            self.turn_left(scalar)
        elif action == "R":
            self.turn_right(scalar)
        elif action == "F":
            self.move_forward(scalar)

    def get_bearing(self):
        return self.bearing

    def get_coordinates(self):
        return self.coordinates


class WaypointFerry(Ferry):
    def __init__(self, waypoint=(10, 1)):
        super().__init__()
        self.waypoint = waypoint

    def get_waypoint(self):
        return self.waypoint

    def move_north(self, distance):
        self.waypoint = (self.waypoint[0], self.waypoint[1] + distance)

    def move_east(self, distance):
        self.waypoint = (self.waypoint[0] + distance, self.waypoint[1])

    def move_south(self, distance):
        self.waypoint = (self.waypoint[0], self.waypoint[1] - distance)

    def move_west(self, distance):
        self.waypoint = (self.waypoint[0] - distance, self.waypoint[1])

    def rotate_90_clockwise(self):
        x, y = self.get_waypoint()
        self.waypoint = (y, -x)

    def rotate_90_counter_clockwise(self):
        x, y = self.get_waypoint()
        self.waypoint = (-y, x)

    def turn_left(self, degrees):
        for x in range(int(degrees / 90)):
            self.rotate_90_counter_clockwise()

    def turn_right(self, degrees):
        for x in range(int(degrees / 90)):
            self.rotate_90_clockwise()

    def move_forward(self, distance):
        x, y = self.get_coordinates()
        x = x + (distance * self.waypoint[0])
        y = y + (distance * self.waypoint[1])
        self.coordinates = (x, y)


def find_next_bus(start_time, schedule):
    time = start_time
    while True:
        for bus in schedule:
            if bus == "x":
                continue
            if time % bus == 0:
                return (time, bus)
        time = time + 1


def calculate_product(schedule):
    product = 1
    for bus in schedule:
        if bus == "x":
            pass
        else:
            product = product * bus
    return product


def find_minute_offset_timestamp(schedule):
    product = calculate_product(schedule)
    sum = 0
    for index in range(len(schedule)):
        bus_id = schedule[index]
        if bus_id == "x":
            continue
        remainder = index - bus_id
        pi = int(product / bus_id)
        inverse = pow(pi, -1, bus_id)
        sum = sum + (remainder * pi * inverse)
    return product - (sum % product)


class Emulator:
    def __init__(self):
        self.mask = ""
        self.memory = {}

    def execute(self, instruction):
        op, value = instruction.split(" = ")
        if "mask" in instruction:
            self.set_mask(value)
        elif "mem" in instruction:
            addr = int(op[4:-1])
            value = int(value)
            self.set_memory(addr, value)

    def set_mask(self, mask):
        self.mask = mask

    def calc_mask(self, value):
        output = ""
        binary = "{0:036b}".format(value)
        for i in range(36):
            if self.mask[i] == "0":
                output = output + "0"
            elif self.mask[i] == "1":
                output = output + "1"
            elif self.mask[i] == "X":
                output = output + binary[i]
        output = int(output, 2)
        return output

    def set_memory(self, addr, value):
        output = self.calc_mask(value)
        self.memory[addr] = output


class Emulator2(Emulator):
    def __init__(self):
        super().__init__()

    def set_floating_memory(self, addr, value):
        floating_bits = addr.count("X")
        for i in range(2 ** floating_bits):
            pattern = "{0:0%db}" % floating_bits
            bits = pattern.format(i)
            new_addr = ""
            for c in addr:
                if c == "X":
                    new_addr = new_addr + bits[0]
                    bits = bits[1:]
                else:
                    new_addr = new_addr + c
            new_addr = int(new_addr, 2)
            self.memory[new_addr] = value

    def set_memory(self, addr, value):
        dest = ""
        addr_binary = "{0:036b}".format(addr)
        binary = "{0:036b}".format(value)
        for i in range(36):
            if self.mask[i] == "0":
                dest = dest + addr_binary[i]
            elif self.mask[i] == "1":
                dest = dest + "1"
            elif self.mask[i] == "X":
                dest = dest + "X"

        self.set_floating_memory(dest, value)
