import math
import random
import numpy as np


class Player:
    def __init__(self, isFirst, array):
        self.isFirst = isFirst
        self.array = array
        self.tree = _GameTree(isFirst, 4)
        self.updateR = [100, 200, 260, 320, 370, 400, 430, 450, 470, 490]

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
                self.tree.root, self.tree.search_depth, -float('inf'), float('inf'), mode, currentRound)[0]
        else:
            pass
        self.tree.shift(decision, mode)
        if currentRound in self.updateR:
            self.tree.modify_depth(board, currentRound)
        return decision


class _Node:
    """
    决策树节点, 记录决策内容. belong表示谁做的决策, 己方为 isFirst, 反之为 not isFirst.
    因其记录的是到达这一步的决策, 其面临的下一步决策就是另一方的. 所以 belong=isFirst 的是 min 节点, 反之为 max 节点.
    board 为此次决策之后的棋盘
    """

    PARM1 = 1
    PARM2 = 1
    PARM3 = 1
    PARM4 = 1
    PARM = [PARM1, PARM2, PARM3, PARM4]

    def __init__(self, mode, decision, belong, board, parent=None):
        self.mode = mode
        self.decision = decision
        self.parent = parent
        self.child = []
        self.belong = belong
        self.board = board

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

    def get_available_pos(self, belong, rround):
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
            for tile in ava:
                x = tile[0]
                y = tile[1]
                right = get_right(x, y)
                left = get_left(x, y)
                up = get_up(x, y)
                down = get_down(x, y)
                if (left == right and left >= 3) or (up == down and up >= 3):
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
                    if (left == right and left >= 3) or (up == down and up >= 3):
                        L.append(tile)
                    if left != 1 and right != 1 and up != 1 and down != 1:
                        l.append(tile)
                if not L:
                    L = l
                    if not L:
                        L.append(random.choice(ava))
            else:
                L = []
        return L

    def point(self, isFirst, currentRound):
        # mons
        mons = []
        ylist = []
        if isFirst:
            ylist = [0, 1, 2, 3]
        else:
            ylist = [4, 5, 6, 7]
        mon = 0
        for x in range(4):
            currentv = 0
            for y in ylist:
                nextv = self.board.getValue((x, y))
                if nextv*currentv != 0 and self.board.getBelong((x, y)):
                    mon += np.sign(nextv-currentv)
                    currentv = nextv
        mons.append(abs(mon))
        mon = 0
        for y in ylist:
            currentv = 0
            for x in range(4):
                nextv = self.board.getValue((x, y))
                if nextv*currentv != 0 and self.board.getBelong((x, y)):
                    mon += np.sign(nextv-currentv)
                    currentv = nextv
        mons.append(abs(mon))
        mon = mons[0]+mons[1]
        # dif
        differ = 0
        L1 = self.board.getScore(isFirst)
        L2 = self.board.getScore(not isFirst)
        for i in range(min(len(L1), len(L2))):
            dif = L1[-1-i]-L2[-1-i]
            if dif != 0:
                differ = (1 << abs(dif))*(2*(dif > 0)-1)
                break
        # empty
        emp = len(self.board.getNone(isFirst)) - \
            len(self.board.getNone(not isFirst))
        return mon+differ+emp

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

    def __init__(self, isFirst, sd):
        self.root = _Node(None, None, not isFirst, None)
        self.isFirst = isFirst
        self.search_depth = sd

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
            return decision, node.point(self.isFirst, rround)
        else:
            if self.isFirst:  # 我是先手, 决策顺序是我p, 对p, 我d, 对d
                if node.belong:  # 轮到对方决策, min 节点
                    value = float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround)
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
                            if alpha >= beta:
                                break
                    if value == float('inf'):
                        return decision, node.point(self.isFirst, rround)
                    return decision, value
                else:  # 轮到己方决策, max 节点
                    value = -float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround)
                        hasput = node.get_child_decision()
                        if len(toput) == 1 and depth == self.search_depth:
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
                            if alpha >= beta:
                                break
                    if value == -float('inf'):
                        return decision, node.point(self.isFirst, rround)
                    return decision, value
            else:  # 对方先手, 决策顺序是对p, 我p, 对d, 我d
                if node.belong:  # 轮到我方决策, max 节点
                    value = -float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround)
                        hasput = node.get_child_decision()
                        if len(toput) == 1 and depth == self.search_depth:
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
                            if alpha >= beta:
                                break
                    if value == -float('inf'):
                        return decision, node.point(self.isFirst, rround)
                    return decision, value
                else:  # 轮到对方决策, min 节点
                    value = float("inf")
                    if mode == "position":
                        toput = node.get_available_pos(not node.belong, rround)
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
                            if alpha >= beta:
                                break
                    if value == float('inf'):
                        return decision, node.point(self.isFirst, rround)
                    return decision, value

    def modify_depth(self, board, currentRound):
        left = board.getTime(self.isFirst)
        used = 5-left
        bound = [2, 4]
        if currentRound < 400 and currentRound > 100:
            bound = [3, 4]
        if 500/currentRound < 5/used and self.search_depth < bound[1]:
            self.search_depth += 1
        elif 500/currentRound > 5/used and self.search_depth > bound[0]:
            self.search_depth -= 1
