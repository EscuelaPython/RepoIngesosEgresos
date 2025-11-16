import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class FinanzasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Ingresos y Egresos")
        self.root.geometry("900x600")
        
        # Conexión a la base de datos
        self.conn = sqlite3.connect('finanzas.db')
        self.crear_tablas()
        
        # Variables de control
        self.tipo_movimiento = tk.StringVar(value="ingreso")
        self.monto = tk.DoubleVar()
        self.categoria = tk.StringVar()
        self.descripcion = tk.StringVar()
        self.fecha = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        # Configurar el estilo
        self.configurar_estilo()
        
        # Crear widgets
        self.crear_widgets()
        
    def configurar_estilo(self):
        """Configura el estilo de los widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TEntry', font=('Arial', 10))
        style.configure('TCombobox', font=('Arial', 10))
        style.configure('TRadiobutton', background='#f0f0f0', font=('Arial', 10))
        
    def crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT,
                descripcion TEXT,
                fecha TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    def crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de entrada de datos
        input_frame = ttk.LabelFrame(main_frame, text="Nuevo Movimiento", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tipo de movimiento
        ttk.Label(input_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(input_frame, text="Ingreso", variable=self.tipo_movimiento, 
                       value="ingreso").grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(input_frame, text="Egreso", variable=self.tipo_movimiento, 
                       value="egreso").grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Monto
        ttk.Label(input_frame, text="Monto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.monto).grid(row=1, column=1, columnspan=2, 
                                                           sticky=tk.EW, padx=5)
        
        # Categoría
        ttk.Label(input_frame, text="Categoría:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.categoria_cb = ttk.Combobox(input_frame, textvariable=self.categoria)
        self.categoria_cb.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5)
        self.actualizar_categorias()
        
        # Descripción
        ttk.Label(input_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.descripcion).grid(row=3, column=1, columnspan=2, 
                                                                  sticky=tk.EW, padx=5)
        
        # Fecha
        ttk.Label(input_frame, text="Fecha:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.fecha).grid(row=4, column=1, columnspan=2, 
                                                           sticky=tk.EW, padx=5)
        
        # Botones de acción
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Agregar", command=self.agregar_movimiento).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Nueva Categoría", command=self.agregar_categoria).pack(side=tk.LEFT, padx=5)
        
        # Frame de visualización de datos
        data_frame = ttk.LabelFrame(main_frame, text="Registros", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar movimientos
        columns = ("id", "fecha", "tipo", "categoria", "descripcion", "monto")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("monto", text="Monto")
        
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("fecha", width=100, anchor=tk.CENTER)
        self.tree.column("tipo", width=80, anchor=tk.CENTER)
        self.tree.column("categoria", width=120, anchor=tk.CENTER)
        self.tree.column("descripcion", width=200)
        self.tree.column("monto", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame de controles de visualización
        controls_frame = ttk.Frame(data_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Filtros
        ttk.Label(controls_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
        
        self.filtro_tipo = ttk.Combobox(controls_frame, values=["Todos", "Ingreso", "Egreso"], 
                                      state="readonly")
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.pack(side=tk.LEFT, padx=5)
        
        self.filtro_mes = ttk.Combobox(controls_frame, 
                                      values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], 
                                      state="readonly")
        self.filtro_mes.set("Todos")
        self.filtro_mes.pack(side=tk.LEFT, padx=5)
        
        self.filtro_anio = ttk.Combobox(controls_frame, 
                                       values=["Todos"] + [str(i) for i in range(2020, 2031)], 
                                       state="readonly")
        self.filtro_anio.set("Todos")
        self.filtro_anio.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Aplicar Filtros", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Eliminar Seleccionado", command=self.eliminar_movimiento).pack(side=tk.RIGHT, padx=5)
        
        # Frame de resumen
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(summary_frame, text="Resumen:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.total_ingresos = ttk.Label(summary_frame, text="Ingresos: $0.00", font=('Arial', 10))
        self.total_ingresos.pack(side=tk.LEFT, padx=10)
        
        self.total_egresos = ttk.Label(summary_frame, text="Egresos: $0.00", font=('Arial', 10))
        self.total_egresos.pack(side=tk.LEFT, padx=10)
        
        self.balance = ttk.Label(summary_frame, text="Balance: $0.00", font=('Arial', 10, 'bold'))
        self.balance.pack(side=tk.LEFT, padx=10)
        
        # Inicializar la tabla y resumen
        self.actualizar_tabla()
        self.actualizar_resumen()
        
    def agregar_movimiento(self):
        """Agrega un nuevo movimiento a la base de datos"""
        try:
            if not self.monto.get() or self.monto.get() <= 0:
                messagebox.showerror("Error", "El monto debe ser un valor positivo")
                return
                
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO movimientos (tipo, monto, categoria, descripcion, fecha)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.tipo_movimiento.get(),
                self.monto.get(),
                self.categoria.get(),
                self.descripcion.get(),
                self.fecha.get()
            ))
            self.conn.commit()
            
            self.limpiar_formulario()
            self.actualizar_tabla()
            self.actualizar_resumen()
            messagebox.showinfo("Éxito", "Movimiento agregado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el movimiento: {str(e)}")
            
    def eliminar_movimiento(self):
        """Elimina el movimiento seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un movimiento para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este movimiento?"):
            try:
                item = self.tree.item(selected[0])
                movimiento_id = item['values'][0]
                
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM movimientos WHERE id = ?', (movimiento_id,))
                self.conn.commit()
                
                self.actualizar_tabla()
                self.actualizar_resumen()
                messagebox.showinfo("Éxito", "Movimiento eliminado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el movimiento: {str(e)}")
                
    def actualizar_tabla(self):
        """Actualiza el Treeview con los movimientos según los filtros"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Construir consulta SQL con filtros
        query = "SELECT id, fecha, tipo, categoria, descripcion, monto FROM movimientos"
        conditions = []
        params = []
        
        tipo = self.filtro_tipo.get()
        if tipo != "Todos":
            conditions.append("tipo = ?")
            params.append(tipo.lower())
            
        mes = self.filtro_mes.get()
        if mes != "Todos":
            conditions.append("strftime('%m', fecha) = ?")
            params.append(mes)
            
        anio = self.filtro_anio.get()
        if anio != "Todos":
            conditions.append("strftime('%Y', fecha) = ?")
            params.append(anio)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY fecha DESC"
        
        # Ejecutar consulta y llenar tabla
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            # Formatear el monto con 2 decimales
            formatted_row = list(row)
            formatted_row[5] = f"{row[5]:.2f}"
            self.tree.insert("", tk.END, values=formatted_row)
            
    def actualizar_resumen(self):
        """Actualiza los totales de ingresos, egresos y balance"""
        cursor = self.conn.cursor()
        
        # Total ingresos
        cursor.execute("SELECT SUM(monto) FROM movimientos WHERE tipo = 'ingreso'")
        total_ing = cursor.fetchone()[0] or 0
        
        # Total egresos
        cursor.execute("SELECT SUM(monto) FROM movimientos WHERE tipo = 'egreso'")
        total_egr = cursor.fetchone()[0] or 0
        
        # Actualizar etiquetas
        self.total_ingresos.config(text=f"Ingresos: ${total_ing:.2f}")
        self.total_egresos.config(text=f"Egresos: ${total_egr:.2f}")
        self.balance.config(text=f"Balance: ${(total_ing - total_egr):.2f}")
        
    def actualizar_categorias(self):
        """Actualiza la lista de categorías en el combobox"""
        cursor = self.conn.cursor()
        tipo = self.tipo_movimiento.get()
        
        cursor.execute("SELECT nombre FROM categorias WHERE tipo = ? ORDER BY nombre", (tipo,))
        categorias = [row[0] for row in cursor.fetchall()]
        
        self.categoria_cb['values'] = categorias
        if categorias:
            self.categoria.set(categorias[0])
            
    def agregar_categoria(self):
        """Muestra un diálogo para agregar una nueva categoría"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Categoría")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Nombre de la categoría:").pack(padx=10, pady=(10, 5))
        
        nombre = ttk.Entry(dialog)
        nombre.pack(padx=10, pady=5)
        nombre.focus()
        
        ttk.Label(dialog, text="Tipo:").pack(padx=10, pady=5)
        
        tipo = ttk.Combobox(dialog, values=["ingreso", "egreso"], state="readonly")
        tipo.set(self.tipo_movimiento.get())
        tipo.pack(padx=10, pady=5)
        
        def guardar_categoria():
            if not nombre.get():
                messagebox.showerror("Error", "El nombre de la categoría no puede estar vacío")
                return
                
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO categorias (nombre, tipo)
                    VALUES (?, ?)
                ''', (nombre.get(), tipo.get()))
                self.conn.commit()
                
                self.actualizar_categorias()
                dialog.destroy()
                messagebox.showinfo("Éxito", "Categoría agregada correctamente")
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Esta categoría ya existe para este tipo")
                
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Guardar", command=guardar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def limpiar_formulario(self):
        """Limpia el formulario de entrada"""
        self.monto.set(0)
        self.descripcion.set("")
        self.fecha.set(datetime.now().strftime("%Y-%m-%d"))
        
    def __del__(self):
        """Cierra la conexión a la base de datos al destruir la aplicación"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanzasApp(root)
    root.mainloop()