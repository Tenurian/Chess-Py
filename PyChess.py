#!/usr/bin/python3

from abc import ABC,abstractmethod
from enum import Enum

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
                LightPawn = Pawn(Color.LIGHT, Location(x, 6))
                DarkPawn  = Pawn(Color.DARK,  Location(x, 1))
                self.__board[1][x] = DarkPawn
                self.__board[6][x] = LightPawn
                self.__pieces[Color.DARK].append(DarkPawn)
                self.__pieces[Color.LIGHT].append(LightPawn)
                
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
                D1,D2,L1,L2 = genPieces[p]
                    
                self.__board[D1L.y][D1L.x] = D1
                self.__board[D2L.y][D2L.x] = D2
                self.__board[L1L.y][L1L.x] = L1
                self.__board[L2L.y][L2L.x] = L2
                self.__pieces[Color.DARK].append(D1)
                self.__pieces[Color.DARK].append(D2)
                self.__pieces[Color.LIGHT].append(L1)
                self.__pieces[Color.LIGHT].append(L2)

            # Statically place the regency
            DK = King(Color.DARK, Location(3,0))
            self.__board[DK.getLocation().y][DK.getLocation().x] = DK
            self.__pieces[Color.DARK].append(DK)

            DQ = Queen(Color.DARK, Location(4,0))
            self.__board[DQ.getLocation().y][DQ.getLocation().x] = DQ
            self.__pieces[Color.DARK].append(DQ)
            
            
            LK = King(Color.LIGHT, Location(4,7))
            self.__board[LK.getLocation().y][LK.getLocation().x] = LK
            self.__pieces[Color.LIGHT].append(LK)
            
            LQ = Queen(Color.LIGHT, Location(3,7))
            self.__board[LQ.getLocation().y][LQ.getLocation().x] = LQ
            self.__pieces[Color.LIGHT].append(LQ)
            
    def __str__(self):
        return ''.join(["---------------------------------\n| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(*(p.SYMBOL if p else ' ' for p in row)) for row in self.__board]) + "---------------------------------\n"

    def getPieceAtLocation(self,location):
        return self.__board[location.y][location.x]

    def removePieceAtLocation(self,location):
        if self.__board[location.y][location.x]:
            for index,piece in enumerate(self.__pieces[self.__board[location.y][location.x].COLOR]):
                if piece == self.__board[location.y][location.x]:
                    return self.__pieces[piece.COLOR].pop(index)

    def movePieceToLocation(self,piece,destination):
        current_loc = piece.getLocation()
        self.__board[destination.y][destination.x] = piece
        if self.getPieceAtLocation(destination) != None:
            self.removePieceAtLocation(destination)
        self.__board[current_loc.y][current_loc.x] = None

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
    
    def getLocation(self):
        return self.__location
    
    @abstractmethod
    def getValidLocations(self,board):
        return None
    
    def tryMove(self,destination,board):
        if destination in self.getValidLocations(board):
            if board.getPieceAtLocation(destination) != None:
                board.removePieceAtLocation(destination)
            board.movePieceToLocation(self.__location,destination)

class Pawn(Piece): # color, location
    __firstmove = True
    __is_ep_valid = False
    def __init__(self,color,location):
        super().__init__(color, PieceType.PAWN, location)

    def getValidLocations(self,board):
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

    def getValidLocations(self,board):
        curr_loc = self.getLocation()
        N = E = S = W = True
        valid_locs = []
        for i in range(1,8):
            if N and (curr_loc.y - i >= 0): # N
                NL = Location(curr_loc.x, curr_loc.y - i)
                N_cell = board.getPieceAtLocation(NL) #unintentionally funny
                if N_cell != None:
                    N = False
                    if N_cell.COLOR != self.COLOR:
                        valid_locs.append(NL)
                else:
                    valid_locs.append(NL)
                        
            if E and (curr_loc.x + i <= 7): # E
                EL = Location(curr_loc.x + i, curr_loc.y)
                E_cell = board.getPieceAtLocation(EL)
                if E_cell != None:
                    E = False
                    if E_cell.COLOR != self.COLOR:
                        valid_locs.append(EL)
                else:
                    valid_locs.append(EL)
            
            if S and (curr_loc.y + i <= 7): # S
                SL = Location(curr_loc.x, curr_loc.y + i)
                S_cell = board.getPieceAtLocation(SL)
                if S_cell != None:
                    S = False
                    if S_cell.COLOR != self.COLOR:
                        valid_locs.append(SL)
                else:
                    valid_locs.append(SL)
            
            if W and (curr_loc.x - i >= 0): # W
                WL = Location(curr_loc.x - i, curr_loc.y)
                W_cell = board.getPieceAtLocation(WL)
                if W_cell != None:
                    W = False
                    if W_cell.COLOR != self.COLOR:
                        valid_locs.append(WL)
                else:
                    valid_locs.append(WL)
        
        return valid_locs
        # raise "This Method has not yet been implemented"

class Knight(Piece): # color, location
    def __init__(self,color,location):
        super().__init__(color, PieceType.KNIGHT, location)

    def getValidLocations(self,board):
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
        valid_locs = [ loc for loc in probable_locs if board.getPieceAtLocation(loc) == None or board.getPieceAtLocation(loc).COLOR != self.COLOR ]
        return valid_locs
        # raise "This Method has not yet been implemented"

class Bishop(Piece): # color, location, piecetype override for queen
    def __init__(self, color, location, piecetype = PieceType.BISHOP):
        # input validation for queen
        if type(location) == PieceType:
            temp = location
            location = piecetype
            piecetype = temp
        super().__init__(color, piecetype, location)

    def getValidLocations(self,board):
        raise "This Method has not yet been implemented"

class Queen(Rook,Bishop):
    def __init__(self,color,location):
        super().__init__(color = color, location = location, piecetype = PieceType.QUEEN)

    def getValidLocations(self,board):
        return Rook.getValidLocations(board).append(Bishop.getValidLocations(board))

class King(Piece):
    def __init__(self, color, location):
        super().__init__(color, PieceType.KING, location)

    def getValidLocations(self,board):
        possible_locs = [
            Location(self.getLocation().x-1, self.getLocation().y-1),   # nw
            Location(self.getLocation().x-1, self.getLocation().y+0),   # n
            Location(self.getLocation().x-1, self.getLocation().y+1),   # ne
            Location(self.getLocation().x+0, self.getLocation().y+1),   # e
            Location(self.getLocation().x+1, self.getLocation().y+1),   # se
            Location(self.getLocation().x+1, self.getLocation().y+0),   # s
            Location(self.getLocation().x+1, self.getLocation().y-1),   # sw
            Location(self.getLocation().x+0, self.getLocation().y-1)    # w
        ]
        valid_locations = [loc for loc in probable_locs if board.getPieceAtLocation(loc) == None or board.getPieceAtLocation(loc).COLOR != self.COLOR ]
        return valid_locations
        #still need to add in moving into check validation

if  __name__ == "__main__":
    board = Board()
    print(board)
    print(board.getPieceAtLocation(Location(6,6)))
    print([str(l) for l in board.getPieceAtLocation(Location(0,6)).getValidLocations(board)])
    print(board.getPieceAtLocation(Location(0,1)))
    print([str(l) for l in board.getPieceAtLocation(Location(0,1)).getValidLocations(board)])
