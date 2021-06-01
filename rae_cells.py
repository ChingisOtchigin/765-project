from hashlib import sha1
from petri_dish import *
from abor_evolve import *
import numpy as np

startingEnergy = 1
hunger = 0.1

choiceSharingThreshold = 1 #if probability is higher, cell takes the action
choiceReproductionThreshold = 0.2
shareAmount = 0.1

pd = PetriDish(50, 25)
tk = pd.draw(hex_size=15)

numFoodSensors = 7
numCellSensors = 6
numActions = 2 #reproduce or share

numGenomeInputs = (numCellSensors + numFoodSensors)*numActions

class NiceCell(Cell):
    def __init__(self, genome, hex_pair, energy=startingEnergy):
        Cell.__init__(self, hex_pair=hex_pair)
        self.genome = genome
        self.energy = energy   
        self.hex_pair = hex_pair

    def getProbabilitiesOfReproducing(self, neighbourConcentrations, neighbourCells):
        indexOffset = 0
        reproducingProbs = np.zeros(6)

        for i in range(0,6):
            for c in range(0, neighbourConcentrations.size):
                reproducingProbs[i] += self.genome[c]*neighbourConcentrations[(c + i)%6]
            for n in range(0, neighbourCells.size):
                reproducingProbs[i] += self.genome[n + numFoodSensors]*neighbourCells[((n + i)%6)]

        return reproducingProbs

    def getProbabilitiesOfSharing(self, neighbourConcentrations, neighbourCells):
        indexOffset = (numFoodSensors+numCellSensors)
        sharingProbs = np.zeros(6)

        for i in range(0,6):
            for c in range(0, neighbourConcentrations.size):
                sharingProbs[i] += self.genome[c + indexOffset]*neighbourConcentrations[(c + i)%6]
            for n in range(0, neighbourCells.size):
                sharingProbs[i] += self.genome[n + indexOffset + numFoodSensors]*neighbourCells[((n + i)%6)]
                #print("checking genome: " , n + indexOffset + numFoodSensors)

        return sharingProbs

def getIndexOfNeighbour(center, neighbour):

    leftr = center.row
    leftc = (center.col - 1)

    if (neighbour.row == center.row): #center neighbours
        if(neighbour.col > center.col):
            return 3
        else:
            return 0
    elif(neighbour.row < center.row): #top neighbours
        #check if the cell to the left of the center is a shared neighbour
        for n in neighbour.neighbors:  
            if(n.row == leftr and n.col == leftc):
                return 1
        return 2
    else:
        for n in neighbour.neighbors:
            if(n.row == leftr and n.col == leftc):
                return 5
        return 4
                

def getLivingNeighbours(hex):
    #print("getting neighbours for", hex.row, ", ", hex.col)

    neighbours = hex.neighbors
    living = np.zeros(6)

    for n in neighbours:
        index = getIndexOfNeighbour(hex, n)
        #print("index of neighbor ", n.row, ", ", n.col, ": ", index)
        #print("has cell:" , n.cell)
        if(n.cell != None):
            living[index] = 1

    return living

def getConcentrationNeighbours(hex):
    neighbours = hex.neighbors
    conc = np.zeros(7)

    for n in neighbours:
        index = getIndexOfNeighbour(hex, n)
        conc[index] = n.contents

    conc[6] = hex.contents

    return conc

def getNeighborAtIndex(centerHex, index):
    neighbours = centerHex.neighbors

    for n in neighbours:
        i = getIndexOfNeighbour(centerHex, n)
        if(i == index):
            return n

    return None


def share(cell, hex, percent):
    
    #print(cell.hex_pair.row, ", ", cell.hex_pair.col, ", share: ", percent)
    shareAmount = cell.energy*percent
    cell.energy = cell.energy - shareAmount

    Hex.updateConcentration(hex, (hex.contents + shareAmount))

    return

def reproduce(cell, hex):
    #print(cell.hex_pair.row, ", ", cell.hex_pair.col, ", reproduce: ", hex)

    genome = combine_genome(cell.genome, cell.genome)
    cell.energy = cell.energy/2

    NiceCell(genome, hex, cell.energy/2)
    return


def eat(cell):
    hex = cell.hex_pair
    conc = hex.contents
    Hex.updateConcentration(hex, 0)

    cell.energy = cell.energy + conc



def cellTurn(cell):
    cell.energy = cell.energy - hunger

    if(cell.energy <= 0):
        # kill cell
        hex = cell.hex
        hex.unpair_cell()
        return
        
    #get neighbouring cells
    conc = getConcentrationNeighbours(cell.hex_pair)
    living = getLivingNeighbours(cell.hex_pair)

    #print("conc: ", conc)
    #print("living: ", living)

    if(sum(living) < 1):
        cell.hex.unpair_cell()

    probsShare = NiceCell.getProbabilitiesOfSharing(cell,conc,living)
    maxShare = np.argmax(probsShare)

    probsReproduce = NiceCell.getProbabilitiesOfReproducing(cell,conc,living)
    maxReproduce = np.argmax(probsReproduce)

    if(probsShare[maxShare] > choiceSharingThreshold):
        shareHex = getNeighborAtIndex(cell.hex_pair, maxShare)
        share(cell, shareHex, shareAmount)

    if(probsReproduce[maxReproduce] > choiceReproductionThreshold):
        reprodHex = getNeighborAtIndex(cell.hex_pair, maxReproduce)
        reproduce(cell, reprodHex)

    return

def initialiseConcentrations(pd):
    
    for i, hex_row in enumerate(pd.hex_grid):
        for h in hex_row:
            Hex.updateConcentration(self = h, concentration = i/len(pd.hex_grid))


def nice_cell_evo(tk, pd, time_step = 0.5):

    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[10][44], startingEnergy)
    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[10][43], startingEnergy)
    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[10][45], startingEnergy)

    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[15][44], startingEnergy)
    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[15][43], startingEnergy)
    NiceCell([random.random() for _ in range(numGenomeInputs)], pd.hex_grid[15][45], startingEnergy)

    def update_cell(row, col):
        h = pd.hex_grid[row][col]
        c = h.cell

        if(c != None):
            cellTurn(c)

        col += 1
        if col == pd.grid_width:
            col = 0
            row = row + 1 if row < pd.grid_height - 1 else 0
    
        tk.after(2, lambda: update_cell(row, col))
    

    tk.after(2, lambda: update_cell(0,0))

    


### run ###

initialiseConcentrations(pd)
nice_cell_evo(tk, pd)



def correct_quit(tk):
    
    tk.destroy()
    tk.quit()
    quit()

quit_button = Button(tk, text = "Quit", command = lambda :correct_quit(tk))
quit_button.pack(pady=10)
tk.mainloop()



