from tkinter import *

class Hex:
    def __init__(self, cell=None, contents=None):
        self.cell = cell
        self.contents = contents
    
    def draw(self, x, y, size, canvas, color = '#D5D8D3'): 
        dx = (3**0.5 * size) // 2

        p1 = (x + dx    , y + size // 2 )
        p2 = (x + dx    , y - size // 2 )
        p3 = (x         , y - size      )
        p4 = (x - dx    , y - size // 2 )
        p5 = (x - dx    , y + size // 2 )
        p6 = (x         , y + size      )

        self.canvas = canvas
        self.polygon = canvas.create_polygon(p1,p2,p3,p4,p5,p6, fill=color, outline='grey', width=1) #store this to access it directly
    
    def update_color(self, new_color):
        self.canvas.itemconfig(self.polygon, fill=new_color)

class Cell:
    def __init__(self, hex_pair = None):
        self.hex = hex_pair

class PetriDish:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.hex_grid = [[Hex() for _ in range(grid_width)] for _ in range(grid_height)]
            

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
         return self.hex_grid[index]