import tkinter as tk
from tkinter import messagebox, ttk
from base_datos import inicializar_base_datos
from servicios import autenticar
from validaciones import ErrorValidacion
from ui.principal import Principal

BG = "#111827"
CARD = "#1f2937"
INPUT = "#252f3d"
BLUE = "#2563eb"
TEXT = "#f9fafb"
MUTED = "#9ca3af"

class AppShell(tk.Tk):
    def __init__(self):
        super().__init__()
        inicializar_base_datos()
        self.title("Sistema de Gestión — Sprint 1")
        self.geometry("1100x700")
        self.minsize(920, 620)
        self.configure(bg=BG)
        self.usuario = None
        self.ultima_actividad = 0
        self.pantalla_login()

    def limpiar(self):
        for w in self.winfo_children():
            w.destroy()

    def pantalla_login(self):
        self.limpiar()
        cont = tk.Frame(self, bg=BG)
        cont.pack(fill="both", expand=True)
        card = tk.Frame(cont, bg=CARD, padx=42, pady=32)
        card.place(relx=.5, rely=.5, anchor="center", relwidth=.68, relheight=.82)
        tk.Label(card, text="Acceso seguro", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(card, text="Sprint 1 · Usuarios, seguridad y clientes",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 28))
        self.login_user = tk.StringVar()
        self.login_pass = tk.StringVar()
        self._entrada(card, "Usuario", self.login_user)
        self._entrada(card, "Contraseña", self.login_pass, password=True)
        self.login_msg = tk.Label(card, text="",
                                  bg=CARD, fg="#fca5a5", font=("Segoe UI", 10))
        self.login_msg.pack(anchor="w", pady=(6, 10))
        tk.Button(card, text="Iniciar sesión", command=self.iniciar_sesion,
                  bg=BLUE, fg="white", activebackground="#1d4ed8",
                  activeforeground="white", bd=0, padx=16, pady=11,
                  font=("Segoe UI", 11, "bold"), cursor="hand2").pack(fill="x", pady=8)
        tk.Label(card, text="Puedes continuar de manera segura.",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(16, 0))
        tk.Label(card, text="Acceso inicial: admin / Admin123!",
                 bg=CARD, fg="#cbd5e1", font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))
        self.bind_all("<Key>", self._actividad)
        self.bind_all("<Button>", self._actividad)

    def _entrada(self, parent, texto, variable, password=False):
        tk.Label(parent, text=texto, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 7))
        entry = tk.Entry(parent, textvariable=variable, show="•" if password else "",
                         bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat",
                         font=("Segoe UI", 12))
        entry.pack(fill="x", ipady=9, pady=(0, 16))

    def iniciar_sesion(self):
        try:
            self.usuario = autenticar(self.login_user.get(), self.login_pass.get())
            self.ultima_actividad = __import__("time").time()
            self.unbind_all("<Key>")
            self.unbind_all("<Button>")
            self.bind_all("<Key>", self._actividad)
            self.bind_all("<Button>", self._actividad)
            self.cargar_principal()
        except ErrorValidacion as exc:
            self.login_msg.config(text=str(exc))

    def _actividad(self, event=None):
        if self.usuario:
            self.ultima_actividad = __import__("time").time()

    def cargar_principal(self):
        self.limpiar()
        Principal(self).pack(fill="both", expand=True)
        self.after(30000, self._vigilar_sesion)

    def _vigilar_sesion(self):
        if self.usuario and __import__("time").time() - self.ultima_actividad >= 900:
            messagebox.showinfo("Sesión", "La sesión se cerró por inactividad.")
            self.usuario = None
            self.pantalla_login()
            return
        if self.usuario:
            self.after(30000, self._vigilar_sesion)
