__author__ = 'vikentiik'
from copy import deepcopy
import logbook
from timeit import default_timer as timer
logger = logbook.Logger(__file__)
from os import path
logger.handlers.append(logbook.FileHandler('log/' + path.split(__file__)[1] + '.log', bubble=True))


class BoomException(Exception):
    pass


class InvalidMoveException(Exception):
    pass


def move(crd, state):
    target = state.peek(crd)
    if target == '*':
        raise BoomException('boom')
    elif target != '.':
        raise InvalidMoveException()
    else:
        result = state.copy()
        result.discover(crd)
    return result


g_quality_calc_cnt = 0
g_find_cnt = 0
class MSState(object):

    scale, data = None, None
    quality = None

    def __lt__(self, other):
        return self.get_quality() < other.get_quality()

    #caching quality is about 30% speedup on 20x20 cases
    def calculate_quality(self):
        global g_quality_calc_cnt
        g_quality_calc_cnt += 1
        self.quality = len(self.data) - len(self.find_all('.'))
        return self.quality
    # def quality(self):
    #     return len(self.data) - len(self.find_all('.'))
    def get_quality(self):
        return self.quality or self.calculate_quality()

    def copy(self):
        #not copying the moves
        result = MSState(self.scale, self.scale ** 2 * '#')
        result.update_state(self)
        return result

    def __repr__(self):
        repr = '{}\n'.format(self.scale)
        for row in range(0, self.scale):
            for col in range(0, self.scale):
                repr += str(self.peek((row,col)))
            repr += '\n'
        return repr

    def update_state(self, state):
        assert self.scale == state.scale
        assert state.scale ** 2 == len(state.data)
        self.data = deepcopy(state.data)
        self.quality = None

    def update_cell(self, crd, value):
        assert all([self.is_crd_valid for _crd in crd])
        self.moves = []
        row, col = crd
        offset = row * self.scale + col
        self.data[offset] = value
        self.quality = None

    def __init__(self, scale, data):
        assert scale ** 2 == len(data)
        self.scale = scale
        self.data = list(data)
        self.quality = None

    def scan(self):
        index = 0
        for elm in self.data:
            yield index, elm
            index += 1

    def peek(self, crd):
        row, col = crd
        offset = row * self.scale + col
        return self.data[offset]

    # def discover(self, crd):
    #     #can't have this recursive, it's too depp for default python's stack
    #     neig_crds = self.get_neighbor_crds(crd)
    #     mines_around = 0
    #     for neig in neig_crds:
    #         if self.peek(neig) == '*':
    #             mines_around += 1
    #     self.update_cell(crd, mines_around)
    #     #print '==discovering'
    #     #print self
    #     if mines_around == 0:
    #         for neig in neig_crds:
    #             if self.peek(neig) == '.': #can't be a '*', i just discovered zero of those around
    #                 self.discover(neig)

    #I do a bunch of real moves and choose one by calculating quality for each.
    #(!not really) Instead, I can make dummy moves than only count how much would be discovered,
    #but do not do update_cell's.
    #What does that buy?
    #Fucking nothing, I can't run a discovery without updating the cells for the recursive
    #discoveries to operate properly..
    def discover(self, start_crd):
        queue = list()
        queue.append(start_crd)
        while len(queue):
            crd = queue.pop(0)
            if self.peek(crd) in '012345678': continue #discovered already
            neig_crds = self.get_neighbor_crds(crd)
            mines_around = [self.peek(neig_crd) for neig_crd in neig_crds].count('*') #eww
            self.update_cell(crd, str(mines_around))
            if not mines_around:
                queue.extend(neig_crds)

    def is_crd_valid(self, crd):
        return crd in range(0, self.scale)

    def get_neighbor_crds(self, crd):
        result = []
        row, col = crd
        for c_row in range(row - 1, row + 1 + 1):
            if self.is_crd_valid(c_row):
                for c_col in range(col - 1, col + 1 + 1):
                    if self.is_crd_valid(c_col):
                        if (row, col) != (c_row, c_col): #can't be it's own neighbor
                            result.append((c_row, c_col))
        return result

    #this is 7.4 s/case against old 9.3 s/case or something like that
    def find_all(self, value):
        global g_find_cnt
        g_find_cnt += 1
        return [(idx // self.scale, idx % self.scale) for idx, elm in self.scan() if elm == value]
        # result = []
        # for row in range(0, self.scale):
        #     for col in range(0, self.scale):
        #         crd = (row, col)
        #         if self.peek(crd) == value:
        #             result.append(crd)
        # return result

    def is_solved(self):
        return len(list(self.possible_moves())) == 0

    def possible_moves(self):
        for row in range(0, self.scale):
            for col in range(0, self.scale):
                if self.peek((row, col)) == '.':
                    yield (row, col)


def parse_cases(file):
    case_states = []
    cases_count = int(file.readline())
    for i in range(0, cases_count):
        case_scale = int(file.readline())
        case_data = ''
        for i in range(0, case_scale):
            case_data += (file.readline()).strip()
        assert len(case_data) == case_scale ** 2, 'data len: {}, case_scale: {}'.format(len(case_data), case_scale)
        case_states.append(MSState(case_scale, case_data))
    return case_states

# def solve_case(state, moves_made = 0)
#     if state.is_solved():
#         return moves_made
#     moves_made += 1
#     moves = [move(move_crd, state) for move_crd in state.possible_moves()]
#     if any([next_move.is_solved() for next_move in moves]):
#         print moves_made
#         return moves_made
#     else:
#         solutions = [solve_case(case, moves_made) for case in moves]
#         return min(solutions)

def solve_case(state):
    start = timer()
    moves_made = 0
    while True:
        if state.is_solved():
            logger.info('solve_case: {}, scale: {}'.format(timer() - start, state.scale))
            return moves_made
        possible_moves = [move(crd, state) for crd in state.possible_moves()]
        #possible_moves.sort(reverse = True)#let's see how much time I wasted sorting random shit
        #..it's.. worse? hard to tell... let it run for 3 hours as i did last time.
        #on large sets this sort has got to make a difference
        #indeed, case 41 is 720 sec this way..
        best_move = possible_moves[0]
        for _move in possible_moves: #this way case 41(1) is 250 sec, 42 is 138
            if _move.get_quality() > best_move.get_quality():
                best_move = _move
        state = best_move
        moves_made += 1
