calls = 0
fails = 0

def load_board(file):
    grid = []
    with open(file) as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append([int(x) for x in line])
    return grid


def show_board(grid):
    for i in range(9):
        if i in (3, 6):
            print("------+-------+------")
        line = ""
        for j in range(9):
            if j in (3, 6):
                line += "| "
            line += str(grid[i][j]) + " "
        print(line)
    print()


def init_domains(grid):
    dom = {}
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                dom[(i, j)] = {grid[i][j]}
            else:
                dom[(i, j)] = set(range(1, 10))
    return dom


def neighbors(r, c):
    n = set()

    for j in range(9):
        if j != c:
            n.add((r, j))

    for i in range(9):
        if i != r:
            n.add((i, c))

    br = (r // 3) * 3
    bc = (c // 3) * 3

    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if (i, j) != (r, c):
                n.add((i, j))

    return n


def make_arc_consistent(dom):
    q = []
    for cell in dom:
        for nb in neighbors(*cell):
            q.append((cell, nb))

    while q:
        a, b = q.pop(0)

        if reduce_domain(dom, a, b):
            if len(dom[a]) == 0:
                return False

            for k in neighbors(*a):
                if k != b:
                    q.append((k, a))

    return True


def reduce_domain(dom, a, b):
    changed = False
    for val in list(dom[a]):
        if dom[b] == {val}:
            dom[a].discard(val)
            changed = True
    return changed


def pick_cell(dom, used):
    best = None
    size = 10

    for cell in dom:
        if cell not in used and len(dom[cell]) < size:
            best = cell
            size = len(dom[cell])

    return best


def prune(dom, used, cell, val):
    removed = []

    for nb in neighbors(*cell):
        if nb not in used and val in dom[nb]:
            dom[nb].discard(val)
            removed.append((nb, val))

            if len(dom[nb]) == 0:
                return False, removed

    return True, removed


def restore(dom, removed):
    for cell, val in removed:
        dom[cell].add(val)


def solve_bt(dom, used):
    global calls, fails
    calls += 1

    if len(used) == 81:
        return used

    cell = pick_cell(dom, used)

    for val in list(dom[cell]):
        used[cell] = val
        old = set(dom[cell])
        dom[cell] = {val}

        ok, removed = prune(dom, used, cell, val)

        if ok:
            ans = solve_bt(dom, used)
            if ans:
                return ans

        restore(dom, removed)
        dom[cell] = old
        del used[cell]

    fails += 1
    return None


def run(file):
    global calls, fails
    calls = 0
    fails = 0

    print("=" * 40)
    print("File:", file)
    print("=" * 40)

    grid = load_board(file)
    print("Input:")
    show_board(grid)

    dom = init_domains(grid)

    if not make_arc_consistent(dom):
        print("No solution (AC-3 failed)\n")
        return

    used = {}
    for cell in dom:
        if len(dom[cell]) == 1:
            used[cell] = next(iter(dom[cell]))

    ans = solve_bt(dom, used)

    if not ans:
        print("No solution found\n")
    else:
        res = [[0]*9 for _ in range(9)]
        for (i, j), v in ans.items():
            res[i][j] = v

        print("Solved:")
        show_board(res)

    print("Calls:", calls)
    print("Fails:", fails)
    print()


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))

    files = ["easy.txt", "medium.txt", "hard.txt", "evil.txt"]
    files = [os.path.join(base, f) for f in files]

    for f in files:
        try:
            run(f)
        except FileNotFoundError:
            print("Missing file:", f, "\n")