import sys
import json
import constraint

def load_data():
    with open("MacedonianWords.json", "r", encoding="utf-8") as f:
        words = json.load(f)
    with open("123combo.json", "r", encoding="utf-8") as f:
        combos = json.load(f)
    return words, combos

def get_slots(grid_size, question_blocks):
    """Identifies horizontal and vertical word slots in the grid."""
    horizontal_slots = []
    for r in range(grid_size):
        current_slot = []
        for c in range(grid_size):
            if (r, c) not in question_blocks:
                current_slot.append((r, c))
            else:
                if len(current_slot) >= 1:
                    horizontal_slots.append(tuple(current_slot))
                current_slot = []
        if len(current_slot) >= 1:
            horizontal_slots.append(tuple(current_slot))

    vertical_slots = []
    for c in range(grid_size):
        current_slot = []
        for r in range(grid_size):
            if (r, c) not in question_blocks:
                current_slot.append((r, c))
            else:
                if len(current_slot) >= 1:
                    vertical_slots.append(tuple(current_slot))
                current_slot = []
        if len(current_slot) >= 1:
            vertical_slots.append(tuple(current_slot))
            
    return horizontal_slots, vertical_slots

def solve(grid_size, question_blocks):
    words, combos = load_data()
    
    h_slots, v_slots = get_slots(grid_size, question_blocks)
    
    problem = constraint.Problem()
    
    all_slots = []
    for i, slot in enumerate(h_slots):
        slot_name = f"h_{i}"
        all_slots.append((slot_name, slot))
    for i, slot in enumerate(v_slots):
        slot_name = f"v_{i}"
        all_slots.append((slot_name, slot))

    if not all_slots:
        print("No slots found in the grid.")
        return

    # Add variables (slots) to the problem
    for name, coords in all_slots:
        length = str(len(coords))
        
        # Priority 1: Real words
        domain = list(words.get(length, []))
        
        # Priority 2: Combinations (for length 1, 2, 3)
        if length in combos:
            real_set = set(domain)
            for c in combos[length]:
                if c not in real_set:
                    domain.append(c)
        
        if not domain:
            print(f"Error: No words or combinations found for length {length} (slot {name})")
            return

        problem.addVariable(name, domain)

    # Add intersection constraints
    cell_to_slots = {}
    for slot_name, coords in all_slots:
        for idx, coord in enumerate(coords):
            if coord not in cell_to_slots:
                cell_to_slots[coord] = []
            cell_to_slots[coord].append((slot_name, idx))
    
    for coord, info in cell_to_slots.items():
        if len(info) > 1:
            for i in range(len(info)):
                for j in range(i + 1, len(info)):
                    s1_name, s1_idx = info[i]
                    s2_name, s2_idx = info[j]
                    
                    def intersection_constraint(w1, w2, idx1=s1_idx, idx2=s2_idx):
                        return w1[idx1].lower() == w2[idx2].lower()
                    
                    problem.addConstraint(intersection_constraint, (s1_name, s2_name))

    print(f"Solving {grid_size}x{grid_size} crossword...")
    solution = problem.getSolution()
    
    if solution:
        grid = [[" " for _ in range(grid_size)] for _ in range(grid_size)]
        for r, c in question_blocks:
            grid[r][c] = "■"
            
        for name, coords in all_slots:
            word = solution[name]
            for idx, (r, c) in enumerate(coords):
                grid[r][c] = word[idx].upper()
        
        print("\nSolution found:")
        print("-" * (grid_size * 2 + 1))
        for row in grid:
            print("|" + " ".join(row) + "|")
        print("-" * (grid_size * 2 + 1))
    else:
        print("No solution found.")

def main():
    try:
        line = sys.stdin.readline()
        if not line: return
        grid_size = int(line.strip())
    except ValueError:
        print("Invalid grid size. Defaulting to 4.")
        grid_size = 4

    question_blocks = set()
    print(f"Grid size: {grid_size}")
    print("Enter question block coordinates as 'row col' (0-indexed). Empty line to start solving:")
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            break
        try:
            r, c = map(int, line.split())
            if 0 <= r < grid_size and 0 <= c < grid_size:
                question_blocks.add((r, c))
            else:
                print(f"Coordinates out of bounds: {r}, {c}")
        except ValueError:
            print("Invalid input. Use 'row col'.")

    solve(grid_size, question_blocks)

if __name__ == "__main__":
    main()
