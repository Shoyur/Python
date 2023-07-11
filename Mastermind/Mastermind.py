import webbrowser
import pygame as py
import random


# Pour voir le secret en bas...
CHEAT = 0

#Pour limiter les FPS.
DÉLAI = py.time.Clock()

NB_PIONS = 4
NB_TOURS = 10
NB_COUL = 6

ROUGE = 255,1,1
BLEU = 1,1,255
JAUNE = 255,255,1
VERT = 1,255,1
BLANC = 255,255,255
NOIR = 1,1,1
GRIS = 80,80,80
ROUGE_F = 255,60,60
TURQUOISE = 1,235,235
ROSE = 235,1,235
BRUN = 114,64,34
CIEL = 80,80,255



class Tour:

    def __init__(self, tour, col_sel, col_tour, trous_pleins) -> None:

        # Combientième tour de jeu.
        self.tour = tour
        # La couleur sélectionné à droite, de 0 à 5 (index de la liste des couleurs jouables.)
        self.col_sel = col_sel
        # Les 4 couleurs choisies de ces 4 trous.
        self.col_tour = col_tour
        # Les 4 trous du tour.
        self.trous_pleins = trous_pleins
        # Liste des 4 positions du tour
        # [objet py.Rect, couleur si autre que gris]
        self.liste_4x = []
        self.gen_4x(self.tour)
    
    def gen_4x(self, tour):
        for i in range(NB_PIONS):
            self.liste_4x.append([py.Rect((i+1)*30-11, tour*45-11, 22, 22), -1])


class Jeu:

    def __init__(self) -> None:

        # Init pour pygame.
        py.init()
        py.display.set_icon(py.image.load('Mastermind-icon.png'))
        self.écran = py.display.set_mode((245, 12*45))
        py.display.set_caption('MSTRMND')

        # Objet combientième tour qui contient les infos du jeu au présent.
        self.tour = Tour(1, -1, [0]*NB_PIONS, [0]*NB_PIONS)

        # La combinaison à trouver, généré par l'ordinateur.
        self.secret = [0]*NB_PIONS
        # Flag pour savoir s'il faut arrêter le jeu.
        self.fin_du_jeu = 0
        # Liste des 6 couleurs jouables
        # [objet py.Rect, sélectionné, couleur_jouable]
        self.six_couleurs = [[py.Rect(204, i*30+34, 22, 22),0] for i in range(NB_COUL)]

        # Démarrer la 1ère fenêtre menu pour sélectionner les 6 couleurs jouables.
        self.menu_départ()


    # Nombre à constante d'un RGB
    def int_2_couleur(self, couleur):
        if couleur == 0: couleur = NOIR
        elif couleur == 1: couleur = ROUGE
        elif couleur == 2: couleur = BLEU
        elif couleur == 3: couleur = JAUNE
        elif couleur == 4: couleur = VERT
        elif couleur == 5: couleur = BLANC
        elif couleur == 6: couleur = TURQUOISE
        elif couleur == 7: couleur = ROSE
        elif couleur == 8: couleur = BRUN
        elif couleur == 9: couleur = CIEL
        else: couleur = GRIS
        return couleur

    # On génère une combinaison aléatoire [?,?,?,?].
    def gen_secret(self):
        secret = []
        for _ in range(NB_PIONS): secret.append(self.six_couleurs[random.randint(0,5)][2])
        return secret

    # Menu de départ.
    def menu_départ(self):
        # Les 10 couleurs possibles.
        couleurs_choisies = [[i,0] for i in range(10)]
        # Instancier les 10 objects Rect pygame pour le collide des 10 cercles.
        for i in range(5): 
            couleurs_choisies[i].append(py.Rect((i+1)*40-6, 109, 22, 22))
            couleurs_choisies[i+5].append(py.Rect((i+1)*40-6, 149, 22, 22))
        combien_choisies = 0
        self.écran = py.display.set_mode((245, 260))
        boucle_menu = True
        bouton_jouer = py.Rect(30, 200, 80, 30)
        bouton_quitter = py.Rect(135, 200, 80, 30)
        lien_couleur = BLANC
        while boucle_menu:
            souris = py.mouse.get_pos()
            fond_écran = py.image.load("bg-menu.jpg")
            self.écran.blit(fond_écran,[0,0])
            lien = self.écran.blit(py.font.SysFont('tahoma', 16).render("INSTRUCTIONS", True, lien_couleur), (65, 30))
            texte = self.écran.blit(py.font.SysFont('tahoma', 12).render("CHOISIR 6 COULEURS DE PIONS :", True, BLANC), (32, 70))
            # Dessiner les 10 cercles.
            for i in range(5):
                py.draw.circle(self.écran, self.int_2_couleur(couleurs_choisies[i][0]), ((i+1)*40+5, 120), 12)
                if couleurs_choisies[i][1] == 1: 
                    py.draw.circle(self.écran, BLANC if i == 0 else NOIR, ((i+1)*40+5, 120), 15, width=3)
                py.draw.circle(self.écran, self.int_2_couleur(couleurs_choisies[i+5][0]), ((i+1)*40+5, 160), 12)
                if couleurs_choisies[i+5][1] == 1: 
                    py.draw.circle(self.écran, NOIR, ((i+1)*40+5, 160), 15, width=3)
            texte = "JOUER"
            possible_jouer = BLANC if combien_choisies == NB_COUL else GRIS
            texte = py.font.SysFont('tahoma', 14).render(texte, True, possible_jouer)
            py.draw.rect(self.écran, NOIR, bouton_jouer)
            py.draw.rect(self.écran, possible_jouer, bouton_jouer, width=1)
            self.écran.blit(texte, texte.get_rect(center=bouton_jouer.center))
            texte = "QUITTER"
            texte = py.font.SysFont('tahoma', 14).render(texte, True, BLANC)
            py.draw.rect(self.écran, NOIR, bouton_quitter)
            py.draw.rect(self.écran, BLANC, bouton_quitter, width=1)
            self.écran.blit(texte, texte.get_rect(center=bouton_quitter.center))
            # Rafraîchir la fenêtre.
            py.display.flip()
            # Tous les événements de souris-clavier.
            for action in py.event.get():
                # Si on clique
                if action.type == py.MOUSEBUTTONDOWN:
                    # Sur l'hyperlien des instructions.
                    if lien.collidepoint(souris): 
                        webbrowser.open(r"https://fr.wikihow.com/jouer-au-Mastermind")
                    # Si on clique JOUER et qu'on a 6 couleurs de choisies.
                    elif bouton_jouer.collidepoint(souris) and combien_choisies == NB_COUL: 
                        boucle_menu = False
                    elif bouton_quitter.collidepoint(souris): 
                        return
                    # Si à l'intérieur de la hauteur des 10 cercles.
                    for i in range(5):
                        # Si on collide, mettre le flag à 1, pour choisi.
                        if couleurs_choisies[i][2].collidepoint(souris): 
                            couleurs_choisies[i][1] = 1 if couleurs_choisies[i][1] == 0 else 0
                        elif couleurs_choisies[i+5][2].collidepoint(souris): 
                            couleurs_choisies[i+5][1] = 1 if couleurs_choisies[i+5][1] == 0 else 0
                if action.type == py.QUIT: 
                    return
            combien_choisies = 0
            for i in range(NB_TOURS): 
                if couleurs_choisies[i][1] == 1: 
                    combien_choisies += 1
            if lien.collidepoint(souris): 
                lien_couleur = NOIR
            else: 
                lien_couleur = BLANC
            DÉLAI.tick(60)
        # Liste qui contient les 6 couleurs jouables.
        inc_couleur = 0
        for i in range(NB_TOURS): 
            if couleurs_choisies[i][1] == 1: 
                self.six_couleurs[inc_couleur].append(i)
                inc_couleur += 1
        # Grossir l'écran pour le vrai jeu.
        self.écran = py.display.set_mode((245, 540))
        # Tous effacer en remettant en gris.
        self.écran.fill(GRIS)
        # Démarrer la boucle principale.
        self.boucle_de_jeu()

    # Sin on a perdu ou gagné.
    def fin_de_jeu(self):
        self.écran.fill(GRIS)
        self.tour = Tour(1, -1, [0]*NB_PIONS, [0]*NB_PIONS)
        self.secret = self.gen_secret()
        self.fin_du_jeu = 0
        for i in range(NB_COUL): 
            self.six_couleurs[i][1] = 0

    # Appellé pour vérifier en boucle et dessiner le résultat.
    def boucle_de_jeu(self):
        # Pour le while.
        self.boucle_de_jeu = True
        # Générer un code secret.
        self.secret = self.gen_secret()
        # 1ère mise à jour du dessin de l'écran.
        self.dessin()
        # Boucle de jeu principale.
        while self.boucle_de_jeu:
            for action in py.event.get():
                if action.type == py.MOUSEBUTTONDOWN:
                    # Position x,y au click de la souris pour rafraichir comme il le faut
                    self.souris = py.mouse.get_pos()
                    self.souris_pos_x, self.souris_pos_y = self.souris
                    # On a clické pour recommencer une partie
                    if self.fin_du_jeu == 1: 
                        self.fin_de_jeu()
                    # Est-ce qu'on a cliqué sur une des 6 couleurs à droite ?
                    if 203 <= self.souris_pos_x <= 227:
                        for i in range(NB_COUL):
                            self.six_couleurs[i][1] = 0
                            if self.six_couleurs[i][0].collidepoint(self.souris):
                                self.six_couleurs[i][1] = 1
                                self.tour.col_sel = self.six_couleurs[i][2]
                    # On clique peut-être à gauche sur un des 4.
                    elif 18 <= self.souris_pos_x <= 132 and self.tour.col_sel != -1:
                        for i in range(NB_PIONS):
                            if self.tour.liste_4x[i][0].collidepoint(self.souris):
                                self.tour.liste_4x[i][1] = self.tour.col_sel
                                self.tour.col_tour[i] = self.tour.col_sel
                                self.tour.trous_pleins[i] = 1
                                # Si une self.rangée_clickée remplie !!! CORRECTION
                                if self.tour.trous_pleins == [1,1,1,1]: 
                                    self.correction()
                    self.dessin()
                if action.type == py.QUIT: self.boucle_de_jeu = False
        py.quit()

    # À chaque fois qu'on a rempli une rangée
    def correction(self):
        if self.tour.tour <= 10:
            for i_qté_pin_rouge in range(4):
                if self.tour.col_tour[i_qté_pin_rouge] == self.secret[i_qté_pin_rouge]: 
                    self.qté_pin_rouge += 1
                    self.test_secret[i_qté_pin_rouge] = 1
                    self.test_couleurs_du_tour[i_qté_pin_rouge] = 1
            # Début correction pins blanches
            for i_qté_pin_blanche in range(4):
                # Si trou plein 1 à 4 n'est pas la bonne couleur
                if self.test_couleurs_du_tour[i_qté_pin_blanche] == 0:
                    for i_blanc2 in range(4):
                        if i_qté_pin_blanche != i_blanc2 and \
                            self.test_couleurs_du_tour[i_qté_pin_blanche] != 1 and \
                            self.test_secret[i_blanc2] != 1 and \
                            self.tour.col_tour[i_qté_pin_blanche] == self.secret[i_blanc2]:
                                self.test_secret[i_blanc2] = 1
                                self.test_couleurs_du_tour[i_qté_pin_blanche] = 1
                                self.qté_pin_blanche += 1
            # Dessiner pins rouges
            for i_dessin_rouge in range(0, self.qté_pin_rouge):
                if i_dessin_rouge < 2: 
                    py.draw.circle(self.écran, ROUGE, (140+(i_dessin_rouge+1)*12, self.tour.tour*45-6), 5)
                else: 
                    py.draw.circle(self.écran, ROUGE, (140+((i_dessin_rouge+1)-2)*12, self.tour.tour*45+6), 5)
            # Dessiner pins blanches
            for i_dessin_blanche in range(self.qté_pin_rouge, self.qté_pin_rouge+self.qté_pin_blanche):
                if i_dessin_blanche < 2: 
                    py.draw.circle(self.écran, BLANC, (140+(i_dessin_blanche+1)*12, self.tour.tour*45-6), 5)
                else: 
                    py.draw.circle(self.écran, BLANC, (140+((i_dessin_blanche+1)-2)*12, self.tour.tour*45+6), 5)
        # Réussite !!!
        if self.qté_pin_rouge == NB_PIONS: 
            self.fin(1)
        # Échec !!!
        elif self.tour.tour == NB_TOURS and self.qté_pin_rouge < NB_PIONS: 
            self.fin(0)
        # Rafraîchir avant de passer au tour suivant
        self.dessin()
        # Tour suivant...
        self.tour = Tour(self.tour.tour + 1, self.tour.col_sel, [0]*NB_PIONS, [0]*NB_PIONS)

    # Si on gagne ou perd.
    def fin(self, réussite):
        for i in range(NB_PIONS): 
            py.draw.circle(self.écran, self.int_2_couleur(self.secret[i]), ((i+1)*30, 11*45), 12)
        py.draw.rect(self.écran, (1,200,50) if réussite == 1 else ROUGE_F, py.Rect(0, 0, 245, 12*45), width=7)
        py.display.flip()
        self.fin_du_jeu = 1

    def dessin(self):
        self.qté_pin_rouge = 0
        self.qté_pin_blanche = 0
        self.test_secret = [0]*NB_PIONS
        self.test_couleurs_du_tour = [0]*NB_PIONS
        # Position x,y au click de la souris pour rafraichir comme il le faut
        self.souris = py.mouse.get_pos()
        self.souris_pos_x, self.souris_pos_y = self.souris
        # Nous sommes dans la section de jeu
        for i in range(NB_PIONS): 
            py.draw.circle(self.écran, self.int_2_couleur(self.tour.liste_4x[i][1]), (30*(i+1), 45*self.tour.tour), 12)
        # Dessiner la zone de jeu
        for i1 in range(1,11):
            for i2 in range(1,5):
                # 4 ronds vides
                py.draw.circle(self.écran, NOIR, ((i2)*30, i1*45), 12, width=1)
                # 4 ronds de corrections
                if i2 < 3: 
                    py.draw.circle(self.écran, NOIR, (140+i2*12, i1*45-6), 5, width=1)
                else: 
                    py.draw.circle(self.écran, NOIR, (140+(i2-2)*12, i1*45+6), 5, width=1)
            py.draw.rect(self.écran, GRIS, py.Rect(12, i1*45-18, 126, 36), width=2) # GRIS OK
        # Le rectangle qui indique le tour
        if self.fin_du_jeu != 1: 
            py.draw.rect(self.écran, NOIR, py.Rect(12, self.tour.tour*45-18, 126, 36), width=2)
        # Le rectangle sur la réponse
        else: 
            py.draw.rect(self.écran, NOIR, py.Rect(12, (11*45)-18, 126, 36), width=2)
        # Cacher l'ancien possible choix (écrire par dessus les 6)
        py.draw.rect(self.écran, GRIS, py.Rect(199, 29, 32, 200))
        # Dessiner les 6 couleurs à choisir
        for i in range(NB_COUL):
            py.draw.circle(self.écran, self.int_2_couleur(self.six_couleurs[i][2]), (215, i*30+45), 12)
            # Dessiner un cercle blanc dans un cercle noir, s'il y a une couleur sélectionnée.
            if self.six_couleurs[i][1] == 1: 
                py.draw.circle(self.écran, BLANC, (215, i*30+45), 13, width=2)
                py.draw.circle(self.écran, NOIR, (215, i*30+45), 16, width=3)
        # Mode CHEAT (debug), affiche le secret en bas.
        if CHEAT:
            for i in range(NB_PIONS): 
                py.draw.circle(self.écran, self.int_2_couleur(self.secret[i]), ((i+1)*30, 11*45), 12)
        py.display.flip()

partie = Jeu()