from tkinter import *
import random

class Hex:
    def __init__(self, row, col, cell=None, contents=None):
        self.row = row
        self.col = col
        self.cell = cell
        self.neighbors = None
        self.contents = contents
        self.polygon = None
        self.color = '#D5D8D3'
    
    def draw(self, x, y, size, canvas): 
        dx = (3**0.5 * size) // 2

        p1 = (x + dx    , y + size // 2 )
        p2 = (x + dx    , y - size // 2 )
        p3 = (x         , y - size      )
        p4 = (x - dx    , y - size // 2 )
        p5 = (x - dx    , y + size // 2 )
        p6 = (x         , y + size      )

        self.canvas = canvas
        self.polygon = canvas.create_polygon(p1,p2,p3,p4,p5,p6, fill=self.color, outline='grey', width=1) #store this to access it directly
    
    def update_color(self, new_color):
        if self.polygon:
            self.canvas.itemconfig(self.polygon, fill=new_color)
        else:
            self.color = new_color
        
    def pair_cell(self, cell):
        self.cell = cell
        self.update_color(cell.color)
    
    def unpair_cell(self):
        self.cell = None
        self.update_color('#D5D8D3')

class Cell:
    def __init__(self, color='red', hex_pair = None):
        self.hex = hex_pair
        self.color = color

        hex_pair.pair_cell(self)
    
    def change_color(self, new_color):
        #Always call this
        self.color = new_color
        self.hex.update_color(new_color)

class RussianFlagCell(Cell):
    def __init__(self, genome, hex_pair, target_color, energy=500):
        """Target colour is an rgb tuple"""
        Cell.__init__(self, hex_pair=hex_pair)
        self.target_color = target_color
        self.genome = genome
        self.rgb = [int(255 * gene) for gene in genome]
        self.change_color('#' + ''.join([format(x, '02x') for x in self.rgb]))
        self.energy = energy    

class PetriDish:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_grid = [[Hex(j, i) for i in range(grid_width)] for j in range(grid_height)]

        #this is gonna look horrible
        for index, row in enumerate(self.hex_grid):
            if index == 0:
                self[0][0].neighbors = [self[0][1], self[1][0]]
                self[0][-1].neighbors = [self[0][-2], self[1][-2], self[1][-1]]
                for j in range(1, grid_width - 1):
                    self[0][j].neighbors = [self[0][j - 1], self[1][j-1], self[1][j], self[0][j + 1]]
            elif index == grid_height - 1:
                if index % 2: #outies
                    self[-1][0].neighbors = [self[-1][1], self[-2][0]]
                    self[-1][-1].neighbors = [self[-1][-2], self[-2][-2], self[-2][-1]]
                    for j in range(1, grid_width - 1):
                        self[-1][j].neighbors = [self[-1][j - 1], self[-2][j-1], self[-2][j], self[-1][j + 1]]
                else: #innies
                    self[-1][0].neighbors = [self[-1][1], self[-2][1], self[-2][0]]
                    self[-1][-1].neighbors = [self[-1][-2], self[-2][-1]]
                    for j in range(1, grid_width - 1):
                        self[-1][j].neighbors = [self[-1][j - 1], self[-2][j], self[-2][j + 1], self[-1][j + 1]]
            elif index % 2: #outies
                self[index][0].neighbors = [self[index - 1][0], self[index][1], self[index + 1][0]]
                self[index][-1].neighbors = [self[index - 1][-1], self[index - 1][-2], self[index][-2], self[index + 1][-2], self[index + 1][-1]]
                for j in range(1, grid_width - 1):
                        self[index][j].neighbors = [self[index][j - 1], self[index - 1][j - 1], self[index - 1][j], self[index][j + 1], self[index + 1][j], self[index + 1][j - 1]]
            else: #innies
                self[index][0].neighbors = [self[index - 1][0], self[index - 1][1], self[index][1], self[index + 1][1], self[index + 1][0]]
                self[index][-1].neighbors = [self[index - 1][-1], self[index][-2], self[index + 1][-1]]
                for j in range(1, grid_width - 1):
                        self[index][j].neighbors = [self[index][j - 1], self[index - 1][j], self[index - 1][j + 1], self[index][j + 1], self[index + 1][j + 1], self[index + 1][j]]
            

    def draw(self, hex_size=12, background='#98ee90'):
        """Don't forget to call tk mainloop on the return value of this function"""
        tk = Tk()
        tk.title('The Petri Dish')

        hex_width = int(3**0.5 * hex_size)
        hex_height = int(hex_size * 1.5)

        self.canvas = Canvas(tk, width= (hex_width * (self.grid_width + 2)), height= (hex_height * (self.grid_height + 2)), background=background)
        self.canvas.pack()

        current_x = int(hex_width * 1.5)
        current_y = int(hex_size * 2.5)

        #draw da hexes
        for i, hex_row in enumerate(self.hex_grid):
            for h in hex_row:
                h.draw(current_x, current_y, hex_size, self.canvas)
                current_x += hex_width
            current_x = int(hex_width * 1.5) if i % 2 else hex_width * 2
            current_y += hex_size * 1.5 

        return tk
    
    def __getitem__(self, index):
        try:
            return self.hex_grid[index]
        except:
            print(f'Hex Grid Error at row index {index}')
            quit()