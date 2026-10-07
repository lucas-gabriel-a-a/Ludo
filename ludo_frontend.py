"""
LUDO em Python (terminal)  -  4 cores, 4 peoes por cor.

Como jogar:   python ludo.py

REGRAS IMPLEMENTADAS
 - Dado aleatorio de 1 a 6 a cada lancamento.
 - Cada cor tem 4 peoes, que comecam na base.
 - Para sair da base, o jogador precisa tirar 1 ou 6 (o peao vai para a
   casa inicial da sua cor).
 - O jogador escolhe qual peao mover (quando ha mais de um movimento possivel).
 - Captura: se o peao para numa casa ocupada por peao de OUTRA cor, esse
   peao volta para a base. Peoes da mesma cor podem dividir a casa.
 - A casa inicial de cada cor e protegida: nela nao ha captura.
   (Somente as casas iniciais de cada cor sao seguras contra captura.)
 - Cada peao percorre a trilha comum (51 casas apos a casa inicial) e entra
   na sua reta final colorida (5 casas), terminando no centro.
 - Para chegar ao centro e preciso numero exato. Se o dado for maior que o
   necessario, o peao avanca ate o centro e volta o restante.
 - Tirar 6 da direito a jogar de novo (tres 6 seguidos = perde a vez).
   Capturar um peao ou levar um peao ao centro tambem da jogada extra.
 - O jogo termina quando os 4 peoes de uma cor chegam ao centro.
"""
import os
import random
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------------------------------------------------
# CONFIGURACOES (ajuste como preferir)
# ----------------------------------------------------------------------
BONUS_CAPTURA = True            # captura da jogada extra
BONUS_CHEGADA = True            # chegar ao centro da jogada extra
TRES_SEIS_PERDE_VEZ = True      # 3 seis seguidos: perde a vez
CASAS_ESTRELA_SEGURAS = False   # estrelas nao protegem; somente casas iniciais sao seguras
PAUSA_BOT = float(os.environ.get("LUDO_PAUSA", "0.9"))  # segundos
LIMPAR_TELA = os.environ.get("LUDO_LIMPAR", "1") == "1"
USAR_CORES = os.environ.get("NO_COLOR") is None
HISTORICO = 7                   # linhas de mensagens exibidas sob o tabuleiro

if os.name == "nt":
    os.system("")  # habilita codigos ANSI no terminal do Windows

# ----------------------------------------------------------------------
# CONSTANTES DO TABULEIRO
# ----------------------------------------------------------------------
TRILHA = 52        # casas da trilha comum
PEOES = 4          # peoes por cor
BASE = -1          # passo de um peao na base
FIM_TRILHA = 50    # ultimo passo na trilha comum (51 a 55 = reta final)
FINAL = 56         # passo do centro (chegada)

# Cada peao tem um "passo" (progresso): -1 base, 0 casa inicial,
# 1..50 trilha comum, 51..55 reta final, 56 chegada.

CORES = [
    {"nome": "Vermelho", "sigla": "Vm", "inicio": 0,  "fundo": "41", "texto": "91"},
    {"nome": "Verde",    "sigla": "Vd", "inicio": 13, "fundo": "42", "texto": "92"},
    {"nome": "Amarelo",  "sigla": "Am", "inicio": 26, "fundo": "43", "texto": "93"},
    {"nome": "Azul",     "sigla": "Az", "inicio": 39, "fundo": "44", "texto": "94"},
]

# Coordenadas (linha, coluna) das 52 casas da trilha, em sentido horario,
# numa grade 15x15. A casa 0 e a inicial do Vermelho.
CAMINHO = [
    (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
    (5, 6), (4, 6), (3, 6), (2, 6), (1, 6), (0, 6),
    (0, 7), (0, 8),
    (1, 8), (2, 8), (3, 8), (4, 8), (5, 8),
    (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14),
    (7, 14), (8, 14),
    (8, 13), (8, 12), (8, 11), (8, 10), (8, 9),
    (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8),
    (14, 7), (14, 6),
    (13, 6), (12, 6), (11, 6), (10, 6), (9, 6),
    (8, 5), (8, 4), (8, 3), (8, 2), (8, 1), (8, 0),
    (7, 0), (6, 0),
]
assert len(CAMINHO) == TRILHA

RETA = [
    [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5)],
    [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7)],
    [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9)],
    [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7)],
]
BASES = [
    [(1, 1), (1, 4), (4, 1), (4, 4)],
    [(1, 10), (1, 13), (4, 10), (4, 13)],
    [(10, 10), (10, 13), (13, 10), (13, 13)],
    [(10, 1), (10, 4), (13, 1), (13, 4)],
]
CENTRO = (7, 7)

INICIOS = {c["inicio"]: k for k, c in enumerate(CORES)}
ESTRELAS = set()
SEGURAS = set(INICIOS)


# ----------------------------------------------------------------------
# FUNCOES AUXILIARES
# ----------------------------------------------------------------------
def pintar(txt, codigos):
    if not USAR_CORES:
        return txt
    return f"\033[{codigos}m{txt}\033[0m"


def nome_colorido(cor):
    c = CORES[cor]
    return pintar(c["nome"], "1;" + c["texto"])


def limpar():
    os.system("cls" if os.name == "nt" else "clear")


def entrada(msg):
    try:
        return input(msg)
    except (EOFError, KeyboardInterrupt):
        print("\nJogo encerrado.")
        sys.exit(0)


def pedir_int(msg, minimo, maximo, padrao):
    while True:
        r = entrada(msg).strip()
        if r == "":
            return padrao
        if r.isdigit() and minimo <= int(r) <= maximo:
            return int(r)
        print(f"  Digite um numero entre {minimo} e {maximo}.")


def celula_trilha(cor, passo):
    """Indice (0..51) da casa da trilha onde o peao esta (passo 0..50)."""
    return (CORES[cor]["inicio"] + passo) % TRILHA


def coordenada(cor, idx, passo):
    if passo == BASE:
        return BASES[cor][idx]
    if passo <= FIM_TRILHA:
        return CAMINHO[celula_trilha(cor, passo)]
    if passo < FINAL:
        return RETA[cor][passo - FIM_TRILHA - 1]
    return CENTRO


def status_peao(p):
    if p == BASE:
        return "base"
    if p == FINAL:
        return "FINAL"
    if p == 0:
        return "inicio"
    if p > FIM_TRILHA:
        return f"reta {p - FIM_TRILHA}/6"
    return f"{p} passos"


# ----------------------------------------------------------------------
# JOGO
# ----------------------------------------------------------------------
class Jogo:
    def __init__(self, ativas, humanos):
        self.ativas = ativas                 # cores em jogo, na ordem de turno
        self.humanos = set(humanos)
        self.peoes = {c: [BASE] * PEOES for c in ativas}
        self.hist = []

    # ---------------- mensagens ----------------
    def dizer(self, msg):
        print(msg)
        self.hist.append(msg)
        self.hist = self.hist[-HISTORICO:]

    # ---------------- regras ----------------
    def destino(self, cor, i, dado):
        """Passo de destino do peao i com o dado (None se nao puder mover)."""
        p = self.peoes[cor][i]
        if p == FINAL:
            return None
        if p == BASE:
            return 0 if dado in (1, 6) else None
        novo = p + dado
        if novo > FINAL:                     # passou do centro: volta o resto
            novo = FINAL - (novo - FINAL)
        return novo

    def opcoes(self, cor, dado):
        """Lista de peoes que podem ser movidos (so um peao da base e listado)."""
        res = []
        base_listada = False
        for i, p in enumerate(self.peoes[cor]):
            if p == FINAL:
                continue
            if p == BASE:
                if dado in (1, 6) and not base_listada:
                    res.append(i)
                    base_listada = True
                continue
            res.append(i)
        return res

    def inimigos_em(self, cor, passo):
        """Peoes de outras cores que seriam capturados ao parar nesse passo."""
        if passo < 0 or passo > FIM_TRILHA:
            return []
        cel = celula_trilha(cor, passo)
        if cel in SEGURAS:
            return []
        achados = []
        for outra, lista in self.peoes.items():
            if outra == cor:
                continue
            for j, q in enumerate(lista):
                if 0 <= q <= FIM_TRILHA and celula_trilha(outra, q) == cel:
                    achados.append((outra, j))
        return achados

    def mover(self, cor, i, dado):
        novo = self.destino(cor, i, dado)
        self.peoes[cor][i] = novo
        capturados = self.inimigos_em(cor, novo)
        for oc, j in capturados:
            self.peoes[oc][j] = BASE
        return novo, capturados, novo == FINAL

    def venceu(self, cor):
        return all(p == FINAL for p in self.peoes[cor])

    def descrever(self, cor, i, dado):
        p = self.peoes[cor][i]
        novo = self.destino(cor, i, dado)
        if p == BASE:
            txt = "sai da base para a casa inicial"
        elif p + dado > FINAL:
            txt = f"avança {FINAL - p} e volta {p + dado - FINAL} (passou do final)"
        elif novo == FINAL:
            txt = "chega ao FINAL"
        elif novo > FIM_TRILHA:
            txt = f"entra na reta final (casa {novo - FIM_TRILHA} de 6)"
        else:
            txt = f"avança {dado} casa(s)"
        capt = self.inimigos_em(cor, novo)
        if capt:
            nomes = ", ".join(f"{CORES[o]['nome']} {j + 1}" for o, j in capt)
            txt += f" e CAPTURA {nomes}"
        return txt

    # ---------------- bot ----------------
    def ameacado(self, cor, passo):
        if not (0 <= passo <= FIM_TRILHA):
            return False
        cel = celula_trilha(cor, passo)
        if cel in SEGURAS:
            return False
        for o, lista in self.peoes.items():
            if o == cor:
                continue
            for q in lista:
                if 0 <= q <= FIM_TRILHA:
                    d = (cel - celula_trilha(o, q)) % TRILHA
                    if 1 <= d <= 6:
                        return True
        return False

    def pontuar(self, cor, i, dado):
        p = self.peoes[cor][i]
        novo = self.destino(cor, i, dado)
        s = novo * 0.5
        if novo == FINAL:
            s += 100
        capt = self.inimigos_em(cor, novo)
        if capt:
            s += 70 + 10 * len(capt)
        if p == BASE:
            s += 40
        if self.ameacado(cor, p):
            s += 25
        if self.ameacado(cor, novo):
            s -= 25
        elif novo > FIM_TRILHA or (novo <= FIM_TRILHA and celula_trilha(cor, novo) in SEGURAS):
            s += 10
        if p != BASE and p + dado > FINAL:
            s -= 40
        return s + random.random()

    def escolher_bot(self, cor, opcoes, dado):
        return max(opcoes, key=lambda i: self.pontuar(cor, i, dado))

    # ---------------- humano ----------------
    def escolher_humano(self, cor, opcoes, dado):
        if len(opcoes) == 1:
            return opcoes[0]
        print("Escolha o peão para mover:")
        for i in opcoes:
            print(f"  [{i + 1}] Peão {i + 1} ({status_peao(self.peoes[cor][i])}): "
                  f"{self.descrever(cor, i, dado)}")
        while True:
            r = entrada("Peão: ").strip()
            if r.isdigit() and int(r) - 1 in opcoes:
                return int(r) - 1
            print("  Opção inválida.")

    # ---------------- tela ----------------
    def desenhar(self, cor_vez=None):
        if LIMPAR_TELA:
            limpar()
        cel = {}
        for r in range(15):
            for c in range(15):
                cel[(r, c)] = ("   ", "0")

        for k, cor in enumerate(CORES):                    # quadrantes das bases
            r0 = 0 if k in (0, 1) else 9
            c0 = 0 if k in (0, 3) else 9
            for r in range(r0, r0 + 6):
                for c in range(c0, c0 + 6):
                    cel[(r, c)] = ("   ", cor["fundo"])
            for pos in BASES[k]:
                cel[pos] = (" o ", "30;" + cor["fundo"])
            for pos in RETA[k]:
                cel[pos] = (" = ", "30;" + cor["fundo"])

        for idx, pos in enumerate(CAMINHO):                # trilha
            if idx in INICIOS:
                cel[pos] = (" S ", "1;30;" + CORES[INICIOS[idx]]["fundo"])
            elif idx in ESTRELAS:
                cel[pos] = (" * ", "1")
            else:
                cel[pos] = (" . ", "2")
        cel[CENTRO] = (" F ", "1;30;47")

        ocupantes = {}
        finalizados = 0
        for c in self.ativas:                              # peoes
            for i, p in enumerate(self.peoes[c]):
                if p == FINAL:
                    finalizados += 1
                    continue
                ocupantes.setdefault(coordenada(c, i, p), []).append((c, i))
        for pos, lista in ocupantes.items():
            cores_aqui = {c for c, _ in lista}
            if len(lista) == 1:
                c, i = lista[0]
                txt = f"{CORES[c]['sigla']}{i + 1}"
            else:
                c = next(iter(cores_aqui))
                txt = f"x{len(lista)} "
            estilo = "1;" + CORES[c]["texto"] + ";40" if len(cores_aqui) == 1 else "1;97;40"
            cel[pos] = (txt, estilo)
        if finalizados:
            cel[CENTRO] = (f"F{finalizados}".ljust(3), "1;30;47")

        print()
        for r in range(15):
            print("  " + "".join(pintar(*cel[(r, c)]) for c in range(15)))
        print()
        print("  S = casa inicial (protegida)   * = casa segura   = = reta final   F = chegada")
        print("  xN = N peões na mesma casa     o = vaga na base")
        print()
        for c in self.ativas:
            marca = ">>" if c == cor_vez else "  "
            tipo = "" if c in self.humanos else " (bot)"
            partes = "  ".join(f"{i + 1}:{status_peao(p)}" for i, p in enumerate(self.peoes[c]))
            print(f" {marca} {nome_colorido(c)}{tipo}: {partes}")
        print()
        for linha in self.hist:
            print("  " + linha)
        print()

    # ---------------- loop principal ----------------
    def jogar(self):
        vez = 0
        while True:
            cor = self.ativas[vez]
            nome = nome_colorido(cor)
            humano = cor in self.humanos
            seis = 0
            while True:
                self.desenhar(cor)
                if humano:
                    entrada(f"Vez de {CORES[cor]['nome']}. Pressione ENTER para lançar o dado...")
                else:
                    print(f"Vez de {CORES[cor]['nome']} (bot)...")
                    time.sleep(PAUSA_BOT)

                dado = random.randint(1, 6)
                self.dizer(f"{nome} tirou [{dado}].")
                seis = seis + 1 if dado == 6 else 0
                if TRES_SEIS_PERDE_VEZ and seis == 3:
                    self.dizer("  Três 6 seguidos! Perdeu a vez.")
                    time.sleep(PAUSA_BOT)
                    break

                extra = dado == 6
                opcoes = self.opcoes(cor, dado)
                if not opcoes:
                    self.dizer("  Nenhum movimento possível.")
                    if not humano:
                        time.sleep(PAUSA_BOT)
                else:
                    if humano:
                        i = self.escolher_humano(cor, opcoes, dado)
                    else:
                        i = self.escolher_bot(cor, opcoes, dado)
                    texto = self.descrever(cor, i, dado)
                    _, capturados, chegou = self.mover(cor, i, dado)
                    self.dizer(f"  Peão {i + 1} {texto}.")
                    if self.venceu(cor):
                        self.desenhar(cor)
                        print("=" * 50)
                        print(f"  *** {CORES[cor]['nome'].upper()} VENCEU O JOGO! ***")
                        print("=" * 50)
                        return cor
                    if capturados and BONUS_CAPTURA:
                        extra = True
                    if chegou and BONUS_CHEGADA:
                        extra = True
                    if not humano:
                        time.sleep(PAUSA_BOT)

                if not extra:
                    break
                self.dizer("  Jogada extra!")
            vez = (vez + 1) % len(self.ativas)


# ----------------------------------------------------------------------
# CONFIGURACAO INICIAL
# ----------------------------------------------------------------------
def configurar():
    if LIMPAR_TELA:
        limpar()
    print("=" * 50)
    print("                      L U D O")
    print("=" * 50)
    print(__doc__.split("REGRAS IMPLEMENTADAS")[1].split('"""')[0].rstrip())
    print()
    n = pedir_int("Número de jogadores (2 a 4) [4]: ", 2, 4, 4)
    ativas = {2: [3, 0], 3: [3, 0, 1], 4: [3, 0, 1, 2]}[n]
    humanos = []
    for k, c in enumerate(ativas):
        padrao = "h" if k == 0 else "b"
        while True:
            r = entrada(f"{CORES[c]['nome']} é (H)umano ou (B)ot? [{padrao.upper()}]: ").strip().lower()
            r = r or padrao
            if r in ("h", "b"):
                break
            print("  Digite H ou B.")
        if r == "h":
            humanos.append(c)
    return Jogo(ativas, humanos)


# ----------------------------------------------------------------------
# FRONTEND GRAFICO (Tkinter)
# ----------------------------------------------------------------------
# A versao grafica usa a mesma classe Jogo e as mesmas regras da versao
# de terminal. O mouse e usado para lancar o dado e escolher o peao.
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    tk = None
    messagebox = None


class LudoGUI:
    """Interface grafica opcional para o mesmo motor de regras do Ludo."""

    TAM = 46
    MARGEM = 18
    CORES_GUI = ["#e53935", "#43a047", "#fbc02d", "#1e88e5"]
    CORES_CLARAS = ["#ffcdd2", "#c8e6c9", "#fff9c4", "#bbdefb"]
    FUNDO = "#eeeeee"

    def __init__(self, root, jogo):
        self.root = root
        self.jogo = jogo
        self.vez = 0
        self.dado = None
        self.opcoes = []
        self.aguardando_dado = True
        self.seis_seguidos = 0
        self.encerrado = False
        self.auto_id = None

        root.title("Ludo - Frontend")
        root.resizable(False, False)
        root.configure(bg=self.FUNDO)

        self.canvas = tk.Canvas(
            root,
            width=15 * self.TAM + 2 * self.MARGEM,
            height=15 * self.TAM + 2 * self.MARGEM,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=8, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.clique_tabuleiro)

        painel = tk.Frame(root, bg=self.FUNDO)
        painel.grid(row=0, column=1, sticky="n", padx=(0, 14), pady=14)

        self.lbl_turno = tk.Label(
            painel, text="", font=("Arial", 16, "bold"),
            bg=self.FUNDO, wraplength=230
        )
        self.lbl_turno.pack(pady=(0, 10))

        self.lbl_dado = tk.Label(
            painel, text="Dado: -", font=("Arial", 30, "bold"),
            width=7, height=2, relief="ridge", bg="white"
        )
        self.lbl_dado.pack(pady=5)

        self.btn_dado = tk.Button(
            painel, text="🎲 LANÇAR DADO", font=("Arial", 12, "bold"),
            width=20, height=2, command=self.lancar_dado
        )
        self.btn_dado.pack(pady=8)

        self.lbl_instrucao = tk.Label(
            painel, text="", font=("Arial", 11),
            bg=self.FUNDO, wraplength=230, justify="left"
        )
        self.lbl_instrucao.pack(pady=8)

        self.lista = tk.Label(
            painel, text="", font=("Consolas", 9),
            bg="white", justify="left", anchor="w",
            relief="groove", padx=8, pady=8
        )
        self.lista.pack(fill="x", pady=8)

        tk.Button(
            painel, text="Novo jogo", width=20,
            command=self.novo_jogo
        ).pack(pady=4)

        tk.Button(
            painel, text="Fechar", width=20,
            command=root.destroy
        ).pack(pady=4)

        self.log = []
        self.atualizar()
        self.agendar_bot()

    def adicionar_log(self, texto):
        self.log.append(texto)
        self.log = self.log[-6:]

    def pos_pixel(self, pos):
        r, c = pos
        x = self.MARGEM + c * self.TAM + self.TAM / 2
        y = self.MARGEM + r * self.TAM + self.TAM / 2
        return x, y

    def retangulo(self, pos, margem=1):
        r, c = pos
        x1 = self.MARGEM + c * self.TAM + margem
        y1 = self.MARGEM + r * self.TAM + margem
        x2 = self.MARGEM + (c + 1) * self.TAM - margem
        y2 = self.MARGEM + (r + 1) * self.TAM - margem
        return x1, y1, x2, y2

    def desenhar_tabuleiro(self):
        self.canvas.delete("all")

        # Fundo das quatro bases.
        for k, cor in enumerate(CORES):
            r0 = 0 if k in (0, 1) else 9
            c0 = 0 if k in (0, 3) else 9
            x1 = self.MARGEM + c0 * self.TAM
            y1 = self.MARGEM + r0 * self.TAM
            x2 = self.MARGEM + (c0 + 6) * self.TAM
            y2 = self.MARGEM + (r0 + 6) * self.TAM
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=self.CORES_CLARAS[k], outline=self.CORES_GUI[k], width=2
            )

            # Vagas dos peoes.
            for i, pos in enumerate(BASES[k]):
                x, y = self.pos_pixel(pos)
                self.canvas.create_oval(
                    x - 15, y - 15, x + 15, y + 15,
                    fill="white", outline=self.CORES_GUI[k], width=2
                )

        # Trilha.
        for idx, pos in enumerate(CAMINHO):
            fill = "white"
            outline = "#777777"
            width = 1
            if idx in INICIOS:
                k = INICIOS[idx]
                fill = self.CORES_CLARAS[k]
                outline = self.CORES_GUI[k]
                width = 3
            elif idx in ESTRELAS:
                fill = "#eeeeee"
                outline = "#555555"
                width = 2

            x1, y1, x2, y2 = self.retangulo(pos, 1)
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill, outline=outline, width=width
            )
            if idx in ESTRELAS:
                self.canvas.create_text(
                    (x1+x2)/2, (y1+y2)/2, text="★",
                    fill="#555555", font=("Arial", 13, "bold")
                )

        # Retas finais.
        for k, reta in enumerate(RETA):
            for pos in reta:
                x1, y1, x2, y2 = self.retangulo(pos, 1)
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.CORES_CLARAS[k],
                    outline=self.CORES_GUI[k],
                    width=1
                )

        # Centro.
        x1, y1, x2, y2 = self.retangulo(CENTRO, 0)
        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="white", outline="#333333", width=2
        )
        self.canvas.create_text(
            (x1+x2)/2, (y1+y2)/2, text="F",
            font=("Arial", 18, "bold")
        )

        # Marca visual dos movimentos disponíveis.
        if self.dado is not None and not self.encerrado:
            cor = self.jogo.ativas[self.vez]
            for i in self.opcoes:
                p = self.jogo.peoes[cor][i]
                pos = coordenada(cor, i, p)
                x, y = self.pos_pixel(pos)
                self.canvas.create_oval(
                    x - 20, y - 20, x + 20, y + 20,
                    outline=self.CORES_GUI[cor], width=4,
                    dash=(5, 3), tags=("opcao",)
                )

        self.desenhar_peoes()

    def desenhar_peoes(self):
        ocupantes = {}
        for cor in self.jogo.ativas:
            for i, p in enumerate(self.jogo.peoes[cor]):
                if p == FINAL:
                    continue
                pos = coordenada(cor, i, p)
                ocupantes.setdefault(pos, []).append((cor, i))

        for pos, lista in ocupantes.items():
            total = len(lista)
            base_x, base_y = self.pos_pixel(pos)

            for n, (cor, i) in enumerate(lista):
                # Pequeno deslocamento quando ha mais de um peao na mesma casa.
                offsets = {
                    1: [(0, 0)],
                    2: [(-9, 0), (9, 0)],
                    3: [(-9, -7), (9, -7), (0, 9)],
                    4: [(-9, -9), (9, -9), (-9, 9), (9, 9)],
                }
                ox, oy = offsets[min(total, 4)][n % 4]
                x, y = base_x + ox, base_y + oy
                raio = 11 if total > 1 else 14

                tag = f"peca_{cor}_{i}"
                self.canvas.create_oval(
                    x-raio, y-raio, x+raio, y+raio,
                    fill=self.CORES_GUI[cor],
                    outline="black", width=2,
                    tags=(tag,)
                )
                self.canvas.create_text(
                    x, y, text=str(i+1), fill="white",
                    font=("Arial", 9, "bold"), tags=(tag,)
                )

    def atualizar(self):
        self.desenhar_tabuleiro()
        if self.encerrado:
            return

        cor = self.jogo.ativas[self.vez]
        nome = CORES[cor]["nome"]
        humano = cor in self.jogo.humanos

        self.lbl_turno.config(
            text=f"Vez: {nome}" + (" (Você)" if humano else " (Bot)"),
            fg=self.CORES_GUI[cor]
        )
        self.lbl_dado.config(text=f"Dado: {self.dado if self.dado else '-'}")

        if self.dado is None:
            self.lbl_instrucao.config(
                text="Clique em 'LANÇAR DADO' para começar a jogada."
                if humano else "O bot está pensando..."
            )
        else:
            if humano:
                self.lbl_instrucao.config(
                    text="Clique em um peão destacado para movê-lo."
                    if self.opcoes else "Nenhum movimento possível."
                )
            else:
                self.lbl_instrucao.config(text="O bot está escolhendo um peão...")

        linhas = []
        for c in self.jogo.ativas:
            marca = ">> " if c == cor else "   "
            estados = " | ".join(
                f"{i+1}:{status_peao(p)}"
                for i, p in enumerate(self.jogo.peoes[c])
            )
            linhas.append(f"{marca}{CORES[c]['nome']}\n    {estados}")
        if self.log:
            linhas.append("\n" + "\n".join(self.log))
        self.lista.config(text="\n".join(linhas))

        # Botão só fica disponível para humano sem dado lançado.
        self.btn_dado.config(
            state=("normal" if humano and self.dado is None else "disabled")
        )

    def lancar_dado(self):
        if self.encerrado or self.dado is not None:
            return

        cor = self.jogo.ativas[self.vez]
        if cor not in self.jogo.humanos:
            return

        dado = random.randint(1, 6)
        self.dado = dado
        self.seis_seguidos = self.seis_seguidos + 1 if dado == 6 else 0
        self.adicionar_log(f"{CORES[cor]['nome']} tirou {dado}.")

        if TRES_SEIS_PERDE_VEZ and self.seis_seguidos == 3:
            self.adicionar_log("Três 6 seguidos: perdeu a vez.")
            self.root.after(800, self.encerrar_rodada)
            self.atualizar()
            return

        self.opcoes = self.jogo.opcoes(cor, dado)
        if not self.opcoes:
            self.adicionar_log("Nenhum movimento possível.")
            self.root.after(800, self.encerrar_rodada)
        self.atualizar()

    def clique_tabuleiro(self, event):
        if self.encerrado or self.dado is None:
            return

        cor = self.jogo.ativas[self.vez]
        if cor not in self.jogo.humanos or not self.opcoes:
            return

        # Descobre a peça clicada pela distância até seu centro.
        clicado = None
        melhor = 999999
        for i in self.opcoes:
            p = self.jogo.peoes[cor][i]
            x, y = self.pos_pixel(coordenada(cor, i, p))
            dist = (event.x-x)**2 + (event.y-y)**2
            if dist <= 24**2 and dist < melhor:
                melhor = dist
                clicado = i

        if clicado is not None:
            self.executar_movimento(cor, clicado)

    def executar_movimento(self, cor, i):
        dado = self.dado
        texto = self.jogo.descrever(cor, i, dado)
        _, capturados, chegou = self.jogo.mover(cor, i, dado)
        self.adicionar_log(f"Peão {i+1}: {texto}.")

        if self.jogo.venceu(cor):
            self.encerrado = True
            self.atualizar()
            messagebox.showinfo(
                "Fim de jogo",
                f"{CORES[cor]['nome']} venceu o jogo!"
            )
            return

        extra = dado == 6
        if capturados and BONUS_CAPTURA:
            extra = True
        if chegou and BONUS_CHEGADA:
            extra = True

        if extra:
            self.dado = None
            self.opcoes = []
            self.adicionar_log("Jogada extra!")
            self.atualizar()
            # O mesmo jogador continua imediatamente. Para bot, agenda
            # o proximo lancamento em vez de ficar aguardando um clique.
            if cor not in self.jogo.humanos:
                self.agendar_bot()
        else:
            self.encerrar_rodada()

    def encerrar_rodada(self):
        self.dado = None
        self.opcoes = []
        self.vez = (self.vez + 1) % len(self.jogo.ativas)
        self.seis_seguidos = 0
        self.atualizar()
        self.agendar_bot()

    def agendar_bot(self):
        if self.encerrado:
            return
        cor = self.jogo.ativas[self.vez]
        if cor not in self.jogo.humanos:
            if self.auto_id is not None:
                self.root.after_cancel(self.auto_id)
            self.auto_id = self.root.after(900, self.jogada_bot)

    def jogada_bot(self):
        self.auto_id = None
        if self.encerrado:
            return

        cor = self.jogo.ativas[self.vez]
        if cor in self.jogo.humanos:
            return

        dado = random.randint(1, 6)
        self.dado = dado
        self.seis_seguidos = self.seis_seguidos + 1 if dado == 6 else 0
        self.adicionar_log(f"{CORES[cor]['nome']} (bot) tirou {dado}.")

        if TRES_SEIS_PERDE_VEZ and self.seis_seguidos == 3:
            self.adicionar_log("Três 6 seguidos: bot perdeu a vez.")
            self.atualizar()
            self.root.after(700, self.encerrar_rodada)
            return

        opcoes = self.jogo.opcoes(cor, dado)
        self.opcoes = opcoes
        self.atualizar()

        if not opcoes:
            self.root.after(700, self.encerrar_rodada)
            return

        i = self.jogo.escolher_bot(cor, opcoes, dado)
        self.root.after(650, lambda: self.executar_movimento(cor, i))

    def novo_jogo(self):
        if self.auto_id is not None:
            try:
                self.root.after_cancel(self.auto_id)
            except Exception:
                pass

        # Mantem a configuracao atual de cores, humanos e bots.
        self.jogo = Jogo(self.jogo.ativas, self.jogo.humanos)
        self.vez = 0
        self.dado = None
        self.opcoes = []
        self.seis_seguidos = 0
        self.encerrado = False
        self.log = []
        self.atualizar()
        self.agendar_bot()


def configurar_gui(root):
    """Janela inicial da versao grafica.

    Cada cor pode ser configurada independentemente como Humano, Bot ou
    Fora do jogo. Assim e possivel jogar, por exemplo, com 2 humanos,
    2 humanos + 1 bot, ou 2 humanos + 2 bots.
    """
    configuracao = tk.Toplevel(root)
    configuracao.title("Configurar Ludo")
    configuracao.resizable(False, False)
    configuracao.grab_set()

    frame = tk.Frame(configuracao, padx=20, pady=20)
    frame.pack()

    tk.Label(frame, text="LUDO", font=("Arial", 24, "bold")).pack(pady=(0, 8))
    tk.Label(
        frame,
        text="Escolha quais cores participam e quem controla cada uma.",
        justify="left"
    ).pack(pady=(0, 12))

    tk.Label(frame, text="Número de jogadores (2 a 4):").pack(anchor="w")
    numero = tk.IntVar(value=4)
    tk.Spinbox(frame, from_=2, to=4, textvariable=numero, width=5).pack(
        anchor="w", pady=(0, 12)
    )

    nomes = ["Vermelho", "Verde", "Amarelo", "Azul"]
    escolhas = []

    # Azul e Humano como padrao. As demais cores participam como bots,
    # permitindo imediatamente uma partida humano x bots.
    for k, nome in enumerate(nomes):
        padrao = "Humano" if k == 3 else "Bot"
        var = tk.StringVar(value=padrao)
        escolhas.append(var)

        linha = tk.Frame(frame)
        linha.pack(fill="x", pady=3)
        tk.Label(linha, text=f"{nome}:", width=10, anchor="w").pack(side="left")
        tk.OptionMenu(linha, var, "Humano", "Bot", "Fora do jogo").pack(side="left")

    aviso = tk.Label(frame, text="", fg="#c62828", justify="left", wraplength=330)
    aviso.pack(pady=(8, 0))

    def iniciar():
        try:
            n = max(2, min(4, int(numero.get())))
        except (TypeError, ValueError):
            aviso.config(text="Número de jogadores inválido.")
            return

        # A ordem dos turnos segue a ordem das cores no tabuleiro, mas somente
        # as cores marcadas como Humano ou Bot participam.
        ativas = [c for c in range(4) if escolhas[c].get() != "Fora do jogo"]

        if len(ativas) != n:
            aviso.config(text=f"Selecione exatamente {n} cores para participar.")
            return

        humanos = [c for c in ativas if escolhas[c].get() == "Humano"]
        bots = [c for c in ativas if escolhas[c].get() == "Bot"]

        if not humanos:
            aviso.config(text="Escolha pelo menos um jogador humano.")
            return

        # Guarda a configuracao por cor. O Jogo usa o conjunto de humanos,
        # portanto cada cor selecionada conserva exatamente o tipo escolhido.
        configuracao.destroy()
        jogo = Jogo(ativas, humanos)
        LudoGUI(root, jogo)

    tk.Button(
        frame, text="Começar jogo", command=iniciar,
        width=22, height=2
    ).pack(pady=(15, 5))


def iniciar_gui():
    if tk is None:
        print("Tkinter não está disponível nesta instalação do Python.")
        print("Use a versão de terminal ou instale o suporte do Tkinter.")
        return

    root = tk.Tk()
    root.withdraw()
    configurar_gui(root)
    root.deiconify()
    root.mainloop()


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    """
    Por padrão, apresenta a escolha entre terminal e frontend gráfico.
    Também aceita:
        python ludo.py --gui
        python ludo.py --terminal
    """
    if "--gui" in sys.argv:
        iniciar_gui()
        return

    if "--terminal" in sys.argv:
        modo = "t"
    else:
        print("=" * 50)
        print("                    L U D O")
        print("=" * 50)
        print("1 - Versão gráfica (mouse)")
        print("2 - Versão terminal (original)")
        while True:
            modo = entrada("Escolha [1]: ").strip().lower() or "1"
            if modo in ("1", "2", "g", "t"):
                break
            print("Digite 1 ou 2.")

    if modo in ("1", "g"):
        iniciar_gui()
        return

    while True:
        jogo = configurar()
        jogo.jogar()
        r = entrada("\nJogar novamente? (s/n) [n]: ").strip().lower()
        if r != "s":
            break
    print("Até a próxima!")


if __name__ == "__main__":
    main()
