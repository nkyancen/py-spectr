import numpy as np

import tkinter.filedialog as fd
import tkinter as tk 
import tkinter.messagebox as tkbox

import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from matplotlib import ticker

from decimal import *

from ESR_class import *

norm_spectr = ESR_Normal_Spectr()

line1 = Lorenz_Line()
line2 = Lorenz_Line()
# ~ dline = Double_Line()

def split_spectr(main_win, base_spectr): #производное окно с нормализованным спектром
    if base_spectr.file_sp == '':
        tkbox.showwarning('Ошибка','Сначала выберите спектр ', parent = main_win)
        return

    norm_fig = Figure(figsize = (6, 5.5), dpi = 100)
    NormAx = norm_fig.add_subplot()
    NormAx.set_position([0.05, 0.05, 0.93, 0.92])
    norm_line, = NormAx.plot(norm_spectr.field, norm_spectr.intens, lw=1.5)
    lorenz_line1, = NormAx.plot(norm_spectr.field, line1.y, lw=1, ls='--', color = 'magenta')
    lorenz_line2, = NormAx.plot(norm_spectr.field, line2.y, lw=1, ls='-.', color = 'cyan')
    double_line, = NormAx.plot(norm_spectr.field, line1.y + line2.y, lw=1.3, color = 'green')
    
    
    norm_window = tk.Toplevel(main_win)    
    norm_window.title("Изменение спектра")
    norm_window.geometry("1280x900")
    norm_window.resizable(False, False)
    norm_window.focus_force()
    
    # ~ hmin_var = tk.DoubleVar(value = Decimal(base_spectr.begin_norm).quantize(Decimal("1.00")))
    hmin_var = tk.DoubleVar(value = base_spectr.begin_norm)        
    hmax_var = tk.DoubleVar(value = base_spectr.end_norm)
    
    dx1_var = tk.DoubleVar(value = line1.x_pp)    
    int1_var = tk.DoubleVar(value = line1.int_deriv)    
    center1_var = tk.DoubleVar(value = line1.center)
    
    dx2_var = tk.DoubleVar(value = line2.x_pp)    
    int2_var = tk.DoubleVar(value = line2.int_deriv)    
    center2_var = tk.DoubleVar(value = line2.center)
    
    def refresh_spectr():
        base_spectr.begin_norm = float(hmin_var.get())
        base_spectr.end_norm = float(hmax_var.get())
        norm_spectr.normalize(base_spectr)
        refresh_line()
        
    def refresh_line():
        line1.int_deriv = float(int1_var.get())
        line1.x_pp = float(dx1_var.get())
        line1.center = float(center1_var.get())
        
        line2.int_deriv = float(int2_var.get())
        line2.x_pp = float(dx2_var.get())
        line2.center = float(center2_var.get())
        
        line1.line_derivative(norm_spectr.field)
        line2.line_derivative(norm_spectr.field)
    
    def redraw_spectr():
        refresh_spectr()
        
        norm_line.set_data(norm_spectr.field, norm_spectr.intens)
        NormAx.set_xlim(1.05*min(norm_spectr.field), 1.05*max(norm_spectr.field))
        # ~ NormAx.set_ylim(min(norm_spectr.intens) * (1 - np.sign(min(norm_spectr.intens))*0.1), 
                        # ~ max(norm_spectr.intens) * (1 + np.sign(max(norm_spectr.intens)) * 0.1))
        NormAx.set_ylim(-1.2, 1.2)
        redraw_line()
    
    def redraw_line():
        refresh_line()
        
        lorenz_line1.set_data(norm_spectr.field, line1.y)
        lorenz_line2.set_data(norm_spectr.field, line2.y)
        double_line.set_data(norm_spectr.field, line1.y + line2.y)
        norm_canvas.draw()
    
    # ~ def apply_line():
        # ~ redraw_line()
        
    def export_line_param():
        param_data = ''
        for i, l in enumerate([line1, line2]):
            param_data += f'Line {i + 1} \n  H_0, Oe     dHpp, Oe      I_pp      2DH, Oe        Im  \n '
            param_data +=  '%.3f      %.3f     %.3e    %.3f     %.3e \n\n' % l.get_parameters(norm_spectr)
            
        with open(base_spectr.file_sp.split('/')[-1].split('.')[0] + '_парметры_линий.dat', 'w', encoding = 'utf8') as export_file:
                print(param_data, file = export_file) 
     
    norm_canvas = FigureCanvasTkAgg(norm_fig, master = norm_window)
    redraw_spectr()
    redraw_line() 
    norm_toolbar = NavigationToolbar2Tk(norm_canvas, norm_window)
    norm_toolbar.update()
    
    field_frame = tk.Frame(norm_window, 
                    pady = 2,
                    height = 3)
                              
    field_interval_label = tk.Label(field_frame, 
                             height = 2,
                             text = 'Выбран интервал полей: от')
                              
    field_interval_label_2 = tk.Label(field_frame, 
                               height = 2,
                               text = ' до ')
    
    hmin_spinbox = tk.Spinbox(field_frame,
                      width = 14,
                      justify = tk.CENTER,
                      textvariable = hmin_var,
                      from_ = min(base_spectr.field),
                      to = max(base_spectr.field),
                      increment = 0.01,
                      command = redraw_spectr,
                      font = 13)
    
    hmax_spinbox = tk.Spinbox(field_frame,
                      width = 14,
                      justify = tk.CENTER,
                      textvariable = hmax_var,
                      from_ = min(base_spectr.field),
                      to = max(base_spectr.field),
                      increment = 0.01,
                      command = redraw_spectr,
                      font = 13)
   
        
    apply_interval_field_button = tk.Button(field_frame,
                                     text = 'Обновить',
                                     command = redraw_spectr)
     
     
    field_base_interval_label = tk.Label(field_frame, 
                                   height = 2,
                                   text = ' (В дипазоне от  %.3f  до  %.3f )' % (min(base_spectr.field), max(base_spectr.field)))
    
    line_frame = tk.Frame(norm_window, 
                    pady = 2,
                    height = 10)    
     
    apply_line_button = tk.Button(line_frame,
                           text = 'Применить',
                           command = redraw_line,
                           pady = 3)
    
    export_line_button = tk.Button(line_frame,
                           text = 'Экспорт',
                           command = export_line_param,
                           pady = 5)   
    
    line1_frame = tk.Frame(line_frame, 
                    pady = 3,
                    height = 8, 
                    borderwidth = 1, 
                    relief = 'solid')  
    
    line1_label = tk.Label(line1_frame, 
                        height = 2,
                        text = 'Линия 1')
    
    line1_ampl_label = tk.Label(line1_frame, 
                               height = 2,
                               text = 'Амплитуда = ')
    
    line1_ampl_spinbox = tk.Spinbox(line1_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = int1_var,
                            from_ = 0.0,
                            to = 1.0,
                            increment = 0.001,
                            command = redraw_line,
                            font = 13)

    line1_dx_label = tk.Label(line1_frame, 
                        height = 2,
                        text = 'Ширина = ')
    
    line1_dx_spinbox = tk.Spinbox(line1_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = dx1_var,
                            from_ = 0.0,
                            to = 2 * (norm_spectr.field[-1] - norm_spectr.field[0]),
                            increment = (norm_spectr.field[-1] - norm_spectr.field[0]) / 500,
                            command = redraw_line,
                            font = 13)
    
    line1_center_label = tk.Label(line1_frame, 
                        height = 2,
                        text = 'Центр = ')
    
    line1_center_spinbox = tk.Spinbox(line1_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = center1_var,
                            from_ = norm_spectr.field[0],
                            to = norm_spectr.field[-1],
                            increment = (norm_spectr.field[-1] - norm_spectr.field[0]) / 500,
                            command = redraw_line,
                            font = 13)
    
    line2_frame = tk.Frame(line_frame, 
                    pady = 3,
                    height = 8, 
                    borderwidth = 1, 
                    relief = 'solid')  
    
    line2_label = tk.Label(line2_frame, 
                        height = 2,
                        text = 'Линия 2') 
                    
    
    
    line2_ampl_label = tk.Label(line2_frame, 
                               height = 2,
                               text = 'Амплитуда = ')
    
    line2_ampl_spinbox = tk.Spinbox(line2_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = int2_var,
                            from_ = 0.0,
                            to = 1.0,
                            increment = 0.001,
                            command = redraw_line,
                            font = 13)

    line2_dx_label = tk.Label(line2_frame, 
                        height = 2,
                        text = 'Ширина = ')
    
    line2_dx_spinbox = tk.Spinbox(line2_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = dx2_var,
                            from_ = 0.0,
                            to = (norm_spectr.field[-1] - norm_spectr.field[0]),
                            increment = (norm_spectr.field[-1] - norm_spectr.field[0]) / 500,
                            command = redraw_line,
                            font = 13)
    
    line2_center_label = tk.Label(line2_frame, 
                        height = 2,
                        text = 'Центр = ')
    
    line2_center_spinbox = tk.Spinbox(line2_frame,
                            width = 14,
                            justify = tk.CENTER,
                            textvariable = center2_var,
                            from_ = norm_spectr.field[0],
                            to = norm_spectr.field[-1],
                            increment = (norm_spectr.field[-1] - norm_spectr.field[0]) / 500,
                            command = redraw_line,
                            font = 13)
    
    field_frame.pack(fill = 'x', pady = 3, padx = 10)
    
    field_interval_label.pack(side = 'left')
    hmin_spinbox.pack(side = 'left')
    field_interval_label_2.pack(side = 'left')
    hmax_spinbox.pack(side = 'left')
    field_base_interval_label.pack(side = 'left', padx = 10)   
    apply_interval_field_button.pack(side = 'left', padx = 10)
    
    norm_canvas.get_tk_widget().pack(fill = 'x', padx = 20, pady = 10)
    
    line_frame.pack(pady = 3, padx = 10)
    line1_frame.grid(row = 0, column = 0)
    line1_label.grid(row = 0, column = 0, columnspan = 2)
    line1_dx_label.grid(row = 1, column = 0, padx = 5)
    line1_dx_spinbox.grid(row = 1, column = 1, padx = 2)
    line1_ampl_spinbox.grid(row = 2, column = 1, padx = 2)
    line1_ampl_label.grid(row = 2, column = 0, padx = 5)
    line1_center_label.grid(row = 3, column = 0, padx = 5)
    line1_center_spinbox.grid(row = 3, column = 1, padx = 2 )
    
    line2_frame.grid(row = 0, column = 1)    
    line2_label.grid(row = 0, column = 0, columnspan = 2)
    line2_dx_label.grid(row = 1, column = 0, padx = 5)
    line2_dx_spinbox.grid(row = 1, column = 1, padx = 2)
    line2_ampl_spinbox.grid(row = 2, column = 1, padx = 2)
    line2_ampl_label.grid(row = 2, column = 0, padx = 5)
    line2_center_label.grid(row = 3, column = 0, padx = 5)
    line2_center_spinbox.grid(row = 3, column = 1, padx = 2 )
    
    apply_line_button.grid(row = 1, column = 0, padx = 10)
    export_line_button.grid(row = 1, column = 1, padx = 10)
