import numpy as np

class ESR_Spectr: # класс для чтения исходников, вывода на экран и обработки спектра
    """
    ESR_Spectr data with Field, Intensity and Gain
    Include methods Open and Extract
    """
    def __init__(self):
        # внешние атрибуты
        self.file_sp = ''
        self.field = []
        self.intensity = []
        
        self.h_pp = [] # массив с полями пиков
        self.int_pp = [] # массив с интенсивностью пиков
        self.begin_norm = 0.0 # начало и конец области нормализации
        self.end_norm = 0.0 
        
        # внутренние атрибуты
        self.__gain = 1.0
        self.__n_modes = []
        self.__h_res = []
        self.__dh_res = []   
        self.__int_res = []
    
    
    def open_spectr(self, file_spectra): # открываем двоичный файл со спектром
        self.file_sp, = file_spectra
        extension = self.file_sp.split('.')[-1]
        if extension == 'spe':
            A = np.memmap(file_spectra[0], np.uint16, 'r')
        
            a = A[4106:4136:5]

            b = A[4107:4137:5].astype('float32') - 16398

            param = a * np.power(2, b)

            central_field = param[0]
            spread_field = param[1]
            power_attenuation = param[3]
            modulation_amplitude = param[2]
            gain_value = param[4]
            gain_order = param[5]
            
            self.field = np.arange(central_field - spread_field / 2, central_field + spread_field / 2, spread_field / 4095)
            self.__gain = (gain_value * np.power(10, gain_order)) * np.power(10, - power_attenuation/20) * modulation_amplitude
            self.intensity = (A[5:4100].astype('float32') - 16380) / self.__gain
            
        elif extension == 'txt' or 'dat':
            data = np.genfromtxt(file_spectra[0], skip_header = 1).reshape(8190, order ='F')
            
            self.field = data[:4095].reshape(4095)
            self.intensity = data[4095:].reshape(4095)
        self.begin_norm = min(self.field)
        self.end_norm = max(self.field)
    
    def get_gain(self):
        return self.__gain
    
    def refresh_parameters(self): # обновляем параметры спектра
        if len(self.h_pp) > 0 and len(self.h_pp) % 2 == 0: # проверка на четность пиков при добавлении пика и расчет резонансных характеристик линии
            self.__n_modes.append(len(self.h_pp) // 2 - 1)
            self.__h_res.append((self.h_pp[-1] + self.h_pp[-2]) / 2)
            self.__dh_res.append(np.sqrt(3)*np.abs(self.h_pp[-1] - self.h_pp[-2]))
            self.__int_res.append(2 / 3 * np.abs(self.int_pp[-1] - self.int_pp[-2]) * np.abs(self.h_pp[-1] - self.h_pp[-2]))
        elif len(self.h_pp) // 2 < len(self.__h_res): # удаляем параметры резонансной линии с конца списка при удалении пика на графике
            del self.__n_modes[-1]
            del self.__h_res[-1]
            del self.__dh_res[-1]
            del self.__int_res[-1]
    
    
    def export(self): # экспорт спектра в data-файл
        ex_data = '   H, Oe         I \n'
        for i in range(len(self.field)):
            ex_data += f'{self.field[i]:.6f}    {self.intensity[i]:.6f} \n'
        
        with open(self.file_sp.split('/')[-1].split('.')[0] + '_спектр.dat', 'w', encoding = 'utf8') as export_file:
                print(ex_data, file = export_file)


    def export_parameters(self):  # экспорт параметров резонансных линий в data-файл
        param_data = ' n   H, Oe       g     dH, Oe     I_n       I_n/I_0\n'
        for i in range(self.__n_modes[-1] + 1):
            param_data += f'{self.__n_modes[i]:2d}   {self.__h_res[i]:.3f}  {1069.795 / self.__h_res[i]:.3f}   {self.__dh_res[i]:.3f}    {self.__int_res[i]:.3e}     {self.__int_res[i] / self.__int_res[0]:.3f}\n'
            
        with open(self.file_sp.split('/')[-1].split('.')[0] + '_парметры.dat', 'w', encoding = 'utf8') as export_file:
                print(param_data, file = export_file)    


class ESR_Normal_Spectr: # класс для нормализации спектра и апросимации его лоренцевыми линиями
    """
    Normalize ESR_Spectr data with Field, Intensity amd Gain
    include method of export parameters
    """
    def __init__(self):
        self.field = []
        self.intens = []
        self.center_field = 3300.0
        self.koef_normalize = 1.0
    
    def normalize(self, spectr): # определяем вид нормализованного спектра
        del self.field[:] # чистим массивы на всякий случай
        del self.intens[:]
        # ~ if hmin > hmax:
            # ~ hmin, hmax = hmax, hmin
        for i in range(len(spectr.field)): # определяем границы нормализации
            if spectr.field[i] >= spectr.begin_norm and spectr.field[i] <= spectr.end_norm:
                self.field.append(spectr.field[i])
                self.intens.append(spectr.intensity[i])
        self.center_field = (self.field[0] + self.field[-1]) / 2
        self.koef_normalize = (max(self.intens) - min(self.intens)) / 2
        
        min_int = min(self.intens)
        for i in range(len(self.field)): # нормализуем спектр
            self.field[i] = self.field[i] / self.center_field - 1
            self.intens[i] = (self.intens[i] - min_int) / self.koef_normalize - 1
        
# класс, определяющий лоренцеву линию и операции над ней
class Lorenz_Line:
    """
    Form of Lorenz line and it derivative
    """
    
    def __init__(self):
        self.int_deriv = 0.50
        self.x_pp = 0.002
        self.center = 0.0
        self.y = np.array([])
    
    def recalc(self):
        self.__ampl = 4 /3 * self.int_deriv * self.x_pp 
        self.__b = 4 / (3 * np.power(self.x_pp, 2) )
    
    def line_derivative(self, x):
        self.y = np.empty(len(x)) # чистим массив на всякий случай
        self.recalc() # пересчитываем коэффициенты
        for i in range(len(x)):
            self.y[i] = 2 * self.__ampl * self.__b * (x[i] - self.center) / np.power(1 + self.__b * np.power(x[i] - self.center, 2), 2)
            # ~ self.y.append(2 * self.__ampl * self.__b * (x[i] - self.center) / np.power(1 + self.__b * np.power(x[i] - self.center, 2), 2))
        # ~ return self.y
    
    def get_parameters(self, norm_sp):
        # ~ param_data = f' H_0, Oe      Im     2DH, Oe\n '
        dHpp = self.x_pp * norm_sp.center_field
        dH = dHpp * np.power(3, 1/2)
        H0 = (self.center + 1) * norm_sp.center_field
        Ipp = 2 * self.int_deriv * norm_sp.koef_normalize
        Im = 2/3 * Ipp * dHpp
        return (H0, dHpp, Ipp, dH, Im)
    
