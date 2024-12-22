import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.signal import butter, filtfilt  # Импортируем функции для фильтрации

mpl.rcParams['font.size'] = 20
mpl.rcParams['axes.titlesize'] = 20
mpl.rcParams['axes.labelsize'] = 20

class SpectrumAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Спектральный Анализатор")
        self.root.geometry("800x480")

        control_frame = tk.Frame(root)
        control_frame.pack(pady=20)

        self.file_path = tk.StringVar()

        # Первая строка: выбор файла
        browse_button = tk.Button(control_frame, text="Выбрать CSV файл", command=self.browse_file, width=20)
        browse_button.grid(row=0, column=0, padx=10)

        self.file_entry = tk.Entry(control_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=1, padx=10)

        # Вторая строка: управление сигналами
        waveform_label = tk.Label(control_frame, text="Выберите канал для сигналов")
        waveform_label.grid(row=1, column=0, padx=10)

        self.waveform_channel = tk.StringVar()
        channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.waveform_channel_combobox = ttk.Combobox(control_frame, textvariable=self.waveform_channel, values=channels, width=5)
        self.waveform_channel_combobox.current(0)  # Устанавливаем значение по умолчанию
        self.waveform_channel_combobox.grid(row=1, column=1, padx=10)

        plot_waveform_button = tk.Button(control_frame, text="Построить сигналы", command=self.plot_waveform, width=20)
        plot_waveform_button.grid(row=5, column=0, padx=10, pady=20)

        # Опции для фильтрации сигнала
        self.filter_waveform_var = tk.BooleanVar()
        filter_waveform_check = tk.Checkbutton(control_frame, text="Фильтровать сигнал", variable=self.filter_waveform_var)
        filter_waveform_check.grid(row=5, column=1, padx=10, pady=20)

        waveform_cutoff_label = tk.Label(control_frame, text="Срез частоты (МГц)")
        waveform_cutoff_label.grid(row=5, column=2, padx=10, pady=20)
        self.waveform_cutoff_entry = tk.Entry(control_frame, width=10)
        self.waveform_cutoff_entry.grid(row=5, column=3, padx=10)
        self.waveform_cutoff_entry.insert(0, '10')  # Значение по умолчанию

        # Третья строка: управление спектром
        spectrum_label = tk.Label(control_frame, text="Выберите канал для спектра")
        spectrum_label.grid(row=2, column=0, padx=10)

        self.spectrum_channel = tk.StringVar()
        self.spectrum_channel_combobox = ttk.Combobox(control_frame, textvariable=self.spectrum_channel, values=channels, width=5)
        self.spectrum_channel_combobox.current(0)
        self.spectrum_channel_combobox.grid(row=2, column=1, padx=10)

        plot_spectrum_button = tk.Button(control_frame, text="Построить спектр", command=self.plot_spectrum, width=20)
        plot_spectrum_button.grid(row=6, column=0, padx=10)

        # Опции для фильтрации спектра
        self.filter_spectrum_var = tk.BooleanVar()
        filter_spectrum_check = tk.Checkbutton(control_frame, text="Фильтровать спектр", variable=self.filter_spectrum_var)
        filter_spectrum_check.grid(row=6, column=1, padx=10, pady=0)

        spectrum_cutoff_label = tk.Label(control_frame, text="Срез частоты (МГц)")
        spectrum_cutoff_label.grid(row=6, column=2, padx=10, pady=0)
        self.spectrum_cutoff_entry = tk.Entry(control_frame, width=10)
        self.spectrum_cutoff_entry.grid(row=6, column=3, padx=10, pady = 0)
        self.spectrum_cutoff_entry.insert(0, '10')  # Значение по умолчанию

        # Центральная частота
        central_freq_label = tk.Label(control_frame, text="Центральная частота (МГц)")
        central_freq_label.grid(row=3, column=0, padx=10)
        self.central_freq_entry = tk.Entry(control_frame, width=10)
        self.central_freq_entry.grid(row=3, column=1, padx=10)
        self.central_freq_entry.insert(0, '0')  # Значение по умолчанию

        # Ширина полосы частот
        freq_bandwidth_label = tk.Label(control_frame, text="Ширина полосы (МГц)")
        freq_bandwidth_label.grid(row=4, column=0, padx=10)
        self.freq_bandwidth_entry = tk.Entry(control_frame, width=10)
        self.freq_bandwidth_entry.grid(row=4, column=1, padx=10)
        self.freq_bandwidth_entry.insert(0, '1')  # Значение по умолчанию

    def browse_file(self):
        filetypes = (
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title='Открыть файл', initialdir='/', filetypes=filetypes)
        if filename:
            self.file_path.set(filename)

    def butter_lowpass_filter(self, data, cutoff_freq, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff_freq / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y

    def plot_waveform(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите CSV файл.")
            return

        try:
            print(f"Загрузка файла: {file_path}")
            data = pd.read_csv(file_path, header=None)
            print("Файл успешно загружен.")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл {file_path} не найден.")
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")
            return

        data = data.apply(pd.to_numeric, errors='coerce')

        if data.isnull().values.any():
            messagebox.showwarning("Предупреждение", "Обнаружены отсутствующие или нечисловые значения. Они будут заполнены нулями.")
            data = data.fillna(0)

        num_points = data.shape[0]
        num_columns = data.shape[1]
        print(f"Количество точек: {num_points}, количество столбцов: {num_columns}")

        time_step = 13e-9
        fs = 1 / time_step  # Частота дискретизации
        time = np.arange(0, num_points * time_step, time_step)
        if len(time) > num_points:
            time = time[:num_points]

        selected_channel = self.waveform_channel.get()
        channel_index = ord(selected_channel.upper()) - ord('A')
        if channel_index < 0 or channel_index >= num_columns:
            messagebox.showerror("Ошибка", f"Выбранный канал {selected_channel} недоступен.")
            return

        signal = data.iloc[:, channel_index].values

        if not np.issubdtype(signal.dtype, np.number):
            messagebox.showerror("Ошибка", f"Канал {selected_channel} содержит нечисловые данные.")
            return

        if np.isnan(signal).any() or np.isinf(signal).any():
            print(f"Канал {selected_channel} содержит некорректные значения. Замена на нули.")
            signal = np.nan_to_num(signal)

        # Применение фильтра, если включено
        if self.filter_waveform_var.get():
            try:
                cutoff_freq = float(self.waveform_cutoff_entry.get()) * 1e6  # Преобразуем в Гц
                print(f"Применение фильтра низких частот с частотой среза {cutoff_freq} Гц")
                signal = self.butter_lowpass_filter(signal, cutoff_freq, fs)
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите числовое значение для частоты среза фильтра.")
                return

        fig = plt.Figure(figsize=(10, 7))
        ax = fig.add_subplot(111)
        ax.plot(time, signal)
        ax.set_title(f'Сигнал канала {selected_channel}', fontsize=20)
        ax.set_xlabel('Время (сек)', fontsize=20)
        ax.set_ylabel('Амплитуда', fontsize=20)
        ax.grid(True)

        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"Сигнал канала {selected_channel}")
        plot_window.geometry("1200x800")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, plot_window)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_spectrum(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите CSV файл.")
            return

        try:
            central_freq = float(self.central_freq_entry.get())
            freq_bandwidth = float(self.freq_bandwidth_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числовые значения для центральной частоты и ширины полосы.")
            return

        try:
            print(f"Загрузка файла: {file_path}")
            data = pd.read_csv(file_path, header=None)
            print("Файл успешно загружен.")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл {file_path} не найден.")
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")
            return

        data = data.apply(pd.to_numeric, errors='coerce')

        if data.isnull().values.any():
            messagebox.showwarning("Предупреждение", "Обнаружены отсутствующие или нечисловые значения. Они будут заполнены нулями.")
            data = data.fillna(0)

        num_points = data.shape[0]
        num_columns = data.shape[1]
        print(f"Количество точек: {num_points}, количество столбцов: {num_columns}")

        time_step = 13e-9
        fs = 1 / time_step  # Частота дискретизации
        time = np.arange(0, num_points * time_step, time_step)
        if len(time) > num_points:
            time = time[:num_points]

        selected_channel = self.spectrum_channel.get()
        channel_index = ord(selected_channel.upper()) - ord('A')
        if channel_index < 0 or channel_index >= num_columns:
            messagebox.showerror("Ошибка", f"Выбранный канал {selected_channel} недоступен.")
            return

        signal = data.iloc[:, channel_index].values

        if not np.issubdtype(signal.dtype, np.number):
            messagebox.showerror("Ошибка", f"Канал {selected_channel} содержит нечисловые данные.")
            return

        if np.isnan(signal).any() or np.isinf(signal).any():
            print(f"Канал {selected_channel} содержит некорректные значения. Замена на нули.")
            signal = np.nan_to_num(signal)

        # Применение фильтра, если включено
        if self.filter_spectrum_var.get():
            try:
                cutoff_freq = float(self.spectrum_cutoff_entry.get()) * 1e6  # Преобразуем в Гц
                print(f"Применение фильтра низких частот с частотой среза {cutoff_freq} Гц")
                signal = self.butter_lowpass_filter(signal, cutoff_freq, fs)
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите числовое значение для частоты среза фильтра.")
                return

        try:
            spectrum = np.fft.fft(signal)
            freq = np.fft.fftfreq(len(signal), d=time_step)
            amplitude = np.abs(spectrum)
            amplitude_normalized = (amplitude / np.max(amplitude))  # Нормализация амплитуды

            print(f"Построение спектра для канала {selected_channel}")

            pos_mask = freq >= 0
            freq = freq[pos_mask]
            amplitude_normalized = amplitude_normalized[pos_mask]
            freq_mhz = freq / 1e6

            fig = plt.Figure(figsize=(10, 7))
            ax = fig.add_subplot(111)
            ax.plot(freq_mhz, amplitude_normalized, label='Амплитуда спектра')

            # Выделение области вокруг центральной частоты
            lower_freq = central_freq - freq_bandwidth / 2
            upper_freq = central_freq + freq_bandwidth / 2

            lower_freq = max(lower_freq, freq_mhz.min())
            upper_freq = min(upper_freq, freq_mhz.max())

            ax.axvspan(lower_freq, upper_freq, color='yellow', alpha=0.3, label='Выделенная область')

            ax.annotate(f'{lower_freq:.2f} МГц',
                        xy=(lower_freq, ax.get_ylim()[1]*0.9),
                        xytext=(lower_freq, ax.get_ylim()[1]*0.85),
                        arrowprops=dict(facecolor='black', shrink=0.05),
                        ha='center',
                        fontsize=16)

            ax.annotate(f'{upper_freq:.2f} МГц',
                        xy=(upper_freq, ax.get_ylim()[1]*0.9),
                        xytext=(upper_freq, ax.get_ylim()[1]*0.90),
                        arrowprops=dict(facecolor='black', shrink=0.05),
                        ha='center',
                        fontsize=16)

            # Поиск максимальной амплитуды в выделенной области
            selected_indices = np.where((freq_mhz >= lower_freq) & (freq_mhz <= upper_freq))[0]
            if selected_indices.size > 0:
                max_idx = selected_indices[np.argmax(amplitude_normalized[selected_indices])]
                max_freq = freq_mhz[max_idx]
                max_amp = amplitude_normalized[max_idx]
                ax.plot(max_freq, max_amp, 'ro')  # Красная точка
                ax.annotate(f'Максимум\n{max_freq:.2f} МГц',
                            xy=(max_freq, max_amp),
                            xytext=(max_freq, max_amp + ax.get_ylim()[1]*0.05),
                            arrowprops=dict(facecolor='red', shrink=0.05),
                            ha='center',
                            fontsize=16)

            ax.set_title(f'Спектр канала {selected_channel}', fontsize=20)
            ax.set_xlabel('Частота (МГц)', fontsize=20)
            ax.set_ylabel('Нормированная Амплитуда', fontsize=20)
            ax.grid(True)
            ax.legend(fontsize=16)

            plot_window = tk.Toplevel(self.root)
            plot_window.title(f"Спектр канала {selected_channel}")
            plot_window.geometry("1200x1080")

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, plot_window)
            toolbar.update()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении спектра для канала {selected_channel}: {e}")
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectrumAnalyzerGUI(root)
    root.mainloop()
