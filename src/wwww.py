import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Функция для производной лоренцовой линии
def lorentzian_derivative(x, x0, gamma, amplitude):
    return amplitude * (2 * gamma * (x - x0)) / ((x - x0)**2 + gamma**2)**2

# Функция для производной двух наложенных лоренцовых линий
def double_lorentzian_derivative(x, x0_1, gamma_1, amplitude_1, x0_2, gamma_2, amplitude_2):
    return lorentzian_derivative(x, x0_1, gamma_1, amplitude_1) + lorentzian_derivative(x, x0_2, gamma_2, amplitude_2)

# Функция для чтения данных спектра из файла
def read_spectrum(file_path):
    # Читаем файл, удаляя BOM, если он есть
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        data = np.loadtxt(f)
    x = data[:, 0]
    y = data[:, 1]
    return x, y

# Функция для нормировки спектра в диапазоне от -1 до 1
def normalize_spectrum(y):
    y_min = np.min(y)
    y_max = np.max(y)
    return 2 * (y - y_min) / (y_max - y_min) - 1

# Функция для подбора параметров производных лоренцовых линий
def fit_lorentzian_derivatives(x, y):
    try:
        # Установим фиксированные начальные значения для диагностики
        initial_guess = [x[len(x)//4], 1, 1, x[3*len(x)//4], 1, 1]
        print(f"Initial guess: {initial_guess}")
        params, _ = curve_fit(double_lorentzian_derivative, x, y, p0=initial_guess)
        print(f"Fitted parameters: {params}")
        return params
    except Exception as e:
        print(f"Exception in fitting: {e}")
        raise RuntimeError("Automatic fitting failed")

# Функция для сохранения параметров производных лоренцовых линий в файл
def save_params(params, file_path):
    with open(file_path, 'w') as f:
        f.write(f'Lorentzian 1: x0 = {params[0]}, gamma = {params[1]}, amplitude = {params[2]}\n')
        f.write(f'Lorentzian 2: x0 = {params[3]}, gamma = {params[4]}, amplitude = {params[5]}\n')

# Функция для создания графического интерфейса
def create_gui():
    root = tk.Tk()
    root.title("EPR Spectrum Analyzer")
    
    def open_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                x, y = read_spectrum(file_path)
                
                # Проверка данных на NaN и бесконечности
                if np.any(np.isnan(x)) or np.any(np.isnan(y)) or np.any(np.isinf(x)) or np.any(np.isinf(y)):
                    raise ValueError("Data contains NaN or infinite values")
                
                y = normalize_spectrum(y)
                
                try:
                    params = fit_lorentzian_derivatives(x, y)
                    fitted = True
                except Exception as e:
                    print(f"Exception in fitting: {e}")
                    messagebox.showerror("Error", "Automatic fitting failed. Please enter parameters manually.")
                    params = [x[len(x)//4], 1, 1, x[3*len(x)//4], 1, 1]  # Начальные значения в случае сбоя подбора параметров
                    fitted = False
                
                fig, ax = plt.subplots()
                ax.plot(x, y, label='Normalized Spectrum')
                if fitted:
                    fitted_curve = double_lorentzian_derivative(x, *params)
                    ax.plot(x, fitted_curve, label='Fitted Lorentzian Derivatives')
                ax.legend()
                plt.show()
                
                def manual_input():
                    params[0] = simpledialog.askfloat("Input", "x0 (center) for Lorentzian 1", initialvalue=params[0])
                    params[1] = simpledialog.askfloat("Input", "gamma (width) for Lorentzian 1", initialvalue=params[1])
                    params[2] = simpledialog.askfloat("Input", "amplitude (height) for Lorentzian 1", initialvalue=params[2])
                    params[3] = simpledialog.askfloat("Input", "x0 (center) for Lorentzian 2", initialvalue=params[3])
                    params[4] = simpledialog.askfloat("Input", "gamma (width) for Lorentzian 2", initialvalue=params[4])
                    params[5] = simpledialog.askfloat("Input", "amplitude (height) for Lorentzian 2", initialvalue=params[5])
                    
                    fig, ax = plt.subplots()
                    ax.plot(x, y, label='Normalized Spectrum')
                    fitted_curve = double_lorentzian_derivative(x, *params)
                    ax.plot(x, fitted_curve, label='Manually Fitted Lorentzian Derivatives')
                    ax.legend()
                    plt.show()
                
                manual_button = tk.Button(root, text="Manual Input", command=manual_input)
                manual_button.pack()
                
                save_button = tk.Button(root, text="Save Parameters", command=lambda: save_params(params, 'lorentzian_params.txt'))
                save_button.pack()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading and fitting data: {e}")
    
    open_button = tk.Button(root, text="Open Spectrum File", command=open_file)
    open_button.pack()
    
    root.mainloop()

# Запуск программы
create_gui()
