from petri_dish import *

pd = PetriDish(10, 5)

tk = pd.draw(hex_size=30)
pd[0][1].update_color('blue')

pd[3][7].update_color('red')
tk.mainloop()

