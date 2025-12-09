# -*- coding: utf-8 -*-

import tkinter.filedialog as fd
import tkinter as tk
import tkinter.messagebox as tkbox

import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)



from ESR_class import *
from Snap_class import *

import Split_Spectr as splitsp

plt.style.use('bmh')

spectr = ESR_Spectr()

def open_plot():
    fv = fd.askopenfilenames(filetypes = [('PS100.X spectre', '.spe'),
                                          ('Data files', ['.dat','.txt']),
                                          ('All types', '.*')])
    
    try:
        spectr.open_spectr(fv)
        top_label["text"] = fv
    except:
        tkbox.showwarning('Ошибка','Выберите файл', parent = main_window)
        return

    line.set_data(spectr.field, spectr.intensity)
    SpAx.set_xlim(1.01*min(spectr.field) - 0.01*max(spectr.field), 1.01*max(spectr.field) - 0.01*min(spectr.field))
    SpAx.set_ylim(min(spectr.intensity) * (1 - np.sign(min(spectr.intensity))*0.1), max(spectr.intensity) * (1 + np.sign(max(spectr.intensity)) * 0.1))

    del spectr.h_pp[:]
    del spectr.int_pp[:]
    snap_cursor.bullet.set_data(spectr.h_pp, spectr.int_pp)
    snap_cursor.left_line.set_xdata(spectr.begin_norm)
    snap_cursor.right_line.set_xdata(spectr.end_norm)
    
    snap_cursor.cross.set_data(line.get_data())
    snap_cursor.x, snap_cursor.y = line.get_data()
    
    # required to update canvas and attached toolbar!
    main_canvas.draw()


def export_plot():
    if spectr.file_sp == '':
        tkbox.showwarning('Ошибка','Сначала выберите спектр', parent = main_window)
        return
    
    spectr.export()
    tkbox.showinfo('Информация','Экспорт спектра завершен', parent = main_window)
    

def export_param():
    if spectr.file_sp == '':
        tkbox.showwarning('Ошибка','Сначала выберите спектр', parent = main_window)
        return
    
    try:
        spectr.export_parameters()
        tkbox.showinfo('Информация','Экспорт параметров завершен', parent = main_window)
    except:
        tkbox.showwarning('Ошибка','Выберите хотя бы одну резонансную линию', parent = main_window)
        return


# the figure that will contain the plot
main_fig = Figure(figsize = (10, 8), dpi = 100)
  
# adding the subplot
SpAx = main_fig.add_subplot()
SpAx.set_position([0.055, 0.05, 0.93, 0.92])
    
# plotting the empty graph
line, = SpAx.plot(spectr.field, spectr.intensity)

# the main Tkinter window
main_window = tk.Tk()

# setting the title 
main_window.title('EPR_ProData')
  
# dimensions of the main window
w = main_window.winfo_screenwidth()
h = main_window.winfo_screenheight() - 80
main_window.geometry(f"{w}x{h}")
main_window.resizable(False, False)

top_label = tk.Label(main_window, 
              pady = 2, 
              height = 2,
              text = '') 

frame_button = tk.Frame(main_window, 
                 pady = 5, 
                 height = 4)

hotkey_label = tk.Label(main_window,
                pady = 5,
                padx = 5,
                text = f"Основные: a - добавить точку, z - удалить точку;\nДополнительно: b - добавить начало интервала, n - добавить конец интервала,\n{'m - сбросить границы интервала': >58}",
                justify = tk.LEFT,
                font = "Verdana 12 normal")

# button that displays the plot
plot_open_button = tk.Button(master = frame_button,
                     command = open_plot,
                     height = 2, 
                     width = 10,
                     text = "Открыть")

plot_export_button = tk.Button(master = frame_button, 
                       command = export_plot,
                       height = 2, 
                       width = 10,
                       text = "Экспорт\nспектра")

export_param_button = tk.Button(master = frame_button, 
                        command = export_param,
                        height = 2, 
                        width = 10,
                        text = "Параметры")

split_spectr_button = tk.Button(master = frame_button, 
                        command = lambda: splitsp.split_spectr(main_window, spectr),
                        height = 2, 
                        width = 10,
                        text = "Разделение\nлиний")

# creating the Tkinter canvas
# containing the Matplotlib figure
main_canvas = FigureCanvasTkAgg(main_fig, master = main_window)  
    
# placing the canvas on the Tkinter window
##canvas.get_tk_widget().pack()

snap_cursor = SnappingCursor(SpAx, line, spectr)
main_canvas.mpl_connect('motion_notify_event', snap_cursor.on_mouse_move)
main_canvas.mpl_connect('key_press_event', lambda event: snap_cursor.on_press(event, spectr))

# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(main_canvas, main_window)
toolbar.update()

top_label.pack(fill = 'x')

# placing the toolbar on the Tkinter window
main_canvas.get_tk_widget().pack(padx =  10, fill = tk.X)

# place the button 
# in main window
frame_button.pack(padx = 250, side = 'left')
plot_open_button.pack(side = 'left')
plot_export_button.pack(side = 'left', padx = 50, ipady = 2)
export_param_button.pack(side = 'left')
split_spectr_button.pack(side = 'left', padx = 50)

hotkey_label.pack(padx = 20)  
# run the gui
main_window.mainloop()
