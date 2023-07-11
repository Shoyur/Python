import pygame as py
import webbrowser
import socket
import select


################################################################ DÉCLARATIONS ################################################################

# Limiter les FPS
clock = py.time.Clock()

# Ma version pour affichage au menu de départ
MA_VERSION = "0.7"

# RGB
BRUN = (114,64,34)
ROUGE = (235,1,1)
BLEU = (1,1,235)
JAUNE = (255,255,1)
VERT = (1,120,1)
BLANC = (255,255,255)
TURQUOISE = (1,235,235)
ROSE = (235,1,235)
NOIR = (1,1,1)
BEIGE = (220,140,80) 
CIEL = (80,80,255)

# Barrières
BARRIERES_JOUEUR1 = [0 for i in range(10)]
BARRIERES_JOUEUR2 = [py.Rect(102+i*30, 23, 5, 77) for i in range(10)]
for i in range(0, 10):
    BARRIERES_JOUEUR1[i] = [-1, py.Rect(102+i*30, 540, 5, 77)]
# No. de la barrière sur la souris. -1 = rien, Autre = 0 à 9
# Vertical = 1, Horizontal = 2
BARRIERE_EN_MAIN = [-1, 1]

# Cases des 2 pions, sur 9x9, en [Y, X, #, 0] = [rangée, colonne, couleur, 1 = pion en main]
PION1 = [240, 500, ROUGE, 0]
#.............................PION2 = [240, 140, BLEU]
PION2 = [240, 140, BLEU]

# Méga matrice de départ
MATRICE = [[0 for y in range(17)] for x in range(17)]

# Populer les cases
# [y][x][rect(), couleur, pion]
# y = rangée
# x = colonne
# rect = coordonnées de la case, pour collidepoint et snap
# couleur = normal ou non, si case déplacement possible
# 0 = pas de pion, 1 = pion joueur #1, 2 = pion joueur #2
for y in range(0, 17, 2):
    for x in range(0, 17, 2):
        MATRICE[y][x] = [py.Rect(40+x/2*45, 120+y/2*45, 40, 40), BRUN, 0]

# Populer les SNAPS de barrières
# [y][x][rect(), barrière]
# y = rangée
# x = colonne
# rect = coordonnées pour collidepoint et snap
# barrière : 0 = aucune, 1 = vertical, 2 = horizontal
for y in range(1, 16, 2):
    for x in range(1, 16, 2):
        MATRICE[y][x] = [py.Rect(24+(x+1)/2*45, 104+(y+1)/2*45, 27, 27), 0]

# Bit pour savoir si la partie est terminée
GAGNANT = False

# IP de l'autre joueur
IP_P2 = ""

# À qui le tour, 1 = ici, 2 = l'autre
TOUR = 1

# Lien socket
SOCK_BIND = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_mon_ip = socket.gethostbyname(socket.gethostname())
socket_port = 54325
SOCK_BIND.bind((socket_mon_ip, socket_port))

# Test LAN ou non.
LAN = True


################################################################ FONCTIONS ################################################################



# Mettre les 3 bits de la barrière à 0 ou à 1
def inscrire_obstacle(y, x, sens, bit):
    if sens == 2: MATRICE[y][x-1] = bit; MATRICE[y][x+1] = bit
    else: MATRICE[y-1][x] = bit; MATRICE[y+1][x] = bit



# Vérifie si c'est un snap barrière
def si_snap_barrière(pos):
    for y in range(1, 16, 2):
        for x in range(1, 16, 2):
            if MATRICE[y][x][0].collidepoint(pos): 
                return True, y, x
    return False, False, False



# Vérifie si c'est l'espace est libre pour une barrière
def barrière_espace_libre(y, x):
    if MATRICE[y][x][1] == 0:
        if (BARRIERE_EN_MAIN[1] == 2 and MATRICE[y][x-1] == 0 and MATRICE[y][x+1] == 0) or \
            (BARRIERE_EN_MAIN[1] == 1 and MATRICE[y-1][x] == 0 and MATRICE[y+1][x] == 0):
            return True
    return False



# Vérifie si on ne bloque pas complètement l'autre joueur
# Algorithme "depth first" !!!
def si_chemin_possible(y, x, joueur):
    if joueur == 1: case_pion_y = int((PION1[1]-140)/45*2); case_pion_x = int((PION1[0]-60)/45*2); but = "0."
    elif joueur == 2: case_pion_y = int((PION2[1]-140)/45*2); case_pion_x = int((PION2[0]-60)/45*2); but = "16."
    inscrire_obstacle(y, x, BARRIERE_EN_MAIN[1], 1)
    déplacements_possibles = {}
    for y_d in range(0, 17, 2):
        for x_d in range(0, 17, 2):
            possibles = []
            # Haut, Gauche, Droite, Bas
            if y_d > 0 and MATRICE[y_d-1][x_d] == 0 and (y_d-2 != case_pion_y or x_d != case_pion_x): possibles.append([str(y_d-2) + "." + str(x_d), 1])
            if x_d > 0 and MATRICE[y_d][x_d-1] == 0 and (y_d != case_pion_y or x_d-2 != case_pion_x): possibles.append([str(y_d) + "." + str(x_d-2), 1])
            if x_d < 16 and MATRICE[y_d][x_d+1] == 0 and (y_d != case_pion_y or x_d+2 != case_pion_x): possibles.append([str(y_d) + "." + str(x_d+2), 1])
            if y_d < 16 and MATRICE[y_d+1][x_d] == 0 and (y_d+2 != case_pion_y or x_d != case_pion_x): possibles.append([str(y_d+2) + "." + str(x_d), 1])
            déplacements_possibles[str(y_d) + "." + str(x_d)] = possibles
    début_case_pion = str(case_pion_y) + "." + str(case_pion_x)
    del possibles, case_pion_y, case_pion_x, y_d, x_d
    déplacements_faits = {}
    déplacements_faits[début_case_pion] = déplacements_possibles[début_case_pion]; del début_case_pion
    prochain = [0,0]
    while True:
        # Pour chaque clé, ainsi que le paquet de valeurs attachées
        for case, directions in déplacements_faits.items():
            # Pour chaque direction dans le paquet de directions
            for valeurs in directions:
                # Prochaine valeur à 1, à mettre en prochaine clé || Sortir de la boucle imbriquée
                if prochain[0] == 0 and valeurs[1] == 1: prochain = [1, valeurs[0]]; break
            # Sortir de la boucle principale
            if prochain[0] == 1: break
        # Si aucune à 1 dans les valeurs = pas trouvé de chemin, return False
        if prochain[0] == 0: inscrire_obstacle(y, x, BARRIERE_EN_MAIN[1], 0); return False
        # Sinon, continue
        else:
            # Effacer prochain[1] (prochaine clé) ... dans toutes les values déjà présentes
            for case, directions in déplacements_faits.items():
                for valeurs in directions:
                    if valeurs[0] == prochain[1]: valeurs[1] = 0
            # Effacer aussi les prochaines values ... de toutes les values déjà présentes
            une_seule_fois = ""
            for case, directions in déplacements_faits.items():
                for inc in range(len(directions)):
                    for i in range(len(déplacements_possibles[prochain[1]])):
                        if directions[inc][0] == déplacements_possibles[prochain[1]][i][0] and une_seule_fois != directions[inc][0]: 
                            déplacements_faits[case][inc][1] = 0
                            une_seule_fois = directions[inc][0]
            for i, j in déplacements_possibles[prochain[1]]:
                if i.startswith(but):
                    inscrire_obstacle(y, x, BARRIERE_EN_MAIN[1], 0)
                    return True
            # oui, ajouter la nouvelle entrée
            déplacements_faits[prochain[1]] = déplacements_possibles[prochain[1]]
            # enlever des prochaines valeurs si elles sont déjà dans les clés déjà présentes
            for case, directions in déplacements_faits.items():
                for i in range(len(déplacements_faits[prochain[1]])):
                    if case == déplacements_faits[prochain[1]][i][0]: 
                        déplacements_faits[prochain[1]][i][1] = 0
                        break
        prochain = [0,0]



def placer_la_barrière(y, x, sens):
    barrière = py.Rect(0, 0, 5 if sens == 1 else 77, 77 if sens == 1 else 5)
    barrière.center = MATRICE[y][x][0].center
    BARRIERES_JOUEUR1[BARRIERE_EN_MAIN[0]] = [0, barrière]
    inscrire_obstacle(y, x, sens, 1)
    BARRIERE_EN_MAIN[0] = -1
    BARRIERE_EN_MAIN[1] = 1
    MATRICE[y][x][1] = BARRIERE_EN_MAIN[1]



def reset_cases_possibles():
    PION1[3] = 0
    for y in range(0, 17, 2):
        for x in range(0, 17, 2):
            MATRICE[y][x][1] = BRUN



def vider_buffer_socket(socket):
    entrée = [socket]
    while True:
        données, o, e = select.select(entrée, [], [], 0.0)
        if len(données) == 0: break
        for s in données: s.recv(15)



# Écran de départ pour se connecter
def menu_départ():
    global IP_P2
    global TOUR
    lien_instructions_couleur = BLANC
    texte_haut_textbox = py.font.SysFont('tahoma', 13)
    textbox_actif = False
    textbox_couleur = BLANC
    texte_entré = ""
    texte_sur_surface_font = py.font.SysFont('tahoma', 15)
    tentative_connexion = False
    menu_départ = True
    while menu_départ:
        fond_écran = py.image.load("img_bg_menu.png")
        écran.blit(fond_écran,[0,0])
        écran.blit(texte_haut_textbox.render("Quoridor Online " + MA_VERSION + " par Mike More.", True, BLANC), (30, 400))
        écran.blit(texte_haut_textbox.render("Inspiré du jeu de table Quoridor par Mirko Marchesi.", True, BLANC), (30, 420))
        lien = écran.blit(texte_haut_textbox.render("Clic moi pour les instructions", True, lien_instructions_couleur), (30, 495))
        écran.blit(texte_haut_textbox.render("Entrez l'adresse IP de l'autre joueur et pesez Entrée :", True, BLANC), (30, 515))
        if not tentative_connexion: écran.blit(texte_haut_textbox.render("Votre adresse IP est " + socket_mon_ip, True, BLANC), (30, 575))
        textbox = py.draw.rect(écran, textbox_couleur, py.Rect(30, 540, 150, 30), width=1)
        for event in py.event.get():
            textbox_couleur = CIEL if textbox_actif else BLANC
            if event.type == py.MOUSEBUTTONDOWN:
                pos = event.pos
                if lien.collidepoint(pos): webbrowser.open(r"https://www.gigamic.com/files/catalog/products/rules/quoridor-classic-fr.pdf")
                if textbox.collidepoint(pos): textbox_actif = not textbox_actif
                else: textbox_actif = False
            if event.type == py.KEYDOWN:
                if textbox_actif:
                    if event.key == py.K_RETURN:
                        textbox_actif = False
                        # Il faut essayer de se connecter
                        tentative_connexion = True
                        IP_P2 = texte_entré
                    elif event.key == py.K_BACKSPACE: texte_entré = texte_entré[:-1]
                    else: texte_entré += event.unicode
            if event.type == py.QUIT:
                py.quit()
                exit()
        if tentative_connexion: 
            écran.blit(texte_haut_textbox.render("Tentative de connexion à " + IP_P2 + " (" + str(socket_port) + ") ....", True, BLANC), (30, 595))
        if lien.collidepoint(py.mouse.get_pos()): lien_instructions_couleur = CIEL
        else: lien_instructions_couleur = BLANC
        texte_sur_surface = texte_sur_surface_font.render(texte_entré, True, textbox_couleur)
        écran.blit(texte_sur_surface, (38, 545))
        py.display.update()
        py.display.flip()

        if tentative_connexion: break
    # Tentatives de connexion
    while True:
        données_test = "TEST"
        données_test = données_test.encode("ascii")
        SOCK_BIND.sendto(données_test, (IP_P2, socket_port))
        data2, addr = SOCK_BIND.recvfrom(15) 
        if data2.decode("ascii") == "TEST": break
        clock.tick(10)
    SOCK_BIND.sendto(données_test, (IP_P2, socket_port))
    # Si le présent joueur a le IP le plus grand, c'est lui qui choisi le joueur #1
    if IP_P2.split(".")[-1] > socket_mon_ip.split(".")[-1]: TOUR = 2


# Action lorsqu'un pion atteint le la ligne d'arrivée
def fin_de_partie(joueur):
    global GAGNANT
    global PION1
    global PION2
    dessin(VERT if joueur == 1 else ROUGE)
    while 1:
        for event in py.event.get():
            if event.type == py.MOUSEBUTTONDOWN: 
                for i in range(0, 10):
                    BARRIERES_JOUEUR1[i] = [-1, py.Rect(102+i*30, 540, 5, 77)]
                    BARRIERES_JOUEUR2[i] = py.Rect(102+i*30, 23, 5, 77)
                PION1 = [240, 500, ROUGE, 0]
                PION2 = [240, 140, BLEU]
                for y in range(0, 17, 2):
                    for x in range(0, 17, 2):
                        MATRICE[y][x][2] = 0
                for y in range(1, 16, 2):
                    for x in range(1, 16, 2):
                        MATRICE[y][x][1] = 0
                GAGNANT = False
                return 



################################################################ BOUCLE DE JEU ################################################################



# Mouvements et cliques de souris
def événements():
    global GAGNANT
    global TOUR
    global SOCK_BIND
    couleur_pion_possible = BLANC
    MATRICE[int((PION1[1]-140)/45*2)][int((PION1[0]-60)/45*2)][2] = 1
    MATRICE[int((PION2[1]-140)/45*2)][int((PION2[0]-60)/45*2)][2] = 1

    ################## ÉVÉNEMENTS ##################
    if not LAN or TOUR == 1:
        pos = py.mouse.get_pos()
        for event in py.event.get():
            if event.type == py.QUIT: py.quit(); exit()
            if event.type == py.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Si on clique sur la planche de jeu
                    if pos[1] < 530:
                        # Si une barrière en main, vérifier si on peut la déposer.
                        if BARRIERE_EN_MAIN[0] != -1: 
                            snap_ou_non, y, x = si_snap_barrière(pos)
                            if snap_ou_non and barrière_espace_libre(y, x) and si_chemin_possible(y, x, 1) and si_chemin_possible(y, x, 2):
                                if LAN: 
                                    data = "B." + str(BARRIERE_EN_MAIN[1]) + "." + str(abs(y-16)) + "." + str(abs(x-16))
                                    data = data.encode("ascii")
                                    SOCK_BIND.sendto(data, (IP_P2, socket_port))
                                    print("J'Envoie : ", data) 
                                placer_la_barrière(y, x, BARRIERE_EN_MAIN[1])
                                TOUR = 2
                        # Si on clique le pion
                        elif PION1[3] == 0: 
                            rect = py.Rect(PION1[0]-15,PION1[1]-15, 30, 30)
                            if rect.collidepoint(pos): PION1[3] = 1
                        # Si on a le pion en main, vérifier si on peut le déposer.
                        elif PION1[3] == 1:
                            sortir = 0
                            for y in range(0, 17, 2):
                                for x in range(0, 17, 2):
                                    # rect, couleur, pion
                                    rect, couleur, a = MATRICE[y][x]
                                    if MATRICE[y][x][1] == BLANC and rect.collidepoint(pos):
                                        if y == 0: GAGNANT = 1
                                        y_p = int((PION1[1]-140)/45*2); x_p = int((PION1[0]-60)/45*2)
                                        MATRICE[y_p][x_p][2] = 0
                                        MATRICE[y][x][2] = 1
                                        reset_cases_possibles()
                                        PION1[0] = MATRICE[y][x][0].centerx
                                        PION1[1] = MATRICE[y][x][0].centery
                                        sortir = 1
                                        # LAN :
                                        TOUR = 2
                                        if LAN: 
                                            data = "P." + str(abs(y-16)) + "." + str(abs(x-16))
                                            data = data.encode("ascii")
                                            print("J'envoie : ", data)
                                            SOCK_BIND.sendto(data, (IP_P2, socket_port))
                                        break
                                if sortir == 1: break
                    # Si on clique une barrière libre en bas
                    elif pos[1] > 530 and BARRIERE_EN_MAIN[0] == -1:
                        for i in range(10):
                            if BARRIERES_JOUEUR1[i][1].collidepoint(pos) and BARRIERES_JOUEUR1[i][0] == -1: BARRIERE_EN_MAIN[0] = i; break
                elif event.button == 2: BARRIERE_EN_MAIN[1] = 2 if BARRIERE_EN_MAIN[1] == 1 else 1
                elif event.button == 3: BARRIERE_EN_MAIN[0] = -1; BARRIERE_EN_MAIN[1] = 1; reset_cases_possibles()
            if PION1[3] == 1:
                y_p = int((PION1[1]-140)/45*2); x_p = int((PION1[0]-60)/45*2)
                # Haut, Gauche, Droite, Bas.
                # Si pas bloqué par une barrière
                if y_p > 0 and MATRICE[y_p-1][x_p] == 0:
                    # Si prochaine case n'est pas l'autre pion.
                    if MATRICE[y_p-2][x_p][2] == 0: MATRICE[y_p-2][x_p][1] = couleur_pion_possible
                    # S'il existe une case en sautant par dessus l'autre pion. (L'autre pion est dans cette direction)
                    elif y_p > 2:
                        # ET pas de barrière entre ces 2 prochaines cases.
                        if MATRICE[y_p-3][x_p] == 0: MATRICE[y_p-4][x_p][1] = couleur_pion_possible
                        # Il existe une barrière qui empêche le saut par dessus l'autre pion.
                        # Alors on vérifie pour des déplacements en diagonale.
                        else:
                            # Diagonale gauche
                            if x_p > 0 and MATRICE[y_p-2][x_p-1] == 0: MATRICE[y_p-2][x_p-2][1] = couleur_pion_possible
                            # Diagonale droite
                            if x_p < 16 and MATRICE[y_p-2][x_p+1] == 0: MATRICE[y_p-2][x_p+2][1] = couleur_pion_possible
                if x_p > 0 and MATRICE[y_p][x_p-1] == 0:
                    if MATRICE[y_p][x_p-2][2] == 0: MATRICE[y_p][x_p-2][1] = couleur_pion_possible
                    elif x_p > 2:
                        if MATRICE[y_p][x_p-3] == 0: MATRICE[y_p][x_p-4][1] = couleur_pion_possible
                        else:
                            if y_p < 16 and MATRICE[y_p+1][x_p-2] == 0: MATRICE[y_p+2][x_p-2][1] = couleur_pion_possible
                            if y_p > 0 and MATRICE[y_p-1][x_p-2] == 0: MATRICE[y_p-2][x_p-2][1] = couleur_pion_possible
                if x_p < 16 and MATRICE[y_p][x_p+1] == 0:
                    if MATRICE[y_p][x_p+2][2] == 0: MATRICE[y_p][x_p+2][1] = couleur_pion_possible
                    elif x_p < 14:
                        if MATRICE[y_p][x_p+3] == 0: MATRICE[y_p][x_p+4][1] = couleur_pion_possible
                        else:
                            if y_p > 0 and MATRICE[y_p-1][x_p+2] == 0: MATRICE[y_p-2][x_p+2][1] = couleur_pion_possible
                            if y_p < 16 and MATRICE[y_p+1][x_p+2] == 0: MATRICE[y_p+2][x_p+2][1] = couleur_pion_possible
                if y_p < 16 and MATRICE[y_p+1][x_p] == 0:
                    if MATRICE[y_p+2][x_p][2] == 0: MATRICE[y_p+2][x_p][1] = couleur_pion_possible
                    elif y_p < 14:
                        if MATRICE[y_p+3][x_p] == 0: MATRICE[y_p+4][x_p][1] = couleur_pion_possible
                        else:
                            if x_p < 16 and MATRICE[y_p+2][x_p+1] == 0: MATRICE[y_p+2][x_p+2][1] = couleur_pion_possible
                            if x_p > 0 and MATRICE[y_p+2][x_p-1] == 0: MATRICE[y_p+2][x_p-2][1] = couleur_pion_possible
    else:
        # On attend pour un retour de l'autre joueur
        # data = "1.B." + str(abs(y-16)) + "." + str(abs(x-16))
        # data = "1.P." + str(MATRICE[abs(y-16)][abs(x-16)][0].centerx) + "." + str(MATRICE[abs(y-16)][abs(x-16)][0].centery)
        print("Je suis en Mode écoute 1...")
        clock.tick(100)
        vider_buffer_socket(SOCK_BIND)
        clock.tick(100)
        print("Je suis en Mode écoute 2...")
        while True:
            données_in, addr = SOCK_BIND.recvfrom(15)
            if données_in: break
            clock.tick(10)
        données_in = données_in.decode("ascii").split(".")
        print("Oui, y'a du données_in et c'est : ", données_in)
        if données_in[0] == "P": 
            print("Ouais Pion", données_in[2:])
            y_p = int((PION2[1]-140)/45*2); x_p = int((PION2[0]-60)/45*2)
            MATRICE[y_p][x_p][2] = 0
            MATRICE[int(données_in[1])][int(données_in[2])][2] = 1
            PION2[0] = MATRICE[int(données_in[1])][int(données_in[2])][0].centerx
            PION2[1] = MATRICE[int(données_in[1])][int(données_in[2])][0].centery
        elif données_in[0] == "B": 
            print("Ouais Barrière", données_in[2:])
            placer_la_barrière(int(données_in[2]), int(données_in[3]), int(données_in[1]))
        # EXCEPTION...
        else: print("Il y a officiellement eu une erreur avec données_in qui vaut : ", données_in)
        TOUR = 1
        del données_in
            
                   



# Rafraîchissements de l'écran à 60Hz
def dessin(fond):
    ################### DESSIN ###################
    pos = py.mouse.get_pos()

    écran.fill(fond)
    # 35,115
    if not GAGNANT and TOUR == 1:
        py.draw.rect(écran, NOIR, (30, 110, 420, 520), width=2)
        py.draw.rect(écran, BEIGE, (32, 112, 416, 516))
    elif not GAGNANT and TOUR == 2:
        py.draw.rect(écran, NOIR, (30, 10, 420, 520), width=2)
        py.draw.rect(écran, BEIGE, (32, 12, 416, 516))
    # Les carrés jaunes
    for y in range(1, 16, 2):
        for x in range(1, 16, 2):
            rect, a = MATRICE[y][x]
            py.draw.rect(écran, BEIGE if not GAGNANT else VERT, rect)
    # Les cases de jeu.MATRICE[y][x] = [py.Rect(40+x/2*45, 120+y/2*45, 40, 40), NOIR, 0]
    for y in range(0, 17, 2):
        for x in range(0, 17, 2):
            rect, couleur, a = MATRICE[y][x]
            py.draw.rect(écran, NOIR, rect, width=2)
            py.draw.rect(écran, couleur, (rect[0]+3, rect[1]+3, rect[2]-6, rect[3]-6))
    # Les barrières
    for i in range(10):
        # Joueur #1
        if BARRIERE_EN_MAIN[0] == i:
            barrière = py.Rect(0, 0, 5 if BARRIERE_EN_MAIN[1] == 1 else 77, 77 if BARRIERE_EN_MAIN[1] == 1 else 5)
            barrière.center = pos
            couleur = JAUNE
            snap_ou_non, y, x = si_snap_barrière(pos)
            if snap_ou_non:
                rect = MATRICE[y][x][0]
                barrière.center = rect.center
                if barrière_espace_libre(y, x) and si_chemin_possible(y, x, 1) and si_chemin_possible(y, x, 2): couleur = JAUNE
                else: couleur = ROUGE
            py.draw.rect(écran, couleur, barrière)
        else: py.draw.rect(écran, JAUNE, BARRIERES_JOUEUR1[i][1])
        # Joueur #2
        py.draw.rect(écran, JAUNE, BARRIERES_JOUEUR2[i])
    # Les pions
    py.draw.circle(écran, PION2[2], (PION2[0], PION2[1]), 14)
    if PION1[3] == 1:
        pos_pion = (pos[0], pos[1])
        for y in range(0, 17, 2):
            for x in range(0, 17, 2):
                rect, couleur, a = MATRICE[y][x]
                if couleur == BLANC and rect.collidepoint(pos): pos_pion = rect.center
        py.draw.circle(écran, PION1[2], pos_pion, 14)
    else : py.draw.circle(écran, PION1[2], (PION1[0], PION1[1]), 14)

    if fond != BRUN:
        texte = "VOUS AVEZ GAGNÉ" if fond == VERT else "VOUS AVEZ PERDU"
        texte = py.font.SysFont('tahoma', 32).render(texte, True, BLANC)
        center = texte.get_rect(center=écran.get_rect().center)
        écran.blit(texte, center)

    py.display.flip()
    clock.tick(60)



# Création de la fenêtre Pygame
py.init()
écran = py.display.set_mode((480, 640))
py.display.set_icon(py.image.load('img_icon.png'))
py.display.set_caption('Quoridor Online')

# Pour se connecter en LAN
if LAN: menu_départ()

# Boucle de jeu
while True:
    dessin(BRUN)
    événements()
    if GAGNANT: fin_de_partie(GAGNANT)