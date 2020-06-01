import math
import random
import numpy as np


class Player:
    def __init__(self, isFirst, array):
        self.isFirst = isFirst
        self.array = array
        self.tree = _GameTree(isFirst, 4, 2)
        self.direcnumF = [0,0,0,0]
        self.direcnumN = [0,0,0,0]
        self.filename = "testdir"

    def output(self, currentRound, board, mode):
        lastmode = ""
        decision = (-1,)
        if self.isFirst:
            lastmode = "position" if mode == "direction" else "direction"
        else:
            lastmode = "position" if mode == "position" else "direction"
        self.tree.cut_to_current(board, lastmode)
        if mode == "position" or mode == "direction":
            decision = self.tree.decide(
                self.tree.root, self.tree.get_depth(), -float('inf'), float('inf'), mode, currentRound)[0]
            if mode=='direction':
                if self.isFirst:
                    self.direcnumF[decision]+=1
                else:
                    self.direcnumN[decision]+=1
            file=open(self.filename+'.txt','a')
            file.write(str(self.direcnumF)+ str(self.direcnumN)+ '\n')
        else:
            pass
        self.tree.shift(decision, mode)
        if currentRound % 20 == 0:
            self.tree.modify_depth(board, currentRound)
        return decision


class _Node:
    """
    决策树节点, 记录决策内容. belong表示谁做的决策, 己方为 isFirst, 反之为 not isFirst.
    因其记录的是到达这一步的决策, 其面临的下一步决策就是另一方的. 所以 belong=isFirst 的是 min 节点, 反之为 max 节点.
    board 为此次决策之后的棋盘
    """

    def __init__(self, mode, decision, belong, board, parent=None):
        self.mode = mode
        self.decision = decision
        self.parent = parent
        self.child = []
        self.belong = belong
        self.board = board
        self.trace_child = None

    def set_add_child(self, position, belong):
        b = self.board.copy()
        mode = "position"
        b.add(belong, position)
        self.child.append(_Node(mode, position, belong, b, parent=self))

    def set_move_child(self, direction, belong):
        b = self.board.copy()
        mode = "direction"
        b.move(belong, direction)
        self.child.append(_Node(mode, direction, belong,
                                b, parent=self))

    def get_decision(self):
        return self.decision

    def get_child_decision(self):
        L = []
        for item in self.child:
            L.append(item.decision)
        return L

    def get_available_pos(self, belong, rround, isComplex):
        """
        获取可以落子的位置列表.
        - 如果可以在己方落子, 先添加己方位置.
        - 当且仅当对方空位小于4(主动)或己方没有落子位置时(被动)考虑向对方落子.
        - 向对方落子位置需满足如下条件(主动必须满足, 被动尽量满足):
            - 不能立即被合并
            - 夹在可以合并的两个级别不小于3的棋子之间
        """
        bb = self.board.getRaw()

        def get_right(x, y):
            if y == 7:
                return 0
            else:
                y += 1
                bl = bb[x][y][1]
                v = bb[x][y][0]
                if v != 0:
                    return v
                else:
                    if bl is belong:
                        return 0
                    return get_right(x, y)

        def get_left(x, y):
            if y == 0:
                return 0
            else:
                y -= 1
                bl = bb[x][y][1]
                v = bb[x][y][0]
                if v != 0:
                    return v
                else:
                    if bl is belong:
                        return 0
                    return get_left(x, y)

        def get_up(x, y):
            if x == 0:
                return 0
            else:
                x -= 1
                bl = bb[x][y][1]
                v = bb[x][y][0]
                if v != 0:
                    return v
                else:
                    if bl is belong:
                        return 0
                    return get_up(x, y)

        def get_down(x, y):
            if x == 3:
                return 0
            else:
                x += 1
                bl = bb[x][y][1]
                v = bb[x][y][0]
                if v != 0:
                    return v
                else:
                    if bl is belong:
                        return 0
                    return get_down(x, y)

        pos = self.board.getNext(belong, rround)
        ava = self.board.getNone(not belong)
        L = []
        if pos:  # 主动落子
            L.append(pos)
            if rround > 50:
                if len(ava)<=3 and isComplex:
                    L+=ava
                else:
                    for tile in ava:
                        x = tile[0]
                        y = tile[1]
                        right = get_right(x, y)
                        left = get_left(x, y)
                        up = get_up(x, y)
                        down = get_down(x, y)
                        if (left>=3 and (left==right or left==up or left==down)) or (up>=3 and (up==down or up==right)) or (right>=3 and right==down):
                            L.append(tile)
        else:  # 被动向对方落子
            if ava:
                l = []
                for tile in ava:
                    x = tile[0]
                    y = tile[1]
                    right = get_right(x, y)
                    left = get_left(x, y)
                    up = get_up(x, y)
                    down = get_down(x, y)
                    if (left>=3 and (left==right or left==up or left==down)) or (up>=3 and (up==down or up==right)) or (right>=3 and right==down):
                        L.append(tile)
                    if left != 1 and right != 1 and up != 1 and down != 1:
                        l.append(tile)
                if not L:
                    L = l
                    if not L:
                        L.append(ava[0])
            else:
                L = []
        return L

    def point(self, isFirst):
        values=[0, 2.14, 4.59, 9.85, 21.11, 45.25, 97.00, 207.94, 445.72, 955.42, 2048, 4389.98, 9410.14, 20171.07, 43237.64, 92681.90]
        L, R = np.zeros([4, 4]), np.zeros([4, 4])
        for i in range(4):
            for j in range(4):
                L[i, j] = (2 * self.board.getBelong((i, j)) - 1) * \
                    values[self.board.getValue((i, j))]
                R[i, j] = (2 * self.board.getBelong((i, j + 4)) -
                           1) * values[self.board.getValue((i, j + 4))]

        part1 = np.sum(L) + np.sum(R)
        part2 = np.sum(R > 0) + np.sum(L < 0)
        part3 = np.sum(L == 0) - np.sum(R == 0)
        part4 = np.count_nonzero(R[:3] - R[1:]) + np.count_nonzero(R.T[:3] - R.T[1:]) -\
            np.count_nonzero(L[:3] - L[1:]) - \
            np.count_nonzero(L.T[:3] - L.T[1:])
        return (part1 + part2 + part3 + part4) * (2 * isFirst - 1)

    def __iter__(self):
        """按照从叶到根, 从左到右的顺序迭代"""
        yield self
        if self.child:
            for item in self.child:
                yield item


class _GameTree:
    """
    决策树. 在整场游戏一开始生成, 一直存在, 可避免重复搜索.
    """

    def __init__(self, isFirst, sdc, sds):
        self.root = _Node(None, None, not isFirst, None)
        self.isFirst = isFirst
        self.search_depth_com = sdc
        self.search_depth_sim = sds
        self.complex = True

    def cut_to_current(self, board, mode):
        """
        在对方决策后己方决策前, 将博弈树树根更新为当前局面. 己方决策后这一更新在决策的函数中实现.\\
        mode 为前一次决策的内容. board 为当前棋盘.
        """
        deci = board.getDecision(not self.isFirst)
        if deci:
            for item in self.root.child:
                if item.decision == deci:
                    self.root = item
                    break
            else:
                self.root = _Node(mode, deci, not self.isFirst, board.copy())
        else:  # 可能是回合刚开始我为先手, 也可能是对方已无合法决策
            if self.root.board:
                self.root.belong = not self.root.belong
            else:
                self.root.board = board.copy()

    def shift(self, decision, mode):
        if mode == "position":
            d = self.root.get_child_decision()
            self.root = self.root.child[d.index(decision)]
        elif mode == "direction":
            d = self.root.get_child_decision()
            self.root = self.root.child[d.index((decision,))]
        else:
            self.root.belong = not self.root.belong

    def get_depth(self):
        if self.complex:
            if self.isFirst:
                return self.search_depth_com
            else:
                return self.search_depth_com - 1
        else:
            if self.isFirst:
                return self.search_depth_sim
            else:
                return self.search_depth_sim

    def decide(self, node, depth, alpha, beta, mode, rround):
        """
        返回决策内容和分值
        """
        if self.isFirst:
            tomove = [3, 1, 0, 2]
        else:
            tomove = [2, 0, 1, 3]
        decision = -1
        if depth == 0 or rround >= 500:
            return decision, node.point(self.isFirst)
        else:
            if self.isFirst:  # 我是先手, 决策顺序是我p, 对p, 我d, 对d
                if node.belong:  # 轮到对方决策, min 节点
                    value = float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround, self.complex)
                        hasput = node.get_child_decision()
                        for i in toput:
                            if i in hasput:
                                item = node.child[hasput.index(i)]
                                value = min(self.decide(
                                    item, depth, alpha, beta, "direction", rround)[1], value)
                            else:
                                b = node.board.copy()
                                b.add(not node.belong, i)
                                newnode = _Node(
                                    mode, i, not node.belong, b, parent=node)
                                node.child.append(newnode)
                                value = min(self.decide(
                                    newnode, depth, alpha, beta, "direction", rround)[1], value)
                            if value < beta:
                                beta = value
                                decision = i
                                node.trace_child = node.child[node.get_child_decision().index(
                                    i)]
                            if alpha >= beta:
                                break
                    if mode == "direction":
                        hasmove = node.get_child_decision()
                        rround += 1
                        for i in tomove[::-1]:
                            if (i,) in hasmove:
                                item = node.child[hasmove.index((i,))]
                                value = min(self.decide(item, depth-1,
                                                        alpha, beta, "position", rround)[1], value)
                            else:
                                b = node.board.copy()
                                if b.move(not node.belong, i):
                                    newnode = _Node(
                                        mode, (i,), not node.belong, b, parent=node)
                                    node.child.append(newnode)
                                    value = min(self.decide(
                                        newnode, depth-1, alpha, beta, "position", rround)[1], value)
                            if value < beta:
                                beta = value
                                decision = i
                                # node.trace_child = node.child[node.get_child_decision().index(
                                #     i)]
                            if alpha >= beta:
                                break
                    if value == float('inf'):
                        return decision, node.point(self.isFirst)+33
                    return decision, value
                else:  # 轮到己方决策, max 节点
                    value = -float("inf")
                    if mode == "position":
                        if self.complex and depth == self.get_depth() and node.trace_child is not None:
                            # print("use",rround)
                            return node.trace_child.decision, 0
                        toput = node.get_available_pos(not node.belong, rround,self.complex)
                        hasput = node.get_child_decision()
                        if len(toput) == 1 and depth == self.get_depth():
                            if toput[0] not in hasput:
                                b = node.board.copy()
                                b.add(not node.belong, toput[0])
                                newnode = _Node(
                                    mode, toput[0], not node.belong, b, parent=node)
                                node.child.append(newnode)
                            return toput[0], 0  # 初次调用自己做决策, 只有一个选择, 立刻返回这个选择
                        for i in toput:
                            if i in hasput:
                                item = node.child[hasput.index(i)]
                                value = max(self.decide(
                                    item, depth, alpha, beta, "position", rround)[1], value)
                            else:
                                b = node.board.copy()
                                b.add(not node.belong, i)
                                newnode = _Node(
                                    mode, i, not node.belong, b, parent=node)
                                node.child.append(newnode)
                                value = max(self.decide(
                                    newnode, depth, alpha, beta, "position", rround)[1], value)
                            if value > alpha:
                                alpha = value
                                decision = i
                                node.trace_child = node.child[node.get_child_decision().index(
                                    i)]
                            if alpha >= beta:
                                break
                    if mode == "direction":
                        hasmove = node.get_child_decision()
                        # print(hasmove)
                        for i in tomove:
                            if (i,) in hasmove:
                                item = node.child[hasmove.index((i,))]
                                value = max(self.decide(item, depth-1,
                                                        alpha, beta, "direction", rround)[1], value)
                            else:
                                b = node.board.copy()
                                if b.move(not node.belong, i):
                                    newnode = _Node(
                                        mode, (i,), not node.belong, b, parent=node)
                                    node.child.append(newnode)
                                    value = max(self.decide(
                                        newnode, depth-1, alpha, beta, "direction", rround)[1], value)
                            if value > alpha:
                                alpha = value
                                decision = i
                                # node.trace_child = node.child[node.get_child_decision().index(
                                #     i)]
                            if alpha >= beta:
                                break
                    if value == -float('inf'):
                        return decision, node.point(self.isFirst)-33
                    return decision, value
            else:  # 对方先手, 决策顺序是对p, 我p, 对d, 我d
                if node.belong:  # 轮到我方决策, max 节点
                    value = -float("inf")
                    if mode == "position":
                        if self.complex and depth == self.get_depth() and node.trace_child is not None:
                            # print("use",rround)
                            return node.trace_child.decision, 0
                        toput = node.get_available_pos(not node.belong, rround,self.complex)
                        hasput = node.get_child_decision()
                        if len(toput) == 1 and depth == self.get_depth():
                            if toput[0] not in hasput:
                                b = node.board.copy()
                                b.add(not node.belong, toput[0])
                                newnode = _Node(
                                    mode, toput[0], not node.belong, b, parent=node)
                                node.child.append(newnode)
                            return toput[0], 0  # 初次调用自己做决策, 只有一个选择, 立刻返回这个选择
                        for i in toput:
                            if i in hasput:
                                item = node.child[hasput.index(i)]
                                value = max(self.decide(
                                    item, depth, alpha, beta, "direction", rround)[1], value)
                            else:
                                b = node.board.copy()
                                b.add(not node.belong, i)
                                newnode = _Node(
                                    mode, i, not node.belong, b, parent=node)
                                node.child.append(newnode)
                                value = max(self.decide(
                                    newnode, depth, alpha, beta, "direction", rround)[1], value)
                            if value > alpha:
                                alpha = value
                                decision = i
                                node.trace_child = node.child[node.get_child_decision().index(
                                    i)]
                            if alpha >= beta:
                                break
                    if mode == "direction":
                        hasmove = node.get_child_decision()
                        # print(hasmove)
                        rround += 1
                        for i in tomove:
                            if (i,) in hasmove:
                                item = node.child[hasmove.index((i,))]
                                value = max(self.decide(item, depth-1,
                                                        alpha, beta, "position", rround)[1], value)
                            else:
                                b = node.board.copy()
                                if b.move(not node.belong, i):
                                    newnode = _Node(
                                        mode, (i,), not node.belong, b, parent=node)
                                    node.child.append(newnode)
                                    value = max(self.decide(
                                        newnode, depth-1, alpha, beta, "position", rround)[1], value)
                            if value > alpha:
                                alpha = value
                                decision = i
                                # node.trace_child = node.child[node.get_child_decision().index(
                                #     i)]
                            if alpha >= beta:
                                break
                    if value == -float('inf'):
                        return decision, node.point(self.isFirst)-33
                    return decision, value
                else:  # 轮到对方决策, min 节点
                    value = float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround,self.complex)
                        hasput = node.get_child_decision()
                        for i in toput:
                            if i in hasput:
                                item = node.child[hasput.index(i)]
                                value = min(self.decide(
                                    item, depth, alpha, beta, "position", rround)[1], value)
                            else:
                                b = node.board.copy()
                                b.add(not node.belong, i)
                                newnode = _Node(
                                    mode, i, not node.belong, b, parent=node)
                                node.child.append(newnode)
                                value = min(self.decide(
                                    newnode, depth, alpha, beta, "position", rround)[1], value)
                            if value < beta:
                                beta = value
                                decision = i
                                node.trace_child = node.child[node.get_child_decision().index(
                                    i)]
                            if alpha >= beta:
                                break
                    if mode == "direction":
                        hasmove = node.get_child_decision()
                        for i in tomove[::-1]:
                            if (i,) in hasmove:
                                item = node.child[hasmove.index((i,))]
                                value = min(self.decide(item, depth-1,
                                                        alpha, beta, "direction", rround)[1], value)
                            else:
                                b = node.board.copy()
                                if b.move(not node.belong, i):
                                    newnode = _Node(
                                        mode, (i,), not node.belong, b, parent=node)
                                    node.child.append(newnode)
                                    value = min(self.decide(
                                        newnode, depth-1, alpha, beta, "direction", rround)[1], value)
                            if value < beta:
                                beta = value
                                decision = i
                                # node.trace_child = node.child[node.get_child_decision().index(
                                #     i)]
                            if alpha >= beta:
                                break
                    if value == float('inf'):
                        return decision, node.point(self.isFirst)+33
                    return decision, value

    def modify_depth(self, board, currentRound):
        left = board.getTime(self.isFirst)
        if self.complex and (left-0.7)/5 > (500-currentRound)/500:
            self.search_depth_com=6
        else:
            self.search_depth_com=4
        # print(self.search_depth_com)
        if left < 0.7:
            self.complex = False
