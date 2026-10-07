from pyray import *
from math import cos, sin, tan, sqrt
from random import randint, choice

screen_width = 1920
screen_height = 970

COLORS = (GREEN, RED, BLUE, YELLOW, PURPLE, PINK, ORANGE)

PLAYER_SPEED_MULTIPLIER = 800
MAX_SPEED = 600
PLAYER_BASE_SIZE = 20.0
ship_height = (PLAYER_BASE_SIZE/2)/tan(20*DEG2RAD)

init_window(screen_width, screen_height, "Asteroids")

set_target_fps(60)

class Animation:
    """
    Classe gérant l'ensemble des animations présentes dans le jeu
    """
    def __init__(self, duration, parameter = None):
        self.duration = duration
        self.parameter = parameter
        self.animation_type = None
        
    def destruction(self):
        """
        Fonction: affiche l'animation de destruction d'un astéroïde
        
        L'attribut parameter est ici un tuple qui contient la position de l'asteroide détruit et la couleur de l'animation
        
        Pas de paramètres ni de retour
        """
        if self.duration == 60:
            self.particles = [0]*8
            for i in range(8):
                self.particles[i] = (Vector2(self.parameter[0].x + randint(-20, 20), 
                                             self.parameter[0].y + randint(-20, 20))
                                     )
                
                draw_circle_v(self.particles[i], 1, self.parameter[1])
                
        elif self.duration > 0:
            for i in range(len(self.particles)):
                self.particles[i] = vector2_add(self.particles[i], 
                                                vector2_normalize(vector2_subtract(self.particles[i], self.parameter[0]))
                                                )
                
                draw_circle_v(self.particles[i], 2, fade(self.parameter[1], self.duration/60))
     
    def damage(self):
        """
        Fonction: affiche l'animation lorsque le joueur subit un dégât
        
        Pas de paramètres ni de retour
        """
        
        coeff = 15 - self.duration // 2 
        draw_rectangle(0, 0, 15 - coeff, screen_height, RED)
        draw_rectangle(screen_width - 15 + coeff, 0, 15 - coeff, screen_height, RED)
        draw_rectangle(0, screen_height - 15 + coeff, screen_width, 15 - coeff, RED)
        draw_rectangle(0, 0, screen_width, 20 - coeff, RED)
        
        draw_text("-1", 180, 23, 44, fade(RED, randint(1,10)/10))
        
    def laser(self):
        """
        Fonction: affiche l'animation du laser du joueur
        
        L'attribut parameter est ici untuple qui contient la position du joueur et la position de la fin du laser
        
        Pas de paramètres ni de retours
        """
        draw_spline_bezier_cubic(
                          (self.parameter[0],
                           Vector2(vector2_lerp(self.parameter[0], self.parameter[1], 0.5).x + randint(40,50) * choice([-1, 1]),
                                   vector2_lerp(self.parameter[0], self.parameter[1], 0.5).y + randint(40,50) * choice([-1, 1])
                                   ),
                           Vector2(vector2_lerp(self.parameter[0], self.parameter[1], 0.5).x + randint(40,50) * choice([-1, 1]),
                                   vector2_lerp(self.parameter[0], self.parameter[1], 0.5).y + randint(40,50) * choice([-1, 1])
                                   ),
                           self.parameter[1]
                          ),
                          4,
                          5.0,
                          BLUE
                         )
    
    def transition(self):
        """
        Fonction: affiche l'écran de transition lorsque tous les astéroïdes ont été détruits
        
        L'attribut parameter est ici le niveau
        
        Pas de paramètres ni de retour
        """
        clear_background(BLACK)
        draw_text(f"Level {self.parameter} ", screen_width//2 - 50, screen_height//2 - 100, 36, GREEN)
        
    def game_over(self):
        """ 
        Fonction: affiche l'écran de défaite qui disparait peu à peu
        
        L'attribut parameter est ici un tuple qui contient le score et le niveau
        
        Pas de paramètres ni de retour
        """     
        clear_background(BLACK)
        draw_text("Game Over", screen_width//2 - 110,screen_height//2 - 110 , 50, fade(GREEN, self.duration/240))
        draw_text(f"Score: {self.parameter[0]}", screen_width//2 - 110, screen_height//2 - 40, 20, fade(GREEN, self.duration/240))
        draw_text(f"Niveau: {self.parameter[1]}", screen_width//2 - 110,screen_height//2 - 10 , 20, fade(GREEN, self.duration/240))
        
    def score_point(self):
        """
        Fonction: affiche +1 à côté du score lorsqu'un point est gagné, de manière similaire à la méthode damage
        
        Pas de paramètres ni de retour
        """
        draw_text("+1", 150 + 10 * (len(str(self.parameter)) - 4), 120, 20, fade(choice(COLORS), randint(1,10)/10))
        
class Player:
    """ 
    Classe gérant le joueur: ses contrôles, ses déplacements, ses bonus
    """
    def __init__(self):
        self.velocity = Vector2(0,0)

        self.rotation = 0
        self.can_move = True

        self.projectiles = []
        self.cooldown = 0
        
        self.laser = True
        self.bonus_duration = -1
        self.laser_position = None 
        
        self.lives = 3
        self.invincible_frames = 0
        
        self.color = GREEN

        self.position = Vector2(screen_width/2, screen_height/2 - ship_height/2)
        self.points = []

    def player_control(self):
        """
        Fonction: permet de contrôler le vaisseau en gérant les entrées utilisateur, à la fois pour le mouvement et la rotation
        
        Pas de paramètres ni de retour
        """
        if is_key_down(KEY_LEFT) or is_key_down(KEY_A):
            self.rotation -= 5 * get_frame_time()

        if is_key_down(KEY_RIGHT) or is_key_down(KEY_D):
            self.rotation += 5 * get_frame_time()

        if self.can_move:
            if is_key_down(KEY_UP) or is_key_down(KEY_W):
                self.velocity.x += sin(self.rotation) * PLAYER_SPEED_MULTIPLIER * get_frame_time()
                self.velocity.y += -cos(self.rotation) * PLAYER_SPEED_MULTIPLIER * get_frame_time()
    
            if is_key_down(KEY_DOWN) or is_key_down(KEY_S):
                self.velocity.x -= sin(self.rotation) * PLAYER_SPEED_MULTIPLIER * get_frame_time()
                self.velocity.y -= -cos(self.rotation) * PLAYER_SPEED_MULTIPLIER * get_frame_time()

        if not is_key_down(KEY_DOWN) and not is_key_down(KEY_UP):
            self.velocity.x = self.velocity.x * 0.99
            self.velocity.y = self.velocity.y * 0.99
    
    def shoot(self):
        """
        Fonction: gère les tirs du vaisseau et l'entrée utilisateur pour tirer
        
        Pas de paramètres ni de retour
        """
        if is_key_down(KEY_SPACE) and self.cooldown == 0:
            if len(self.projectiles) == 8:
                self.projectiles.pop(0)
            self.projectiles.append(Projectile(self.rotation,
                                               Vector2(self.position.x + sin(self.rotation) * ship_height, 
                                                       self.position.y - cos(self.rotation) * ship_height), 
                                               self.velocity) )
            self.cooldown = 30
        
    def start_laser(self):
        """
        Fonction: gère les tirs du vaisseau et l'entrée utilisateur pour tirer
        
        Pas de paramètres
        
        Retour: 
            - un booléen qui permet de lancer ou non l'animation correspondant au laser depuis main()
        """
        if is_key_pressed(KEY_B) and self.laser:
            self.can_move = False
            self.bonus_duration = 10
            self.laser_position = Vector2(self.position.x + 600 * sin(self.rotation), 
                                           self.position.y - 600 * cos(self.rotation))
            return True
        return False
    
    def update_position(self):
        """
        Fonction: met à jour la position du joueur en y ajoutant sa vélocité en fonction du temps
        
        Pas de paramètres ni de retour
        """
        self.position.x += self.velocity.x * get_frame_time()
        self.position.y += self.velocity.y * get_frame_time()
        
        if self.laser_position != None:
            self.laser_position.x = self.position.x + 600 * sin(self.rotation)
                                           
            self.laser_position.y = self.position.y - 600 * cos(self.rotation)
    

    def velocity_max_min(self):
        """
        Fonction: change la vélocité du joueur selon qu'il atteigne un minimum ou un maximum de vitesse sur les deux axes
        
        Pas de paramètres ni de retour
        """
        
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        elif abs(self.velocity.x) > MAX_SPEED:
            self.velocity.x = MAX_SPEED * (1 if self.velocity.x > 0 else -1)

        if abs(self.velocity.y) < 0.1:
            self.velocity.y = 0
        elif abs(self.velocity.y) > MAX_SPEED:
            self.velocity.y = MAX_SPEED * (1 if self.velocity.y > 0 else -1)



class Projectile:
    """
    Classe gérant les projectiles du joueur
    """
    def __init__(self, rotation, starting_position, velocity):

        self.velocity = Vector2( 
                                ((20000 + (abs(velocity.x) + abs(velocity.y)) * 34) * sin(rotation)) * get_frame_time(), 
                                ((20000 + (abs(velocity.x) + abs(velocity.y)) * 34) * -cos(rotation)) * get_frame_time()
                                ) # la valeur 20000 est utilisée pour le cas où la valeur de la velocité du joueur est nulle

        self.position = Vector2(starting_position.x, starting_position.y)
        self.lifetime = 3 * 60



class Asteroid:
    """
    Classe gérant les astéroïdes
    """
    def __init__(self, starting_position, size):
        self.position = Vector2(starting_position.x, starting_position.y)
        self.size = size
        self.points = [0] * 6
        self.tracking = randint(1,4) == 1
        self.accelerating = False
        if not self.tracking:
            self.accelerating = randint(1,4) == 1
        
        self.rotation = randint(0, 360) * DEG2RAD
        self.velocity = Vector2(sin(self.rotation) * 125, -cos(self.rotation) * 125 ) 
        # on n'utilise pas le frame_time pour la vélocité ici car à l'init de la fenêtre il est égal à 0
        self.generation()

    def generation(self):
        """
        Fonction: Génère aléatoirement les positions des 6 points d'un astéroïde lors de son initialisation
        
        Pas de paramètres ni de retour
        """
        self.points[0] = Vector2(self.position.x - randint(5 * self.size, 12 * self.size), self.position.y - randint(5 * self.size, 12 * self.size))
        self.points[1] = Vector2(self.position.x - randint(5 * self.size, 12 * self.size), self.position.y + randint(5 * self.size, 12 * self.size))
        self.points[2] = Vector2(self.position.x + randint(-5 * self.size, 5 * self.size), self.position.y + randint(5 * self.size, 12 * self.size))
        self.points[3] = Vector2(self.position.x + randint(5 * self.size, 12 * self.size), self.position.y + randint(5 * self.size, 12 * self.size))
        self.points[4] = Vector2(self.position.x + randint(5 * self.size, 12 * self.size), self.position.y - randint(5 * self.size, 12 * self.size))
        self.points[5] = Vector2(self.position.x - randint(-5 * self.size, 5 * self.size), self.position.y - randint(5 * self.size, 12 * self.size))

    def divide(self):
        """ 
        Fonction: divise un astéroïde en deux et renvoie un tuple de deux astéroïdes plus petits
        
        Pas de paramètres
        
        Retour:
            - un tuple de deux objets de type Asteroid
        """
        return (Asteroid(vector2_add_value(self.position, -self.size * 5), self.size-1), 
                Asteroid(vector2_add_value(self.position, self.size * 5), self.size-1))

    def update_point_position(self, point, modif):
        """
        Fonction: modifie la position d'un point donné d'un astéroïde pour le faire 'traverser' l'écran
                  en utilisant la variable modif qui indique quel calcul faire pour faire faire le même déplacement à l'astéroïde et au point
        
        Paramètre:
            - position (Vector2): la position de l'objet
            
        Retour:
            - modif (int): peut prendre 4 valeurs selon le côté de l'écran 'traversé' (None sinon) 
        """
        if modif == 0:
            self.points[point].x -= screen_width
        elif modif == 1:
            self.points[point].x += screen_width
        elif modif == 2:
            self.points[point].y -= screen_height
        else:
            self.points[point].y += screen_height

    def check_position_asteroid(self):
        """
        Fonction: vérifie si l'astéroïde sort de l'écran et le cas échéant, modifie sa position pour le faire 'traverser' l'écran
                 Retourne un int qui indique par quel côté de l'écran l'asteroide est passé
            
        Retour:
            - modif (int): peut prendre 4 valeurs selon le côté de l'écran 'traversé' (None sinon) 
        """
        if self.position.x > screen_width:
            self.position.x = 0
            modif = 0
        elif self.position.x < 0:
            self.position.x = screen_width
            modif = 1
        elif self.position.y > screen_height:
            self.position.y = 0
            modif = 2
        elif self.position.y < 0:
            self.position.y = screen_height
            modif = 3
        else:
            modif = None
        return modif

    def track_player(self, player_position):
        """
        Fonction: change la vélocité de l'astéroïde afin qu'il 'traque' le joueur
        
        Paramètre: player_position (Vector2): la position du joueur
        
        Pas de retour
        """
        
        self.velocity = vector2_scale(vector2_normalize(vector2_subtract(player_position, self.position)), 200)
        
    def accelerate(self):
        """
        Fonction: change la vélocité de l'astéroïde afin qu'il 'traque' le joueur
        
        Paramètre: player_position (Vector2): la position du joueur
        
        Pas de retour
        """
        if max(abs(self.velocity.x), abs(self.velocity.y)) < 400:
            self.velocity = vector2_scale(self.velocity, 1.001)

class Game:
    """
    Classe faisant la gestion des systèmes du jeu: la création et la destruction des astéroïdes, le score et son stockage dans un fichier
    """
    def __init__(self):
        self.last_input = None
        self.key_was_released = False
        self.difficulty = 1
        self.asteroids = []
        self.asteroids_creation()
        self.score = 0
        self.animations = []
        self.pause = 0

    def asteroids_creation(self):
        """
        Fonction: crée aléatoirement les astéroïdes à l'initialisation de Game
        
        Pas de paramètres ni de retour
        """
        if self.difficulty % 5 == 0:
            position = choice([ Vector2( randint(0, screen_width), choice([0, screen_height]) ), 
                                    Vector2( choice([0, screen_width]), randint(0, screen_height) ) ])

            self.asteroids.append(Asteroid(position, randint(6,7)))
            
            for _ in range((self.difficulty//2)-1):
                position = choice([ Vector2( randint(0, screen_width), choice([0, screen_height]) ), 
                                    Vector2( choice([0, screen_width]), randint(0, screen_height) ) ])
                self.asteroids.append(Asteroid(position, randint(2,3)))
                
        else:
            for _ in range(self.difficulty):
            #choisit aléatoirement entre vertical et horizontal comme axe puis genere une position sur l'axe opposé
                position = choice([ Vector2( randint(0, screen_width), choice([0, screen_height]) ), 
                                    Vector2( choice([0, screen_width]), randint(0, screen_height) ) ])

                self.asteroids.append(Asteroid(position, randint(2,4)))

    def check_position(self, position):
        """
        Fonction: vérifie si l'objet sort de l'écran et le cas échéant, modifie sa position pour le faire 'traverser' l'écran
        
        Paramètre:
            - position (Vector2): la position de l'objet
            
        Pas de retour
        """
        if position.x > screen_width:
            position.x -= screen_width
        elif position.x < 0:
            position.x += screen_width
        if position.y > screen_height:
            position.y -= screen_height
        elif position.y < 0:
            position.y += screen_height

    def remove_asteroid(self, asteroid):
        """
        Fonction: Gère la destruction d'un astéroïde: le diviser en deux si possible; 
                                                      lancer l'animation correspondante; 
                                                      le supprimer des astéroïdes.
                    
        Paramètre:
            - asteroid (Asteroid); l'astéroïde à détruire
            
        Pas de retour
        """
        if asteroid.size > 2:
            self.asteroids.extend(asteroid.divide())
        self.animations.append(Animation(60, (asteroid.position, ORANGE) ))
        
        self.animations[-1].animation_type = self.animations[-1].destruction 
        #l'animation a sa propre méthode comme attribut cela permet de l'utiliser plus tard sans avoir besoin de la chercher
        
        self.asteroids.remove(asteroid)
        
    def is_close(self, position, asteroid):
        """ 
        Fonction: renvoie True si l'objet se trouve à une position proche de l'astéroide concerné, on utilise cette fonction afin 
                d'optimiser le code et d'éviter de faire des recherches de collisions coûteuses
        
        Paramètres:
            - position (Vector2): la position de l'objet avec qui on recherche la proximité
            
            - asteroid (Asteroid): l'astéroïde avec qui on recherche la proximité
            
        Retour: 
            - un booléen qui permet de savoir s'il est nécessaire de vérifier la collision entre l'objet et l'astéroïde
        """
        if asteroid.position.x - 80 <= position.x  <= asteroid.position.x + 80:
            if asteroid.position.y -80 <= position.y <= asteroid.position.y + 80:
                return True
        return False
    
    def draw_asteroid(self):
        """Fonction: gère l'affichage d'un asteroide 
            
            Pas de paramètres ni de retour
        """
        for asteroid in self.asteroids:
            for i in range(5, -1, -1):
                draw_line_v(asteroid.points[i-1], asteroid.points[i], RED if asteroid.tracking else ORANGE if asteroid.accelerating else GREEN)
                
    def save_score(self, highscore):
        """
        Fonction: 
            Sauvegarde le score dans un fichier texte 
            
        Paramètre:
            - highscore (int): la valeur du score
            
        Pas de retour
        """
        if highscore == "" or self.score > int(highscore):
            file = open("score.txt", "w")
            file.write(str(self.score))
            file.close()
            
    def increment_score(self):
        """
        Fonction: fait l'incrémentation du score et lance une animation correspondante
        
        Pas de paramètres ni de retours
        """
        self.score += 1
        self.animations.append(Animation(30, self.score))
        self.animations[-1].animation_type = self.animations[-1].score_point
    
    def next_level(self):
        """
        Fonction: gère le passage d'un niveau à un autre lorsque tous les astéroïdes ont été détruits
        
        Pas de paramètres ni de retours
        """
        self.difficulty += 1
        self.asteroids_creation()
        self.animations.clear()
        
        self.animations.append(Animation(120, self.difficulty))
        self.animations[-1].animation_type = self.animations[-1].transition
        
        self.pause = 120
    
    def draw_laser_interface(self, laser):
        """
        Fonction: Affiche l'élément de l'interface indiquant si le laser est disponible

        Paramètre: laser (bool): l'attribut de player qui indique si le laser est disponible
        """
        draw_rectangle_lines(30, 70, 60, 30, GREEN)
        if laser:
            v1 = Vector2(35, 85)
            v2 = Vector2(85, 85)
            draw_spline_bezier_cubic((v1 ,
                                           Vector2(vector2_lerp(v1, v2, 0.5).x + randint(5,10) * choice([-1, 1]),
                                                   vector2_lerp(v1, v2, 0.5).y + randint(5,10) * choice([-1, 1])
                                                   ),
                                           Vector2(vector2_lerp(v1, v2, 0.5).x + randint(5,10) * choice([-1, 1]),
                                                   vector2_lerp(v1, v2, 0.5).y + randint(5,10) * choice([-1, 1])
                                                   ),
                                          v2
                                          ),
                                          4,
                                          5.0,
                                          BLUE
                                         )
def main(highscore):
    """ 
    Fonction: fonction principale qui gére l'exécution du jeu et l'affichage
    
    Paramètre:
        - highscore (int): le plus haut score lors du lancement de la partie, utilisé dans la méthode save_score de la classe Game
        
    Retour:
        - un booléen qui définit s'il faut revenir au menu ou laisser la fenêtre se fermer
    
    """
    player = Player()
    game = Game()

    while not window_should_close():
        
        if game.pause == 0:
            player.player_control()
            
            player.update_position()
    
            game.check_position(player.position)
    
            player.velocity_max_min()
            
            v1 = Vector2(player.position.x + sin(player.rotation)*(ship_height), player.position.y - cos(player.rotation)*(ship_height) )
            v2 = Vector2(player.position.x - cos(player.rotation)*(PLAYER_BASE_SIZE/2), player.position.y - sin(player.rotation)*(PLAYER_BASE_SIZE/2))
            v3 = Vector2(player.position.x + cos(player.rotation)*(PLAYER_BASE_SIZE/2), player.position.y + sin(player.rotation)*(PLAYER_BASE_SIZE/2))
            v4 = Vector2(player.position.x + sin(player.rotation)*(ship_height/3), player.position.y - cos(player.rotation)*(ship_height/3) )
    
            player.points = (v1, v2, v3, v4)
    
            # détection des collisions entre les projectiles et les astéroïdes et gestion du déplacement et du temps de vie
            for projectile in player.projectiles:
                projectile.lifetime -= 1
                
                if projectile.lifetime <= 0 and player.projectiles != []:
                    player.projectiles.pop(0)
                else:
                    projectile.position.x += projectile.velocity.x * get_frame_time()
                    projectile.position.y += projectile.velocity.y * get_frame_time()
                game.check_position(projectile.position)
    
            # délai entre les tirs du joueur
            if player.cooldown > 0:
                player.cooldown -= 1
            
            if not (player.laser and player.bonus_duration > 0):
                player.shoot()
                if player.start_laser():
                    game.animations.append(Animation(player.bonus_duration, (player.position, player.laser_position) ))
                    
                    game.animations[-1].animation_type = game.animations[-1].laser
            elif player.bonus_duration > 0:
                player.bonus_duration -= 1
                
            if player.laser and player.bonus_duration == 0:
                player.can_move = True
                player.laser = False
    
            # déplacement des astéroides et détection des collisions avec le joueur, les projectiles et le laser
            for asteroid in game.asteroids:
                if asteroid.tracking:
                    asteroid.track_player(player.position)
                elif asteroid.accelerating:
                    asteroid.accelerate()
                asteroid.position.x += asteroid.velocity.x * get_frame_time()
                asteroid.position.y += asteroid.velocity.y * get_frame_time()
                
                modif = asteroid.check_position_asteroid()
                
                for point in range(len(asteroid.points)):
                    asteroid.points[point].x += asteroid.velocity.x * get_frame_time()
                    asteroid.points[point].y += asteroid.velocity.y * get_frame_time()
                    if modif != None:
                        asteroid.update_point_position(point, modif)
                        
                # collision avec le laser
                if player.laser and player.bonus_duration > 0:
                    if check_collision_point_line(asteroid.position, player.position, player.laser_position, 50):
                        game.remove_asteroid(asteroid)
                        game.increment_score()
                
                else:
                    # collision avec les projectiles
                    for projectile in player.projectiles:
                        if game.is_close(projectile.position, asteroid):
                            for i in range(6):
                                if check_collision_point_line(projectile.position, asteroid.points[i], asteroid.points[i-1], 7):
                                    game.remove_asteroid(asteroid)
                                    player.projectiles.remove(projectile)
                                    game.increment_score()
                                    break
                
                #collision entre l'astéroïde et le joueur
                if game.is_close(player.position, asteroid) and player.invincible_frames <= 1:
                     
                    for j in range(6):
                        for point in range(3):
                            if check_collision_point_line(player.points[point], asteroid.points[j], asteroid.points[j-1], 3):
                                if player.invincible_frames == 0:
                                    player.lives -= 1
                                    game.animations.append(Animation(30))
                                    game.animations[-1].animation_type = game.animations[-1].damage
                                    player.invincible_frames = 60 # 1 seconde
                                else:
                                    game.increment_score()
                                if asteroid in game.asteroids: # pour ne pas tenter de supprimer un asteroide deja detruit
                                   game.remove_asteroid(asteroid)
                                   
                                break # pour éviter de chercher d'autres collisions avec le même objet
                    
            if player.invincible_frames != 0:
                player.invincible_frames -= 1
            
            # mort du joueur
            if player.lives == 0 and game.pause == 0:
                game.save_score(highscore)
                game.pause = 480
                game.animations.append(Animation(240, (game.score, game.difficulty)))
                game.animations[-1].animation_type = game.animations[-1].game_over
                
            # passage au niveau suivant
            if game.asteroids == [] and game.animations == []:
                player.position = Vector2(screen_width/2, screen_height/2 - ship_height/2)
                player.rotation = 0
                player.bonus_duration = -1
                player.velocity = vector2_zero()
                player.projectiles.clear()
                player.laser = True
                
                game.next_level()
                
            elif len(game.asteroids) == 1 and game.asteroids[0].size == 2:
                player.invincible_frames = 1 # invincibilité infinie lorsqu'il ne reste qu'un petit astéroïde
            
            # Retour au menu
            if is_key_pressed(KEY_R):
                game.save_score(highscore)
                return True # on sort de la boucle et on revient au menu
            
        else:
            if game.pause == 240: # retour au menu après que le joueur soit mort et que l'animation se soit finie
                return True 
            game.pause -= 1
            
            
        #============================================================
        #                       Partie d'affichage
        begin_drawing()

        clear_background(BLACK)
        
        
        if game.pause == 0:
            if player.invincible_frames != 0:
                player.color = choice(COLORS)
            else:
                player.color = GREEN
            
            draw_line_v(v1, v2, player.color)
            draw_line_v(v1, v3, player.color)
            draw_line_v(v2, v4, player.color)
            draw_line_v(v3, v4, player.color)
    
            for projectile in player.projectiles:
                if projectile != None:
                    draw_circle_v(projectile.position, 4, GREEN)
    
            for asteroid in game.asteroids:
                game.draw_asteroid()
                
            game.draw_laser_interface(player.laser)
            
            draw_text(f"Score: {game.score}", 30, 120, 20, GREEN)
            
            for i in range(3):
                if player.lives - 1 >= i:
                    draw_rectangle(30 + 50 * i, 30, 40, 20, GREEN)
                else:
                    draw_rectangle_lines(30 + 50 * i, 30, 40, 20, GREEN)
        
        for animation in game.animations:
            if animation.duration > 0:
                animation.animation_type()
                animation.duration -= 1
            else:
                game.animations.remove(animation)
                
        end_drawing()
        #============================================================

    game.save_score(highscore)
    close_window()
    return False # afin de ne pas relancer la fenêtre du menu depuis le programme du menu