import numpy as np


class Player:
    def __init__(self, isFirst, array):
        self.isFirst = isFirst
        self.array = array
        self.free = True
        
    def output(self, currentRound, board, mode):
        if mode == "position":
            if currentRound < 50:
                return walk(self, board, currentRound)
            if currentRound < 150:
                if self.isFirst:
                    return walk_s1(self, board, currentRound, 4, -float("inf"), float("inf"))
                return walk_s2(self, board, currentRound, 3, -float("inf"), float("inf"))
            if currentRound % 20 == 0 and self.free:
                if board.getTime(self.isFirst) < 1:
                    self.free = False
            if self.free:
                if self.isFirst:
                    return walk_c1(self, board, currentRound, 4, -float("inf"), float("inf"))
                return walk_c2(self, board, currentRound, 3, -float("inf"), float("inf"))
            if self.isFirst:
                return walk_s1(self, board, currentRound, 4, -float("inf"), float("inf"))
            return walk_s2(self, board, currentRound, 3, -float("inf"), float("inf"))
        elif mode == "direction":
            if self.free:
                if self.isFirst:
                    return dec_c1(self, board, currentRound, 4, -float("inf"), float("inf"))
                else:
                    return dec_c2(self, board, currentRound, 4, -float("inf"), float("inf"))
            return dec_s(self, board, currentRound, 2, -float("inf"), float("inf"))
        else:
            return

def price(self, board):
    values=[0, 2, 5, 12, 27, 58, 121, 248, 503, 1014, 2037]
    L, R = np.zeros([4, 4]), np.zeros([4, 4])
    for i in range(4):
        for j in range(4):
            L[i, j] = (2 * board.getBelong((i, j)) - 1) * values[board.getValue((i, j))]
            R[i, j] = (2 * board.getBelong((i, j + 4)) - 1) * values[board.getValue((i, j + 4))]
    
    part1 = np.sum(L + R)
    part2 = np.sum(R > 0) - np.sum(L < 0)
    part3 = np.count_nonzero(R) - np.count_nonzero(L)
    part4 = np.count_nonzero(R[:3] - R[1:]) + np.count_nonzero(R.T[:3] - R.T[1:]) -\
            np.count_nonzero(L[:3] - L[1:]) - np.count_nonzero(L.T[:3] - L.T[1:])    
    return (2 * part1 + part2 + part3 + part4) * (2 * self.isFirst - 1)

def price_w(self, board):
    values=[0, 2, 5, 12, 27, 58, 121, 248, 503, 1014, 2037]
    L, R = np.zeros([4, 4]), np.zeros([4, 4])
    for i in range(4):
        for j in range(4):
            L[i, j] = (2 * board.getBelong((i, j)) - 1) * values[board.getValue((i, j))]
            R[i, j] = (2 * board.getBelong((i, j + 4)) - 1) * values[board.getValue((i, j + 4))]
    
    part1 = np.sum(L + R)
    part2 = np.sum(R > 0) - np.sum(L < 0)
    part4 = np.sum((R[:3] == R[1:]) * R[:3]) + np.sum((R.T[:3] == R.T[1:]) * R.T[:3]) + \
            np.sum((L[:3] == L[1:]) * L[:3]) + np.sum((L.T[:3] == L.T[1:]) * L.T[:3])
    return (2 * part1 + part2 + part4) * (2 * self.isFirst - 1)

def price_s(self, board):
    return np.sum(2 ** np.array(board.getScore(self.isFirst))) - \
           np.sum(2 ** np.array(board.getScore(not self.isFirst)))  

def walk(self, board, currentRound):
    another = board.getNext(self.isFirst, currentRound)
    if another != ():
        return another
    return board.getNone(not self.isFirst)[0]
    
def walk_s1(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price_s(self, b)
    if depth == 1:
        value = float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                value = min(walk_s1(self, b, currentRound, 0, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price_s(self, b) + 33
        return value
    if depth == 2:
        value = -float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = max(walk_s1(self, b, currentRound, 1, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price_s(self, b) - 33
        return value
    if depth == 3:
        value = float("inf")
        another = board.getNext(False, currentRound)
        available = board.getNone(True)
        if another != ():
            b.add(False, another)
            value = min(walk_s1(self, b, currentRound, 2, alpha, beta), value)
            beta = min(beta, value)
            b = board.copy()
        for p in available:
            b.add(True, p)
            value = min(walk_s1(self, b, currentRound, 2, alpha, beta), value)
            beta = min(beta, value)
            if alpha >= beta:
                break
            b = board.copy()
        return value
    if depth == 4:
        decision = -1
        value = -float("inf")
        another = board.getNext(True, currentRound)
        available = board.getNone(False)
        if another != ():
            b.add(True, another)
            temp = walk_s1(self, b, currentRound, 3, alpha, beta)
            if temp > value:
                value = temp
                decision = another
            alpha = max(alpha, value)
            b = board.copy()
        for p in available:
            b.add(False, p)
            temp = walk_s1(self, b, currentRound, 3, alpha, beta)
            if temp > value:
                value = temp
                decision = p
            alpha = max(alpha, value)
            b = board.copy()
        return decision

def walk_s2(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price_s(self, b)
    if depth == 1:
        value = -float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                value = max(walk_s2(self, b, currentRound, 0, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price_s(self, b) - 33
        return value
    if depth == 2:
        value = float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = min(walk_s2(self, b, currentRound, 1, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price_s(self, b) + 33
        return value
    if depth == 3:
        decision = -1
        value = -float("inf")
        another = board.getNext(False, currentRound)
        available = board.getNone(True)
        if another != ():
            b.add(False, another)
            temp = walk_s2(self, b, currentRound, 2, alpha, beta)
            if temp > value:
                value = temp
                decision = another
            alpha = max(alpha, value)
            b = board.copy()
        for p in available:
            b.add(True, p)
            temp = walk_s2(self, b, currentRound, 2, alpha, beta)
            if temp > value:
                value = temp
                decision = p
            alpha = max(alpha, value)
            b = board.copy()
        return decision
    
def walk_c1(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price_w(self, b)
    if depth == 1:
        value = float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                value = min(walk_c1(self, b, currentRound, 0, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price_w(self, b) + 33
        return value
    if depth == 2:
        value = -float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = max(walk_c1(self, b, currentRound, 1, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price_w(self, b) - 33
        return value
    if depth == 3:
        value = float("inf")
        another = board.getNext(False, currentRound)
        available = board.getNone(True)
        if another != ():
            b.add(False, another)
            value = min(walk_c1(self, b, currentRound, 2, alpha, beta), value)
            beta = min(beta, value)
            b = board.copy()
        for p in available:
            b.add(True, p)
            value = min(walk_c1(self, b, currentRound, 2, alpha, beta), value)
            beta = min(beta, value)
            if alpha >= beta:
                break
            b = board.copy()
        if value == float("inf"):
            return price_w(self, b) + 33
        return value
    if depth == 4:
        decision = -1
        value = -float("inf")
        another = board.getNext(True, currentRound)
        available = board.getNone(False)
        if another != ():
            b.add(True, another)
            temp = walk_c1(self, b, currentRound, 3, alpha, beta)
            if temp > value:
                value = temp
                decision = another
            alpha = max(alpha, value)
            b = board.copy()
        for p in available:
            b.add(False, p)
            temp = walk_c1(self, b, currentRound, 3, alpha, beta)
            if temp > value:
                value = temp
                decision = p
            alpha = max(alpha, value)
            b = board.copy()
        return decision 

def walk_c2(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price_w(self, b)
    if depth == 1:
        value = -float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                value = max(walk_c2(self, b, currentRound, 0, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price_w(self, b) - 33
        return value
    if depth == 2:
        value = float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = min(walk_c2(self, b, currentRound, 1, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price_w(self, b) + 33
        return value
    if depth == 3:
        decision = -1
        value = -float("inf")
        another = board.getNext(False, currentRound)
        available = board.getNone(True)
        if another != ():
            b.add(False, another)
            temp = walk_c2(self, b, currentRound, 2, alpha, beta)
            if temp > value:
                value = temp
                decision = another
            alpha = max(alpha, value)
            b = board.copy()
        for p in available:
            b.add(True, p)
            temp = walk_c2(self, b, currentRound, 2, alpha, beta)
            if temp > value:
                value = temp
                decision = p
            alpha = max(alpha, value)
            b = board.copy()
        return decision
    
def dec_c1(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price(self, b)
    if depth == 1:
        value = float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                value = min(dec_c1(self, b, currentRound, 0, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price(self, b) + 33
        return value
    if depth == 2:
        value = -float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = max(dec_c1(self, b, currentRound, 1, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price(self, b) - 33
        return value
    if depth == 3:
        value = float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                if currentRound < 499:
                    currentRound += 1
                    N1 = b.getNext(True, currentRound)
                    if N1 != ():
                        b.add(True, N1)
                    N2 = b.getNext(False, currentRound)
                    if N2 != ():
                        b.add(False, N2)
                value = min(dec_c1(self, b, currentRound, 2, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price(self, b) + 33
        return value
    if depth == 4:
        decision = -1
        value = -float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                temp = dec_c1(self, b, currentRound, 3, alpha, beta)
                if temp > value:
                    value = temp
                    decision = i
                alpha = max(alpha, value)
            b = board.copy()
        return decision
    
def dec_c2(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price(self, b)
    if depth == 1 or depth == 3:
        value = float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(True, i):
                value = min(dec_c2(self, b, currentRound, depth - 1, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price(self, b) + 33
        return value
    if depth == 2:
        value = -float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                if currentRound < 499:
                    currentRound += 1
                    N1 = b.getNext(True, currentRound)
                    if N1 != ():
                        b.add(True, N1)
                    N2 = b.getNext(False, currentRound)
                    if N2 != ():
                        b.add(False, N2)
                value = max(dec_c2(self, b, currentRound, 1, alpha, beta), value)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == -float("inf"):
            return price(self, b) - 33
        return value
    if depth == 4:
        decision = -1
        value = -float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(False, i):
                if currentRound < 499:
                    currentRound += 1
                    N1 = b.getNext(True, currentRound)
                    if N1 != ():
                        b.add(True, N1)
                    N2 = b.getNext(False, currentRound)
                    if N2 != ():
                        b.add(False, N2)
                temp = dec_c2(self, b, currentRound, 3, alpha, beta)
                if temp > value:
                    value = temp
                    decision = i
                alpha = max(alpha, value)
            b = board.copy()
        return decision

def dec_s(self, board, currentRound, depth, alpha, beta):
    b = board.copy()
    if depth == 0:
        return price(self, b)
    if depth == 1:
        value = float("inf")
        for i in [0, 1, 2, 3]:
            if b.move(not self.isFirst, i):
                value = min(dec_s(self, b, currentRound, 0, alpha, beta), value)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            b = board.copy()
        if value == float("inf"):
            return price(self, b) + 33
        return value
    if depth == 2:
        value = -float("inf")
        for i in [1, 0, 3, 2]:
            if b.move(self.isFirst, i):
                temp = dec_s(self, b, currentRound, 1, alpha, beta)
                if temp > value:
                    value = temp
                    decision = i
                alpha = max(alpha, value)
            b = board.copy()
        return decision
    
