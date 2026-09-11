"""Interface do sistema de cartão ponto."""

import calendar
import queue
import subprocess
import sys
import threading
from datetime import date
from pathlib import Path
from tkinter import StringVar, Tk, filedialog, messagebox, simpledialog, ttk

import empresas as cadastro
import holerite
import planilha
from gerador import MESES_PT, PASTA_SAIDA, gerar_cartao

COR_FUNDO = "#F4F6F8"
COR_CABECALHO = "#37474F"
COR_TEXTO_CABECALHO = "#FFFFFF"
COR_DESTAQUE = "#1565C0"
COR_SUCESSO = "#2E7D32"
COR_ERRO = "#C62828"
COR_APOIO = "#607D8B"

FONTE = "Segoe UI" if sys.platform.startswith("win") else "DejaVu Sans"


class AplicacaoCartaoPonto:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Sistema de Cartão Ponto")
        self.janela.geometry("780x800")
        self.janela.minsize(760, 720)
        self.janela.configure(bg=COR_FUNDO)

        self.fila = queue.Queue()
        self.ultima_pasta = PASTA_SAIDA

        self._configurar_estilo()
        self._montar_cabecalho()
        self._montar_abas()
        self._montar_rodape()

        self._atualizar_resumo_empresa()
        self.janela.after(150, self._consumir_fila)

    # ---------------- Estilo ----------------
    def _configurar_estilo(self):
        estilo = ttk.Style(self.janela)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")

        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure("TLabelframe", background=COR_FUNDO, borderwidth=1)
        estilo.configure(
            "TLabelframe.Label",
            background=COR_FUNDO,
            foreground=COR_CABECALHO,
            font=(FONTE, 10, "bold"),
        )
        estilo.configure("TLabel", background=COR_FUNDO, font=(FONTE, 10))
        estilo.configure(
            "Titulo.TLabel",
            background=COR_CABECALHO,
            foreground=COR_TEXTO_CABECALHO,
            font=(FONTE, 16, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background=COR_CABECALHO,
            foreground="#B0BEC5",
            font=(FONTE, 9),
        )
        estilo.configure("Apoio.TLabel", foreground=COR_APOIO, font=(FONTE, 9))
        estilo.configure("Resumo.TLabel", foreground=COR_CABECALHO, font=(FONTE, 9))
        estilo.configure("Status.TLabel", foreground=COR_APOIO, font=(FONTE, 9))
        estilo.configure(
            "Principal.TButton",
            font=(FONTE, 10, "bold"),
            foreground="#FFFFFF",
            background=COR_DESTAQUE,
            padding=(16, 9),
            borderwidth=0,
        )
        estilo.map(
            "Principal.TButton",
            background=[("active", "#0D47A1"), ("disabled", "#90A4AE")],
        )
        estilo.configure("Secundario.TButton", font=(FONTE, 10), padding=(12, 7))
        estilo.configure("TEntry", padding=4)
        estilo.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", font=(FONTE, 10), padding=(18, 9))

    # ---------------- Cabeçalho ----------------
    def _montar_cabecalho(self):
        ttk.Style(self.janela).configure("Cabecalho.TFrame", background=COR_CABECALHO)

        barra = ttk.Frame(self.janela, padding=(24, 18), style="Cabecalho.TFrame")
        barra.pack(fill="x")

        ttk.Label(barra, text="SISTEMA DE CARTÃO PONTO", style="Titulo.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            barra,
            text="Geração mensal dos cartões ponto por empresa",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(2, 0))

    # ---------------- Abas ----------------
    def _montar_abas(self):
        self.abas = ttk.Notebook(self.janela)
        self.abas.pack(fill="both", expand=True, padx=18, pady=(14, 8))

        aba_individual = ttk.Frame(self.abas, padding=18)
        aba_holerite = ttk.Frame(self.abas, padding=18)
        aba_lote = ttk.Frame(self.abas, padding=18)

        self.abas.add(aba_individual, text="  Um funcionário  ")
        self.abas.add(aba_holerite, text="  Pelo holerite (PDF)  ")
        self.abas.add(aba_lote, text="  Vários (planilha)  ")

        self._montar_aba_individual(aba_individual)
        self._montar_aba_holerite(aba_holerite)
        self._montar_aba_lote(aba_lote)

    def _montar_aba_individual(self, pai):
        # ----- Empresa -----
        grupo_empresa = ttk.Labelframe(pai, text=" Empresa ", padding=14)
        grupo_empresa.pack(fill="x")

        self.var_empresa = StringVar(value=cadastro.listar_empresas()[0])
        combo = ttk.Combobox(
            grupo_empresa,
            textvariable=self.var_empresa,
            values=cadastro.listar_empresas(),
            state="readonly",
            width=22,
            font=(FONTE, 10),
        )
        combo.grid(row=0, column=0, sticky="w")
        combo.bind("<<ComboboxSelected>>", lambda _: self._atualizar_resumo_empresa())

        self.lbl_resumo = ttk.Label(grupo_empresa, text="", style="Resumo.TLabel", justify="left")
        self.lbl_resumo.grid(row=0, column=1, sticky="w", padx=(24, 0))

        # ----- Funcionário -----
        grupo_func = ttk.Labelframe(pai, text=" Funcionário e período ", padding=14)
        grupo_func.pack(fill="x", pady=(14, 0))
        grupo_func.columnconfigure(1, weight=1)

        hoje = date.today()

        ttk.Label(grupo_func, text="Nome").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nome = ttk.Entry(grupo_func, font=(FONTE, 10))
        self.entry_nome.grid(row=0, column=1, columnspan=3, sticky="ew", pady=5, padx=(10, 0))

        ttk.Label(grupo_func, text="Mês").grid(row=1, column=0, sticky="w", pady=5)
        self.var_mes = StringVar(value=MESES_PT[hoje.month].title())
        ttk.Combobox(
            grupo_func,
            textvariable=self.var_mes,
            values=[MESES_PT[m].title() for m in range(1, 13)],
            state="readonly",
            width=16,
            font=(FONTE, 10),
        ).grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(grupo_func, text="Ano").grid(row=1, column=2, sticky="e", pady=5, padx=(20, 0))
        self.spin_ano = ttk.Spinbox(
            grupo_func, from_=2000, to=2100, width=8, font=(FONTE, 10)
        )
        self.spin_ano.set(hoje.year)
        self.spin_ano.grid(row=1, column=3, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(grupo_func, text="Dia inicial").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_inicio = ttk.Entry(grupo_func, width=10, font=(FONTE, 10))
        self.entry_inicio.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(grupo_func, text="Dia final").grid(row=2, column=2, sticky="e", pady=5, padx=(20, 0))
        self.entry_fim = ttk.Entry(grupo_func, width=10, font=(FONTE, 10))
        self.entry_fim.grid(row=2, column=3, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(
            grupo_func,
            text="Deixe os dias em branco se o funcionário trabalhou o mês inteiro.",
            style="Apoio.TLabel",
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(4, 0))

        # ----- Ocorrências -----
        grupo_ocor = ttk.Labelframe(pai, text=" Ocorrências do mês ", padding=14)
        grupo_ocor.pack(fill="x", pady=(14, 0))

        ttk.Label(grupo_ocor, text="Horas extras 50%").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_horas = ttk.Entry(grupo_ocor, width=10, font=(FONTE, 10))
        self.entry_horas.insert(0, "0")
        self.entry_horas.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 8))
        ttk.Label(grupo_ocor, text="dias úteis", style="Apoio.TLabel").grid(
            row=0, column=2, sticky="w", pady=5, padx=(0, 30)
        )

        ttk.Label(grupo_ocor, text="Faltas").grid(row=0, column=3, sticky="w", pady=5)
        self.entry_faltas = ttk.Entry(grupo_ocor, width=10, font=(FONTE, 10))
        self.entry_faltas.insert(0, "0")
        self.entry_faltas.grid(row=0, column=4, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(grupo_ocor, text="Horas extras 100%").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_horas_100 = ttk.Entry(grupo_ocor, width=10, font=(FONTE, 10))
        self.entry_horas_100.insert(0, "0")
        self.entry_horas_100.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 8))
        ttk.Label(grupo_ocor, text="domingos e feriados", style="Apoio.TLabel").grid(
            row=1, column=2, sticky="w", pady=5, padx=(0, 30)
        )

        ttk.Label(grupo_ocor, text="Atestados").grid(row=1, column=3, sticky="w", pady=5)
        self.entry_atestados = ttk.Entry(grupo_ocor, width=10, font=(FONTE, 10))
        self.entry_atestados.insert(0, "0")
        self.entry_atestados.grid(row=1, column=4, sticky="w", pady=5, padx=(10, 0))

        ttk.Label(
            grupo_ocor,
            text="Informe o total do mês (ex: 12 ou 12,5). O sistema distribui "
                 "entre os dias: as de 100% aparecem como domingo trabalhado.",
            style="Apoio.TLabel",
            wraplength=640,
            justify="left",
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=(6, 0))

        # ----- Ação -----
        acoes = ttk.Frame(pai)
        acoes.pack(fill="x", pady=(20, 0))

        self.btn_gerar = ttk.Button(
            acoes, text="Gerar cartão", style="Principal.TButton", command=self.gerar_individual
        )
        self.btn_gerar.pack(side="left")

        ttk.Button(
            acoes, text="Abrir pasta dos cartões", style="Secundario.TButton",
            command=self.abrir_pasta_saida,
        ).pack(side="left", padx=(10, 0))

    def _montar_aba_holerite(self, pai):
        explicacao = ttk.Labelframe(pai, text=" Como funciona ", padding=14)
        explicacao.pack(fill="x")

        ttk.Label(
            explicacao,
            justify="left",
            wraplength=660,
            text="Abra o PDF dos holerites do mês. O sistema lê os funcionários, "
                 "as faltas e a data de admissão de cada um, e gera os cartões.\n"
                 "Horas extras não vêm no holerite — preencha na coluna abaixo "
                 "clicando duas vezes, ou depois na planilha.",
        ).pack(anchor="w")

        acoes = ttk.Frame(pai)
        acoes.pack(fill="x", pady=(16, 0))

        ttk.Button(
            acoes, text="Abrir holerite (PDF)", style="Secundario.TButton",
            command=self.abrir_holerite,
        ).pack(side="left")

        self.btn_gerar_holerite = ttk.Button(
            acoes, text="Gerar todos os cartões", style="Principal.TButton",
            command=self.gerar_do_holerite, state="disabled",
        )
        self.btn_gerar_holerite.pack(side="left", padx=(10, 0))

        self.btn_salvar_planilha = ttk.Button(
            acoes, text="Salvar planilha para conferir", style="Secundario.TButton",
            command=self.salvar_planilha_do_holerite, state="disabled",
        )
        self.btn_salvar_planilha.pack(side="left", padx=(10, 0))

        quadro = ttk.Labelframe(pai, text=" Funcionários encontrados ", padding=10)
        quadro.pack(fill="both", expand=True, pady=(16, 0))

        colunas = ("nome", "faltas", "extras", "extras100", "inicio", "aviso")
        self.lista_holerite = ttk.Treeview(
            quadro, columns=colunas, show="headings", height=12
        )
        for coluna, titulo, largura in (
            ("nome", "Funcionário", 205),
            ("faltas", "Faltas", 50),
            ("extras", "Extras 50%", 80),
            ("extras100", "Extras 100%", 85),
            ("inicio", "Dia inicial", 70),
            ("aviso", "Observação", 175),
        ):
            self.lista_holerite.heading(coluna, text=titulo)
            self.lista_holerite.column(coluna, width=largura)

        self.lista_holerite.pack(fill="both", expand=True, side="left")
        self.lista_holerite.bind("<Double-1>", self._editar_celula_holerite)

        rolagem = ttk.Scrollbar(
            quadro, orient="vertical", command=self.lista_holerite.yview
        )
        rolagem.pack(side="right", fill="y")
        self.lista_holerite.configure(yscrollcommand=rolagem.set)

        self.registros_holerite = []

    def _montar_aba_lote(self, pai):
        explicacao = ttk.Labelframe(pai, text=" Como funciona ", padding=14)
        explicacao.pack(fill="x")

        passos = (
            "1. Clique em \"Criar planilha em branco\" e salve o arquivo.\n"
            "2. Preencha uma linha por funcionário (empresa, nome, mês, ano, "
            "horas extras, faltas, atestados).\n"
            "3. Clique em \"Importar planilha e gerar\" e selecione o arquivo preenchido."
        )
        ttk.Label(explicacao, text=passos, justify="left", wraplength=660).pack(anchor="w")

        acoes = ttk.Frame(pai)
        acoes.pack(fill="x", pady=(16, 0))

        ttk.Button(
            acoes, text="Criar planilha em branco", style="Secundario.TButton",
            command=self.criar_planilha_modelo,
        ).pack(side="left")

        self.btn_importar = ttk.Button(
            acoes, text="Importar planilha e gerar", style="Principal.TButton",
            command=self.importar_planilha,
        )
        self.btn_importar.pack(side="left", padx=(10, 0))

        resultado = ttk.Labelframe(pai, text=" Resultado ", padding=10)
        resultado.pack(fill="both", expand=True, pady=(16, 0))

        self.lista_resultado = ttk.Treeview(
            resultado, columns=("funcionario", "situacao"), show="headings", height=8
        )
        self.lista_resultado.heading("funcionario", text="Funcionário")
        self.lista_resultado.heading("situacao", text="Situação")
        self.lista_resultado.column("funcionario", width=280)
        self.lista_resultado.column("situacao", width=360)
        self.lista_resultado.pack(fill="both", expand=True, side="left")

        rolagem = ttk.Scrollbar(
            resultado, orient="vertical", command=self.lista_resultado.yview
        )
        rolagem.pack(side="right", fill="y")
        self.lista_resultado.configure(yscrollcommand=rolagem.set)

    def _montar_rodape(self):
        rodape = ttk.Frame(self.janela, padding=(20, 8))
        rodape.pack(fill="x")

        self.var_status = StringVar(value="Pronto.")
        ttk.Label(rodape, textvariable=self.var_status, style="Status.TLabel").pack(anchor="w")

    # ---------------- Ações ----------------
    def _atualizar_resumo_empresa(self):
        empresa = cadastro.obter_empresa(self.var_empresa.get())
        self.lbl_resumo.configure(
            text=f"{empresa['nome']}\nCNPJ: {empresa['cnpj']}\n"
            + cadastro.resumo_jornada(empresa)
        )

    def _escolher_pasta(self, titulo="Onde salvar os cartões?"):
        """Pergunta a pasta de destino. Devolve None se o usuário cancelar."""
        escolhida = filedialog.askdirectory(
            title=titulo,
            initialdir=str(self.ultima_pasta),
            mustexist=False,
        )
        if not escolhida:
            return None

        self.ultima_pasta = Path(escolhida)
        return self.ultima_pasta

    def _status(self, mensagem):
        self.var_status.set(mensagem)
        self.janela.update_idletasks()

    def gerar_individual(self):
        try:
            mes = [m for m, nome in MESES_PT.items() if nome.title() == self.var_mes.get()][0]
            ano = int(self.spin_ano.get())
            ultimo_dia = calendar.monthrange(ano, mes)[1]

            if not self.entry_nome.get().strip():
                raise ValueError("Informe o nome do funcionário.")

            pasta = self._escolher_pasta()
            if pasta is None:
                self._status("Geração cancelada.")
                return

            caminho = gerar_cartao(
                pasta_saida=pasta,
                empresa_codigo=self.var_empresa.get(),
                nome=self.entry_nome.get().strip(),
                mes=mes,
                ano=ano,
                horas_extras=self._numero(self.entry_horas.get(), "Extras 50%"),
                horas_extras_100=self._numero(self.entry_horas_100.get(), "Extras 100%"),
                faltas=int(self._numero(self.entry_faltas.get(), "Faltas")),
                atestados=int(self._numero(self.entry_atestados.get(), "Atestados")),
                dia_inicio=int(self._numero(self.entry_inicio.get(), "Dia inicial", padrao=1)),
                dia_fim=int(self._numero(self.entry_fim.get(), "Dia final", padrao=ultimo_dia)),
            )

            self._status(f"Cartão gerado: {caminho}")
            messagebox.showinfo(
                "Cartão gerado",
                f"Cartão de {self.entry_nome.get().strip()} gerado com sucesso.\n\n{caminho}",
            )

        except Exception as erro:
            self._status("Falha ao gerar o cartão.")
            messagebox.showerror("Não foi possível gerar", str(erro))

    def abrir_holerite(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar o PDF dos holerites",
            filetypes=[("PDF", "*.pdf")],
        )
        if not caminho:
            return

        self._status("Lendo o holerite...")
        try:
            registros = holerite.ler_holerite(caminho)
        except Exception as erro:
            self._status("Não foi possível ler o holerite.")
            messagebox.showerror("Não foi possível ler o holerite", str(erro))
            return

        for registro in registros:
            registro["dia_inicio"] = holerite.dia_inicial_por_admissao(registro)
            registro["atestados"] = 0

        self.registros_holerite = registros
        self._recarregar_lista_holerite()

        self.btn_gerar_holerite.configure(state="normal")
        self.btn_salvar_planilha.configure(state="normal")

        competencia = f"{registros[0]['mes']:02d}/{registros[0]['ano']}"
        empresa = registros[0]["empresa_codigo"] or "?"
        self._status(
            f"{len(registros)} funcionário(s) — {empresa}, competência {competencia}."
        )

    def _recarregar_lista_holerite(self):
        self.lista_holerite.delete(*self.lista_holerite.get_children())
        for indice, registro in enumerate(self.registros_holerite):
            self.lista_holerite.insert(
                "", "end", iid=str(indice),
                values=(
                    registro["nome"],
                    registro["faltas"],
                    registro["horas_extras"],
                    registro["horas_extras_100"],
                    registro["dia_inicio"],
                    "; ".join(registro["avisos"]),
                ),
            )

    def _editar_celula_holerite(self, evento):
        """Duplo clique em Faltas, Horas extras ou Dia inicial edita o valor."""
        item = self.lista_holerite.identify_row(evento.y)
        coluna = self.lista_holerite.identify_column(evento.x)
        if not item or coluna not in ("#2", "#3", "#4", "#5"):
            return

        campo, rotulo = {
            "#2": ("faltas", "Faltas"),
            "#3": ("horas_extras", "Horas extras de 50%"),
            "#4": ("horas_extras_100", "Horas extras de 100%"),
            "#5": ("dia_inicio", "Dia inicial"),
        }[coluna]

        registro = self.registros_holerite[int(item)]
        resposta = simpledialog.askstring(
            rotulo,
            f"{rotulo} de {registro['nome']}:",
            initialvalue=str(registro[campo]),
            parent=self.janela,
        )
        if resposta is None:
            return

        try:
            valor = float(str(resposta).strip().replace(",", "."))
        except ValueError:
            messagebox.showerror("Valor inválido", f"'{resposta}' não é um número.")
            return

        registro[campo] = valor if campo.startswith("horas_extras") else int(valor)
        self._recarregar_lista_holerite()

    def salvar_planilha_do_holerite(self):
        caminho = filedialog.asksaveasfilename(
            title="Salvar planilha preenchida",
            defaultextension=".xlsx",
            initialfile="Funcionários do mês.xlsx",
            filetypes=[("Planilha do Excel", "*.xlsx")],
        )
        if not caminho:
            return

        try:
            planilha.criar_planilha_modelo(caminho, self.registros_holerite)
            self._status(f"Planilha salva: {caminho}")
            messagebox.showinfo("Planilha salva", str(caminho))
        except Exception as erro:
            messagebox.showerror("Não foi possível salvar", str(erro))

    def gerar_do_holerite(self):
        pendentes = [
            r for r in self.registros_holerite if not r.get("empresa_codigo")
        ]
        if pendentes:
            messagebox.showerror(
                "Empresa não reconhecida",
                "O CNPJ do holerite não corresponde a nenhuma empresa cadastrada.",
            )
            return

        pasta = self._escolher_pasta()
        if pasta is None:
            self._status("Geração cancelada.")
            return

        self.abas.select(2)
        self.lista_resultado.delete(*self.lista_resultado.get_children())

        trabalhos = [
            {
                "pasta_saida": pasta,
                "empresa_codigo": r["empresa_codigo"],
                "nome": r["nome"],
                "mes": r["mes"],
                "ano": r["ano"],
                "horas_extras": r["horas_extras"],
                "horas_extras_100": r["horas_extras_100"],
                "faltas": r["faltas"],
                "atestados": r.get("atestados", 0),
                "dia_inicio": r["dia_inicio"],
                "dia_fim": calendar.monthrange(r["ano"], r["mes"])[1],
            }
            for r in self.registros_holerite
        ]

        self.btn_importar.configure(state="disabled")
        threading.Thread(
            target=self._processar_lote, args=(trabalhos,), daemon=True
        ).start()

    def criar_planilha_modelo(self):
        caminho = filedialog.asksaveasfilename(
            title="Salvar planilha em branco",
            defaultextension=".xlsx",
            initialfile="Funcionários do mês.xlsx",
            filetypes=[("Planilha do Excel", "*.xlsx")],
        )
        if not caminho:
            return

        try:
            planilha.criar_planilha_modelo(caminho)
            self._status(f"Planilha criada: {caminho}")
            messagebox.showinfo(
                "Planilha criada",
                f"Preencha a planilha e depois use \"Importar planilha e gerar\".\n\n{caminho}",
            )
        except Exception as erro:
            messagebox.showerror("Não foi possível criar a planilha", str(erro))

    def importar_planilha(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar planilha preenchida",
            filetypes=[("Planilha do Excel", "*.xlsx")],
        )
        if not caminho:
            return

        try:
            registros = planilha.ler_planilha(caminho)
        except Exception as erro:
            messagebox.showerror("Planilha inválida", str(erro))
            return

        pasta = self._escolher_pasta()
        if pasta is None:
            self._status("Geração cancelada.")
            return

        for registro in registros:
            registro["pasta_saida"] = pasta

        self.lista_resultado.delete(*self.lista_resultado.get_children())
        self.btn_importar.configure(state="disabled")
        threading.Thread(
            target=self._processar_lote, args=(registros,), daemon=True
        ).start()

    def _processar_lote(self, registros):
        """Roda fora da tela; manda os resultados pela fila."""
        gerados = falhas = 0

        for registro in registros:
            nome = registro["nome"]
            try:
                arquivo = gerar_cartao(**registro)
                self.fila.put(("linha", nome, f"Gerado: {Path(arquivo).name}"))
                gerados += 1
            except Exception as erro:
                self.fila.put(("linha", nome, f"ERRO: {erro}"))
                falhas += 1

            self.fila.put(
                ("status", f"Processando... {gerados + falhas}/{len(registros)}")
            )

        pasta = registros[0].get("pasta_saida") if registros else PASTA_SAIDA
        self.fila.put(("fim", gerados, falhas, pasta))

    def _consumir_fila(self):
        """Só a tela mexe na tela: lê o que as gerações produziram."""
        try:
            while True:
                mensagem = self.fila.get_nowait()

                if mensagem[0] == "linha":
                    self.lista_resultado.insert(
                        "", "end", values=(mensagem[1], mensagem[2])
                    )
                elif mensagem[0] == "status":
                    self.var_status.set(mensagem[1])
                elif mensagem[0] == "fim":
                    gerados, falhas, pasta = mensagem[1], mensagem[2], mensagem[3]
                    self.btn_importar.configure(state="normal")
                    self.var_status.set(
                        f"Concluído: {gerados} cartão(ões) gerado(s), {falhas} com erro."
                    )
                    messagebox.showinfo(
                        "Geração concluída",
                        f"{gerados} cartão(ões) gerado(s).\n{falhas} com erro.\n\n"
                        f"Pasta: {pasta}",
                    )
        except queue.Empty:
            pass

        self.janela.after(150, self._consumir_fila)

    def abrir_pasta_saida(self):
        pasta = self.ultima_pasta
        pasta.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(pasta)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(pasta)])
        else:
            subprocess.Popen(["xdg-open", str(pasta)])

    @staticmethod
    def _numero(texto, campo, padrao=0):
        texto = str(texto).strip().replace(",", ".")
        if not texto:
            return padrao
        try:
            return float(texto)
        except ValueError:
            raise ValueError(f"{campo}: '{texto}' não é um número válido.") from None


def abrir():
    janela = Tk()
    AplicacaoCartaoPonto(janela)
    janela.mainloop()
