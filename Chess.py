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

            # Dynamically place the rooks, knights, and bishops
            for i,p in enumerate([PieceType.ROOK,PieceType.KNIGHT,PieceType.BISHOP]):
                D1 = D2 = L1 = L2 = None
                D1L = Location(i,0)
                D2L = Location(7-i,0)
                L1L = Location(i, 7)
                L2L = Location(7-i, 7)
                match p:
                    case PieceType.ROOK:
                        D1 = Rook(Color.DARK, D1L)
                        D2 = Rook(Color.DARK, D2L)
                        L1 = Rook(Color.LIGHT, L1L)
                        L2 = Rook(Color.LIGHT, L2L)
                    case PieceType.BISHOP:
                        D1 = Bishop(Color.DARK, D1L)
                        D2 = Bishop(Color.DARK, D2L)
                        L1 = Bishop(Color.LIGHT, L1L)
                        L2 = Bishop(Color.LIGHT, L2L)
                    case PieceType.KNIGHT:
                        D1 = Knight(Color.DARK, D1L)
                        D2 = Knight(Color.DARK, D2L)
                        L1 = Knight(Color.LIGHT, L1L)
                        L2 = Knight(Color.LIGHT, L2L)
                    case _:
                        raise "This should not be happening."
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


            print(self)
            
    def __str__(self):
        return ''.join(["---------------------------------\n| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(*(p.SYMBOL if p else ' ' for p in row)) for row in self.__board]) + "---------------------------------"

    def getPieceAtLocation(self,location):
        return self.__board[location.y][location.x]

    def removePieceAtLocation(self,location):
        if self.__board[location.y][location.x]:
            for index,piece in enumerate(self.__pieces[self.__board[location.y][location.x].COLOR]):
                if piece == self.__board[location.y][location.x]:
                    return self.__pieces[piece.COLOR].pop(index)

    def movePieceToLocation(self,current_loc,destination):
        self.__board[destination.y][destination.x] = getPieceAtLocation(current_loc)
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
        # print(color,piecetype,location)
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
    def __init__(self,color,location):
        super().__init__(color, PieceType.PAWN, location)

    def getValidLocations(self,board):
        # if first move
        # ternary y + (-2 if color == color.light else 2), x
        # don't forget en passant
        # in addition to just simply 
        # ternary y + (-1 if color == color.light else 1), x if board@loc(x,y) == None
        # as well as
        # ternary y + (-1 if color == color.light else 1), x+-1 if board@loc(x,y).COLOR != self.COLOR
        raise "This Method has not yet been implemented"

class Rook(Piece): # color, location, piecetype override for queen
    def __init__(self, color, location, piecetype = PieceType.ROOK):
        print('Rook: Creating',piecetype)
        print(color,piecetype,location)
        print(type(color),type(piecetype),type(location))
        super().__init__(color, piecetype, location)

    def getValidLocations(self,board):
        raise "This Method has not yet been implemented"

class Knight(Piece): # color, location
    def __init__(self,color,location):
        super().__init__(color, PieceType.KNIGHT, location)

    def getValidLocations(self,board):
        raise "This Method has not yet been implemented"

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
        return Rook.getValidLocations(board) or Bishop.getValidLocations(board)

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
        probable_locations = [ loc if -1 not in [loc.x,loc,y] and 8 not in [loc.x,loc.y] for loc in possible_locs ]
        valid_locations = [loc if board[loc.y][loc.x] == None or board[loc.y][loc.x].COLOR != self.COLOR for loc in probable_locations]

        #still need to add in moving into check validation

if  __name__ == "__main__":
    print("now we're cooking with gas")
    board = Board()