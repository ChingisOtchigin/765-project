from petri_dish import *
from abor_evolve import *
import time

def manhattan_distance(set1, set2):
    return sum(abs(pair[0] - pair[1]) for pair in zip(set1, set2))

def get_russian_flag_color(h, grid_height):
    return [(255, 255, 255), (0,0,255), (255, 0, 0)][int(h.row > pd.grid_height // 3) + int(h.row > 2 * grid_height // 3)]

def run_russian_flag_evo(tk, pd, time_step = 0.5):
    for row in pd.hex_grid:
        for h in row:
            new_cell = RussianFlagCell([random.random() for _ in range(3)], h, get_russian_flag_color(h, pd.grid_height))

    def update_cell(row, col):
        h = pd.hex_grid[row][col]
        c = h.cell

        #try fill it by growing out neighbours
        if c == None:
            sorted_neighbours = sorted([x.cell for x in h.neighbors if x.cell], key=lambda x: manhattan_distance(x.rgb, x.target_color))
            if not len(sorted_neighbours) < 2:
                RussianFlagCell(combine_genome(sorted_neighbours[0].genome, sorted_neighbours[1].genome), h, get_russian_flag_color(h, pd.grid_height))
        else:
            #check if this cell is still alive, if not kill it
            c.energy = c.energy - manhattan_distance(c.rgb, c.target_color)
            if c.energy < 0:
                h.unpair_cell()

        col += 1
        if col == pd.grid_width:
            col = 0
            row = row + 1 if row < pd.grid_height - 1 else 0
    
        tk.after(2, lambda: update_cell(row, col))

    tk.after(2, lambda: update_cell(0,0))




    

######################################
######################################

pd = PetriDish(50, 25)
tk = pd.draw(hex_size=15)

######################################
#########  CODE GOES HERE  ###########
######################################

#run_russian_flag_evo(tk, pd)



#########################################
#########################################
def correct_quit(tk):
    tk.destroy()
    tk.quit()
    quit()

quit_button = Button(tk, text = "Quit", command = lambda :correct_quit(tk))
quit_button.pack(pady=10)
tk.mainloop()

