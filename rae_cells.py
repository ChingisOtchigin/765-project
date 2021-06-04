from hashlib import sha1
from random import randint
from petri_dish import *
from abor_evolve import *
import numpy as np

startingEnergy = 1
hunger = 0.2

choiceSharingThreshold = 0.5 #if probability is higher, cell takes the action
choiceReproductionThreshold = 0.5
shareAmount = 0.5
neighbourHungerFactor = 1

pd = PetriDish(30, 30)
tk = pd.draw(hex_size=15)

numFoodSensors = 7
numCellSensors = 6
numActions = 2 #reproduce or share

numGenomeInputs = (numCellSensors*2 + numFoodSensors*6)*2 #cell sensors only require 2 genes e.g. there is or is not a cell

randomGenome = [random.random() for _ in range(numGenomeInputs)]
bestGenomes = np.array([randomGenome, randomGenome, randomGenome])

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
            for c in range(0, 7):
                x = [0, self.genome[c*6+4], self.genome[c*6+5],1]
                y = [self.genome[c*6], self.genome[c*6+1], self.genome[c*6+2], self.genome[c*6+3]]
                reproducingProbs[i] += np.interp(neighbourConcentrations[(c + i)%6], x, y)

            for n in range(0, 6):
                x = [-1,1]
                y = [self.genome[(7*6) + n*2], self.genome[(7*6) + n*2 + 1] ]
                reproducingProbs[i] += np.interp(neighbourCells[((n + i)%6)], x, y)

        return reproducingProbs

    def getProbabilitiesOfSharing(self, neighbourConcentrations, neighbourCells):
        indexOffset = (numCellSensors*2 + numFoodSensors*6)
        sharingProbs = np.zeros(6)

        for i in range(0,6):
            for c in range(0, 7):
                x = [0, self.genome[c*6+4 + indexOffset], self.genome[c*6+5 + indexOffset],1]
                y = [self.genome[c*6 + indexOffset], self.genome[c*6+1 + indexOffset], self.genome[c*6+2 + indexOffset], self.genome[c*6+3 + indexOffset]]
                sharingProbs[i] += np.interp(neighbourConcentrations[(c + i)%6], x, y)

            for n in range(0, 6):
                x = [0,1]
                y = [self.genome[(7*6) + n*2 + indexOffset], self.genome[(7*6) + n*2 + 1 + indexOffset] ]
                sharingProbs[i] += np.interp(neighbourCells[((n + i)%6)], x, y)

        return sharingProbs

def getIndexOfNeighbour(center, neighbour):

    if (neighbour.row == center.row): #center neighbours
        if(neighbour.col > center.col):
            return 3
        else:
            return 0
    elif(neighbour.row < center.row): #top neighbours

        if(neighbour.row%2 == 0): #All evens are outies
            if(neighbour.col == center.col):
                return 1
            else:
                return 2
        else:
            if(neighbour.col == center.col):
                return 2
            else:
                return 1
    else:
        if(neighbour.row%2 == 0): #All evens are outies
            if(neighbour.col == center.col):
                return 5
            else:
                return 4
        else:
            if(neighbour.col == center.col):
                return 4
            else:
                return 5


def mutateGenome(genome, mu = 0.05):
    outGenome = []

    for i in range(0, len(genome)):
        mutation = mu*random.randint(-1,1)
        if(genome[i] + mutation < -1):
            outGenome.append(-1)
        elif(genome[i] + mutation > 1):
            outGenome.append(1)
        else:
            outGenome.append(genome[i] + mutation)
    
    return outGenome



def getLivingNeighbours(hex):

    neighbours = hex.neighbors
    living = np.zeros(6)

    for n in neighbours:
        index = getIndexOfNeighbour(hex, n)
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
    shareAmount = min(1 - hex.contents, shareAmount)
    cell.energy = cell.energy - shareAmount

    Hex.updateConcentration(hex, (hex.contents + shareAmount))

    return

def reproduce(cell, hex):
    #print(cell.hex_pair.row, ", ", cell.hex_pair.col, ", reproduce: ", hex)

    genome = mutateGenome(cell.genome)
    cell.energy = cell.energy/2

    cell = NiceCell(genome, hex, cell.energy/2)
    return


def eat(cell):
    hex = cell.hex_pair
    conc = hex.contents
    Hex.updateConcentration(hex, 0)

    cell.energy = cell.energy + conc

def updateBestGenomes(genome):
    bestGenomes[2] = bestGenomes[1]
    bestGenomes[1] = bestGenomes[0]
    bestGenomes[0] = genome

def cellTurn(cell):
    eat(cell)
    living = getLivingNeighbours(cell.hex_pair)
    adjustedHunger = hunger*(neighbourHungerFactor**sum(living))

    cell.energy = cell.energy - adjustedHunger

    if(cell.energy <= 0):

        # kill cell
        hex = cell.hex
        hex.unpair_cell()
        updateBestGenomes(cell.genome)
        Hex.updateConcentration(hex, 0)

        return
        
    #get neighbouring cells
    conc = getConcentrationNeighbours(cell.hex_pair)
    living = getLivingNeighbours(cell.hex_pair)

    probsShare = NiceCell.getProbabilitiesOfSharing(cell,conc,living)
    maxShare = np.argmax(probsShare)

    probsReproduce = NiceCell.getProbabilitiesOfReproducing(cell,conc,living)
    maxReproduce = np.argmax(probsReproduce)

    if(probsShare[maxShare] > choiceSharingThreshold):
        shareHex = getNeighborAtIndex(cell.hex_pair, maxShare)
        if(shareHex!= None):
            share(cell, shareHex, shareAmount)

    if(probsReproduce[maxReproduce] > choiceReproductionThreshold):
        reprodHex = getNeighborAtIndex(cell.hex_pair, maxReproduce)
        if(reprodHex!= None):
            reproduce(cell, reprodHex)

    return

def initialiseConcentrations(pd):

    radius = 30
    row = random.randint(0, pd.grid_height-1)
    col = random.randint(0, pd.grid_width-1)
    
    for i, hex_row in enumerate(pd.hex_grid):
        for h in hex_row:
            _concentration = 0
            dif = ((h.row - row)**2 + (h.col- col)**2)**(0.5)

            if(dif <= radius):
                _concentration = (float)(radius - dif)/radius

            Hex.updateConcentration(self = h, concentration = _concentration)

def getListOfLivingCells(pd):
    livingCellsList = []

    for i, hex_row in enumerate(pd.hex_grid):
        for h in hex_row:
            if (h.cell != None):
                livingCellsList.append(h.cell)

    return livingCellsList
            
def initialiseGeneration(genomes):
    initialiseConcentrations(pd)

    for i in range(0, genomes.shape[0]):
        NiceCell(genomes[i], pd.hex_grid[int(pd.grid_height/3)][int(pd.grid_width/2) +  i], startingEnergy)


def nice_cell_evo(tk, pd, time_step = 0.5):

    #Initialise
    initialiseConcentrations(pd)
    
    initialGenomes = np.empty((6, numGenomeInputs))
    for i in range(0, initialGenomes.shape[0]):
        initialGenomes[i] = [random.uniform(-1.0, 1.0) for _ in range(numGenomeInputs)]

    print("Initial genomes: ", initialGenomes)
    initialiseGeneration(initialGenomes)

    #Main loop here
    def update_cells():
        livingCellsList = getListOfLivingCells(pd)

        for cell in livingCellsList:
            tk.after(10, lambda: cellTurn(cell))
        
        if(len(livingCellsList) > 0):
            tk.after(10, lambda: update_cells())
        else:
            genomes = breedFromBest(6)
            initialiseGeneration(genomes)
            tk.after(10, lambda: update_cells())

    tk.after(2, lambda: update_cells())


def breedFromBest(outputSize):
    out = np.empty((outputSize, numGenomeInputs))

    for i in range(0, outputSize):
        random1 = randint(0, (bestGenomes.shape[0] - 1))
        out[i] = mutateGenome(bestGenomes[random1])
    return out


### run ###

nice_cell_evo(tk, pd)

def correct_quit(tk):

    print("best genomes: ", bestGenomes)
    tk.destroy()
    tk.quit()
    quit()

quit_button = Button(tk, text = "Quit", command = lambda :correct_quit(tk))
quit_button.pack(pady=10)
tk.mainloop()



