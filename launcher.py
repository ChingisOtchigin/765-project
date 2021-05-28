from petri_dish import *
from abor_evolve import *

pd = PetriDish(10, 5)

tk = pd.draw(hex_size=30)
pd[0][1].update_color('blue')

pd[3][7].update_color('red')


def correct_quit(tk):
        tk.destroy()
        tk.quit()

quit_button = Button(tk, text = "Quit", command = lambda :correct_quit(tk))
quit_button.pack(pady=10)
tk.mainloop()

