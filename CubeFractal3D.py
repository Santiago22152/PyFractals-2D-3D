import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class FractalCubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Cubos Fractales 3D")
        
        # Variables de control
        self.max_depth = tk.IntVar(value=3)
        self.draw_diagonals = tk.BooleanVar(value=True)
        self.draw_edges = tk.BooleanVar(value=True)
        self.draw_faces = tk.BooleanVar(value=False)
        self.color_mode = tk.StringVar(value="Niveles")
        
        # Configurar la interfaz
        self.create_widgets()
        
        # Configurar el cierre adecuado
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def draw_cube(self, ax, origin, size, depth, max_depth, draw_diagonals=True, draw_edges=True, draw_faces=False, color='b'):
        """Recursively draw fractal cubes with multiple visualization options"""
        if depth > max_depth:
            return
        
        x, y, z = origin
        s = size
        
        # Define los 8 vértices del cubo
        vertices = np.array([
            [x, y, z],
            [x+s, y, z],
            [x+s, y+s, z],
            [x, y+s, z],
            [x, y, z+s],
            [x+s, y, z+s],
            [x+s, y+s, z+s],
            [x, y+s, z+s]
        ])
        
        # Dibuja las aristas del cubo
        if draw_edges:
            edges = [
                [vertices[0], vertices[1]],
                [vertices[1], vertices[2]],
                [vertices[2], vertices[3]],
                [vertices[3], vertices[0]],
                [vertices[4], vertices[5]],
                [vertices[5], vertices[6]],
                [vertices[6], vertices[7]],
                [vertices[7], vertices[4]],
                [vertices[0], vertices[4]],
                [vertices[1], vertices[5]],
                [vertices[2], vertices[6]],
                [vertices[3], vertices[7]]
            ]
            
            for edge in edges:
                ax.plot3D(*zip(*edge), color=color, linewidth=0.5)
        
        # Dibuja las diagonales principales
        if draw_diagonals:
            # Diagonal principal (vértice 0 a vértice 6)
            ax.plot([x, x+s], [y, y+s], [z, z+s], color=color, linewidth=1)
            # Diagonal secundaria (vértice 1 a vértice 7)
            ax.plot([x+s, x], [y, y+s], [z, z+s], color=color, linewidth=1)
        
        # Dibuja las caras del cubo (opcional)
        if draw_faces:
            faces = [
                [vertices[0], vertices[1], vertices[2], vertices[3]],  # abajo
                [vertices[4], vertices[5], vertices[6], vertices[7]],  # arriba
                [vertices[0], vertices[1], vertices[5], vertices[4]],  # frente
                [vertices[2], vertices[3], vertices[7], vertices[6]],  # atrás
                [vertices[1], vertices[2], vertices[6], vertices[5]],  # derecha
                [vertices[0], vertices[3], vertices[7], vertices[4]]   # izquierda
            ]
            
            ax.add_collection3d(Poly3DCollection(faces, 
                                               facecolors='cyan', 
                                               linewidths=0.5, 
                                               edgecolors='blue', 
                                               alpha=0.1))
        
        # Divide en 8 subcubos y aplica recursión
        if depth < max_depth:
            new_size = size / 2
            for i in [0, 1]:
                for j in [0, 1]:
                    for k in [0, 1]:
                        new_origin = (x + i*new_size, y + j*new_size, z + k*new_size)
                        # Cambia el color para niveles más profundos
                        if self.color_mode.get() == "Niveles":
                            new_color = (color if depth < 2 else ['red', 'green', 'purple'][depth % 3])
                        elif self.color_mode.get() == "Aleatorio":
                            new_color = np.random.choice(['red', 'green', 'blue', 'purple', 'orange'])
                        else:
                            new_color = color
                            
                        self.draw_cube(ax, new_origin, new_size, depth+1, max_depth, 
                                     draw_diagonals, draw_edges, draw_faces, new_color)

    def create_widgets(self):
        # Frame de controles
        control_frame = ttk.LabelFrame(self.root, text="Configuración", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Controles de profundidad
        ttk.Label(control_frame, text="Niveles de recursión:").grid(row=0, column=0, sticky=tk.W)
        ttk.Scale(control_frame, from_=1, to=6, variable=self.max_depth, 
                 orient=tk.HORIZONTAL, command=lambda _: self.update_slider_label()).grid(row=0, column=1)
        self.depth_label = ttk.Label(control_frame, text=f"Nivel: {self.max_depth.get()}")
        self.depth_label.grid(row=0, column=2, padx=5)
        
        # Opciones de visualización
        ttk.Checkbutton(control_frame, text="Mostrar diagonales", variable=self.draw_diagonals).grid(row=1, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(control_frame, text="Mostrar aristas", variable=self.draw_edges).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        ttk.Checkbutton(control_frame, text="Mostrar caras", variable=self.draw_faces).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        
        # Selector de modo de color
        ttk.Label(control_frame, text="Esquema de colores:").grid(row=4, column=0, sticky=tk.W)
        ttk.Combobox(control_frame, textvariable=self.color_mode, 
                     values=["Niveles", "Único", "Aleatorio"], state="readonly").grid(row=4, column=1)
        
        # Botones
        ttk.Button(control_frame, text="Generar", command=self.generate_fractal).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(control_frame, text="Rotar Automático", command=self.toggle_rotation).grid(row=6, column=0, columnspan=2)
        
        # Frame de visualización
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Barra de herramientas de matplotlib
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Estado de rotación automática
        self.rotating = False
        self.rotation_id = None
    
    def update_slider_label(self):
        self.depth_label.config(text=f"Nivel: {self.max_depth.get()}")
    
    def generate_fractal(self):
        self.ax.clear()
        
        # Configurar color inicial según el modo seleccionado
        if self.color_mode.get() == "Único":
            color = 'blue'
        elif self.color_mode.get() == "Aleatorio":
            color = np.random.choice(['red', 'green', 'blue', 'purple', 'orange'])
        else:
            color = 'b'  # Para modo "Niveles"
        
        # Llamar a la función de generación de fractales
        self.draw_cube(
            self.ax, 
            origin=(0, 0, 0), 
            size=10, 
            depth=0, 
            max_depth=self.max_depth.get(),
            draw_diagonals=self.draw_diagonals.get(),
            draw_edges=self.draw_edges.get(),
            draw_faces=self.draw_faces.get(),
            color=color
        )
        
        # Configuración del gráfico
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title(f'Cubo Fractal 3D (Niveles: {self.max_depth.get()})')
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_zlim(0, 10)
        self.ax.view_init(elev=30, azim=45)
        
        self.canvas.draw()
    
    def toggle_rotation(self):
        if self.rotating:
            self.stop_rotation()
        else:
            self.start_rotation()
    
    def start_rotation(self):
        if not self.rotating:
            self.rotating = True
            self.rotate_cube()
    
    def stop_rotation(self):
        if self.rotating:
            self.root.after_cancel(self.rotation_id)
            self.rotating = False
    
    def rotate_cube(self):
        self.ax.view_init(elev=30, azim=self.ax.azim + 1)
        self.canvas.draw()
        self.rotation_id = self.root.after(50, self.rotate_cube)
    
    def on_close(self):
        self.stop_rotation()
        plt.close('all')
        self.root.destroy()

def run_app():
    root = tk.Tk()
    app = FractalCubeApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()