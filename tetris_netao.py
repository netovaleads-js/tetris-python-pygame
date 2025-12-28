import pygame
import random
import os
import sys

# --- FUNÇÃO PARA CORRIGIR CAMINHO DE ARQUIVO áudio
def caminho_recurso(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CONFIGURAÇÕES ---
TAMANHO_BLOCO = 40 
COLUNAS, LINHAS = 10, 20
LARGURA, ALTURA = COLUNAS * TAMANHO_BLOCO, LINHAS * TAMANHO_BLOCO

PRETO = (10, 10, 15)
BRANCO = (255, 255, 255)
CINZA = (40, 40, 50)
AMARELO = (255, 255, 0)

FORMATOS = {
    'I': [(0, -1), (0, 0), (0, 1), (0, 2)],
    'J': [(0, 0), (-1, 0), (0, 1), (0, 2)],
    'L': [(0, 0), (1, 0), (0, 1), (0, 2)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'S': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'Z': [(0, 0), (1, 0), (0, -1), (-1, -1)]
}
CORES = [(0, 255, 255), (0, 0, 255), (255, 165, 0), (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)]

# --- CLASSES ---
class Particula:
    def __init__(self, x, y, cor):
        self.x, self.y, self.cor = x, y, cor
        self.vx, self.vy = random.uniform(-5, 5), random.uniform(-5, 5)
        self.vida = 255

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 12

    def desenhar(self, superficie):
        if self.vida > 0:
            s = pygame.Surface((8, 8))
            s.set_alpha(self.vida)
            s.fill(self.cor)
            superficie.blit(s, (self.x, self.y))

# --- FUNÇÕES ---
def criar_peca():
    tipo = random.choice(list(FORMATOS.keys()))
    return {'x': COLUNAS // 2, 'y': 1, 'formato': FORMATOS[tipo], 'cor': random.choice(CORES)}

def validar_movimento(peca, grade, dx=0, dy=0, novo_formato=None):
    formato = novo_formato if novo_formato else peca['formato']
    for b in formato:
        nx, ny = peca['x'] + b[0] + dx, peca['y'] + b[1] + dy
        if nx < 0 or nx >= COLUNAS or ny >= LINHAS: return False
        if ny >= 0 and grade[ny][nx] != PRETO: return False
    return True

def eliminar_linhas(grade, particulas):
    linhas_a_remover = []
    # Primeiro, identifica todas as linhas que estão cheias
    for y in range(LINHAS):
        if PRETO not in grade[y]:
            linhas_a_remover.append(y)
    
    # Se houver linhas cheias, gera partículas e remove
    for y in linhas_a_remover:
        for x in range(COLUNAS):
            cor_bloco = grade[y][x]
            for _ in range(6):
                particulas.append(Particula(x*TAMANHO_BLOCO + 20, y*TAMANHO_BLOCO + 20, cor_bloco))
        
        # Remove a linha e adiciona uma nova no topo
        del grade[y]
        grade.insert(0, [PRETO for _ in range(COLUNAS)])
    
    if len(linhas_a_remover) > 0:
        try: som_limpar.play()
        except: pass
            
    return len(linhas_a_remover)

def desenhar_texto(texto, tamanho, cor, x, y):
    fonte = pygame.font.SysFont("Arial", tamanho, bold=True)
    superficie = fonte.render(texto, True, cor)
    retangulo = superficie.get_rect(center=(x, y))
    tela.blit(superficie, retangulo)

def desenhar_bloco_estilizado(superficie, cor, x, y, tamanho=TAMANHO_BLOCO):
    pygame.draw.rect(superficie, cor, (x, y, tamanho, tamanho))
    pygame.draw.rect(superficie, BRANCO, (x, y, tamanho, tamanho), 1)

def tela_inicio():
    tela.fill(PRETO)
    desenhar_texto("TETRIS Netão", 45, AMARELO, LARGURA//2, ALTURA//2 - 50)
    desenhar_texto("Pressione uma tecla", 22, BRANCO, LARGURA//2, ALTURA//2 + 20)
    pygame.display.update()
    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                esperando = False

# --- INICIALIZAÇÃO ---
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tetris do Netão v2.0 - Expert")
clock = pygame.time.Clock()

try:
    pygame.mixer.init()
    # Usamos o caminho_recurso aqui:
    pygame.mixer.music.load(caminho_recurso("musica_fundo.mp3"))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    
    som_limpar = pygame.mixer.Sound(caminho_recurso("limpar_linha.wav"))
except Exception as e:
    print(f"Erro ao carregar áudio: {e}")
    som_limpar = None

# Otimização da Grade
grid_surface = pygame.Surface((LARGURA, ALTURA))
grid_surface.fill(PRETO)
for y in range(LINHAS):
    for x in range(COLUNAS):
        pygame.draw.rect(grid_surface, CINZA, (x*TAMANHO_BLOCO, y*TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

# CHAMADA DA TELA DE INÍCIO
tela_inicio()

# --- VARIÁVEIS DO JOGO ---
grade = [[PRETO for _ in range(COLUNAS)] for _ in range(LINHAS)]
lista_particulas = []
peca_atual, proxima_peca = criar_peca(), criar_peca()
pontos = 0
nivel = 1
linhas_totais = 0
tempo_queda = 0
velocidade_base = 400

# --- LOOP PRINCIPAL ---
rodando = True
while rodando:
    velocidade_atual = max(100, velocidade_base - (nivel - 1) * 50)
    tela.blit(grid_surface, (0, 0))
    tempo_queda += clock.get_rawtime()
    clock.tick()

    for e in pygame.event.get():
        if e.type == pygame.QUIT: rodando = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LEFT and validar_movimento(peca_atual, grade, dx=-1): peca_atual['x'] -= 1
            if e.key == pygame.K_RIGHT and validar_movimento(peca_atual, grade, dx=1): peca_atual['x'] += 1
            if e.key == pygame.K_UP:
                f = [(-y, x) for x, y in peca_atual['formato']]
                if validar_movimento(peca_atual, grade, novo_formato=f): peca_atual['formato'] = f
            if e.key == pygame.K_DOWN and validar_movimento(peca_atual, grade, dy=1): peca_atual['y'] += 1

    if tempo_queda > velocidade_atual:
        if validar_movimento(peca_atual, grade, dy=1): 
            peca_atual['y'] += 1
        else:
            for b in peca_atual['formato']:
                gx, gy = peca_atual['x'] + b[0], peca_atual['y'] + b[1]
                if gy >= 0: grade[gy][gx] = peca_atual['cor']
            
            # --- Lógica de Linhas Simultâneas e Pontuação ---
            linhas_ganhas = eliminar_linhas(grade, lista_particulas)
            
            # Multiplicador de pontos por combo
            if linhas_ganhas == 1: pontos += 100
            elif linhas_ganhas == 2: pontos += 300
            elif linhas_ganhas == 3: pontos += 500
            elif linhas_ganhas >= 4: pontos += 800
            
            linhas_totais += linhas_ganhas
            nivel = (linhas_totais // 5) + 1
            
            peca_atual, proxima_peca = proxima_peca, criar_peca()
            if not validar_movimento(peca_atual, grade): rodando = False
        tempo_queda = 0

    # Desenhos
    for y in range(LINHAS):
        for x in range(COLUNAS):
            if grade[y][x] != PRETO: desenhar_bloco_estilizado(tela, grade[y][x], x*TAMANHO_BLOCO, y*TAMANHO_BLOCO)

    for b in peca_atual['formato']:
        desenhar_bloco_estilizado(tela, peca_atual['cor'], (peca_atual['x']+b[0])*TAMANHO_BLOCO, (peca_atual['y']+b[1])*TAMANHO_BLOCO)

    for p in lista_particulas[:]:
        p.atualizar(); p.desenhar(tela)
        if p.vida <= 0: lista_particulas.remove(p)

    # UI
    desenhar_texto(f"PONTOS: {pontos}", 22, AMARELO, 85, 30)
    desenhar_texto(f"LEVEL: {nivel}", 20, BRANCO, 70, 65)
    desenhar_texto("PRÓXIMA:", 18, BRANCO, LARGURA - 75, 30)
    for b in proxima_peca['formato']:
        desenhar_bloco_estilizado(tela, proxima_peca['cor'], LARGURA - 85 + (b[0]*20), 65 + (b[1]*20), 20)
    
    pygame.display.update()

# Game Over
tela.fill(PRETO)
desenhar_texto("GAME OVER", 55, (255, 0, 0), LARGURA//2, ALTURA//2)
desenhar_texto(f"PONTUAÇÃO FINAL: {pontos}", 25, BRANCO, LARGURA//2, ALTURA//2 + 60)
pygame.display.update()
pygame.time.delay(3000)
pygame.quit()