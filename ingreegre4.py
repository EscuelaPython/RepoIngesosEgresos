import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkinter import simpledialog

class AplicacionFinanzas:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Financiero - Ingresos/Egresos Franklin Cedeño")
        self.root.geometry("1200x750")
        
        # Variables de configuración
        self.moneda_base = "$"  # Moneda base para conversiones
        self.tipo_cambio = 36.0  # Valor por defecto (1$ = 36 Bs.)
        
        # Variables de control
        self.tipo_movimiento = tk.StringVar(value="ingreso")
        self.monto = tk.DoubleVar()
        self.categoria = tk.StringVar()
        self.descripcion = tk.StringVar()
        self.fecha = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.cuenta = tk.StringVar()
        self.moneda = tk.StringVar(value="$")
        
        # Conectar a la base de datos
        self.conectar_db()
        
        # Configurar interfaz
        self.configurar_interfaz()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()
        
    def conectar_db(self):
        """Establece conexión con la base de datos"""
        self.conn = sqlite3.connect('finanzas.db')
        self.cursor = self.conn.cursor()
        
    def configurar_interfaz(self):
        """Configura todos los elementos de la interfaz gráfica"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de registro
        registro_frame = ttk.LabelFrame(main_frame, text="Nuevo Movimiento", padding="10")
        registro_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Formulario de registro
        ttk.Label(registro_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(registro_frame, text="Ingreso", variable=self.tipo_movimiento, 
                       value="ingreso", command=self.actualizar_categorias).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(registro_frame, text="Egreso", variable=self.tipo_movimiento, 
                       value="egreso", command=self.actualizar_categorias).grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(registro_frame, text="Monto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(registro_frame, textvariable=self.monto, width=15).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(registro_frame, text="Moneda:").grid(row=1, column=2, sticky=tk.W, padx=5)
        ttk.Combobox(registro_frame, textvariable=self.moneda, values=["$", "Bs."], 
                    state="readonly", width=5).grid(row=1, column=3, sticky=tk.W)
        
        ttk.Label(registro_frame, text="Cuenta:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.cuenta_cb = ttk.Combobox(registro_frame, textvariable=self.cuenta)
        self.cuenta_cb.grid(row=2, column=1, columnspan=3, sticky=tk.EW)
        
        ttk.Label(registro_frame, text="Categoría:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.categoria_cb = ttk.Combobox(registro_frame, textvariable=self.categoria)
        self.categoria_cb.grid(row=3, column=1, columnspan=3, sticky=tk.EW)
        
        ttk.Label(registro_frame, text="Descripción:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(registro_frame, textvariable=self.descripcion).grid(row=4, column=1, columnspan=3, sticky=tk.EW)
        
        ttk.Label(registro_frame, text="Fecha:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(registro_frame, textvariable=self.fecha).grid(row=5, column=1, sticky=tk.W)
        
        # Botones de acción
        btn_frame = ttk.Frame(registro_frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Registrar", command=self.registrar_movimiento).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="+ Categoría", command=self.agregar_categoria).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="+ Cuenta", command=self.agregar_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Tipo Cambio", command=self.configurar_tipo_cambio).pack(side=tk.LEFT, padx=5)
        
        # Panel de visualización
        datos_frame = ttk.LabelFrame(main_frame, text="Registros", padding="10")
        datos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar movimientos
        columns = ("id", "fecha", "tipo", "cuenta", "moneda", "monto", "categoria", "descripcion")
        self.tree = ttk.Treeview(datos_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configurar columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("cuenta", text="Cuenta")
        self.tree.heading("moneda", text="Moneda")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("descripcion", text="Descripción")
        
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("fecha", width=100, anchor=tk.CENTER)
        self.tree.column("tipo", width=80, anchor=tk.CENTER)
        self.tree.column("cuenta", width=150, anchor=tk.CENTER)
        self.tree.column("moneda", width=60, anchor=tk.CENTER)
        self.tree.column("monto", width=100, anchor=tk.CENTER)
        self.tree.column("categoria", width=120, anchor=tk.CENTER)
        self.tree.column("descripcion", width=200,anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Controles de filtrado
        filtros_frame = ttk.Frame(datos_frame)
        filtros_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(filtros_frame, text="Filtrar:").pack(side=tk.LEFT, padx=5)
        
        self.filtro_tipo = ttk.Combobox(filtros_frame, values=["Todos", "Ingreso", "Egreso"], 
                                      state="readonly", width=10)
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.pack(side=tk.LEFT, padx=5)
        
        self.filtro_moneda = ttk.Combobox(filtros_frame, values=["Todos", "$", "Bs."], 
                                        state="readonly", width=5)
        self.filtro_moneda.set("Todos")
        self.filtro_moneda.pack(side=tk.LEFT, padx=5)
        
        self.filtro_cuenta = ttk.Combobox(filtros_frame, state="readonly", width=15)
        self.filtro_cuenta.set("Todos")
        self.filtro_cuenta.pack(side=tk.LEFT, padx=5)
        
        self.filtro_mes = ttk.Combobox(filtros_frame, 
                                      values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], 
                                      state="readonly", width=5)
        self.filtro_mes.set("Todos")
        self.filtro_mes.pack(side=tk.LEFT, padx=5)
        
        self.filtro_anio = ttk.Combobox(filtros_frame, 
                                       values=["Todos"] + [str(i) for i in range(2020, 2031)], 
                                       state="readonly", width=5)
        self.filtro_anio.set("Todos")
        self.filtro_anio.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filtros_frame, text="Aplicar", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=5)
        ttk.Button(filtros_frame, text="Eliminar", command=self.eliminar_movimiento).pack(side=tk.RIGHT, padx=5)
        
        # Panel de resumen
        resumen_frame = ttk.Frame(main_frame)
        resumen_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Resumen por moneda
        ttk.Label(resumen_frame, text="Resumen:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.resumen_bs = ttk.Label(resumen_frame, text="Bs.: Ing. 0.00 - Egr. 0.00 - Bal. 0.00", 
                                  font=('Arial', 10))
        self.resumen_bs.pack(side=tk.LEFT, padx=10)
        
        self.resumen_usd = ttk.Label(resumen_frame, text="$: Ing. 0.00 - Egr. 0.00 - Bal. 0.00", 
                                   font=('Arial', 10))
        self.resumen_usd.pack(side=tk.LEFT, padx=10)
        
        self.resumen_total = ttk.Label(resumen_frame, text="Total ($): 0.00", 
                                     font=('Arial', 10, 'bold'))
        self.resumen_total.pack(side=tk.LEFT, padx=10)
        
    def cargar_datos_iniciales(self):
        """Carga datos iniciales y configura la aplicación"""
        # Crear tablas si no existen
        self.crear_tablas()
        
        # Cargar tipo de cambio
        self.cargar_tipo_cambio()
        
        # Actualizar comboboxes
        self.actualizar_cuentas()
        self.actualizar_categorias()
        self.actualizar_filtros()
        
        # Cargar datos iniciales
        self.actualizar_tabla()
        self.actualizar_resumen()
        
    def crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cuenta TEXT NOT NULL,
                moneda TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT,
                descripcion TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cuentas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                moneda TEXT NOT NULL,
                saldo_inicial REAL DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        ''')
        
        # Insertar datos iniciales si no existen
        self.cursor.execute('''
            INSERT OR IGNORE INTO config (clave, valor) 
            VALUES ('tipo_cambio', ?)
        ''', (str(self.tipo_cambio),))
        
        self.conn.commit()
        
    def cargar_tipo_cambio(self):
        """Carga el tipo de cambio desde la base de datos"""
        self.cursor.execute("SELECT valor FROM config WHERE clave = 'tipo_cambio'")
        resultado = self.cursor.fetchone()
        if resultado:
            try:
                self.tipo_cambio = float(resultado[0])
            except (ValueError, TypeError):
                self.tipo_cambio = 36.0
        
    def configurar_tipo_cambio(self):
        """Permite configurar el tipo de cambio"""
        nuevo_tipo = simpledialog.askfloat(
            "Tipo de Cambio",
            f"Establezca el tipo de cambio (1$ = Bs.):",
            initialvalue=self.tipo_cambio,
            minvalue=0.1,
            maxvalue=1000
        )
        
        if nuevo_tipo is not None:
            self.tipo_cambio = nuevo_tipo
            self.cursor.execute('''
                INSERT OR REPLACE INTO config (clave, valor)
                VALUES ('tipo_cambio', ?)
            ''', (str(self.tipo_cambio),))
            self.conn.commit()
            self.actualizar_resumen()
            messagebox.showinfo("Éxito", f"Tipo de cambio actualizado: 1$ = {self.tipo_cambio} Bs.")
        
    def actualizar_cuentas(self):
        """Actualiza la lista de cuentas en los comboboxes"""
        self.cursor.execute("SELECT nombre FROM cuentas ORDER BY nombre")
        cuentas = [row[0] for row in self.cursor.fetchall()]
        
        self.cuenta_cb['values'] = cuentas
        self.filtro_cuenta['values'] = ["Todos"] + cuentas
        
        if cuentas:
            self.cuenta.set(cuentas[0])
            self.filtro_cuenta.set("Todos")
        
    def actualizar_categorias(self):
        """Actualiza la lista de categorías según el tipo de movimiento"""
        tipo = self.tipo_movimiento.get()
        self.cursor.execute("SELECT nombre FROM categorias WHERE tipo = ? ORDER BY nombre", (tipo,))
        categorias = [row[0] for row in self.cursor.fetchall()]
        
        self.categoria_cb['values'] = categorias
        if categorias:
            self.categoria.set(categorias[0])
        
    def actualizar_filtros(self):
        """Actualiza los filtros disponibles"""
        self.actualizar_cuentas()
        
        # Actualizar años disponibles
        self.cursor.execute("SELECT DISTINCT strftime('%Y', fecha) FROM movimientos ORDER BY fecha DESC")
        anios = ["Todos"] + [row[0] for row in self.cursor.fetchall() if row[0]]
        self.filtro_anio['values'] = anios
        
    def registrar_movimiento(self):
        """Registra un nuevo movimiento en la base de datos"""
        try:
            # Validaciones
            if not self.monto.get() or self.monto.get() <= 0:
                messagebox.showerror("Error", "El monto debe ser un valor positivo")
                return
                
            if not self.cuenta.get():
                messagebox.showerror("Error", "Debe seleccionar una cuenta")
                return
                
            # Insertar movimiento
            self.cursor.execute('''
                INSERT INTO movimientos (fecha, tipo, cuenta, moneda, monto, categoria, descripcion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.fecha.get(),
                self.tipo_movimiento.get(),
                self.cuenta.get(),
                self.moneda.get(),
                self.monto.get(),
                self.categoria.get(),
                self.descripcion.get()
            ))
            
            self.conn.commit()
            
            # Actualizar interfaz
            self.limpiar_formulario()
            self.actualizar_tabla()
            self.actualizar_resumen()
            
            messagebox.showinfo("Éxito", "Movimiento registrado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el movimiento: {str(e)}")
        
    def actualizar_tabla(self):
        """Actualiza la tabla con los movimientos según los filtros aplicados"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Construir consulta con filtros
        query = "SELECT id, fecha, tipo, cuenta, moneda, monto, categoria, descripcion FROM movimientos"
        conditions = []
        params = []
        
        # Aplicar filtros
        tipo = self.filtro_tipo.get()
        if tipo != "Todos":
            conditions.append("tipo = ?")
            params.append(tipo.lower())
            
        moneda = self.filtro_moneda.get()
        if moneda != "Todos":
            conditions.append("moneda = ?")
            params.append(moneda)
            
        cuenta = self.filtro_cuenta.get()
        if cuenta != "Todos":
            conditions.append("cuenta = ?")
            params.append(cuenta)
            
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
        self.cursor.execute(query, params)
        
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        
    def actualizar_resumen(self):
        """Calcula y muestra los resúmenes financieros"""
        # Obtener totales por moneda
        self.cursor.execute('''
            SELECT moneda, tipo, SUM(monto) 
            FROM movimientos 
            GROUP BY moneda, tipo
        ''')
        
        resultados = self.cursor.fetchall()
        
        # Inicializar variables
        ingresos_bs = 0
        egresos_bs = 0
        ingresos_usd = 0
        egresos_usd = 0
        
        # Procesar resultados
        for moneda, tipo, monto in resultados:
            monto = monto or 0
            if moneda == "Bs.":
                if tipo == "ingreso":
                    ingresos_bs += monto
                else:
                    egresos_bs += monto
            else:  # $
                if tipo == "ingreso":
                    ingresos_usd += monto
                else:
                    egresos_usd += monto
        
        # Calcular totales convertidos
        total_ingresos = ingresos_usd + (ingresos_bs / self.tipo_cambio)
        total_egresos = egresos_usd + (egresos_bs / self.tipo_cambio)
        
        # Actualizar etiquetas
        self.resumen_bs.config(
            text=f"Bs.: Ing. {ingresos_bs:,.2f} - Egr. {egresos_bs:,.2f} - Bal. {ingresos_bs - egresos_bs:,.2f}"
        )
        
        self.resumen_usd.config(
            text=f"$: Ing. {ingresos_usd:,.2f} - Egr. {egresos_usd:,.2f} - Bal. {ingresos_usd - egresos_usd:,.2f}"
        )
        
        self.resumen_total.config(
            text=f"Total ($): {total_ingresos - total_egresos:,.2f}"
        )
        
    def eliminar_movimiento(self):
        """Elimina el movimiento seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un movimiento para eliminar")
            return
            
        movimiento_id = self.tree.item(seleccion[0])['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este movimiento?"):
            try:
                self.cursor.execute("DELETE FROM movimientos WHERE id = ?", (movimiento_id,))
                self.conn.commit()
                
                self.actualizar_tabla()
                self.actualizar_resumen()
                
                messagebox.showinfo("Éxito", "Movimiento eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el movimiento: {str(e)}")
        
    def agregar_categoria(self):
        """Agrega una nueva categoría"""
        nombre = simpledialog.askstring(
            "Nueva Categoría", 
            f"Ingrese el nombre de la categoría ({self.tipo_movimiento.get()}):"
        )
        
        if nombre:
            try:
                self.cursor.execute('''
                    INSERT INTO categorias (nombre, tipo)
                    VALUES (?, ?)
                ''', (nombre, self.tipo_movimiento.get()))
                
                self.conn.commit()
                self.actualizar_categorias()
                
                messagebox.showinfo("Éxito", "Categoría agregada correctamente")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Esta categoría ya existe para este tipo")
        
    def agregar_cuenta(self):
        """Agrega una nueva cuenta bancaria"""
        nombre = simpledialog.askstring("Nueva Cuenta", "Ingrese el nombre de la cuenta:")
        
        if nombre:
            moneda = simpledialog.askstring(
                "Moneda de la Cuenta", 
                "Seleccione la moneda:", 
                initialvalue="$",
                parent=self.root
            )
            
            if moneda and moneda in ["$", "Bs."]:
                try:
                    self.cursor.execute('''
                        INSERT INTO cuentas (nombre, moneda)
                        VALUES (?, ?)
                    ''', (nombre, moneda))
                    
                    self.conn.commit()
                    self.actualizar_cuentas()
                    
                    messagebox.showinfo("Éxito", "Cuenta agregada correctamente")
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Esta cuenta ya existe")
            else:
                messagebox.showerror("Error", "Moneda no válida. Use $ o Bs.")
        
    def limpiar_formulario(self):
        """Limpia el formulario de registro"""
        self.monto.set(0)
        self.descripcion.set("")
        self.fecha.set(datetime.now().strftime("%Y-%m-%d"))
        self.moneda.set("$")
        
    def __del__(self):
        """Cierra la conexión a la base de datos al cerrar la aplicación"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionFinanzas(root)
    root.mainloop()