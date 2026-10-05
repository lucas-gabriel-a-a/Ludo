#!/usr/bin/env python3
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
   (As casas marcadas com '*' tambem sao seguras - veja CASAS_ESTRELA_SEGURAS.)
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
CASAS_ESTRELA_SEGURAS = True    # casas '*' tambem protegem contra captura
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
ESTRELAS = {(c["inicio"] + 8) % TRILHA for c in CORES} if CASAS_ESTRELA_SEGURAS else set()
SEGURAS = set(INICIOS) | ESTRELAS


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
    ativas = {2: [0, 2], 3: [0, 1, 2], 4: [0, 1, 2, 3]}[n]
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


def main():
    while True:
        jogo = configurar()
        jogo.jogar()
        r = entrada("\nJogar novamente? (s/n) [n]: ").strip().lower()
        if r != "s":
            break
    print("Até a próxima!")


if __name__ == "__main__":
    main()
