from prompt_toolkit.shortcuts.progress_bar.base import E
from traitlets.traitlets import Bool
from enum import Enum
from functools import partial

class Color(Enum):
    WHITE = 0
    BLACK = 1

##################################################################3
class Peca:
  color: Color
  dama: bool = False

  def __init__(self, p_color):
    self.color = p_color

  def valor(self):
    r = 'w'
    if self.color == Color.BLACK:
      r = 'b'
    if self.dama:
      r = r.upper()
    return r

  def direcao(self):
    r = 1
    if self.color == Color.BLACK:
      r = -1
    return r

##################################################################3
class Fundo:
  color: Color
  lin: int
  col: int

  def __init__(self, p_color, p_lin, p_col):
    self.color = p_color
    self.lin = p_lin
    self.col = p_col

  def valor(self):
    r = ' '
    if self.color == Color.BLACK:
      r = 'X'
    return r


##################################################################3
class Tabuleiro:
  tamanho: int
  ocupa: int
  valores: list = []
  fundo: list = []
  movimentos: list = []
  proxCor: Color
  comidas: list = []
  n_jogadas: int

  def __init__(self, p_tamanho = 8, p_ocupa = 2):
    self.tamanho = p_tamanho
    self.ocupa = p_ocupa
    self.fundo = []
    self.valores = []
    self.comidas = []
    self.proxCor = Color.WHITE
    self.n_jogadas = 0

    for l in range(self.tamanho):
      lf = []
      lv = []
      for c in range(self.tamanho):
        v = None
        if (c + l) % 2 == 0:
          f = Fundo(Color.WHITE, l, c)
          if c < self.ocupa:
            v = Peca(Color.WHITE)
          if c >= self.tamanho - self.ocupa:
            v = Peca(Color.BLACK)
        else:
          f = Fundo(Color.BLACK, l, c)
        lf.append(f)
        lv.append(v)
      self.fundo.append(lf)
      self.valores.append(lv)

  def toString(self):
    r = ''
    for l in self.fundo:
      for c in l:
        if c.color == Color.WHITE:
          p = self.valores[c.lin][c.col]
          if p is None:
            r = r + ' '
          else:
            r = r + p.valor()
    return r

  def print(self):
    tam = 3
    #Imprime a primeira linha
    l = self.fundo[0]
    n = 0
    txt = '|'
    for c in l:
      letra = chr(n + 65)
      txt = txt + ' ' + letra + ' |'
      n = n + 1
    print('-'*len(txt))
    print(txt)
    print('-'*(len(txt)+2))

    #imprime o resto
    n = 1
    txt='Comidas: '
    for c in self.comidas:
      txt = txt + f'{c.valor()},'
    print(txt)

    for l in self.fundo:
      txt = '|'
      cnt = '|'
      for c in l:
        p = self.valores[c.lin][c.col]
        txt = txt + c.valor() * tam + '|'
        if p is None:
          cnt = cnt + c.valor() * tam + '|'
        else:
          cnt = cnt + ' ' + p.valor() + ' |'
      txt = txt + ' |'
      cnt = cnt + f'{n}|'
      print(txt)
      print(cnt)
      print(txt)
      print('-'*len(txt))
      n = n + 1

  def eValido(self, lin, col):
    if lin < 0 or lin >= self.tamanho:
      return False
    if col < 0 or col >= self.tamanho:
      return False
    return True

  def lerMovimentosPeca(self, peca, lin, col):
    if peca is None:
      return
    if self.proxCor != peca.color:
      return
    d = peca.direcao()
    ldc = [-1, 1]
    ldl = [-1, 1]
    t = self.tamanho
    ln = lin
    cn = col

    de = (lin, col)
    for dl in ldl:
      for dc in ldc:
        comida = None #Peca a ser comida
        for s in range(1, t):
          ln = lin + s * dl
          cn = col + s * dc
          if not self.eValido(ln, cn):
            break
          p_d = self.valores[ln][cn]
          pos_p_d = (ln, cn)
          if p_d is None: #Esta de destino esta vazia
            if not peca.dama and dc != d and comida is None: #Uma peca não pode ser mover para atrás a não ser para comer
              break
            para = (ln,cn)
            m = Movimento(de, para, self, comida)
            self.movimentos.append(m)
            if peca.dama:
              continue
            else:
              break #peca so anda uma casa
          #encontrou uma casa ocupada
          if p_d.color == peca.color: #o destino e mesma cor que a sua, pare
            break
          if comida is not None: #Ja comeu 1 e vai encontra outa do adversário, pare
            break
          comida=pos_p_d #a peca de destino e da cor oposta. Vai pegar na proxima rodada

  def lerMovimentosPeca1(self, peca, lin, col):
    if peca is None:
      return
    if self.proxCor != peca.color:
      return
    d = peca.direcao()
    ldc = [ d ]
    ldl = [ -1 , 1 ]
    t = 2
    if peca.dama:
      ldc = [-1, 1]
      t = self.tamanho
    ln = lin
    cn = col

    de = (lin, col)
    for dc in ldc:
      for dl in ldl:
        comida = None #Peca a ser comida
        for s in range(1, t):
          ln = lin + s * dl
          cn = col + s * dc
          if not self.eValido(ln, cn):
            break
          p_d = self.valores[ln][cn]
          pos_p_d = (ln, cn)
          if p_d is None: #Esta de destino esta vazia
            para = (ln,cn)
            m = Movimento(de, para, self, comida)
            self.movimentos.append(m)
            continue
          if p_d.color == peca.color: #o destino e mesma cor que a sua, pare
            break
          if comida is not None: #Ja comeu 1 e vai encontra outa do adversário, pare
            break
          #PARA PECA SIMPLES###############
          if not peca.dama: #verifica se pode ir para o proximo para comer a peca
            ln_n = lin + (s + 1) * dl
            cn_n = col + (s + 1) * dc
            if not self.eValido(ln_n, cn_n): #Não tem proxima casa
              break
            p_d_n = self.valores[ln_n][cn_n]
            if p_d_n is not None: #Esta destino apos não esta vazia
              break
            #executa o movimento de comer
            para = (ln_n,cn_n)
            comida=pos_p_d
            m = Movimento(de, para, self, comida)
            self.movimentos.append(m)
            break
          #PARA DAMA###############
          comida=pos_p_d #a peca de destino e da cor oposta. Vai pegar na proxima rodada

  def lerMovimentos(self):
    self.movimentos = []
    for l in self.fundo:
      for c in l:
        p = self.valores[c.lin][c.col]
        self.lerMovimentosPeca(p, c.lin, c.col)


  def imprimirMovimentos(self):
    for m in self.movimentos:
      m.print()

  def imprimirMovLinha(self):
    txt = ''
    for m in self.movimentos:
      txt = txt + m.converteTXT() + ','
    print(txt)

  def copiarDados(self, tab):
    self.valores = []
    for lv in tab.valores:
      n_lv = []
      for v in lv:
        vc = None
        if v is not None:
          vc = Peca(v.color)
          vc.dama = v.dama
        n_lv.append(vc)
      self.valores.append(n_lv)
    self.proxCor = tab.proxCor
    self.n_jogadas = tab.n_jogadas

  def executarMovimento(self, movi):
    if movi.come is not None: #Se tem uma peca retirada
      c = self.valores[movi.come[0]][movi.come[1]]
      self.comidas.append(c)
      self.valores[movi.come[0]][movi.come[1]] = None
    p = self.valores[movi.de[0]][movi.de[1]]
    self.valores[movi.de[0]][movi.de[1]] = None
    self.valores[movi.para[0]][movi.para[1]] = p
    #Decide a promoção para a damas
    if p.color == Color.WHITE and movi.para[1] == self.tamanho -1:
      p.dama = True
    if p.color == Color.BLACK and movi.para[1] == 0:
      p.dama = True
    self.n_jogadas = self.n_jogadas + 1

    #Define o proxima cor a mover
    if self.proxCor == Color.WHITE:
      self.proxCor = Color.BLACK
    else:
      self.proxCor = Color.WHITE

  def lerMovimento(self, de, para):
    print('l_m', de, para)
    for m in self.movimentos:
      if m.de == de and m.para == para:
        return m
    return None

  def verificarGanhador(self):
    if self.n_jogadas > 200:
      return True, None #Empate por jogo longo
    if len(self.movimentos) > 0:
      return None, None
    w = 0
    b = 0
    for lv in self.valores:
      for v in lv:
        if v is not None:
          if v.color == Color.WHITE:
            w = w + 1
          else:
            b = b + 1

    if w == b: # Empate
      return True, None

    if w > b: # Branco ganha
      return False, Color.WHITE

    return False, Color.BLACK

##################################################################3
class Movimento:
  de: tuple = ()
  para: tuple = ()
  tab_de: Tabuleiro
  tab_para: Tabuleiro
  come: tuple = ()

  def __init__(self, p_de, p_para, p_tab, p_come):
    self.de = p_de
    self.para = p_para
    self.come = p_come
    self.valor = 0
    self.nivel = -1
    self.tab_de = Tabuleiro(p_tab.tamanho, p_tab.ocupa)
    self.tab_para = Tabuleiro(p_tab.tamanho, p_tab.ocupa)
    self.tab_de.copiarDados(p_tab)
    self.tab_para.copiarDados(p_tab)
    self.tab_para.executarMovimento(self)

  def converte(self, pos):
    return f'{ chr(pos[1] + 65) }{ pos[0]+1 }'

  def converteTXT(self):
    txt = ''
    if self.come is not None:
      pc = self.converte(self.come)
      txt = f'come ={pc}'
    de = self.converte(self.de)
    para = self.converte(self.para)
    return f'{ de }-{ para }{ txt }'

  def print(self):
    txt = self.converteTXT()
    print(txt)

  def expandir(self, p_nivel):
    self.nivel = p_nivel - 1
    self.tab_para.lerMovimentos()
    if self.nivel > 0:
      for m in self.tab_para.movimentos:
        m.expandir(self.nivel)

  def avaliar(self, p_cor, p_valor):
    ganhar = float(15)
    empatar = float(1)
    comerDama = float(8)
    fazerDama = float(7)
    comerPeca = float(2)
    self.valor = None
    if p_cor == self.tab_de.proxCor:
      fator = float(1)
    else:
      fator = float(-1)
    empate,ganhador = self.tab_para.verificarGanhador()
    r = random.random() / 10
    v_valor = p_valor + r * fator
    if empate is not None: #Houve fim do jogo
      #print('FIM', self.nivel, v_valor)
      if empate:
        self.valor = v_valor
      else:
        if ganhador == p_cor:
          self.valor = ganhar
        else:
          self.valor = -ganhar
    else: # jogo não acabou
      #print('OK', self.nivel, v_valor)
      if self.come is not None: #Houve a captura de uma peça
        capt = self.tab_de.valores[self.come[0]][self.come[1]]
        if capt.dama:
          v_valor = v_valor + comerDama * fator
        else:
          v_valor = v_valor + comerPeca * fator
      p_de = self.tab_de.valores[self.de[0]][self.de[1]]
      p_para = self.tab_para.valores[self.para[0]][self.para[1]]
      if not p_de.dama and p_para.dama: # fez uma dama
        v_valor = v_valor + fazerDama * fator
      #print('ZERO', self.nivel, len(self.tab_para.movimentos))
      if self.nivel == 0 or len(self.tab_para.movimentos) == 0:
         self.valor = v_valor
      else:
        for m in self.tab_para.movimentos:
          m.avaliar(p_cor, v_valor)

  def lerValor(self, p_min=False):
    #print('lerValor',self.valor,self.nivel)
    if len(self.tab_para.movimentos) == 0 or self.nivel == 0:
      #print('zer',self.valor,self.nivel)
      return self.valor
    vmin = not p_min
    if vmin:
      self.valor = self.lerValorMinimo(vmin)
      #print('min',self.valor,self.nivel)
    else:
      self.valor = self.lerValorMaximo(vmin)
      #print('max',self.valor,self.nivel)
    return self.valor

  def lerValorMinimo(self, p_min=False):
    ve = None
    for m in self.tab_para.movimentos:
      v = m.lerValor(p_min)
      if ve is None:
        ve = v
      elif ve > v:
        ve = v
    #print('MINIMO',ve)
    return ve

  def lerValorMaximo(self, p_min=False):
    ve = None
    for m in self.tab_para.movimentos:
      v = m.lerValor(p_min)
      if ve is None:
        ve = v
      elif ve < v:
        ve = v
    #print('MAXIMO',ve)
    return ve

  def eDama(self):
    peca = self.tab_para.valores[self.para[0]][self.para[1]]
    return peca.dama

  def exibirNivel(self, p_nivel):
    vnivel = p_nivel + 1
    for m in self.tab_para.movimentos:
      txt = ' ' * vnivel
      d = 'D' if m.eDama() else'P'
      print(f'{txt}{ m.converteTXT() }-({ m.valor }):{self.tab_para.proxCor.name}<{m.nivel}>{d}.')
      if (m.nivel > 0):
        m.exibirNivel(vnivel)

##################################################################3
class Jogador:
  color: Color

  def __init__(self, p_color):
    self.color = p_color

  def converte(self, txt) -> int:
    tc, tl = txt
    c = ord(tc.upper()) - ord("A")
    l = int(tl) - 1
    return (l,c)

  def lerMovimento(self, tabuleiro):
    while True:
      txt = input(f"{self.color.name}'s joga: ").strip()
      if txt == '':
        print('Saiu do Jogo')
        return None
      l = txt.split('-')
      if len(l) < 2:
        print('Erro: Faltou-')
        continue
      de = self.converte(l[0])
      para = self.converte(l[1])
      m = tabuleiro.lerMovimento(de,para)
      if m is None:
        print("Movimento invalido")
        continue
      return m

##################################################################3
import random
import time
class JogadorAleatorio:
  color: Color

  def __init__(self, p_color):
    self.color = p_color

  def converte(self, txt) -> int:
    tc, tl = txt
    c = ord(tc.upper()) - ord("A")
    l = int(tl) - 1
    return (l,c)

  def lerMovimento(self, tabuleiro):
    if not tabuleiro.movimentos:
      print('Saiu do Jogo')
      return None
    m = random.choice(tabuleiro.movimentos)
    m.print()
    #time.sleep(1)
    #txt = input("Tecle <ENTER> para continuar")
    return m

##################################################################3
import random
import time
class JogadorMinMax:
  color: Color
  nivel: int

  def __init__(self, p_color, p_nivel, p_eventos):
    self.color = p_color
    self.nivel = p_nivel
    self.eventos = p_eventos

  def converte(self, txt) -> int:
    tc, tl = txt
    c = ord(tc.upper()) - ord("A")
    l = int(tl) - 1
    return (l,c)

  def lerMovimento(self, tabuleiro, exibir=False):
    if not tabuleiro.movimentos:
      print('Saiu do Jogo')
      return None

    print('Inicio', self.nivel)
    for m in tabuleiro.movimentos:
      m.expandir(self.nivel)


    for m in tabuleiro.movimentos:
      valor = float(0)
      m.avaliar(self.color, valor)
    p_min = False

    ve = None
    me = None
    vMin = False
    for m in tabuleiro.movimentos:
      v = m.lerValor(vMin)
      self.eventos.adicionarEvento(m,v)
      #txt = input(f'valor:{v} Tecle<enter>')
      if ve is None:
        ve = v
        me = m
      elif ve < v:
        ve = v
        me = m

    nivel = 1
    print(f'Escolhido:{ me.converteTXT() }-({ ve }):{self.color.name}')
    print(f'Tabuleiro:[{me.tab_para.toString()}]')
    if exibir:
      for m in tabuleiro.movimentos:
        txt = ' ' * nivel
        print(f'{txt}{ m.converteTXT() }-({ m.valor }):{self.color.name}.')
        m.exibirNivel(nivel)

    #txt = input(f'{self.color.name} Tecle<enter>')
    return me

class TipoJogador(Enum):
    HUMANO = 0
    ALEATORIO = 1
    MINMAX = 2
##################################################################3
import os

class Evento:
  def __init__(self, p_color, p_tab, p_valor, p_classe = None):
    self.color = p_color
    self.tab = p_tab
    if p_classe is None:
      self.classe = self.classificar(p_valor)
    else:
      self.classe = p_classe

  def classificar(self, p_valor):
    if p_valor <= -7:
      return 0
    if p_valor > -7 and p_valor <= -1.5:
      return 1
    if p_valor > -1.5 and p_valor < 1.5:
      return 2
    if p_valor >= 1.5 and p_valor < 7:
      return 3
    if p_valor >= 7:
      return 4

  def toString(self):
    return f'{self.color},{self.tab},{self.classe}\n'

class ListaEvento:
  tamanho: int

  def __init__(self, p_tamanho, p_path = '/content/drive/MyDrive/IA'):
    self.lista = {}
    self.tamanho = p_tamanho
    self.path = p_path
    self.lerArquivo()

  def adicionarEvento(self, p_move: Movimento, p_valor: float):
    tab = p_move.tab_para.toString()
    cor = p_move.tab_de.proxCor.value
    key = f'{cor}:{tab}'
    if key in self.lista:
      return
    e = Evento(cor, tab, p_valor)
    self.lista[key] = e

  def print(self):
    for key in self.lista:
      e = self.lista[key]
      print(e.toString())

  def lerNomeArquivo(self):
    return f'damas_{self.tamanho}.csv'

  def lerArquivo(self):
    os.chdir(self.path)
    arq = self.lerNomeArquivo()
    if not os.path.isfile(arq):
      return
    with open(arq, 'r') as f:
      lines = f.readlines()
      for line in lines:
        l = line.split(',')
        cor = int(l[0])
        tab= l[1]
        classe = int(l[2])
        e = Evento(cor, tab, 0, classe)
        key = f'{cor}:{tab}'
        self.lista[key] = e
      f.close()

  def salvarArquivo(self):
    os.chdir(self.path)
    arq = self.lerNomeArquivo()

    l = []
    for key in self.lista:
      e = self.lista[key]
      l.append(e.toString())

    print('itens:',len(l))
    with open(arq, 'w') as f:
      f.writelines(l)
      f.close()

##################################################################3
class Damas:
  tabuleiro: Tabuleiro
  j_branco: Jogador
  j_preto: Jogador
  lsEvento: ListaEvento

  def __init__(self, tamanho = 8, p_ocupa = 2, p_tipoJW = TipoJogador.HUMANO, p_tipoJB = TipoJogador.HUMANO ):
    #self.lsEvento = ListaEvento(tamanho)
    self.tabuleiro = Tabuleiro(tamanho, p_ocupa)
    self.tipoJW = p_tipoJW
    self.tipoJB = p_tipoJB
    self.j_branco = self.criarJogador(p_tipoJW, Color.WHITE)
    self.j_preto = self.criarJogador(p_tipoJB, Color.BLACK)
    self.tabuleiro.lerMovimentos()

  def criarJogador(self, p_tipo, p_cor):
    j = None
    if(p_tipo == TipoJogador.HUMANO):
      j = Jogador(p_cor)
    elif(p_tipo == TipoJogador.ALEATORIO):
      j = JogadorAleatorio(p_cor)
    elif(p_tipo == TipoJogador.MINMAX):
      j = JogadorMinMax(p_cor, 3, self.lsEvento)
    return j

  def converte(self, txt) -> int:
    tc, tl = txt
    c = ord(tc.upper()) - ord("A")
    l = int(tl) - 1
    return (l,c)

  def mover(self, l_move):
    for t_move in l_move:
      l = t_move.split('-')
      de = self.converte(l[0])
      para = self.converte(l[1])
      m = self.tabuleiro.lerMovimento(de,para)
      if m is None:
        return
      self.tabuleiro.executarMovimento(m)
      self.tabuleiro.lerMovimentos()

  def verificarFim(self):
    empate, j_g = self.tabuleiro.verificarGanhador()
    if empate is not None: # Jogo acabou
      if empate is True:
        print('Jogo empatado')
        return True
      if j_g == Color.WHITE:
        print('Brancos vencem')
        return True
      print('Pretos vencem')
      return True
    return False

  def proximoJogador(self):
    j = self.j_branco
    if self.tabuleiro.proxCor == Color.BLACK:
      j = self.j_preto
    return j

  def jogar(self):
    erro = False
    while True:
      #output.clear()
      self.tabuleiro.print()
      self.tabuleiro.imprimirMovLinha()
      if self.verificarFim():
        self.lsEvento.salvarArquivo()
        return
      j = self.proximoJogador()

      m = j.lerMovimento(self.tabuleiro)
      if m is None:
       return
      self.tabuleiro.executarMovimento(m)
      self.tabuleiro.lerMovimentos()

D = Damas(tamanho=6, p_ocupa =2, p_tipoJW = TipoJogador.HUMANO, p_tipoJB = TipoJogador.ALEATORIO)
D.jogar()
