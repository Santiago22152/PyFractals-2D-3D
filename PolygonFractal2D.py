import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk
import matplotlib.cm as cm
import sys

class AnimatedFractalGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Fractales con Animación")

        # Configurar el protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Configuración de presets
        self.presets = {
            "Triángulo de Sierpinski": {"sides": 3, "depth": 5, "scale": 0.5, "algorithm": "sierpinski"},
            "Alfombra de Sierpinski": {"sides": 4, "depth": 4, "scale": 0.33, "algorithm": "carpet"},
            "Pentágono Fractal": {"sides": 5, "depth": 3, "scale": 0.38, "algorithm": "regular"},
            "Hexágono Fractal": {"sides": 6, "depth": 3, "scale": 0.35, "algorithm": "regular"},
            "Personalizado": {"sides": 4, "depth": 3, "scale": 0.5, "algorithm": "regular"}
        }

        self.is_running = True
        self.animation_running = False
        self.ani = None
        self.create_widgets()
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.is_running = False
        self.stop_animation()

        if hasattr(self, "fig"):
            plt.close(self.fig)
        
        self.root.destroy()

        sys.exit(0)

    def stop_animation(self):
        """Detiene la animacion de manera segura"""
        if hasattr(self, "ani") and self.ani:
            try:
                self.ani.event_source.stop()
            except:
                pass
            self.animation_running = False
    
    def create_widgets(self):
        # Frame de controles
        control_frame = ttk.LabelFrame(self.root, text="Configuración", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Selector de preset
        ttk.Label(control_frame, text="Tipo de fractal:").grid(row=0, column=0, sticky=tk.W)
        self.preset_var = tk.StringVar(value="Triángulo de Sierpinski")
        self.preset_menu = ttk.Combobox(control_frame, textvariable=self.preset_var, 
                                      values=list(self.presets.keys()), state="readonly")
        self.preset_menu.grid(row=0, column=1, pady=5)
        self.preset_menu.bind("<<ComboboxSelected>>", self.update_controls)
        
        # Controles para parámetros
        ttk.Label(control_frame, text="Lados:").grid(row=1, column=0, sticky=tk.W)
        self.sides_var = tk.IntVar(value=3)
        self.sides_spin = ttk.Spinbox(control_frame, from_=3, to=8, textvariable=self.sides_var)
        self.sides_spin.grid(row=1, column=1, pady=5)
        
        ttk.Label(control_frame, text="Profundidad:").grid(row=2, column=0, sticky=tk.W)
        self.depth_var = tk.IntVar(value=5)
        self.depth_spin = ttk.Spinbox(control_frame, from_=1, to=7, textvariable=self.depth_var)
        self.depth_spin.grid(row=2, column=1, pady=5)
        
        ttk.Label(control_frame, text="Escala:").grid(row=3, column=0, sticky=tk.W)
        self.scale_var = tk.DoubleVar(value=0.5)
        self.scale_spin = ttk.Spinbox(control_frame, from_=0.1, to=0.9, increment=0.05, 
                                    textvariable=self.scale_var)
        self.scale_spin.grid(row=3, column=1, pady=5)
        
        # Selector de algoritmo
        ttk.Label(control_frame, text="Algoritmo:").grid(row=4, column=0, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="sierpinski")
        self.algorithm_menu = ttk.Combobox(control_frame, textvariable=self.algorithm_var,
                                         values=["sierpinski", "carpet", "regular"], state="readonly")
        self.algorithm_menu.grid(row=4, column=1, pady=5)
        
        # Opción de animación
        self.animate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Mostrar animación", variable=self.animate_var).grid(row=5, column=0, columnspan=2, pady=5)
        
        # Velocidad de animación
        ttk.Label(control_frame, text="Velocidad (ms):").grid(row=6, column=0, sticky=tk.W)
        self.speed_var = tk.IntVar(value=200)
        self.speed_spin = ttk.Spinbox(control_frame, from_=50, to=1000, increment=50, 
                                    textvariable=self.speed_var)
        self.speed_spin.grid(row=6, column=1, pady=5)
        
        # Botones
        generate_btn = ttk.Button(control_frame, text="Generar Fractal", command=self.generate_fractal)
        generate_btn.grid(row=7, column=0, columnspan=2, pady=5)
        
        stop_btn = ttk.Button(control_frame, text="Detener Animación", command=self.stop_animation)
        stop_btn.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Frame de visualización
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.update_controls()
    
    def update_controls(self, event=None):
        preset_name = self.preset_var.get()
        if preset_name != "Personalizado":
            preset = self.presets[preset_name]
            self.sides_var.set(preset["sides"])
            self.depth_var.set(preset["depth"])
            self.scale_var.set(preset["scale"])
            self.algorithm_var.set(preset["algorithm"])
    
    def stop_animation(self):
        if self.ani:
            self.ani.event_source.stop()
            self.animation_running = False
    
    def generate_fractal(self):
        self.stop_animation()
        self.ax.clear()
        
        sides = self.sides_var.get()
        depth = self.depth_var.get()
        scale = self.scale_var.get()
        algorithm = self.algorithm_var.get()
        animate = self.animate_var.get()
        speed = self.speed_var.get()
        
        # Almacenar todos los elementos a dibujar
        self.all_elements = []
        
        # Generar elementos según el algoritmo
        if algorithm == "sierpinski" and sides == 3:
            self.prepare_sierpinski(depth)
        elif algorithm == "carpet" and sides == 4:
            self.prepare_carpet(depth)
        else:
            self.prepare_regular_fractal(sides, depth, scale)
        
        if animate:
            self.setup_animation(sides, depth, algorithm, speed)
        else:
            self.draw_all_elements()
            self.ax.set_title(f"Fractal {sides}-gonal\nProfundidad: {depth} - Algoritmo: {algorithm}")
            self.canvas.draw()
    
    def draw_all_elements(self):
        """Dibuja todos los elementos de una vez"""
        for element in self.all_elements:
            vertices, depth, color = element
            closed = np.vstack([vertices, vertices[0]])
            self.ax.plot(closed[:, 0], closed[:, 1], color=color, lw=1.5)
    
    def setup_animation(self, sides, depth, algorithm, speed):
        """Configura la animación paso a paso"""
        self.current_sides = sides
        self.current_depth = depth
        self.current_algorithm = algorithm

        
        def init():
            self.ax.clear()
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            self.ax.set_title(f"Fractal {self.current_sides}-gonal\nProfundidad: {self.current_depth} - Algoritmo: {self.current_algorithm}")
            return []
        
        def update(frame):
            self.ax.clear()
            self.ax.set_aspect('equal')
            self.ax.axis('off')
            self.ax.set_title(f"Fractal {self.current_sides}-gonal\nProfundidad: {self.current_depth} - Algoritmo: {self.current_algorithm}")
            
            # Dibujar todos los elementos hasta el frame actual
            for i in range(min(frame+1, len(self.all_elements))):
                vertices, depth, color = self.all_elements[i]
                closed = np.vstack([vertices, vertices[0]])
                self.ax.plot(closed[:, 0], closed[:, 1], color=color, lw=1.5)
            
            # Mostrar progreso
            progress = min(100, (frame+1)/len(self.all_elements)*100)
            self.ax.text(0.02, 0.95, f"Progreso: {progress:.1f}%", 
                        transform=self.ax.transAxes, fontsize=10)
            
            return []
        
        self.ani = FuncAnimation(
            self.fig, 
            update, 
            frames=len(self.all_elements),
            init_func=init,
            interval=speed,
            repeat=False,
            blit=False
        )
        self.canvas.draw()
        self.animation_running = True
    
    def prepare_sierpinski(self, depth):
        """Prepara los elementos para el triángulo de Sierpinski"""
        colors = cm.plasma(np.linspace(0, 1, depth+1))
        
        def sierpinski(vertices, current_depth):
            self.all_elements.append((vertices.copy(), current_depth, colors[current_depth]))
            
            if current_depth >= depth:
                return
                
            v1, v2, v3 = vertices
            mid1 = (v1 + v2) / 2
            mid2 = (v2 + v3) / 2
            mid3 = (v3 + v1) / 2
            
            sierpinski(np.array([v1, mid1, mid3]), current_depth+1)
            sierpinski(np.array([mid1, v2, mid2]), current_depth+1)
            sierpinski(np.array([mid3, mid2, v3]), current_depth+1)
        
        initial = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]]) * 8 - np.array([4, 2.5])
        sierpinski(initial, 0)
    
    def prepare_carpet(self, depth):
        """Prepara los elementos para la alfombra de Sierpinski"""
        colors = cm.viridis(np.linspace(0, 1, depth+1))
        
        def carpet(x, y, size, current_depth):
            square = np.array([[x, y], [x+size, y], [x+size, y+size], [x, y+size]])
            self.all_elements.append((square.copy(), current_depth, colors[current_depth]))
            
            if current_depth >= depth:
                return
                
            new_size = size / 3
            for i in range(3):
                for j in range(3):
                    if i == 1 and j == 1:
                        continue
                    carpet(x + i*new_size, y + j*new_size, new_size, current_depth+1)
        
        carpet(-4, -4, 8, 0)
    
    def prepare_regular_fractal(self, sides, depth, scale):
        """Prepara elementos para fractales regulares"""
        colors = cm.inferno(np.linspace(0, 1, depth+1))
        
        def generate_polygon(center, radius, rotation=0):
            angles = np.linspace(0, 2*np.pi, sides, endpoint=False) + rotation
            x = center[0] + radius * np.cos(angles)
            y = center[1] + radius * np.sin(angles)
            return np.column_stack([x, y])
        
        def recursive_fractal(vertices, current_depth):
            self.all_elements.append((vertices.copy(), current_depth, colors[current_depth]))
            
            if current_depth >= depth:
                return
                
            center = np.mean(vertices, axis=0)
            new_radius = np.linalg.norm(vertices[0] - center) * scale
            
            for i in range(sides):
                next_i = (i + 1) % sides
                new_center = center + (vertices[i] - center) * (1 - scale)
                new_vertices = generate_polygon(new_center, new_radius)
                recursive_fractal(new_vertices, current_depth+1)
        
        initial = generate_polygon((0, 0), 4)
        recursive_fractal(initial, 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimatedFractalGeneratorApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_close()