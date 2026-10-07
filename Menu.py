from pyray import *
from Asteroids import Game, Animation, main, screen_height, screen_width, COLORS
from random import randint, choice

def credit():
        """
        Fonction: affiche un écran de crédits
        
        Pas de paramètres ni de retours
        """ 
        draw_text("Credits", screen_width//2 - 80, screen_height//10 , 40, GREEN)
        draw_text('Merlin "ça va marcher" B.', screen_width//2 - screen_width//3, screen_height//2, 30, PURPLE)
        draw_text('Titouan "Rapide_plus" M.', screen_width//2 + screen_width//8, screen_height//2, 30, choice((BLACK, GRAY)))

def menu():
    """
    Fonction: fonction gérant le menu, le lancement du jeu et la boucle entre la fin du jeu et le retour au menu
    
    Pas de paramètres ni de retour
    """
    game = Game()
    game.difficulty = 11
    game.asteroids_creation()
    go_back_to_menu = False
    
    menu_aide = False
    page_credits = False
    
    file = open("score.txt", "r")
    highscore = file.readline()
    file.close()
    
    # position et caractéristiques des boutons du menu
    bouton_play = [(screen_width//2 - 50, screen_height//2 -100, 100, 50), GREEN]
    bouton_cancel = [(screen_width//2 - 50, screen_height//2 +100, 100, 50), GREEN]
    bouton_asteroids = [(screen_width//2 - 110, screen_height//2 - 250, 242, 35), GREEN]
    bouton_help = [(screen_width//2 - 50, screen_height//2, 100, 50), GREEN]
    bouton_menu = [(screen_width//2 - 50, screen_height - (screen_height//3), 100, 50), GREEN]
    bouton_credits = [(20, screen_height - 50, 150, 50), GREEN]
    
    while not window_should_close():

        mouse_position = get_mouse_position()
        
        for asteroid in game.asteroids:
            if asteroid.tracking:
                asteroid.track_player(mouse_position)
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

        for asteroid in game.asteroids:
                game.draw_asteroid()
        
        for asteroid in game.asteroids:
            if game.is_close(mouse_position, asteroid):
                if check_collision_point_circle(mouse_position, asteroid.position, 5):
                    game.remove_asteroid(asteroid)
                for i in range(6):
                    if check_collision_point_line(mouse_position, asteroid.points[i], asteroid.points[i-1], 7):
                        game.remove_asteroid(asteroid)
                        break
                    
                
        #============================================================
        #                       Partie d'affichage    
        begin_drawing()
        clear_background(BLACK)
        
        for animation in game.animations:
            if animation.duration > 0:
                animation.animation_type()
                animation.duration -= 1
            else:
                game.animations.remove(animation)
        
        if not menu_aide and not page_credits:
            
            draw_text(b"ASTEROIDS", bouton_asteroids[0][0], bouton_asteroids[0][1], 40, bouton_asteroids[1])
            draw_text(f"Highscore: {highscore}", bouton_asteroids[0][0], bouton_asteroids[0][1] + 70, 15, GREEN)
            draw_triangle(Vector2(bouton_play[0][0] + 40, bouton_play[0][1] + 15), 
                          Vector2(bouton_play[0][0] + 40, bouton_play[0][1] + 35), 
                          Vector2(bouton_play[0][0] + 60, bouton_play[0][1] + 25), 
                          bouton_play[1])
            draw_text(b"?", bouton_help[0][0] + 40, bouton_help[0][1] + 12, 30, bouton_help[1])
            draw_text(b"x", bouton_cancel[0][0] + 40, bouton_cancel[0][1] + 3, 40, bouton_cancel[1])
            draw_text("Credits", bouton_credits[0][0], bouton_credits[0][1], 40, bouton_credits[1])
            if bouton_credits[1] == RED:
                draw_text("Faites un score de 25 au minimum", bouton_credits[0][0], bouton_credits[0][1]-50, 20, GREEN)
            
            draw_rectangle_lines(bouton_play[0][0], bouton_play[0][1], 100, 50, bouton_play[1])
            draw_rectangle_lines(bouton_help[0][0], bouton_help[0][1], 100, 50, bouton_help[1])
            draw_rectangle_lines(bouton_cancel[0][0], bouton_cancel[0][1], 100, 50, bouton_cancel[1])
        
        else:
            
            if not page_credits:
            
                draw_text("Controles:", screen_width//2 - 90, screen_height//10 , 40, GREEN)
                draw_text("Z/Up: Avancer", screen_width//2 - 110, screen_height//10 + 80, 20, GREEN)
                draw_text("Q/Left: Rotation sur la gauche", screen_width//2 - 110, screen_height//10 + 130 , 20, GREEN)
                draw_text("D/Right: Rotation sur la droite", screen_width//2 - 110, screen_height//10 + 180, 20, GREEN)
                draw_text("S/Down: Reculer", screen_width//2 - 110, screen_height//10 + 230, 20, GREEN)
                draw_text("Espace: Tire un projectile", screen_width//2 - 110, screen_height//10 + 280, 20, GREEN)
                draw_text("B: Utiliser le laser", screen_width//2 - 110, screen_height//10 + 330, 20, GREEN)
                draw_text("R: Revenir au menu", screen_width//2 - 110,screen_height//10 + 380, 20, GREEN)
            
            draw_text("MENU", bouton_menu[0][0] + 20, bouton_menu[0][1] + 15, 20, bouton_menu[1])
            draw_rectangle_lines(bouton_menu[0][0], bouton_menu[0][1], 100, 50, bouton_menu[1])
            
        end_drawing()
        
        #============================================================

        # gestion des interactions souris-boutons
        if not menu_aide and not page_credits:
            if check_collision_point_rec(mouse_position, bouton_play[0]):
                bouton_play[1] = WHITE
                if is_mouse_button_pressed(0):
                    go_back_to_menu = main(highscore)
            elif check_collision_point_rec(mouse_position, bouton_cancel[0]):
                bouton_cancel[1] = WHITE
                if is_mouse_button_pressed(0):
                    close_window()
            elif check_collision_point_rec(mouse_position, bouton_asteroids[0]):
                bouton_asteroids[1] = WHITE
                if is_mouse_button_pressed(0):
                    game.asteroids.clear()
                    game.asteroids_creation()
            elif check_collision_point_rec(mouse_position, bouton_help[0]):
                bouton_help[1] = WHITE
                if is_mouse_button_pressed(0):
                    menu_aide = True
            elif check_collision_point_rec(mouse_position, bouton_credits[0]):
                if int(highscore) < 25:
                    bouton_credits[1] = RED
                else:
                    bouton_credits[1] = WHITE
                    if is_mouse_button_pressed(0):
                        page_credits = True
            
            else:
                bouton_play[1], bouton_cancel[1], bouton_asteroids[1], bouton_help[1], bouton_credits[1] = GREEN, GREEN, GREEN, GREEN, GREEN
        
        else:
            if not menu_aide:
                credit()
                game.animations.append(Animation(60, (Vector2(randint(0, screen_width), randint(0, screen_height)), choice(COLORS))))
                game.animations[-1].animation_type = game.animations[-1].destruction
            
            if check_collision_point_rec(mouse_position, bouton_menu[0]):
                bouton_menu[1] = WHITE
                if is_mouse_button_pressed(0):
                    menu_aide = False
                    page_credits = False
            else:
                bouton_menu[1] = GREEN

            if is_key_pressed(KEY_R):
                menu_aide = False
                page_credits = False

        if go_back_to_menu:
            menu()
        
menu()