import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re


class BoxPlotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SBS-Box-Plot-Generator")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")

        self.data_entry = ctk.CTkEntry(self, placeholder_text="Enter data list: e.g., boxplot(salary=[10,20,30,40], age=[15,25,35,45])")
        self.data_entry.pack(pady=10, fill='x', padx=20)

        self.x_label_entry = ctk.CTkEntry(self, placeholder_text="Enter X-axis label")
        self.x_label_entry.pack(pady=5, fill='x', padx=20)

        self.y_label_entry = ctk.CTkEntry(self, placeholder_text="Enter Y-axis label")
        self.y_label_entry.pack(pady=5, fill='x', padx=20)

        self.plot_button = ctk.CTkButton(self, text="Generate Plot", command=self.generate_plot)
        self.plot_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self, text="Save Plot", command=self.save_plot)
        self.save_button.pack(pady=5)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.draggable_texts = []
        self.dragging_text = None
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def generate_plot(self):
        try:
            input_text = self.data_entry.get()
            matches = re.findall(r"(\w+)=\[(.*?)\]", input_text)
            data_dict = {name: list(map(float, values.split(','))) for name, values in matches}

            if all(isinstance(lst, list) and all(isinstance(i, (int, float)) for i in lst) for lst in data_dict.values()):
                self.ax.clear()
                num_datasets = len(data_dict)
                widths = max(0.5, 0.8 - (0.1 * (num_datasets - 1)))
                self.ax.boxplot(list(data_dict.values()), vert=True, patch_artist=True, widths=widths)
                self.ax.set_xticks(range(1, num_datasets + 1))
                self.ax.set_xticklabels(data_dict.keys())
                self.ax.set_xlabel(self.x_label_entry.get())
                self.ax.set_ylabel(self.y_label_entry.get())
                self.ax.set_title("Vertical Box Plot")
                self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
                self.display_statistics(data_dict)
            else:
                raise ValueError("Invalid boxplot data format. Enter valid lists of numbers.")

            self.canvas.draw()
        except Exception as e:
            print(f"Error: {e}")

    def display_statistics(self, data_dict):
        self.draggable_texts.clear()
        y_offset = 0.02
        for name, data in data_dict.items():
            mean = round(np.mean(data), 2)
            std = round(np.std(data, ddof=1), 2)
            q1 = round(np.percentile(data, 25), 2)
            q3 = round(np.percentile(data, 75), 2)
            median = round(np.median(data), 2)
            min_val = round(min(data), 2)
            max_val = round(max(data), 2)
            iqr = round(q3 - q1, 2)
            data_range = round(max_val - min_val, 2)

            stats_text = (f"{name}\nMean: {mean}\nSTD: {std}\nQ1: {q1}\nQ3: {q3}\n"
                          f"Median: {median}\nMin: {min_val}\nMax: {max_val}\nIQR: {iqr}\nRange: {data_range}")

            text_obj = self.ax.text(0.5, y_offset, stats_text, transform=self.ax.transAxes, fontsize=10,
                                    verticalalignment='center', horizontalalignment='center',
                                    bbox=dict(facecolor='white', alpha=0.6), picker=True)
            self.draggable_texts.append((text_obj, 0.5, y_offset))
            y_offset += 0.12

    def save_plot(self):
        self.fig.savefig("boxplot_output.png", dpi=300)
        print("Plot saved as boxplot_output.png")

    def on_press(self, event):
        for text, x, y in self.draggable_texts:
            contains, _ = text.contains(event)
            if contains:
                self.dragging_text = (text, x, y)
                return

    def on_drag(self, event):
        if self.dragging_text and event.inaxes == self.ax:
            text, x, y = self.dragging_text
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            x_new = (event.xdata - x_min) / (x_max - x_min) if event.xdata else x
            y_new = (event.ydata - y_min) / (y_max - y_min) if event.ydata else y
            x_new = max(0, min(1, x_new))
            y_new = max(0, min(1, y_new))
            text.set_position((x_new, y_new))
            self.canvas.draw()

    def on_release(self, event):
        self.dragging_text = None


if __name__ == "__main__":
    app = BoxPlotGUI()
    app.mainloop()
