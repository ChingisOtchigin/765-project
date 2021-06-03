from petri_dish import *
from abor_evolve import *
import time

def manhattan_distance(set1, set2):
    return sum(abs(pair[0] - pair[1]) for pair in zip(set1, set2))

def get_russian_flag_color(h, grid_height):
    return [(255, 255, 255), (0,0,255), (255, 0, 0)][int(h.row > pd.grid_height // 3) + int(h.row > 2 * grid_height // 3)]

def run_russian_flag_evo(tk, pd):
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

def propagate_food_sources(fs, pd):
    food_color = [207, 243, 252]
    pd[0][0].updateConcentration(0.0, food_color)
    masks = []
    for source in fs:
        mask = [[0 for _ in range(pd.grid_width)] for _ in range(pd.grid_height)]
        mask[source[0]][source[1]] = 1.0
        open_list = [source]
        stop = False
        while not stop:
            node = open_list.pop(0)
            if mask[node[0]][node[1]] == 0:
                break
            for n in pd[node[0]][node[1]].neighbors:
                new_node = (n.row, n.col)
                if mask[new_node[0]][new_node[1]] == 0:
                    mask[new_node[0]][new_node[1]] = round(mask[node[0]][node[1]] - 0.1, 1)
                    open_list.append(new_node)
        masks.append(mask)
    
    for i in range(pd.grid_height):
        for j in range(pd.grid_width):
            content_sum = sum(mask[i][j] for mask in masks)
            pd[i][j].updateConcentration(min(1, content_sum), food_color)

def run_competitive_behaviour_evo(tk, pd, genome=None, max_age=10, reproduction_probability=0.9):
    #Cool Combinations to try: Solid 0.85 with age 5, 0.9 with age 7, 0.8 with age 3
    #
    food_sources = sum([[(0,i), (10,i)] for i in [0,20]], [])
    propagate_food_sources(food_sources, pd)

    if genome:
        LIVING_CELLS = [SelfishCell(pd[i][1], genome) for i in range(pd.grid_height)]
    else:
        LIVING_CELLS = [SelfishCell(pd[i][1], [random.random()]) for i in range(pd.grid_height)]


    def update_cell(i):
        if not i < len(LIVING_CELLS):
            i = 0

        cell = LIVING_CELLS[i]
        need_to_be_filled = []
        cell.age += 1

        cell.food_supply = cell.food_supply + cell.hex.contents - 0.4

        #now its yoinking and breeding time
        has_buddies = False
        for n in cell.hex.neighbors:
            neighbor_cell = n.cell
            if neighbor_cell:
                has_buddies = True
                cell.food_supply += neighbor_cell.food_supply * cell.genome[0]
                neighbor_cell.food_supply -= neighbor_cell.food_supply * cell.genome[0]
            else:
                need_to_be_filled.append(n)
            

        if cell.food_supply < 0 or not has_buddies or cell.age == max_age:
            LIVING_CELLS.remove(cell)
            cell.hex.unpair_cell()
            tk.after(2, lambda: update_cell(i + 1))
            return

        for n in need_to_be_filled:
            if random.random() < reproduction_probability: #The reproduction chance matters a ridiculous amount       
                possible_parents = sorted([parent.cell for parent in n.neighbors if parent.cell], key=lambda x: x.food_supply, reverse=True)
                if len(possible_parents) > 1:
                    p1, p2 = possible_parents[:2]
                    if genome:
                        LIVING_CELLS.append(SelfishCell(n, genome))
                    else:
                        LIVING_CELLS.append(SelfishCell(n, combine_genome(p1.genome, p2.genome)))


        tk.after(2, lambda: update_cell(i + 1))

    tk.after(2, lambda: update_cell(0))

    
    

######################################
######################################

#pd = PetriDish(50, 25)
pd = PetriDish(25, 15)
tk = pd.draw(hex_size=20) #usually 15

######################################
#########  CODE GOES HERE  ###########
######################################

#run_russian_flag_evo(tk, pd)
random.seed(1234)
#run_competitive_behaviour_evo(tk, pd,  genome=[0], max_age=5)
#run_competitive_behaviour_evo(tk, pd)
#run_competitive_behaviour_evo(tk, pd, max_age=5)
run_competitive_behaviour_evo(tk, pd,  genome=[0.99], max_age=3)
#run_competitive_behaviour_evo(tk, pd, reproduction_probability=0.3)



# print(f'Neighbors for (0,2):')
# for n in pd[0][2].neighbors:
#     print(f'({n.row}, {n.col})')


#########################################
#########################################
def correct_quit(tk):
    tk.destroy()
    tk.quit()
    quit()

quit_button = Button(tk, text = "Quit", command = lambda :correct_quit(tk))
quit_button.pack(pady=10)
tk.mainloop()

