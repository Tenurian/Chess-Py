#!/usr/bin/python3

from abc import ABC,abstractmethod
from enum import Enum
from copy import deepcopy

class Color(Enum):
    LIGHT = "Light"
    DARK  = "Dark"
    def __str__(self):
        return str(self.value)

class PieceType(Enum):
    KING   = "King"
    QUEEN  = "Queen"
    BISHOP = "Bishop"
    KNIGHT = "Knight"
    ROOK   = "Rook"
    PAWN   = "Pawn"
    def __str__(self):
        return str(self.value)

class Location:
    x = -1
    y = -1
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "(x: {}, y: {})".format(self.x,self.y)

class Board:
    __board = None
    __pieces = {
        Color.LIGHT: [],
        Color.DARK: []
    }

    def __init__(self,initial_state = None):
        if initial_state:
            self.__board = initial_state
            # iterate through the board and extract the relevant pieces
        else:
            # initialize the board as an empty 8x8 grid
            self.__board = []
            for row in range(8):
                self.__board.append([])
                for col in range(8):
                    self.__board[row].append(None)
                    
            # set up the normal starting positions of the board
            # pawns
            for x in range(8):
                self.addPieceToBoard(Pawn(Color.DARK,  Location(x, 1)))
                self.addPieceToBoard(Pawn(Color.LIGHT, Location(x, 6)))
                
            # Using lambdas here because some online interpreters don't support python3.10's
            # 'match-case' syntax, and this essentially does the same job without causing issues
            __genRooks   = lambda D1L,D2L,L1L,L2L: [ Rook(Color.DARK, D1L),  Rook(Color.DARK, D2L),  Rook(Color.LIGHT, L1L),  Rook(Color.LIGHT, L2L) ]
            __genBishops = lambda D1L,D2L,L1L,L2L: [Bishop(Color.DARK, D1L),Bishop(Color.DARK, D2L),Bishop(Color.LIGHT, L1L),Bishop(Color.LIGHT, L2L)]
            __genKnights = lambda D1L,D2L,L1L,L2L: [Knight(Color.DARK, D1L),Knight(Color.DARK, D2L),Knight(Color.LIGHT, L1L),Knight(Color.LIGHT, L2L)]
            
            # Dynamically place the rooks, knights, and bishops
            for i,p in enumerate([PieceType.ROOK,PieceType.KNIGHT,PieceType.BISHOP]):
                D1 = D2 = L1 = L2 = None
                D1L = Location(i,0)
                D2L = Location(7-i,0)
                L1L = Location(i, 7)
                L2L = Location(7-i, 7)
                genPieces = {
                    PieceType.ROOK: __genRooks(D1L,D2L,L1L,L2L),
                    PieceType.BISHOP: __genBishops(D1L,D2L,L1L,L2L),
                    PieceType.KNIGHT: __genKnights(D1L,D2L,L1L,L2L)
                }
                for g in genPieces[p]:
                    self.addPieceToBoard(g)

            # Statically place the regency
            self.addPieceToBoard(King(Color.DARK, Location(3,0)))
            self.addPieceToBoard(Queen(Color.DARK, Location(4,0)))
            
            self.addPieceToBoard(King(Color.LIGHT, Location(4,7)))
            self.addPieceToBoard(Queen(Color.LIGHT, Location(3,7)))
            
    def __str__(self):
        return ''.join(["---------------------------------\n| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(*(p.SYMBOL if p else ' ' for p in row)) for row in self.__board]) + "---------------------------------\n"

    def getPieces(self,color = False):
        if not color:
            return self.__pieces
        else:
            return self.__pieces[color]
    
    def getPieceAtLocation(self,location):
        return self.__board[location.y][location.x]

    def removePieceAtLocation(self,location):
        if self.__board[location.y][location.x]:
            for index,piece in enumerate(self.__pieces[self.__board[location.y][location.x].COLOR]):
                if str(piece.getLocation()) == str(location):
                    return self.__pieces[piece.COLOR].pop(index)
        return None

    def addPieceToBoard(self,piece):
        self.__board[piece.getLocation().y][piece.getLocation().x] = piece
        self.__pieces[piece.COLOR].append(piece)

    def movePieceToLocation(self,piece,destination):
        current_loc = piece.getLocation()
        self.__board[current_loc.y][current_loc.x] = None
        if self.getPieceAtLocation(destination) != None:
            self.removePieceAtLocation(destination)
        self.__board[destination.y][destination.x] = piece
        return piece

class Piece(ABC): # color, piecetype, location
    __SYMBOLS = {
        Color.LIGHT: {
            PieceType.KING: "♚",
            PieceType.QUEEN: "♛",
            PieceType.ROOK: "♜",
            PieceType.BISHOP: "♝",
            PieceType.KNIGHT: "♞",
            PieceType.PAWN: "♟︎"
        },
        Color.DARK: {
            PieceType.KING: "♔",
            PieceType.QUEEN: "♕",
            PieceType.ROOK: "♖",
            PieceType.BISHOP: "♗",
            PieceType.KNIGHT: "♘",
            PieceType.PAWN: "♙"
        }
    }

    __location = None # will change over time, but don't want anything besides itself to alter the location
    __PIECETYPE = None
    COLOR = None
    SYMBOL = None
    
    def __init__(self,color,piecetype,location):
        self.__PIECETYPE = piecetype
        self.COLOR = color
        self.__location = location
        self.SYMBOL = self.__SYMBOLS[color][piecetype]
    
    def __str__(self):
        return "<{} {} ( {} ) @ {}>".format(self.COLOR,self.__PIECETYPE, self.SYMBOL, self.__location)
    
    def getPieceType(self):
        return self.__PIECETYPE
    
    def getLocation(self):
        return self.__location
    
    @abstractmethod
    def getValidLocations(self,board):
        return None
    
    def tryMove(self,destination,board):
        moved_successfully = False
        if destination in self.getValidLocations(board):
            if board.getPieceAtLocation(destination) != None:
                board.removePieceAtLocation(destination)
            board.movePieceToLocation(self.__location,destination)
            moved_successfully = True
        return moved_successfully

class Pawn(Piece): # color, location
    __firstmove = True
    __is_ep_valid = False
    def __init__(self,color,location):
        super().__init__(color, PieceType.PAWN, location)

    def getValidLocations(self,board,forKingCheck = False):
        # if first move
        valid_locs = []
        curr_loc = self.getLocation()
        direction = ( -1 if self.COLOR == Color.LIGHT else 1 )
        if self.__firstmove:
            possible_loc = Location(curr_loc.x, curr_loc.y + (2 * direction))
            if board.getPieceAtLocation(possible_loc) == None:
                valid_locs.append( possible_loc )
        
        # ADD IN THE EN PASSANT LOGIC HERE
        
        if curr_loc.y != (0 if self.COLOR == Color.LIGHT else 7):
            valid_locs.append(Location(curr_loc.x,curr_loc.y + direction))
            if curr_loc.x > 0: # Attacking to the east
                attack_east_loc = Location(curr_loc.x - 1, curr_loc.y + direction)
                if board.getPieceAtLocation(attack_east_loc) != None:
                    if board.getPieceAtLocation(attack_east_loc).COLOR != self.COLOR:
                        valid_locations.append(attack_east_loc)
            
            if curr_loc.x < 7: # Attacking to the west
                attack_west_loc = Location(curr_loc.x + 1, curr_loc.y + direction)
                if board.getPieceAtLocation(attack_west_loc) != None:
                    if board.getPieceAtLocation(attack_west_loc).COLOR != self.COLOR:
                        valid_locations.append(attack_west_loc)
        else:
            raise "This pawn needs to be upgraded"
        return valid_locs

class Rook(Piece): # color, location, piecetype override for queen
    def __init__(self, color, location, piecetype = PieceType.ROOK):
        super().__init__(color, piecetype, location)

    def getValidLocations(self,board,forKingCheck = False):
        curr_loc = self.getLocation()
        N = E = S = W = True
        valid_locs = []
        for i in range(1,8):
            if N and (curr_loc.y - i >= 0): # N
                NL = Location(curr_loc.x, curr_loc.y - i)
                N_cell = board.getPieceAtLocation(NL) #unintentionally funny
                if N_cell != None:
                    if not(forKingCheck and N_cell.getPieceType() == PieceType.KING and N_cell.COLOR != self.COLOR):
                        N = False
                    if N_cell.COLOR != self.COLOR or forKingCheck:
                        valid_locs.append(NL)
                else:
                    valid_locs.append(NL)
                        
            if E and (curr_loc.x + i <= 7): # E
                EL = Location(curr_loc.x + i, curr_loc.y)
                E_cell = board.getPieceAtLocation(EL)
                if E_cell != None:
                    if not(forKingCheck and E_cell.getPieceType() == PieceType.KING and E_cell.COLOR != self.COLOR):
                        E = False
                    if E_cell.COLOR != self.COLOR or forKingCheck:
                        valid_locs.append(EL)
                else:
                    valid_locs.append(EL)
            
            if S and (curr_loc.y + i <= 7): # S
                SL = Location(curr_loc.x, curr_loc.y + i)
                S_cell = board.getPieceAtLocation(SL)
                if S_cell != None:
                    if not(forKingCheck and S_cell.getPieceType() == PieceType.KING and S_cell.COLOR != self.COLOR):
                        S = False
                    if S_cell.COLOR != self.COLOR or forKingCheck:
                        valid_locs.append(SL)
                else:
                    valid_locs.append(SL)
            
            if W and (curr_loc.x - i >= 0): # W
                WL = Location(curr_loc.x - i, curr_loc.y)
                W_cell = board.getPieceAtLocation(WL)
                if W_cell != None:
                    if not(forKingCheck and W_cell.getPieceType() == PieceType.KING and W_cell.COLOR != self.COLOR):
                        W = False
                    if W_cell.COLOR != self.COLOR or forKingCheck:
                        valid_locs.append(WL)
                else:
                    valid_locs.append(WL)
        
        return valid_locs

class Knight(Piece): # color, location
    def __init__(self,color,location):
        super().__init__(color, PieceType.KNIGHT, location)

    def getValidLocations(self,board,forKingCheck = False):
        possible_locs = [
            Location(self.getLocation().x-1, self.getLocation().y-2), # North-North-West
            Location(self.getLocation().x+1, self.getLocation().y-2), # North-North-East
            Location(self.getLocation().x+2, self.getLocation().y-1), # East-North-East
            Location(self.getLocation().x+2, self.getLocation().y+1), # East-South-East
            Location(self.getLocation().x+1, self.getLocation().y+2), # South-South-East
            Location(self.getLocation().x-1, self.getLocation().y+2), # South-South-West
            Location(self.getLocation().x-2, self.getLocation().y+1), # West-South-West
            Location(self.getLocation().x-2, self.getLocation().y-1)  # West-North-West
        ]
        probable_locs = [ loc for loc in possible_locs if (loc.x >= 0 and loc.x <= 7 and loc.y >= 0 and loc.y <= 7) ]
        valid_locs = [ loc for loc in probable_locs if board.getPieceAtLocation(loc) == None or board.getPieceAtLocation(loc).COLOR != self.COLOR or forKingCheck ]
        return valid_locs

class Bishop(Piece): # color, location, piecetype override for queen
    def __init__(self, color, location, piecetype = PieceType.BISHOP):
        # input validation for queen
        if type(location) == PieceType:
            temp = location
            location = piecetype
            piecetype = temp
        super().__init__(color, piecetype, location)

    def getValidLocations(self,board,forKingCheck = False):
        curr_loc = self.getLocation()
        valid_locs = []
        NW = NE = SE = SW = True
        for i in range(1,8):
            if NW and curr_loc.x-i >= 0 and curr_loc.y-i >= 0:
                NWL = Location(curr_loc.x-i,curr_loc.y-i)
                NW_cell = board.getPieceAtLocation(NWL)
                if NW_cell != None:
                    if not(forKingCheck and NW_cell.getPieceType() == PieceType.KING and NW_cell.COLOR != self.COLOR):
                        N = False
                    if self.COLOR != board.getPieceAtLocation(NWL).COLOR or forKingCheck:
                        valid_locs.append(NWL)
                else:
                    valid_locs.append(NWL)
            if NE and curr_loc.x+i <= 7 and curr_loc.y-i >= 0:
                NEL = Location(curr_loc.x+i,curr_loc.y-i)
                NE_cell = board.getPieceAtLocation(NEL)
                if NE_cell != None:
                    if not(forKingCheck and NE_cell.getPieceType() == PieceType.KING and NE_cell.COLOR != self.COLOR):
                        NE = False
                    if self.COLOR != board.getPieceAtLocation(NEL).COLOR or forKingCheck:
                        valid_locs.append(NEL)
                else:
                    valid_locs.append(NEL)
            if SE and curr_loc.x+i <= 7 and curr_loc.y+i <= 7:
                SEL = Location(curr_loc.x+i,curr_loc.y+i)
                SE_cell = board.getPieceAtLocation(SEL)
                if SE_cell != None:
                    if not(forKingCheck and SE_cell.getPieceType() == PieceType.KING and SE_cell.COLOR != self.COLOR):
                        SE = False
                    if self.COLOR != board.getPieceAtLocation(SEL).COLOR or forKingCheck:
                        valid_locs.append(SEL)
                else:
                    valid_locs.append(SEL)
            if SW and curr_loc.x-i >= 0 and curr_loc.y+i <= 7:
                SWL = Location(curr_loc.x-i,curr_loc.y+i)
                SW_cell = board.getPieceAtLocation(SWL)
                if SW_cell != None:
                    if not(forKingCheck and SW_cell.getPieceType() == PieceType.KING and SW_cell.COLOR != self.COLOR):
                        SW = False
                    if self.COLOR != board.getPieceAtLocation(SWL).COLOR or forKingCheck:
                        valid_locs.append(SWL)
                else:
                    valid_locs.append(SWL)
            
        return valid_locs

class Queen(Rook,Bishop):
    def __init__(self,color,location):
        super().__init__(color = color, location = location, piecetype = PieceType.QUEEN)

    def getValidLocations(self,board,forKingCheck = False):
        RookMoves = Rook.getValidLocations(self,board,forKingCheck)
        BishopMoves = Bishop.getValidLocations(self,board,forKingCheck)
        return RookMoves + BishopMoves

class King(Piece):
    def __init__(self, color, location):
        super().__init__(color, PieceType.KING, location)

    def isSurrounded(self,board):
        return len(self.getValidLocations(board)) == 0
        
    def isInCheck(self,board):
        curr_loc = self.getLocation()
        for opponent_piece in board.getPieces(Color.DARK if self.COLOR == Color.LIGHT else Color.LIGHT):
            if str(curr_loc) in [str(v_loc) for v_loc in opponent_piece.getValidLocations(board,True)]:
                return True
        return False
    
    def hasIntercepts(self,board):
        for kings_piece in board.getPieces(self.COLOR):
            if kings_piece != self:
                for v_loc in kings_piece.getValidLocations(board):
                    t_board = deepcopy(board)
                    t_board.movePieceToLocation(kings_piece,v_loc)
                    if not self.isInCheck(t_board):
                        return True
        return False
    
    def isCheckMate(self,board):
        return self.isInCheck(board) and self.isSurrounded(board) and not self.hasIntercepts(board)

    def getValidLocations(self,board):
        all_locs = [
            Location(self.getLocation().x-1, self.getLocation().y-1),   # nw
            Location(self.getLocation().x-1, self.getLocation().y+0),   # n
            Location(self.getLocation().x-1, self.getLocation().y+1),   # ne
            Location(self.getLocation().x+0, self.getLocation().y+1),   # e
            Location(self.getLocation().x+1, self.getLocation().y+1),   # se
            Location(self.getLocation().x+1, self.getLocation().y+0),   # s
            Location(self.getLocation().x+1, self.getLocation().y-1),   # sw
            Location(self.getLocation().x+0, self.getLocation().y-1)    # w
        ]
        
        # Boundary Detection
        possible_locs = []
        for i,loc in enumerate(all_locs):
            if not (loc.x < 0 or loc.x > 7 or loc.y < 0 or loc.y > 7):
                possible_locs.append(loc)
        
        # Technically these aren't really the *valid* locations, only the ones within the
        # boundaries of the board
        probable_locs = [loc for loc in possible_locs if board.getPieceAtLocation(loc) == None or board.getPieceAtLocation(loc).COLOR != self.COLOR ]
        
        occupied_locations = []
        valid_locations = []
        for opp_piece in board.getPieces(Color.DARK if self.COLOR == Color.LIGHT else Color.LIGHT):
            occupied_locations = occupied_locations + [str(l) for l in opp_piece.getValidLocations(board,forKingCheck = True)]
        
        for p in probable_locs:
            if str(p) not in occupied_locations:
                valid_locations.append(p)
        
        print([str(l) for l in valid_locations])
        return valid_locations

if  __name__ == "__main__":
    # board = Board()
    # board = Board( [ [ None for col in range(8) ] for row in range(8) ] )
    # K1 = King(Color.LIGHT, Location(3,3))
    # board.addPieceToBoard(K1)
    # r1 = Rook(Color.DARK, Location(2,0))
    # board.addPieceToBoard(r1)
    # r2 = Rook(Color.DARK, Location(4,0))
    # board.addPieceToBoard(r2)
    # r3 = Rook(Color.DARK, Location(0,2))
    # board.addPieceToBoard(r3)
    # r4 = Rook(Color.DARK, Location(0,4))
    # board.addPieceToBoard(r4)
    # q1 = Queen(Color.DARK, Location(0,0))
    # board.addPieceToBoard(q1)
    # B1 = Rook(Color.LIGHT, Location(0,1))
    # board.addPieceToBoard(B1)
    # print('checkmate:',K1.isCheckMate(board))
    # print(board)

    print("For King valid location checks, when we go thru the list of all opponent's pieces we need to isolate each piece (leaving King's pieces) to get *literally every possible valid move*")

    board = Board( [ [ None for col in range(8) ] for row in range(8) ] )
    K1 = King(Color.DARK, Location(4,0))
    r1 = Rook(Color.LIGHT, Location(0,0))
    q1 = Queen(Color.LIGHT, Location(4,1))
    r2 = Rook(Color.LIGHT, Location(4,7))
    # R1 = Rook(Color.DARK, Location(3,7))
    board.addPieceToBoard(K1)
    board.addPieceToBoard(r1)
    board.addPieceToBoard(q1)
    board.addPieceToBoard(r2)
    # board.addPieceToBoard(R1)
    print('isSurrounded:\t',K1.isSurrounded(board))
    print('isInCheck:\t\t',K1.isInCheck(board))
    print('hasIntercepts:\t',K1.hasIntercepts(board))
    print('checkmate:',K1.isCheckMate(board))
    print(board)
    
