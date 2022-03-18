import numpy as np
from math import inf
import copy
import time

# Black go first
BLACK = 0
WHITE = 1
SELF_BARRIER_COST = -3
OPPONENT_BARRIER_COST = 3
MAX_PRICE = 140
S = ['　', '◆', '◇', '●', '○', '■', '□']

# 0: empty, 1: black flag, 2: white flag, 3: black pieces,
# 4: white pieces, 5: black barriers, 6: white barriers

class Meichu():
    def __init__(self):
        self.game_over = False
        self.checkerboard = np.zeros([9,9],dtype=int)
        self.n_pieces = [5, 5] #soldier
        self.n_barriers = [12, 12] #barrier
        self.budget = [150, 150] #points
        self.color = -1
        self.simulating = False
        self.HistoryTable = {}
#        self.legacy_state = []
#        self.parent_state = []
        
        ### board initialization ###
        self.checkerboard[0,4] = 2  # white flag
        self.checkerboard[-1,4] = 1 # black flag

        loc = [[0,2], [0,6], [1,3], [1,5], [2,4]] #soldier location
        for l in loc:
            self.checkerboard[l[0], l[1]] = 4  # white pieces
            self.checkerboard[8-l[0], l[1]] = 3 # black pieces
            
        # barriers
        loc = [[0,3], [0,5], [1,1], [1,4], [1,7], [2,1], [2,7], [3,2], [3,3], [3,4], [3,5], [3,6]]
        for l in loc:
            self.checkerboard[l[0], l[1]] = 6  # white barriers
            self.checkerboard[8-l[0], l[1]] = 5 # black barriers
        
        self.broad_now = self.checkerboard
        self.gmae_over_now = self.game_over
        self.n_piece_now = self.n_pieces
        self.n_barrier = self.n_barriers
        self.budget_now = self.budget
        
    def bid(self):
        ####################################################
        ##### You can modify the setting by yourself ! #####
        ####################################################
        # color -> BLACK:0  WHITE:1
        # price -> an non-negative <int> value
        color_choice = BLACK
        price = 5
        return color_choice, price
    
    def make_decision(self, who):
        #######################################################
        ##### This is the main part you need to implement #####
        #######################################################
        # return format : [begin_x, begin_y, end_x, end_y]

        if who == self.color: 
            self.simulating = True
            best = self.minimax(5, -inf, inf, who)
            self.simulating = False
            return [best[0], best[1], best[2], best[3]]
        else: 
            return None
#            print("My turn :")
#            move = [int(x) for x in input("Enter the move : ").split()]
#    
    def start(self):
        # bid for black or white
        # please set "bid" function by yourself
        # bid function will return two <int> values
        color_choice, price = self.bid()  #computer choice
        price = min(int(price),MAX_PRICE)
        print('My bid: ', color_choice, price)
        opponent_color_choice = int(input('Please input opponent_color_choice :'))
        opponent_price = int(input('Please input opponent_price :'))
        opponent_price = min(opponent_price,MAX_PRICE)
        assert (color_choice==0 or color_choice==1) and (opponent_color_choice==0 or opponent_color_choice==1)
        if color_choice != opponent_color_choice:
            self.color = color_choice
        elif price > opponent_price:
            self.color = color_choice
            self.budget[self.color] -= max(0, price)+1
        elif price < opponent_price:
            self.color = (1-opponent_color_choice)
            self.budget[1-self.color] -= max(0, price)+1
        else: 
            # Tie -> set player by TA
            print('Tie !')
            self.color = int(input('Please set my player number :'))
            if(self.color == color_choice):
                self.budget[self.color] -= max(0, opponent_price)+1
            else:
                self.budget[1-self.color] -= max(0, price)+1
            
        assert self.color==0 or self.color==1
        print('My color is: {}'.format('BLACK' if self.color == BLACK else 'WHITE'))     
        
        step = 0
        
        while not self.game_over:
            self.show_board()
            if step%2==BLACK: # black's turn
                if self.budget[BLACK] <= 1:
                    print('No budget to move! Only to pass!')
                    step += 1
                    continue
                if self.color==BLACK:
                    print('My color is: {}'.format('BLACK' if self.color == BLACK else 'WHITE'))
                    print("I am thinking...")
                    start = time.time()
                    move = self.make_decision(BLACK)
                    self.make_move(BLACK,move[0],move[1],move[2],move[3])
                    print('My move :',move)                    
                    end = time.time()
                    print("I spend %f s" % (end - start))                    
                else:
                    print('Opponent color is: {}'.format('WHITE' if self.color == BLACK else 'BLACK'))
                    print("Opponent turn :")
                    exception_occur = True
                    while exception_occur:
                        try:
                            move = [int(x) for x in input("Enter the move : ").split()]
                            self.make_move(BLACK,move[0],move[1],move[2],move[3])
                            exception_occur = False
                        except:
                            print("It is invalid move, please enter again")
                step += 1
            else: # white's turn
                if self.budget[WHITE] <= 1:
                    print('No budget to move! Only to pass!')
                    step += 1
                    continue
                if self.color==WHITE:
                    print('My color is: {}'.format('BLACK' if self.color == BLACK else 'WHITE'))
                    print("I am thinking...")
                    start = time.time()
                    move = self.make_decision(WHITE)
                    self.make_move(WHITE,move[0],move[1],move[2],move[3])
                    print('My move :',move)
                    end = time.time()
                    print("I spend %f s" % (end - start))
                else:
                    print('Opponent color is: {}'.format('WHITE' if self.color == BLACK else 'BLACK'))
                    print("Opponent turn :")
                    exception_occur = True
                    while exception_occur:
                        try:
                            move = [int(x) for x in input("Enter the move : ").split()]
                            self.make_move(WHITE,move[0],move[1],move[2],move[3])
                            exception_occur = False
                        except:
                            print("It is invalid move, please enter again")
                            exception_occur = True
                step += 1
        self.terminate()

    def get_pieces(self, color):
        ##############################################################
        ##### You can remove this function if you don't need it. #####
        ##############################################################
        b = np.zeros([9,9], dtype=int)
        if color == BLACK:
            x, y = np.where(self.checkerboard == 3)
        else:
            x, y = np.where(self.checkerboard == 4)
        for i, j in zip(x, y):
            b[i, j] = 1
        return b

    def get_barriers(self, color):
        ##############################################################
        ##### You can remove this function if you don't need it. #####
        ##############################################################
        b = np.zeros([9,9], dtype=int)
        if color == BLACK:
            x, y = np.where(self.checkerboard == 4) #不能穿過白棋，會被白棋擋住
        else:
            x, y = np.where(self.checkerboard == 3) #不能穿過黑棋，會被黑棋擋住
        for i, j in zip(x, y):
            b[i, j] = 1
        
        for k in [1, 2, 5, 6]: #只要是牆壁或是旗子就要被卡住，不管顏色
            x, y = np.where(self.checkerboard == k) 
            for i, j in zip(x, y):
                b[i, j] = 1
        return b

    def get_flags(self, color):
        ##############################################################
        ##### You can remove this function if you don't need it. #####
        ##############################################################
        b = np.zeros([9,9], dtype=int)
        if color == BLACK:
            x, y = np.where(self.checkerboard == 1)
        else:
            x, y = np.where(self.checkerboard == 2)
        for i, j in zip(x, y):
            b[i, j] = 1
        return b
    
    def make_move(self, who, begin_x, begin_y, end_x, end_y):
        
        # if who == 0 -> balck
        # if who == 1 -> white
        
#        print("move: " +str(who), str(begin_x), str(begin_y), str(end_x), str(end_y))
        piece = who+3
#        self.show_board()
                
        assert self.checkerboard[begin_x, begin_y] == piece
        assert begin_x >= 0 and begin_x < 9 and end_x >= 0 and end_x < 9 \
          and begin_y >= 0 and begin_y < 9 and end_y >= 0 and end_y < 9
        assert begin_x == end_x or begin_y == end_y
        assert begin_x != end_x or begin_y != end_y
        check_sum = ((begin_x==end_x)*sum(self.checkerboard[begin_x,min(begin_y,end_y)+1:max(begin_y,end_y)]) \
                  + (begin_y==end_y)*sum(self.checkerboard[min(begin_x,end_x)+1:max(begin_x,end_x),begin_y]))
        assert check_sum == 0
        
        distance = abs(begin_x-end_x) + abs(begin_y-end_y);
        
        if who == BLACK:
            self.budget[BLACK] -= (1 + distance)
#            if self.budget[BLACK] < 0:
#                self.game_over = True
            assert self.budget[BLACK] >= 0
            if self.checkerboard[end_x, end_y] == 0:
                pass
            elif self.checkerboard[end_x, end_y] == 2:
                self.game_over = True
            elif self.checkerboard[end_x, end_y] == 6:
                if not self.simulating:
                    print('Break white barrier!')
                self.n_barriers[WHITE] -= 1
                self.budget[BLACK] -= OPPONENT_BARRIER_COST
            elif self.checkerboard[end_x, end_y] == 4:
                if not self.simulating:
                    print('Take white piece!')
                self.n_pieces[WHITE] -= 1
                if self.n_pieces[WHITE] == 0:
                    self.game_over = True
            elif self.checkerboard[end_x, end_y] == 5:
                if not self.simulating:
                    print('Break black barrier!')
                self.n_barriers[BLACK] -= 1
                self.budget[BLACK] -= SELF_BARRIER_COST
            else:
                raise Exception('Do not move your piece to an occupied place!')
            assert self.budget[BLACK] >= 0
#            if self.budget[BLACK] < 0:
#                self.game_over = True
        else:
            self.budget[WHITE] -= (1 + distance)
#            if self.budget[WHITE] < 0:
#                self.game_over = True
            assert self.budget[WHITE] >= 0
            if self.checkerboard[end_x, end_y] == 0:
                pass
            elif self.checkerboard[end_x, end_y] == 1:
                self.game_over = True
            elif self.checkerboard[end_x, end_y] == 5:
                if not self.simulating:
                    print('Break black barrier!')
                self.n_barriers[BLACK] -= 1
                self.budget[WHITE] -= OPPONENT_BARRIER_COST
            elif self.checkerboard[end_x, end_y] == 3:
                if not self.simulating:
                    print('Take black piece!')
                self.n_pieces[BLACK] -= 1
                if self.n_pieces[BLACK] == 0:
                    self.game_over = True
            elif self.checkerboard[end_x, end_y] == 6:
                if not self.simulating:
                    print('Break white barrier!')
                self.n_barriers[WHITE] -= 1
                self.budget[WHITE] -= SELF_BARRIER_COST
            else:
                raise Exception('Do not move your piece to an occupied place!')
            assert self.budget[WHITE] >= 0
#            if self.budget[WHITE] < 0:
#                self.game_over = True
        # Move
        self.checkerboard[begin_x, begin_y] = 0
        self.checkerboard[end_x, end_y] = piece
        if not self.simulating:
            print('Player {} moved piece from ({},{}) to ({},{})' \
              .format('BLACK' if who==BLACK else 'WHITE',begin_x,begin_y,end_x,end_y))
            print("budget: " + str(self.budget))
        if self.budget[BLACK] <= 1 and self.budget[WHITE] <= 1:
            self.game_over = True
    
    def terminate(self):
        # number == 0
        if self.checkerboard[0, 4] == 3:
            print('BLACK wins!')
        elif self.checkerboard[-1, 4] == 4:
            print('WHITE wins!')
        elif self.n_pieces[BLACK] > self.n_pieces[WHITE]:
            print('BLACK wins!')
        elif self.n_pieces[BLACK] < self.n_pieces[WHITE]:
            print('WHITE wins!')
        elif self.n_barriers[BLACK] > self.n_barriers[WHITE]:
            print('BLACK wins!')
        elif self.n_barriers[BLACK] < self.n_barriers[WHITE]:
            print('WHITE wins!')
        else:
            print('Draw!')
            
    def minimax(self, depth, alpha, beta, player):
        """
        AI function that choice the best move
        :param state: current state of the board
        :param depth: node index in the tree (0 <= depth <= 9),
        but never nine in this case (see iaturn() function)
        :param player: an human or a computer
        :return: a list with [the best row, best col, best score]
        """
#        print("depth: " + str(depth) + " alpha: " + str(alpha) + " beta: " + str(beta))
        
        if player == self.color: #Max
            best = [-1, -1, -1, -1, -inf]
        else:
            best = [-1, -1, -1, -1, +inf]
    
        if self.game_over or depth == 0:
            score = self.evaluate(self.checkerboard, self.color)
            return [-1, -1, -1, -1, score]
        
        ValidMove = self.valid_move(player)
        
        rating = []
        for cell in ValidMove:
            move = str(cell[0]) + "," + str(cell[1]) + "," + str(cell[2]) + "," + str(cell[3])
            try:
                rating.append(self.HistoryTable[ move ]) 
            except KeyError:
                self.HistoryTable[ move ] = 0
                rating.append(self.HistoryTable[ move ])
        ValidMove = [x for _, x in sorted(zip(rating, ValidMove), reverse = True )]; 
        
        for cell in ValidMove:
            
            #記得現在的狀態
            broad_now = copy.deepcopy(self.checkerboard)
            gmae_over_now = self.game_over
            n_piece_now = copy.deepcopy(self.n_pieces)
            n_barrier = copy.deepcopy(self.n_barriers)
            budget_now = copy.deepcopy(self.budget)

            self.make_move(player, cell[0], cell[1], cell[2], cell[3]) #走valid move

            score = self.minimax(depth - 1, alpha, beta, 1 - player)
            
            #恢復之前的狀態
            self.checkerboard = copy.deepcopy(broad_now)
            self.game_over = gmae_over_now
            self.n_pieces = copy.deepcopy(n_piece_now)
            self.n_barriers = copy.deepcopy(n_barrier)
            self.budget = copy.deepcopy(budget_now)
            
            score[0], score[1], score[2], score[3] = cell[0], cell[1], cell[2], cell[3]
            
            if player == self.color: #Max
                if score[4] > best[4]:
                    best = score  # max value
                alpha = max(alpha, score[4])
                if beta <= alpha:
                    break
            else:
                if score[4] < best[4]:
                    best = score  # min value
                beta = min(beta, score[4])
                if beta <= alpha:
                    break
                
        bestMove = str(best[0]) + "," + str(best[1]) + "," + str(best[2]) + "," + str(best[3])
        if bestMove not in self.HistoryTable:
            self.HistoryTable[bestMove] = 0 + depth
        else:
            self.HistoryTable[bestMove] = self.HistoryTable[bestMove] + depth
        
        return best
        
    def evaluate(self, broad, player):
        if self.budget[player] > 0:
            flag_danger = 0
            flag_budget = 0
            
            if player == BLACK:
                if broad[0, 4] == 3:
                    flag_budget = 10000
                elif broad[8, 4] == 4:
                    flag_budget = -10000
                                   
                for i in range(4):
                    if broad[0, 3 - i] == 3:
                        if i == 0:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                    if broad[8, 3 - i] == 4:
                        if i == 0:
                            flag_danger += -50                 
                        else:
                            flag_danger += -10 
                            
                for i in range(4):
                    if broad[0, 5 + i] == 3:
                        if i == 0:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                    if broad[8, 5 + i] == 4:
                        if i == 0:
                            flag_danger += -50                 
                        else:
                            flag_danger += -10
                        
                for i in range(9):
                    if broad[i, 4] == 3:
                        if i == 1:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                    if broad[i, 4] == 4:
                        if i == 7:
                            flag_danger += -50
                        else:
                            flag_danger += -10
                        
                    if broad[i, 3] == 3:
                        flag_danger += 38
                    if broad[i, 3] == 4:
                        flag_danger += -38
                        
                    if broad[i, 5] == 3:
                        flag_danger += 38
                    if broad[i, 5] == 4:
                        flag_danger += -38
                                
            elif player == WHITE:
                if broad[8, 4] == 4:
                    flag_budget = 10000
                elif broad[0, 4] == 3:
                    flag_budget = -10000

                for i in range(4):
                    if broad[0, 3 - i] == 3:
                        if i == 0:
                            flag_danger += -50
                        else:
                            flag_danger += -10
                    if broad[8, 3 - i] == 4:
                        if i == 0:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                        
                for i in range(4):
                    if broad[0, 5 + i] == 3:
                        if i == 0:
                            flag_danger += -50
                        else:
                            flag_danger += -10
                    if broad[8, 5 + i] == 4:
                        if i == 0:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                
                for i in range(9):
                    if broad[i, 4] == 3:
                        if i == 1:
                            flag_danger += -50
                        else:
                            flag_danger += -10
                    if broad[i, 4] == 4:
                        if i == 7:
                            flag_danger += 50
                        else:
                            flag_danger += 10
                        
                    if broad[i, 3] == 3:
                        flag_danger += -38
                    if broad[i, 3] == 4:
                        flag_danger += 38
                        
                    if broad[i, 5] == 3:
                        flag_danger += -38
                    if broad[i, 5] == 4:
                        flag_danger += 38
                    
#                    if i > 4:
#                        for j in range(9):
#                            if self.checkerboard[i, j] == 4:
#                                soldier_attack += 1
#                    if i <= 4:
#                        for j in range(9):
#                            if self.checkerboard[i, j] == 3:
#                                soldier_attack -= 1
                                
#            barriers_black, barriers_white, pieces_black, pieces_white = self.object_number()
            if player == BLACK:
                barriers_num = self.n_barriers[BLACK]
                barriers_oppo = self.n_barriers[WHITE]
                pieces_num = self.n_pieces[BLACK]
                pieces_oppo = self.n_pieces[WHITE]
            else:
                barriers_num = self.n_barriers[WHITE]
                barriers_oppo = self.n_barriers[BLACK]
                pieces_num = self.n_pieces[WHITE]
                pieces_oppo = self.n_pieces[BLACK]
            return flag_budget + 1 * flag_danger + 2 * barriers_num + 40 * pieces_num -  3 * barriers_oppo - +  35 * pieces_oppo # computer budget
        else:
            return -10000

    def valid_move(self, player): #找到士兵然後看直線能不能走 #最遠的五個位子
        cells = []
        pieces_position = []
        
        if player == BLACK:
            x, y = np.where(self.checkerboard == 3)
        else:
            x, y = np.where(self.checkerboard == 4)
        for i, j in zip(x, y):
            pieces_position.append((i, j))
            
#        pieces_position = [(x, y) for x, y in zip(*np.where(self.get_pieces(player) == 1))]
        if player == BLACK:
            cells = self.black_move(pieces_position, player)
        else:
            cells = self.white_move(pieces_position, player)
        return cells
    
    def black_move(self, pieces_position, player):
        cells = []
        for x, y in pieces_position:
            walk = []
            for i in range(x - 1, -1, -1):
                if self.checkerboard[i, y] == 1 + player or  self.checkerboard[i, y] == 3 + player:
                    break
                if self.checkerboard[i, y] == (4 if player == 0 else 3 ) or self.checkerboard[i, y] == 5 or self.checkerboard[i, y] == 6 \
                    or self.checkerboard[i, y] == (2 if player == 0 else 1 ):
                        walk = [x, y, i, y]
                        break
                if i == x - 1:
                    cells.append([x, y, i, y])
                else:
                    walk = [x, y, i, y]
            if walk != []:
                cells.append(walk)
                walk = []
           
            
            for i in range(x + 1, 9, 1):   
                if self.checkerboard[i, y] == 1 + player or  self.checkerboard[i, y] == 3 + player:
                    break
                if self.checkerboard[i, y] == (4 if player == 0 else 3 ) or self.checkerboard[i, y] == 5 or self.checkerboard[i, y] == 6\
                    or self.checkerboard[i, y] == (2 if player == 0 else 1 ):
                        walk = [x, y, i, y]
                        break
                if i == x + 1:
                    cells.append([x, y, i, y])
                else:
                    walk = [x, y, i, y]
            if walk != []:
                cells.append(walk)
                walk = []
           
            for j in range(y - 1, -1, -1):    
                if self.checkerboard[x, j] == 1 + player or  self.checkerboard[x, j] == 3 + player:
                    break
                if self.checkerboard[x, j] == (4 if player == 0 else 3 ) or self.checkerboard[x, j] == 5 or self.checkerboard[x, j] == 6\
                    or self.checkerboard[x, j] == (2 if player == 0 else 1 ):
                        walk = [x, y, x, j]
                        break
                if j == y - 1:
                    cells.append([x, y, x, j])
                else:
                    walk = [x, y, x, j]
            if walk != []:
                cells.append(walk)
                walk = []  

            for j in range(y + 1, 9, 1):    
                if self.checkerboard[x, j] == 1 + player or  self.checkerboard[x, j] == 3 + player:
                    break
                if self.checkerboard[x, j] == (4 if player == 0 else 3 ) or self.checkerboard[x, j] == 5 or self.checkerboard[x, j] == 6\
                    or self.checkerboard[x, j] == (2 if player == 0 else 1 ):
                        walk = [x, y, x, j]
                        break
                if j == y + 1:
                    cells.append([x, y, x, j])
                else:
                    walk = [x, y, x, j]
            if walk != []:
                cells.append(walk)
                walk = []
        return cells
        
    def white_move(self, pieces_position, player):
        cells = []
        for x, y in pieces_position:
            walk = []
            for i in range(x + 1, 9, 1):   
                if self.checkerboard[i, y] == 1 + player or  self.checkerboard[i, y] == 3 + player:
                    break
                if self.checkerboard[i, y] == (4 if player == 0 else 3 ) or self.checkerboard[i, y] == 5 or self.checkerboard[i, y] == 6\
                    or self.checkerboard[i, y] == (2 if player == 0 else 1 ):
                        walk = [x, y, i, y]
                        break
                if i == x + 1:
                    cells.append([x, y, i, y])
                else:
                    walk = [x, y, i, y]
            if walk != []:
                cells.append(walk)
                walk = []
                
            for i in range(x - 1, -1, -1):
                if self.checkerboard[i, y] == 1 + player or  self.checkerboard[i, y] == 3 + player:
                    break
                if self.checkerboard[i, y] == (4 if player == 0 else 3 ) or self.checkerboard[i, y] == 5 or self.checkerboard[i, y] == 6 \
                    or self.checkerboard[i, y] == (2 if player == 0 else 1 ):
                        walk = [x, y, i, y]
                        break
                if i == x - 1:
                    cells.append([x, y, i, y])
                else:
                    walk = [x, y, i, y]
            if walk != []:
                cells.append(walk)
                walk = []
           
            for j in range(y - 1, -1, -1):    
                if self.checkerboard[x, j] == 1 + player or  self.checkerboard[x, j] == 3 + player:
                    break
                if self.checkerboard[x, j] == (4 if player == 0 else 3 ) or self.checkerboard[x, j] == 5 or self.checkerboard[x, j] == 6\
                    or self.checkerboard[x, j] == (2 if player == 0 else 1 ):
                        walk = [x, y, x, j]
                        break
                if j == y - 1:
                    cells.append([x, y, x, j])
                else:
                    walk = [x, y, x, j]
            if walk != []:
                cells.append(walk)
                walk = []  

            for j in range(y + 1, 9, 1):    
                if self.checkerboard[x, j] == 1 + player or  self.checkerboard[x, j] == 3 + player:
                    break
                if self.checkerboard[x, j] == (4 if player == 0 else 3 ) or self.checkerboard[x, j] == 5 or self.checkerboard[x, j] == 6\
                    or self.checkerboard[x, j] == (2 if player == 0 else 1 ):
                        walk = [x, y, x, j]
                        break
                if j == y + 1:
                    cells.append([x, y, x, j])
                else:
                    walk = [x, y, x, j]
            if walk != []:
                cells.append(walk)
                walk = []
        return cells
        
    def show_board(self):
        print('――――――――――――――――――')
        print('Budget: ')
        print('        Black: ', self.budget[BLACK])
        print('        White: ', self.budget[WHITE])
        print('n_pieces: ')
        print('        Black: ', self.n_pieces[BLACK])
        print('        White: ', self.n_pieces[WHITE])
        print('n_barriers: ')
        print('        Black: ', self.n_barriers[BLACK])
        print('        White: ', self.n_barriers[WHITE])
        print()
        print(' y 0  1  2  3  4  5  6  7  8 ')
        print('x  ― ― ― ― ― ― ― ― ― ')
        i = 0
        for line in self.checkerboard:
            print(i,'|{}|{}|{}|{}|{}|{}|{}|{}|{}|'.format(S[line[0]],S[line[1]],S[line[2]], \
                        S[line[3]],S[line[4]],S[line[5]],S[line[6]],S[line[7]],S[line[8]]))
            print('   ― ― ― ― ― ― ― ― ― ')
            i += 1
        print('――――――――――――――――――')


if __name__ == '__main__':
    game = Meichu()
    game.start()
    input("Please press the Enter key to exit ...")

