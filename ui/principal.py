import tkinter as tk
from tkinter import messagebox, ttk
from servicios import resumen, listar_usuarios, crear_usuario, actualizar_usuario, obtener_usuario
from servicios import listar_clientes, crear_cliente, actualizar_cliente, obtener_cliente, eliminar_cliente
from validaciones import ErrorValidacion, ROLES, ESTADOS

BG = "#111827"
SIDE = "#0b1220"
CARD = "#1f2937"
INPUT = "#252f3d"
BLUE = "#2563eb"
TEXT = "#f9fafb"
MUTED = "#9ca3af"
DANGER = "#dc2626"

class Principal(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app = app
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._topbar()
        self._sidebar()
        self.contenido = tk.Frame(self, bg=BG)
        self.contenido.grid(row=1, column=1, sticky="nsew", padx=18, pady=18)
        self.mostrar_dashboard()

    def _topbar(self):
        bar = tk.Frame(self, bg="#172554", height=58)
        bar.grid(row=0, column=1, sticky="ew")
        bar.grid_propagate(False)
        tk.Label(bar, text="🚗  Sistema de Gestión · Sprint 1", bg="#172554", fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=18)
        u = self.app.usuario
        tk.Label(bar, text=f"{u['username']} · {u['rol']}", bg="#172554", fg="#dbeafe",
                 font=("Segoe UI", 10)).pack(side="right", padx=18)

    def _sidebar(self):
        side = tk.Frame(self, bg=SIDE, width=220)
        side.grid(row=0, column=0, rowspan=2, sticky="nsew")
        side.grid_propagate(False)
        tk.Label(side, text="MENÚ", bg=SIDE, fg="#93c5fd",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(24, 10))
        items = [("Inicio", self.mostrar_dashboard), ("Usuarios", self.mostrar_usuarios),
                 ("Clientes", self.mostrar_clientes)]
        if self.app.usuario["rol"] == "administrador":
            items.append(("Gestión de usuarios", self.mostrar_usuarios_admin))
        for texto, cmd in items:
            tk.Button(side, text=texto, command=cmd, anchor="w", bg=SIDE, fg=TEXT,
                      activebackground="#1e293b", activeforeground=TEXT, bd=0,
                      font=("Segoe UI", 10), padx=18, pady=10).pack(fill="x")
        tk.Button(side, text="Cerrar sesión", command=self.cerrar,
                  anchor="w", bg=SIDE, fg="#fca5a5", activebackground="#1e293b",
                  activeforeground="white", bd=0, font=("Segoe UI", 10),
                  padx=18, pady=10).pack(side="bottom", fill="x", pady=16)

    def _titulo(self, titulo, subtitulo=""):
        for w in self.contenido.winfo_children():
            w.destroy()
        tk.Label(self.contenido, text=titulo, bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        if subtitulo:
            tk.Label(self.contenido, text=subtitulo, bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 16))

    def _card(self, parent, titulo, valor, col):
        c = tk.Frame(parent, bg=CARD, padx=18, pady=16)
        c.grid(row=0, column=col, sticky="nsew", padx=6)
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(c, text=titulo, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(c, text=str(valor), bg=CARD, fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(4, 0))

    def mostrar_dashboard(self):
        self._titulo("Inicio", "Resumen del Sprint 1: acceso, usuarios internos y gestión de clientes.")
        datos = resumen()
        cards = tk.Frame(self.contenido, bg=BG)
        cards.pack(fill="x")
        self._card(cards, "Usuarios activos", datos["usuarios"], 0)
        self._card(cards, "Clientes activos", datos["clientes"], 1)
        self._card(cards, "Administradores activos", datos["administradores"], 2)
        panel = tk.Frame(self.contenido, bg=CARD, padx=22, pady=22)
        panel.pack(fill="both", expand=True, pady=18)
        tk.Label(panel, text="Alcance implementado", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        texto = ("HU-10: autenticación con bloqueo por intentos y cierre por inactividad.\n"
                 "HU-09: crear, editar, desactivar usuarios y asignar administrador/empleado.\n"
                 "HU-01: registrar, editar e inactivar clientes con validación de cédula/RUC.")
        tk.Label(panel, text=texto, justify="left", bg=CARD, fg="#d1d5db",
                 font=("Segoe UI", 10), pady=10).pack(anchor="w")

    def _tree(self, columnas, anchos):
        t = ttk.Treeview(self.contenido, columns=columnas, show="headings")
        for c, title, width in zip(columnas, columnas, anchos):
            t.heading(c, text=title.replace("_", " ").title())
            t.column(c, width=width, anchor="w")
        t.pack(fill="both", expand=True, pady=10)
        return t

    def mostrar_usuarios(self):
        self._titulo("Usuarios internos", "Consulta de usuarios y estado actual.")
        if self.app.usuario["rol"] != "administrador":
            tk.Label(self.contenido, text="Solo los administradores gestionan usuarios internos.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w")
            return
        self.mostrar_usuarios_admin()

    def mostrar_usuarios_admin(self):
        self._titulo("Gestión de usuarios", "Crear, editar y desactivar usuarios internos.")
        tk.Button(self.contenido, text="＋ Nuevo usuario", command=lambda: self.form_usuario(),
                  bg=BLUE, fg="white", bd=0, padx=14, pady=9,
                  font=("Segoe UI", 10, "bold")).pack(anchor="e")
        t = self._tree(("id_usuario","nombre","username","rol","estado"), (70,220,150,130,100))
        for r in listar_usuarios():
            t.insert("", "end", values=tuple(r[c] for c in t["columns"]))
        def editar(_=None):
            item = t.focus()
            if item:
                self.form_usuario(int(t.item(item)["values"][0]))
        t.bind("<Double-1>", editar)
        tk.Button(self.contenido, text="Editar seleccionado", command=editar,
                  bg="#334155", fg=TEXT, bd=0, padx=12, pady=8).pack(anchor="w")

    def form_usuario(self, id_usuario=None):
        self._titulo("Registrar usuario" if id_usuario is None else "Actualizar usuario",
                     "Complete los datos del usuario interno.")
        card = tk.Frame(self.contenido, bg=CARD, padx=22, pady=18)
        card.pack(fill="x")
        campos = [("Nombre completo","nombre"),("Nombre de usuario","username"),
                  ("Contraseña","password")]
        vars_ = {k: tk.StringVar() for _, k in campos}
        for label, key in campos:
            tk.Label(card, text=label, bg=CARD, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            e = tk.Entry(card, textvariable=vars_[key], bg=INPUT, fg=TEXT,
                         insertbackground=TEXT, relief="flat", show="•" if key=="password" else "")
            e.pack(fill="x", ipady=8, pady=(4, 12))
        rol = tk.StringVar(value="empleado")
        estado = tk.StringVar(value="Activo")
        for label, var, values in [("Rol", rol, ROLES), ("Estado", estado, ESTADOS)]:
            tk.Label(card, text=label, bg=CARD, fg=TEXT,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Combobox(card, textvariable=var, values=values, state="readonly").pack(fill="x", pady=(4,12))
        if id_usuario:
            r = obtener_usuario(id_usuario)
            if not r:
                messagebox.showerror("Error", "Usuario no encontrado."); return
            vars_["nombre"].set(r["nombre"]); vars_["username"].set(r["username"])
            rol.set(r["rol"]); estado.set(r["estado"])
        def guardar():
            data = {k:v.get() for k,v in vars_.items()}
            data.update(rol=rol.get(), estado=estado.get())
            try:
                if id_usuario:
                    data["id_usuario"] = id_usuario
                    actualizar_usuario(data, self.app.usuario["username"])
                else:
                    crear_usuario(data, self.app.usuario["username"])
                self.mostrar_usuarios_admin()
            except ErrorValidacion as exc:
                messagebox.showerror("Validación", str(exc))
        tk.Button(card, text="Guardar", command=guardar, bg=BLUE, fg="white", bd=0,
                  padx=18, pady=9, font=("Segoe UI", 10, "bold")).pack(anchor="e")

    def mostrar_clientes(self):
        self._titulo("Gestión de clientes", "Registrar, editar e inactivar clientes.")
        top = tk.Frame(self.contenido, bg=BG)
        top.pack(fill="x")
        q = tk.StringVar()
        tk.Entry(top, textvariable=q, bg=INPUT, fg=TEXT, insertbackground=TEXT,
                 relief="flat", width=32).pack(side="left", ipady=8)
        t = self._tree(("id_cliente","nombre","cedula_ruc","telefono","correo","estado"),
                       (70,210,130,120,220,100))
        def cargar():
            for i in t.get_children(): t.delete(i)
            for r in listar_clientes(q.get()):
                t.insert("", "end", values=tuple(r[c] for c in t["columns"]))
        tk.Button(top, text="Buscar", command=cargar, bg="#334155", fg=TEXT, bd=0,
                  padx=14, pady=8).pack(side="left", padx=8)
        tk.Button(top, text="＋ Nuevo cliente", command=lambda: self.form_cliente(),
                  bg=BLUE, fg="white", bd=0, padx=14, pady=8,
                  font=("Segoe UI", 10, "bold")).pack(side="right")
        cargar()
        def editar(_=None):
            item = t.focus()
            if item: self.form_cliente(int(t.item(item)["values"][0]))
        t.bind("<Double-1>", editar)
        tk.Button(self.contenido, text="Editar / Inactivar seleccionado", command=editar,
                  bg="#334155", fg=TEXT, bd=0, padx=12, pady=8).pack(anchor="w")

    def form_cliente(self, id_cliente=None):
        self._titulo("Registrar cliente" if id_cliente is None else "Actualizar cliente")
        card = tk.Frame(self.contenido, bg=CARD, padx=22, pady=18)
        card.pack(fill="x")
        defs = [("Nombre completo","nombre"),("Cédula / RUC","cedula_ruc"),
                ("Teléfono","telefono"),("Correo electrónico","correo")]
        vs = {k:tk.StringVar() for _,k in defs}
        for label,key in defs:
            tk.Label(card,text=label,bg=CARD,fg=TEXT,font=("Segoe UI",10,"bold")).pack(anchor="w")
            tk.Entry(card,textvariable=vs[key],bg=INPUT,fg=TEXT,insertbackground=TEXT,
                     relief="flat").pack(fill="x",ipady=8,pady=(4,10))
        estado = tk.StringVar(value="Activo")
        if id_cliente:
            r = obtener_cliente(id_cliente)
            for _,k in defs: vs[k].set(r[k])
            estado.set(r["estado"])
        ttk.Combobox(card,textvariable=estado,values=ESTADOS,state="readonly").pack(fill="x",pady=(2,12))
        def guardar():
            data={k:v.get() for k,v in vs.items()}; data["estado"]=estado.get()
            try:
                if id_cliente:
                    data["id_cliente"]=id_cliente
                    actualizar_cliente(data,self.app.usuario["username"])
                else:
                    crear_cliente(data,self.app.usuario["username"])
                self.mostrar_clientes()
            except ErrorValidacion as exc:
                messagebox.showerror("Validación",str(exc))
        tk.Button(card,text="Guardar",command=guardar,bg=BLUE,fg="white",bd=0,
                  padx=18,pady=9,font=("Segoe UI",10,"bold")).pack(anchor="e")
        if id_cliente:
            tk.Button(card,text="Inactivar",command=lambda:self._inactivar(id_cliente),
                      bg=DANGER,fg="white",bd=0,padx=14,pady=8).pack(anchor="e",pady=(8,0))

    def _inactivar(self, id_cliente):
        if not messagebox.askyesno("Confirmar", "¿Inactivar este cliente?"):
            return
        try:
            eliminar_cliente(id_cliente, self.app.usuario["username"])
            self.mostrar_clientes()
        except ErrorValidacion as exc:
            messagebox.showerror("No permitido", str(exc))

    def cerrar(self):
        self.app.usuario = None
        self.app.pantalla_login()
