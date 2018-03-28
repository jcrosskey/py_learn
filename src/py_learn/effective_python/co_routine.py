"""
Item 40: Use Coroutines to run many functions concurrently

Threads are costly to start, each executing thread requires about 8MB memory.
Constantly creating new concurrent functions and finishing them uses lots of
overhead and slows everything down.

Coroutines are implemented as as extension to generators. The cost of starting
a generator coroutine is a function call. Once active, they each use less than
1KB of memory until they are exhausted.

Coroutines work by enabling the code consuming a generator to `send` a value
back into the generator function after each `yield` expression. The generator
function receives the value passed to the `send` function as the result of the
corresponding `yield` expression.
"""

from collections import namedtuple


def my_coroutine():
    while True:
        received = yield
        print(f'Received: {received}')


def demo1():
    it = my_coroutine()
    # prepare the generator for receiving the first `send`
    # by advancing it to the first `yield` expression
    next(it)
    it.send('First')
    it.send('Second')


ALIVE = '*'
EMPTY = '-'
Query = namedtuple('Query', ('y', 'x'))
Transition = namedtuple('Transition', ('y', 'x', 'state'))
TICK = object()


def count_neighbors(y, x):
    n_ = yield Query(y+1, x+0)
    ne = yield Query(y+1, x+1)
    e_ = yield Query(y+0, x+1)
    se = yield Query(y-1, x+1)
    s_ = yield Query(y-1, x+0)
    sw = yield Query(y-1, x-1)
    w_ = yield Query(y+0, x-1)
    nw = yield Query(y+1, x-1)
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    return sum([state == ALIVE for state in neighbor_states])


def demo_count_neighbors():
    print('Demo count neighbors with grid size 10 by 5')
    it = count_neighbors(10, 5)
    q1 = next(it)
    print(f'1st yield: {q1}')
    q2 = it.send(ALIVE)
    print(f'2nd yield: {q2}')
    q3 = it.send(ALIVE)
    print(f'3rd yield: {q3}')
    i = 4
    while True:
        try:
            count = it.send(EMPTY)
            print(f'{i}th yield: {count}')
            i += 1
        except StopIteration as e:
            print(f'Live Count: {e.value}, last yield: {count}\n')
            break


def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
        else:
            if neighbors == 3:
                return ALIVE
    return state


def step_cell(y, x):
    state = yield Query(y, x)
    neighbors = yield from count_neighbors(y, x)
    next_state = game_logic(state, neighbors)
    yield Transition(y, x, next_state)
    return neighbors


def demo_step_cell():
    print('Demo step sell with grid size 10 by 5')
    it = step_cell(10, 5)
    q0 = next(it)
    print(f'0-Me:{q0}')
    q1 = it.send(ALIVE)
    print(f'1-Q1:{q1}')
    i = 2
    while True:
        try:
            t1 = it.send(ALIVE)
            print(f'{i}-Q{i}:{t1}')
            i += 1
        except StopIteration as e:
            print(f'Live Count: {e}, Outcome: {t1}\n')
            break


def simulate(height, width):
    while True:
        for y in range(height):
            for x in range(width):
                yield from step_cell(y, x)
                yield TICK


class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def __str__(self):
        s = ''
        for idx in range(self.height):
            s += ''.join(self.rows[idx])
            s += '\n'
            return s

    def query(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def assign(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state


def live_a_generation(grid, sim):
    progeny = Grid(grid.height, grid.width)
    item = next(sim)
    #     print(f'sim item: {item}')
    while item is not TICK:
        # Query
        if isinstance(item, Query):
            state = grid.query(item.y, item.x)
            #             print(f'Sending state {state}')
            item = sim.send(state)
            # Transition
        else:
            progeny.assign(item.y, item.x, item.state)
            item = next(sim)
            return progeny


def demo_game():
    grid = Grid(5, 9)
    grid.assign(0, 3, ALIVE)
    grid.assign(1, 4, ALIVE)
    grid.assign(2, 3, ALIVE)
    grid.assign(2, 4, ALIVE)
    grid.assign(2, 5, ALIVE)
    print(f'Start grid\n{grid}')

    sim = simulate(grid.height, grid.width)
    for i in range(5):
        grid = live_a_generation(grid, sim)
        print(f'Generation {i}:\n{grid}')


if __name__ == '__main__':
    demo_count_neighbors()
    demo_step_cell()
    #     demo_game()
