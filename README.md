Ludo em Python

Jogo de Ludo desenvolvido em Python com duas formas de jogar:

Interface gráfica (Frontend): tabuleiro interativo, controle pelo mouse e dado clicável.

Terminal: versão em texto mantida no mesmo arquivo.

Requisitos

Python 3.10 ou superior recomendado.

A interface gráfica utiliza tkinter, que normalmente já acompanha o Python no Windows.

Não são necessárias bibliotecas externas para executar o jogo.

Arquivos

ludo_frontend.py
README.md

Como executar

Interface gráfica

Abra o terminal na pasta do projeto e execute:

python ludo_frontend.py --gui

A versão gráfica apresenta o tabuleiro e permite jogar utilizando o mouse.

Versão de terminal

Para jogar no terminal:

python ludo_frontend.py --terminal

Se o programa for executado sem argumento, ele poderá apresentar a opção de escolher a interface disponível.

Interface gráfica

Na versão gráfica:

Escolha a quantidade de jogadores.

Configure quais cores serão controladas por humanos ou bots.

O Azul é a cor humana padrão.

Clique no botão do dado para lançar.

Depois do lançamento, os peões que podem ser movimentados ficam disponíveis para seleção.

Clique no peão desejado para realizar o movimento.

O jogo informa capturas, jogadas extras e outros acontecimentos na interface.

Controles

Ação

Controle

Lançar dado

Clique no botão do dado

Escolher peão

Clique no peão disponível

Novo jogo

Botão de novo jogo

Interação geral

Mouse

Regras implementadas

O jogo possui quatro cores:

🔴 Vermelho

🟢 Verde

🟡 Amarelo

🔵 Azul

Cada cor possui quatro peões.

Saída da base

Um peão que está na base pode sair quando o jogador tirar:

1

6

O peão entra na casa inicial da sua cor.

Movimento

Os peões percorrem a trilha comum e depois entram na reta final da própria cor.

Para chegar ao centro é necessário respeitar a regra de movimento definida no código.

Captura

Quando um peão termina seu movimento em uma casa ocupada por um peão adversário, o adversário é capturado e retorna para sua base.

Somente as casas iniciais são protegidas contra captura.

As casas com estrela não são consideradas casas seguras.

Jogada extra

O jogador pode receber uma jogada extra quando:

tira 6;

captura um peão adversário;

leva um peão ao centro, quando essa regra está habilitada.

Quando um bot tira 6, ele realiza a jogada e continua automaticamente para a próxima jogada, sem ficar aguardando uma ação do usuário.

Três 6 seguidos

Quando a regra está habilitada, tirar três 6 consecutivos faz o jogador perder a vez.

Vitória

O jogador vence quando consegue levar os quatro peões da sua cor ao centro.

Bots

Os bots utilizam a lógica de decisão presente no código para escolher entre os movimentos disponíveis.

A escolha considera fatores como:

progresso do peão;

possibilidade de chegar ao centro;

possibilidade de capturar adversários;

saída da base;

segurança da posição;

risco de ser capturado;

possibilidade de entrar na reta final.

Configurações

O comportamento do jogo pode ser ajustado nas constantes do arquivo ludo_frontend.py.

Entre as configurações existentes estão:

BONUS_CAPTURA = True
BONUS_CHEGADA = True
TRES_SEIS_PERDE_VEZ = True
CASAS_ESTRELA_SEGURAS = False

Significado

Configuração

Função

BONUS_CAPTURA

Permite jogada extra após captura

BONUS_CHEGADA

Permite jogada extra ao chegar ao centro

TRES_SEIS_PERDE_VEZ

Ativa a regra dos três 6 seguidos

CASAS_ESTRELA_SEGURAS

Define se estrelas são casas seguras

Na configuração atual, as casas com estrela não são protegidas.

Estrutura básica

O projeto mantém o motor do jogo separado conceitualmente da interface.

O mesmo conjunto de regras é utilizado pela versão de terminal e pela interface gráfica, evitando que as duas versões tenham regras diferentes.

As principais partes do código incluem:

configuração do tabuleiro;

posições da trilha;

posições das bases;

retas finais;

estado dos peões;

validação de movimentos;

captura;

vitória;

inteligência dos bots;

interface gráfica;

interface de terminal.

Solução de problemas

python não é reconhecido

Verifique se o Python está instalado e adicionado ao PATH.

No Windows, também pode tentar:

py --version

e executar:

py ludo_frontend.py --gui

Erro relacionado ao tkinter

No Windows, o instalador oficial do Python normalmente inclui o Tkinter.

Se a instalação do Python foi feita de forma personalizada, reinstale o Python incluindo o componente Tcl/Tk and IDLE.

O bot parece parado

Durante o turno do bot, a interface executa automaticamente as ações necessárias.

Em especial, quando o bot tira 6, ele deve realizar a jogada e continuar para a jogada extra automaticamente.

Objetivo do projeto

O objetivo é oferecer uma implementação completa e interativa do Ludo em Python, permitindo jogar contra bots e utilizar uma interface gráfica com tabuleiro e interação pelo mouse, mantendo também a versão tradicional em terminal.

Licença

Projeto desenvolvido para fins educacionais e de estudo de programação em Python.