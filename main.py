import pygame #Imports των βιβλιοθηκών και των αντικειμένων από τα αντίστοιχα αρχεία
import time
import threading
import sys,os
from pacman import Pacman as pc
from ghosts import Ghost
from maze import Maze
from bullet import Bullet
import numpy as np
from menu import show_menu, draw_text, draw_text_centered, title_font,menu_font, small_font, small_two_font, load_stats, save_stats
from constants import * # Εισαγωγή των διαστάσεων του παραθύρου του παιχνιδιού και άλλων σταθερών
from collections import defaultdict
import pandas as pd
import copy

class GameStats: #Αντικείμενο GameStats για την επεξεργασία των στατιστικών δεδομένων
    def __init__(self, rows, cols):
        
        self.visit_count = [[0]*cols for _ in range(rows)] #πόσες φορές πέρασε ο Pac-Man από κάθε κελί
        
        self.transition_counts = defaultdict(lambda: defaultdict(int)) #πόσες φορές πήγε από κελί A σε B
        self.prev_tile = None
        self.number_of_players=1 #ιδιότητα που μας δείχνει αν είναι 1 ή 2 παικτών το παιχνίδι
        self.high_scores=[] #Λίστα που αποθηκεύονται τα high_scores

        self.playing_times  = [] #Λίστα για την αποθήκευση των χρόνων παιχνιδιού ανά πίστα
        self.survival_times = [] #Λίστα για την αποθήκευση των χρόνων επιβίωσης του pacman ανά πίστα
        self.beginning_time=0.0 #Iδιότητα για να καταγράφουμε τον χρόνο έναρξης του παιχνιδιού
        self.end_playing_time=0.0 #Iδιότητα για να καταγράφουμε τον χρόνο λήξης του παιχνιδιού ανά πίστα

    def log_pacman(self, x, y, tile_size): #Μέθοδος για την καταχώρηση των επισκέψεων του pacaman με βάση τη θέση (x,y) σε pixels
        tx = int(x // tile_size) #Mετατροπή θέσης (x,y) σε πλακίδιο (tx,ty)
        ty = int(y // tile_size)
        
        self.visit_count[ty][tx] += 1 #καταχώρησε την επίσκεψη για το συγκεκριμένο πλακίδιο (tx,ty) σε tiles
      
        if self.prev_tile is not None and (tx, ty) != self.prev_tile: #στην περίπτωση που υπάρχει πλακίδιο prev_tile και αυτό διαφέρει από το (tx,ty)
            self.transition_counts[self.prev_tile][(tx, ty)] += 1 #καταχώρησε το transition από το πλακίδιο prev_tile στο πλακίδιο (tx,ty)  

        self.prev_tile = (tx, ty) #θέσε ως πλακίδιο prev_tile το (tx,ty)  
      
def load_high_scores(stats):
    filename='Statistics/high_scores.csv'
    if not os.path.exists(filename): #Aν δεν υπάρχει το αρχείο φτιάξε το
        df = pd.DataFrame(columns=['name','score']) #Δημιουργία dataframe για την αποθήκευση του ονόματος του παίκτη και του score
        df.to_csv(filename, index=False)
    else:
        df = pd.read_csv(filename)
    stats.high_scores = df[['name','score']].astype({'score':int}).values.tolist() #Μετέτρεψε τη λίστα σε μορφή [[str,in]]

def save_high_scores(stats, filename='Statistics/high_scores.csv'): #Aποθήκευση των high_scores
    filename='Statistics/high_scores.csv'
    df = pd.DataFrame(stats.high_scores, columns=['name','score']) #Δημιουργούμε DataFrame από stats.high_scores    
    df['score'] = df['score'].astype(int) #Βεβαιωνόμαστε ότι η στήλη score είναι ακέραιος
    df.to_csv(filename, index=False)

paused=False #Σημαία που δείχνει αν ο χρήστης έχει κάνει pause το παιχνίδι πατώντας το πλήκτρο P
new_level_cheat=False #Σημαία για τον έλεγχο του cheat να πηγαίνουμε στην επόμενη πίστα με το πλήκτρο Ν
show_ghost_path_cheat=False #Σημαία για τον έλεγχο του cheat να εμφανίζουμε το μονοπάτι του φαντάσματος με το πλήκτρο Α
show_pacman_region_cheat=False #Σημαία για τον έλεγχο του cheat να εμφανίζουμε την περιοχή του pacman με το πλήκτρο R
infinite_lives_cheat=False #Σημαία για τον έλεγχο του cheat για απεριόριστες ζωές του pacman με το πλήκτρο L
infinite_ammunition_cheat=False #Σημαία για τον έλεγχο του cheat για απεριόριστες ζωές του pacman με το πλήκτρο F
pygame.init() #Χρήση της Pygame για την αρχικοποίηση του παιχνιδιού
pygame.mixer.init() #Χρήση της Pygame.mixer για τους ήχους
pygame.mixer.set_num_channels(11) #Καθορισμός των καναλιών ήχου που θα χρησιμοποιήσουμε (10 σύνολο)

music_channel = pygame.mixer.Channel(0) #Κανάλι ήχου για την μουσική παρασκηνίου

screen = pygame.display.set_mode((WIDTH, HEIGHT))#Δημιουργία του παραθύρου στις αντίστοιχες διαστάσεις
arrow_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)#Διάφανο overlay surface για να σχεδιάζουμε το μονοπάτι των φαντασμάτων
pygame.display.set_caption("Pac-Man by PyGame-Over") #Τίτλος του παραθύρου

pygame.event.post(pygame.event.Event(pygame.ACTIVEEVENT, gain=1, state=pygame.WINDOWFOCUSGAINED)) #Εστίαση (focus) του παραθύρου του παιχνιδιού

bullets = [] #Πίνακας για την αποθήκευση των σφαιρών
ghosts=[] #Πίνακας για την αποθήκευση των φαντασμάτων

# maze_array2D = np.array(maze_layout) #Χρησιμοποιούνται στην περίπτωση που σχεδιάσουμε την πίστα ως array αρχικά
# np.save('Assets/Levels/level1.npy', maze_array2D) #έπειτα την σώζουμε ως αρχείο NumPy Array
maze_array2D = np.load('Assets/Levels/level1.npy') #Φορτώνουμε πλέον την πίστα από αρχείο 
maze_layout=maze_array2D.tolist() #MΜετατρέπουμε σε array από NumPy array

dots = [[0 for _ in range(len(maze_layout[0]))] for _ in range(len(maze_layout))] #Δημιουργία του πίνακα που αντιστοιχεί στη θέση των κουκίδων στην οθόνη,
                                                                                  #1 υπαρχει, 0 δεν υπάρχει, 2 power up dot
maze = Maze(maze_layout, tile_size, dots) #Δημιουργία του αντικειμένου maze

pacman_startXPosition=PACMAN_INITIAL_POSITION[0] * tile_size #Αρχικές συντεταγμένες του pacman σε pixels
pacman_startYPosition=PACMAN_INITIAL_POSITION[1] * tile_size
ghost_startXPosition=GHOSTS_DUNGEON_POSITION[0] * tile_size #Αρχικές συντεταγμένες του κόκκινου φαντάσματος σε pixels
ghost_startYPosition=GHOSTS_DUNGEON_POSITION[1] * tile_size   

pacman1 = pc(pacman_startXPosition,pacman_startYPosition, WIDTH, HEIGHT, tile_size) #Δημιουργία των αντικειμένων pacman και φαντασμάτων
pacman1.id = 1 #Αναγνωριστικό του 1ου παίκτη
pacman1.score=0 #Μηδενισμός του score του 1ου παίκτη
pacman1.level=1 #Αρχική πίστα η πρώτη του 1ου παίκτη
pacman1.dots = copy.deepcopy(maze.dots) #Αποθηκεύουμε την maze.dots στην pacman1.dots
pacman1.maze_layout = copy.deepcopy(maze.maze_layout) #Αποθηκεύουμε την maze.layout στην pacman1.maze_layout

pacman2 = pc(pacman_startXPosition,pacman_startYPosition, WIDTH, HEIGHT, tile_size) #Δημιουργία των αντικειμένων pacman και φαντασμάτων
pacman2.id = 2 #Αναγνωριστικό του 2ου παίκτη
pacman2.score=0 #Μηδενισμός του score του 2ου παίκτη
pacman2.level=1 #Αρχική πίστα η πρώτη του 2ου παίκτη
pacman2.dots = copy.deepcopy(maze.dots) #Αποθηκεύουμε την maze.dots στην pacman2.dots
pacman2.maze_layout = copy.deepcopy(maze.maze_layout) #Αποθηκεύουμε την maze.layout στην pacman2.maze_layout

pacman=pacman1 #Θέτουμε ως παίκτη default τον 1ο παίκτη

ghost_red    = Ghost(ghost_startXPosition, ghost_startYPosition, WIDTH, HEIGHT, tile_size, 2, 1)
ghost_purple = Ghost(ghost_startXPosition + tile_size, ghost_startYPosition, WIDTH, HEIGHT, tile_size, 2, 2)
ghost_blue   = Ghost(ghost_startXPosition + (tile_size*2), ghost_startYPosition, WIDTH, HEIGHT, tile_size, 2, 3)
ghost_orange = Ghost(ghost_startXPosition + (tile_size*3), ghost_startYPosition, WIDTH, HEIGHT, tile_size, 2, 4)

ghosts.append(ghost_red) #τοποθέτηση των φαντασμάτων στον πίνακα ghosts
ghosts.append(ghost_purple)
ghosts.append(ghost_blue)
ghosts.append(ghost_orange)

rows = len(maze.maze_layout)
cols = len(maze.maze_layout[0])
stats = GameStats(rows, cols) #Δημιουργούμε το αντικείμενο stats
load_high_scores(stats) #Φόρτωσε τα high_score
load_stats(stats, pacman.level) #φορτώνουμε τα στατιστικά της αντίστοιχης πίστας (Αρχικό level του pacaman είναι η πίστα 1)

num_rows = len(stats.visit_count) #Υπολογισμός μέγιστου αριθμού γραμμών και στηλών
num_cols = len(stats.visit_count[0])
df_visits = pd.DataFrame(stats.visit_count, #φτιάχνουμε το dataFrame df_visits μέσω της panda.DateFrame()
                         index=range(num_rows), #κάθε γραμμή=y, στήλη=x
                         columns=range(num_cols)) # H stats.visit_count είναι λίστα λιστών: rows × cols

records = [] #Μεταβάσεις tile→tile
for (x,y), inner in stats.transition_counts.items(): #H stats.transition_counts: dict[(x,y)] → dict[(nx,ny)]→count
    for (nx,ny), cnt in inner.items():
        records.append({
            'from_x': x, 'from_y': y,
            'to_x': nx, 'to_y': ny,
            'count': cnt
        })
df_trans = pd.DataFrame.from_records(records) #φτιάχνουμε το dataFrame df_trans μέσω της panda.DateFrame()
df_times = pd.DataFrame({'level': range(1, len(stats.playing_times) + 1),'time_sec': stats.playing_times}) #Φτιάχνουμε το dataFrame df_times για την αποθήκευση των χρόνων 
df_surv = pd.DataFrame({ #Φτιάχνουμε το dataFrame df_surv για την αποθήκευση των χρόνων επιβίωσης ανά πίστα                                   #παιχνιδιού ανά πίστα
    'level': range(1, len(stats.survival_times) + 1),
    'survival_sec': stats.survival_times
})
                                                                                                            
def restart_game(ghosts,maze,stats,pacman): #Επανεκκίνση του παχνιδιού
    save_stats(stats, pacman.level)

    menu_music  = pygame.mixer.Sound("Assets/Sounds/background.mp3")
    pygame.mixer.Channel(0).play(menu_music, loops=-1) #Αναπαράγουμε την μουσική παρασκηνίου
    pygame.mixer.Channel(0).set_volume(0.3) #Χαμηλώνουμε την ένταση ώστε να ακούγονται οι ήχοι του παιχνιδιού
    arrow_layer.fill((0, 0, 0, 0))#Καθαρισμός του arrow layer
           
    pacman1.score=0 #Μηδενισμός του score του 1ου παίκτη
    pacman1.level=1 #Αρχική πίστα η πρώτη του 1ου παίκτη
    pacman1.lives=3 #Αρχικοποίηση ζωών 
    pacman2.score=0 #Μηδενισμός του score του 2ου παίκτη
    pacman2.level=1 #Αρχική πίστα η πρώτη του 2ου παίκτη
    pacman2.lives=3 #Αρχικοποίηση ζωών
    pacman=pacman1
    maze_array2D = np.load('Assets/Levels/level1.npy') #Φορτώνουμε πλέον την πίστα από αρχείο 
    maze_layout=maze_array2D.tolist() #MΜετατρέπουμε σε array από NumPy array
    maze.maze_layout=maze_layout #Φορτώνουμε την αρχική maze_layout του level 1
    maze.dots = [[0 for _ in range(len(maze.maze_layout[0]))] for _ in range(len(maze.maze_layout))] #Ανανέωση του πίνακα που αντιστοιχεί στη θέση των κουκίδων στην οθόνη,

    maze.update_maze() #Ανανέωνουμε την πίστα σύμφωνα με το παρόν level που παίζει ο χρήστης
    maze.draw_maze_and_dots(screen,dot_image,power_dot_image,pacman)#Σχεδίασε την πίστα και τις κουκίδες
    maze.recount_total_dots() #υπολόγισε ξανά τον αριθμό των κουκίδων που έχουν απομείνει 
    pacman1.dots=maze.dots
    pacman2.dots=maze.dots
    pacman1.maze_layout=maze.maze_layout
    pacman2.maze_layout=maze.maze_layout        
    pacman.x=PACMAN_INITIAL_POSITION[0] * tile_size #Αρχικές συντεταγμένες του pacman σε pixels
    pacman.y=PACMAN_INITIAL_POSITION[1] * tile_size
    pacman.direction = pygame.Vector2(0, 1) #Aρχική κατεύθυνση κάτω
    pacman.current_frame = 0 #Αρχική σκηνή του pacman με κλειστό στόμα

    for ghost in ghosts[:]: #Ζωντάνεψε όλα τα φαντάσματα στην αρχική τους θέση
        ghost.revive(ghost) 

    pacman.alive=True #θέση των ιδιοτήτων alive σε True για όλα τα sprites
    pacman.hunter=False #Ο pacman είναι θήραμα στην αρχή
    pacman.ghosts_eaten=0 #Μηδενισμός της σημαίας που δείχνει πόσα φαντάσματα έχουν φαγωθεί
    
    for ghost in ghosts[:]: #τοποθέτηση ξανά όλων των φαντασμάτων στον πίνακα ghosts και αρχικοποίησή τους
        ghost.alive=True
        ghost.hunter=True
        ghost.change_skin(False, ghost.id) #Τοποθέτηση αρχικού skin κυνηγού για κάθε φάντασμα

def restart_level(ghosts): #επανεκκίνηση της πίστας όταν ο pacman χάσει μια "ζωή" ή αλλάξει πίστα
    screen.fill((BLACK))  #Καθάρισε όλη την οθόνη με μαύρο χρώμα
    arrow_layer.fill((0, 0, 0, 0))#Καθαρισμός του arrow layer πάνω στο οποίο σχεδιάζουμε στην οθόνη το μονοπάτι του φαντάσματος
    maze.draw_maze_and_dots(screen,dot_image,power_dot_image,pacman)#Σχεδίασε την πίστα και τις κουκίδες
    maze.recount_total_dots() #υπολόγισε ξανά τον αριθμό των κουκίδων που έχουν απομείνει  
    df_visits.to_csv(f"Statistics/visits_level{pacman.level}.csv", index=True) #Αποθήκευσε τα dataframes σε μορφή csv
    df_trans.to_csv(f"Statistics/transitions_level{pacman.level}.csv", index=False)
    df_times.to_csv(f"Statistics/playing_times_level{pacman.level}.csv", index=False)
    df_surv.to_csv(f"Statistics/survival_times_level{pacman.level}.csv", index=False)
    pacman.x=PACMAN_INITIAL_POSITION[0] * tile_size #Αρχικές συντεταγμένες του pacman σε pixels
    pacman.y=PACMAN_INITIAL_POSITION[1] * tile_size
    pacman.direction = pygame.Vector2(0, 1) #Aρχική κατεύθυνση κάτω
    pacman.current_frame = 0 #Αρχική σκηνή του pacman με κλειστό στόμα

    for ghost in ghosts[:]: #Ζωντάνεψε όλα τα φαντάσματα στην αρχική τους θέση
        ghost.revive(ghost) 
    pacman.alive=True #θέση των ιδιοτήτων alive σε True για όλα τα sprites
    pacman.hunter=False #Ο pacman είναι θήραμα στην αρχή
    pacman.ghosts_eaten=0 #Μηδενισμός της σημαίας που δείχνει πόσα φαντάσματα έχουν φαγωθεί
    
    for ghost in ghosts[:]: #τοποθέτηση ξανά όλων των φαντασμάτων στον πίνακα ghosts και αρχικοποίησή τους
        ghost.alive=True
        ghost.hunter=True
        ghost.change_skin(False, ghost.id) #Τοποθέτηση αρχικού skin κυνηγού για κάθε φάντασμα

def new_level(stats, df_visits, df_trans, df_times): #Αλλαγή πίστας
            for channel in range(1,10): #Κλείσιμο όλων των καναλιών ήχουν εκτός από του παρασκηνίου
                pygame.mixer.Channel(channel).fadeout(50)
            pygame.mixer.Channel(0).pause() #Παύση του καναλιού παρασκηνίου
            new_level_sound  = pygame.mixer.Sound("Assets/Sounds/new-level.mp3")
            pygame.mixer.Channel(9).play(new_level_sound, loops=0)
            for i in range(1,6): #Δημιουργία εφέ με το γέμισμα της πίστας με άλλο χρώμα    
                maze.invert_draw(screen)
                maze.invert_draw_maze_and_dots(screen, dot_image, power_dot_image)
                pacman.draw(screen)
                for ghost in ghosts[:]:
                    ghost.draw(screen)
                pygame.display.flip() #Ανανέωσε την οθόνη
                time.sleep(0.4)
                maze.draw(screen,pacman)
                maze.invert_draw_maze_and_dots(screen, dot_image, power_dot_image)
                pacman.draw(screen)
                for ghost in ghosts[:]:
                    ghost.draw(screen)
                pygame.display.flip() #Ανανέωσε την οθόνη
                time.sleep(0.4)
            stats.end_playing_time=time.time() #Καταγραφή τέλους χρόνου παρούσας πίστας
            level_playing_time=stats.end_playing_time - stats.beginning_playing_time #υπολογισμός χρόνου παιχνιδιού
            
            stats.playing_times.append(level_playing_time) #καταγραφή του χρόνου στο αντικείμενο stats για την παρούσα πίστα
            
            save_stats(stats, pacman.level) #αποθήκευσε τα στατιστικά
            df_visits.to_csv(f"Statistics/visits_level{pacman.level}.csv", index=True) #Αποθήκευσε τα dataframes σε μορφή csv
            df_trans.to_csv(f"Statistics/transitions_level{pacman.level}.csv", index=False)
            df_times.to_csv(f"Statistics/playing_times_level{pacman.level}.csv", index=False)
            df_surv.to_csv(f"Statistics/survival_times_level{pacman.level}.csv", index=False)
            pacman.begin_message=True #Σημαία για την εμφάνιση του μηνύματος "READY!"
            pacman.level+=1 #Αύξηση της πίστας κατά 1
            pacman.direction = pygame.Vector2(0, 1) #Aρχική κατεύθυνση κάτω
            pacman.current_frame = 0 #Αρχική σκηνή του pacman με κλειστό στόμα
            maze_array2D = np.load('Assets/Levels/level'+str(pacman.level)+'.npy') #Φόρτωσε την αντίστοιχη πίστα από το αρχείο σύμφωνα με το string που σχηματίζεται
            maze.maze_layout=maze_array2D.tolist() #Μετατροπή σε array από NumPy Array
            maze.dots = [[0 for _ in range(len(maze.maze_layout[0]))] for _ in range(len(maze.maze_layout))] #Ανανέωση του πίνακα που αντιστοιχεί στη θέση των κουκίδων στην οθόνη,
            maze.update_maze() #Ανανέωσε την πίστα σύμφωνα με τις νέες αλλαγές
            restart_level(ghosts) #Επανεκκίνησε την πίστα
            
            pacman.draw(screen) #Εμφάνισε το sprite του pacman
            for ghost in ghosts: #Εμφάνισε τα sprite των φαντασμάτων
                    ghost.draw(screen)
                    
def show_scores(pacman,screen): #Εμφάνισε τον αριθμό των πόντων
    if not pacman.infinite_lives: #Aν το cheat για απεριόριστες ζωές δεν είναι ενεργοποιημένο
        for i in range(pacman.lives):  #Σχεδίασε τον αριθμό των ζωών του pacman       
            screen.blit(pygame.transform.scale(pacman.frames[1], (25, 25)), (50 + (i * 35)+(pacman.id-1)*700, 915))
    else:
            draw_text("Infinite lives", 50+(pacman.id-1)*700, 915, small_two_font, YELLOW) #Σχεδίασε το σκορ
    if not pacman.infinite_ammunition: #Aν το cheat για απεριόριστα πυρομαχικά δεν είναι ενεργοποιημένο        
        for i in range((pacman.ammunition+14)//15): #Σχεδίασε τα πυρομαχικα του pacman     
            screen.blit(pygame.transform.scale(sprite_sheet_bullets_frames[0], (25, 25)), (40 + (i * 12)+(pacman.id-1)*600, 950)) #Σχεδίασε τα πυρομαχικά      
    else:
            draw_text("Infinite ammunition", 40+(pacman.id-1)*600, 950, small_two_font, YELLOW) #Σχεδίασε το σκορ
    
    draw_text("Score "+str(pacman.score), 350, 880, small_two_font, YELLOW) #Σχεδίασε το σκορ
    
    if pacman.id==1: #Εμφάνισε τις ζωές του pacman στην αριστερή ή δεξιά πλευρά
        position=50
    else:
        position=600            
    draw_text("Player "+str(pacman.id)+": ", position, 985, small_two_font, YELLOW) #Σχεδίασε τo χαρακτηριστικό του παίκτη αν πρόκειται για 2 παικτών παιχνίδι
    draw_text(pacman.player_name, position+110, 985, small_two_font, RED) #Σχεδίασε τo όνομα του παίκτη με κόκκινο χρώμα
    pacman.player_name
    
    for i in range(pacman.level): #Σχεδίασε τα φρούτα που αντιστοιχούν στην τρέχουσα πίστα   
        screen.blit(pygame.transform.scale(level_frames[i], (25, 25)),(610+((7-i)*35), 880))
    # pygame.display.flip()
    
def show_ready_message(pacman,stats):
        screen.blit(ready_message_image, (368, 448)) #Σχεδίασε το μήνυμα "Ready!"
        pygame.display.update()
        time.sleep(2) #Κάνε παύση για 2 sec        
        pacman.begin_message=False #Θέσε τη σημαία σε False        
        now = time.time() 
        stats.beginning_playing_time   = now #Κατέγραψε τον χρόνο εκκίνησης του παιχνιδιού
        stats.beginning_survival_time  = now #Κατέγραψε τον χρόνο εκκίνησης της πίστας
    
show_menu(maze, stats, pacman1, pacman2) #εμφάνιση του αρχικού μενού
pygame.display.update() #Ανανέωσε την οθόνη
clock = pygame.time.Clock()
running = True #σημαία για τον έλεγχο της ροής του παιχνιδιού
bulletFiredFlag=False #σημαία ότι έχει γίνει εκτόξευση σφαίρας
  
background_music  = pygame.mixer.Sound("Assets/Sounds/background.mp3") #αρχείο μουσικής παρασκηνίου

pygame.mixer.Channel(0).play(background_music, loops=-1) #Παίξε την μουσική παρασκηνίου
pygame.mixer.Channel(0).set_volume(0.3) #Χαμήλωσε την ένταση για να ακούγονται οι ήχοι του παιχνιδιού

while running: #Βρόχος του παιχνιδιού

    if not pygame.mixer.Channel(4).get_busy() and not pygame.mixer.Channel(6).get_busy() and not paused: #Αν τα κανάλια 4 και 6 δεν παίζουν ήχους (μουσική για pacman hunter)
        pygame.mixer.Channel(0).unpause() #Παίξε την μουσική παρασκηνίου
        pygame.mixer.Channel(0).set_volume(0.3) #Χαμήλωσε την ένταση για να ακούγονται οι ήχοι του παιχνιδιού

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #έξοδος από το παιχνίδι (κλείσιμο παραθύρου)
            running = False #Θέσε τη σημαία False          
          
        if event.type == pygame.KEYDOWN: #Αν πατήθηκε κάποιο πλήκτρο
            if event.key == pygame.K_n: #Αν είναι το πλήκτρο Ν τότε αν η σημαία new_level_cheat είναι False
                new_level_cheat = True #Σήκωσε την σημαία σε True
                if new_level_cheat: 
                    new_level(stats, df_visits, df_trans, df_times) #Πήγαινε στην επόμενη πίστα
                               
            if event.key == pygame.K_a: #Αν είναι το πλήκτρο A τότε αν η σημαία show_ghost_path_cheat είναι False εμφάνισε το path των φαντασμάτων
                show_ghost_path_cheat=True #Σήκωσε τη σημαία show_ghost_path_cheat
                if show_ghost_path_cheat:
                    for ghost in ghosts[:]:
                          if ghost.show_arrow==True: #Κάνε toggle τη σημαία ghost.show_arrow σε όλα τα φαντάσματα
                              ghost.show_arrow=False
                          else:
                              ghost.show_arrow=True
            if event.key == pygame.K_r: #Αν είναι το πλήκτρο R τότε αν η σημαία show_pacman_region_cheat είναι False εμφάνισε την περιοχή του pacman
                show_pacman_region_cheat=True
                if show_pacman_region_cheat:
                    if  pacman.show_pacman_region==True:
                        pacman.show_pacman_region=False
                    else:
                        pacman.show_pacman_region=True
                        
            if event.key == pygame.K_l: #Αν είναι το πλήκτρο L τότε αν η σημαία infinite_lives_cheat είναι False θέσε τη σημαία του pacman infinite_lives για απεριόριστες ζωές
                infinite_lives_cheat=True
                if infinite_lives_cheat:
                    if  pacman.infinite_lives==True:
                        pacman.infinite_lives=False
                    else:
                        pacman.infinite_lives=True
                        
            if event.key == pygame.K_f: #Αν είναι το πλήκτρο F τότε αν η σημαία infinite_ammunition_cheat είναι False θέσε τη σημαία του pacman infinite_ammunition για απεριόριστα πυρομαχικά
                infinite_ammunition_cheat=True
                if infinite_ammunition_cheat:
                    if  pacman.infinite_ammunition==True:
                        pacman.infinite_ammunition=False
                    else:
                        pacman.infinite_ammunition=True
                    
            if event.key == pygame.K_q: #Αν πατήθηκε το πλήκτρο Q κάνε έξοδο από το παιχνίδι       
                stats.high_scores.append(pacman.score) #αποθήκευσε τα high scores
                pygame.quit() #Έξοδος από το παιχνίδι
                sys.exit()
                
            if event.key == pygame.K_p: #Αν ο χρήστης πατήσει το πλήκτρο P γίνονται pause όλα τα κανάλια ήχου
                paused = not paused #Κάνε toggle τη σημαία pause 
                if paused:
                    for i in range(0,11):
                        pygame.mixer.Channel(i).pause() #Κάνε pause όλα τα κανάλια ήχου
                                         
                    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    s.fill((0,0,0,150))           
                    screen.blit(s, (0,0)) #Εμφάνισε ημιδιάφανο μαύρο layer πάνω από το παιχνίδι
                    draw_text_centered("PAUSED", HEIGHT//2, title_font, YELLOW)
                    pygame.display.flip() #Ανανέωσε την οθόνη
                else:
                    for i in range(1,11):
                        pygame.mixer.Channel(i).unpause() #Κάνε unpause όλα τα κανάλια ήχου 
                    if pacman.hunter==False: #Κάνε unpause το κανάλι 0 (μουσική παρασκηνίου) μόνο αν ο pacman δεν είναι κυνηγός
                        pygame.mixer.Channel(0).unpause() 

        elif event.type == pygame.KEYUP: #Ομοίως αν έχει αφεθεί κάποιο πλήκτρο Ν ή Α ή R κάνε False τις αντίστοιχες σημαίες των παραπάνω cheat
            if event.key == pygame.K_n:
                new_level_cheat = False                
            if event.key == pygame.K_a:                
                show_ghost_path_cheat=False
            if event.key == pygame.K_r: 
                show_pacman_region_cheat=False
            if event.key == pygame.K_l: 
                infinite_lives_cheat_cheat=False
            if event.key == pygame.K_f: 
                infinite_ammunition_cheat=False
                            
    if not paused:
    
        bulletFired=pacman.handle_keys(ghosts) #Έλεγξε αν πατήθηκε κάποιο πλήκτρο και αν εκτοξεύθηκε σφαίρα
        if bulletFired: #έλεγξε αν έχει εκτοξευθεί σφαίρα (Τrue αν έχει εκτοξευθεί) Χρησιμεύει για να αποφύγουμε πολλαπλό trigger
            bullets.append(Bullet(pacman.x, pacman.y , WIDTH, HEIGHT, maze.maze_layout, tile_size,pacman.direction)) #καταχώρησε μια σφαίρα στον πίνακα bullets
            gun_sound  = pygame.mixer.Sound("Assets/Sounds/gun.mp3") #Αρχείο ήχου πυροβολισμού
            pygame.mixer.Channel(1).play(gun_sound, loops=0) #Παίξε τον ήχο πυροβολισμού
            pygame.mixer.Channel(1).fadeout(700) #Κάνε fade μετά από 0.7 sec
            if not pacman.infinite_ammunition: #Αν η σημαία infinite ammunition δεν είναι True
                pacman.ammunition=pacman.ammunition-1 #Μείωσε τα πυρομαχικά (σφαίρες) κατά 1
            bulletFiredFlag=True #θέσε τη σημαία σε False 
    
        stats.log_pacman(pacman.x, pacman.y, pacman.tile_size) #καταχώρησε τα στατιστικά πριν την κίνηση του pacman
    
        pacman.move(maze) #Κίνηση του sprite pacman
        
        stats.log_pacman(pacman.x, pacman.y, pacman.tile_size) #καταχώρησε τα στατιστικά μετά την κίνηση του pacman
    
        for ghost in ghosts:
            ghost.move(pacman, maze) #κίνηση του pacman βάσει της θέσης του
        
        for bullet in bullets[:]: #κίνηση όλων των σφαιρών (fireballs)
            bullet.move(screen)
            for ghost in ghosts[:]: #Έλεγχος αν υπάρχει σύγκρουση κάποιας σφαίρας με ένα φάντασμα
                if bullet.check_ghost_collision(ghost):
                    explosion_sound  = pygame.mixer.Sound("Assets/Sounds/explosion.mp3")
                    pygame.mixer.Channel(3).play(explosion_sound, loops=0)
                    ghost.alive = False #Θέσε το φάντασμα ως νεκρό
                    ghost.revive(ghost) #Ζωντάνεψε το φάντασμα1
            if bullet.destoyed or bullet.x>WIDTH-32 or bullet.x<bullet.tile_size: #Αφαίρεσε όποια σφαίρα εκρήχθηκε
                bullets.remove(bullet)
        
        pacman.check_dot_collision(maze, screen, ghosts, CHASING_TIME-pacman.level) #Έλεγξε αν ο pacman έχει συγκρουστεί με κάποιο φάντασμα
              
        if pacman.hunter: #Αν o pacman είναι σε κατάσταση κυνηγού (ιδιότητα hunter True)
            current_time=time.time() #καταχώρηση τρέχοντα χρόνου
            if current_time-pacman.hunting_start_time>= CHASING_TIME-pacman.level or pacman.ghosts_eaten==4:#υπολόγισε την χρονική διαφορά από την ώρα που κατανάλωσε
                pygame.mixer.Channel(4).stop()
                for ghost in ghosts[:]:  #άλλαξε το skin των φαντασμάτων που υπάρχουν στον πίνακα ghoss σε κυνηγούς                
                    ghost.change_skin(False, ghost.id)
                    ghost.hunter=True
                pacman.hunter=False #Θέσε τον pacman σε κατάσταση θηράματος
                pacman.ghosts_eaten=0 #Μηδένισε τον αριθμό των φαντασμάτων που έχουν καταναλωθεί
                
                # pygame.mixer.Channel(0).unpause()
        pygame.display.update() #ανανέωσε την οθόνη
    
        screen.fill((BLACK))  #Καθάρισε όλη την οθόνη με μαύρο χρώμα
        maze.draw_maze_and_dots(screen,dot_image,power_dot_image,pacman)#Σχεδίασε την πίστα και τις κουκίδες
        arrow_layer.fill((0, 0, 0, 0))#Καθαρισμός του arrow layer
        for ghost in ghosts: #Σχεδίασε το μονοπάτι όλων των φαντασμάτων
            ghost.draw_path(arrow_layer)
        screen.blit(arrow_layer, (0, 0))
    
        pacman.draw(screen)  #Σχεδίασε το sprite του pacman
        
        for bullet in bullets[:]: #Σχεδίασε όλες τις σφαίρες 
            bullet.draw(screen)      
        
        for ghost in ghosts[:]: #Για όλα τα φαντάσματα που υπάρχουν στον πίνακα ghosts κάνε τους παρακάτω ελέγχους
                    
            if pacman.check_ghost_collision(ghost) and pacman.alive==True and ghost.alive==True and ghost.hunter==True: #Aν ο pacman έχει συγκρουστεί με φάντασμα και δεν είναι κυνηγός
                end_survival_time = time.time() #Καταγραφή του χρόνου που έχασε ο pacman τη ζωή του
                stats.survival_times.append(end_survival_time - stats.beginning_survival_time) #Υπολογισμός του χρόνου επιβίωσης και αποθήκευσή της στο αντικείμενο stats
                if not pacman.infinite_lives: #Αν το cheat για απεριόριστες ζωές δεν είναι ενεργοποιημένο 
                   pacman.lives=pacman.lives-1 #Αφαίρεσε μια ζωή
                pacman.begin_message=True
                # threading.Thread(target=pacman.death, args=(screen, ghosts)).start()
                pacman.death(screen,ghost,ghosts,maze)
                pacman.dots = copy.deepcopy(maze.dots) #Aποθηκεύουμε τις κουκίδες ώστε αν πρόκειται για παιχνίδι δύο παικτών να μπορούμε να τις ανακτήσουμε στην αλλαγή του παίκτη
                pacman.maze_layout = copy.deepcopy(maze.maze_layout)
                if stats.number_of_players==2 and pacman.lives>=0:#Αν πρόκειται για παιχνίδι δύο παικτών και ο τρέχων παίκτης έχει ζωές, άλλαξε παίκτη
                    if pacman==pacman1:
                        pacman=pacman2
                    else:
                        pacman=pacman1
                
                if pacman.lives>=0: #Αν έχει ο τρέχων παίκτης ζωές
                    
                    pacman.direction = pygame.Vector2(1, 0)  #Αρχική κατεύθυνση του pacman δεξιά
                    
                    maze.dots = copy.deepcopy(pacman.dots) #Aνακτούμε τις κουκίδες της πίστας που είχε ο pacman
                    maze.maze_layout=copy.deepcopy(pacman.maze_layout) #Aνακτούμε την πίστα που είχε ο pacman
                    restart_level(ghosts) #Επανεκκίνησε την πίστα
                    pacman.draw(screen) #Σχεδίασε το sprite του pacman
                    for ghost in ghosts[:]: #Σχεδίασε τα sprite των φαντασμάτων
                        ghost.draw(screen)
                    menu_active = False #Θέσε τη σημαία σε False
                
                elif pacman.lives<0:
                    game_over_sound  = pygame.mixer.Sound("Assets/Sounds/game-over.mp3")
                    pygame.mixer.Channel(9).play(game_over_sound, loops=-1) #Παίξε την μουσική για το game over
                    score_to_save=[pacman.player_name,pacman.score]                    
                    stats.high_scores.append(score_to_save) #Καταχώρησε το score στα high scores
                    save_high_scores(stats) #αποθήκευσε τα high score
                    menu_active = True #Θέσε τη σημαία σε True για να εμφανιστεί το αρχικό menu
                    blink = True #Σημαία για το τρεμόπαιγμα
                    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα
                    blink_interval = 500 #Χρονικό διάστημα σε ms
                    while menu_active: #Βρόχος εμφάνισης αρχικού μενού                 
                        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
                        text="GAME OVER!"
                        draw_text_centered(text, 400, title_font, YELLOW) #Εμφάνισε το μήνυμα GAME OVER
                        if stats.number_of_players==2:#Αν πρόκειται για παιχνίδι 2 παικτών πρόσθεσε και το μήνυμα "player" + 1 ή 2+"!"
                            text="PLAYER "+str(pacman.id)
                            draw_text_centered(text, 450, title_font, YELLOW) #Εμφάνισε και το μήνυμα "PLAYER" + 1 ή 2
                                               
                        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα του μηνύματος "Press Q to Quit" ανά 500ms
                        if current_time - blink_timer > blink_interval:
                            blink = not blink
                            blink_timer = current_time
                        if blink:
                            draw_text_centered("Press any key", HEIGHT - 50, small_font, YELLOW)
                        pygame.display.update()  #Ανανέωσε την οθόνη
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:  #Έξοδος από το παιχνίδι (κλείσιμο παραθύρου)
                                pygame.quit()
                                sys.exit()
                            elif event.type == pygame.KEYDOWN:  #Αν πατηθεί κάποιο πλήκτρο πήγαινε στο αρχικό μενού
                                pygame.mixer.Channel(9).fadeout(50)
                                if stats.number_of_players==2:
                                    if pacman==pacman1: #Άλλαξε παίκτη αφού ο τρέχων παίκτης έχασε όλες τις ζωές του
                                        pacman=pacman2                                    
                                    else:
                                        pacman=pacman1                                    
                                    if pacman.lives<0:                                   
                                        menu_active = False #Θέσε τη σημαία σε False
                                        show_menu(maze, stats, pacman1, pacman2) #Εμφάνισε το αρχικό μενού
                                        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα                                 
                                        restart_game(ghosts,maze,stats,pacman) #Εκκίνηση της πίστας
                                        pacman.draw(screen)
                                        for ghost in ghosts[:]:
                                            ghost.draw(screen)
                                    elif pacman.lives>=0:
                                        pacman.direction = pygame.Vector2(1, 0)  #Αρχική κατεύθυνση του pacman δεξιά
                                        maze.dots = copy.deepcopy(pacman.dots) #Aνακτούμε τις κουκίδες της πίστας που είχε ο pacman
                                        maze.maze_layout=copy.deepcopy(pacman.maze_layout) #Aνακτούμε την πίστα που είχε ο pacman                                    
                                        restart_level(ghosts) #Επανεκκίνησε την πίστα
                                        pacman.draw(screen) #Σχεδίασε το sprite του pacman
                                        for ghost in ghosts[:]: #Σχεδίασε τα sprite των φαντασμάτων
                                            ghost.draw(screen)
                                        menu_active = False #Θέσε τη σημαία σε False
                                elif stats.number_of_players==1: #Aν πρόκειται για παιχνίδι 1 παίκτη
                                        menu_active = False #Θέσε τη σημαία σε False
                                        show_menu(maze, stats,pacman1, pacman2) #Εμφάνισε το αρχικό μενού
                                        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα                                  
                                        restart_game(ghosts,maze,stats,pacman) #Εκκίνηση της πίστας
                                        pacman.draw(screen)
                                        for ghost in ghosts[:]:
                                            ghost.draw(screen)
                     
            if pacman.check_ghost_collision(ghost) and pacman.hunter==True and ghost.alive==True and pacman.alive==True and ghost.hunter==False: #Aν ο pacman έχει συγκρουστεί με φάντασμα και είναι κυνηγός  
                    ghost.alive=False #Θέσε την ιδιότητα alive του φαντάσματος σε False. To φάντασμα είναι νεκρό.               
                    eat_ghost_sound  = pygame.mixer.Sound("Assets/Sounds/eat-ghost.mp3")
                    pygame.mixer.Channel(10).play(eat_ghost_sound, loops=0)                  
                    
                    time.sleep(0.1) #κάνε παύση 0.1 sec
                    start_time_ghost_eaten=time.time() #Κατέγραψε την χρονική στιγμή που καταναλώθηκε το φάντασμα
                    if pacman.ghosts_eaten==4: #Αν έχουν καταναλωθεί 4 φαντάσματα μηδένισε τον μετρητή
                        pacman.ghosts_eaten=0
                    
                    pacman.ghosts_eaten=pacman.ghosts_eaten+1 #Αύξησε τον μετρητή του πόσα φαντάσματα έχουν καταναλωθεί κατά 1                 
                    ghost.trigger_show_points(ghost_points_frames, pacman.ghosts_eaten) #Μαρκάρισε το φάντασμα ότι φαγώθηκε και να εμφανιστούν οι πόντοι
                              
                    pacman.score=pacman.score+(2**(pacman.ghosts_eaten)*100) #Υπολόγισε το αντίστοιχο score και καταχώρησέ το στην ιδιότητα score
                    ghost.revive(ghost) #Ξαναζωντάνεψε το φάντασμα
                    ghost.hunter=True #Κάνε το φάντασμα κυνηγό
                    ghost.change_skin(False,ghost.id) #Άλλαξε το skin του φαντάσματος σε κυνηγό                    
                                                                  
            if pacman.alive:
                ghost.draw(screen) #Σχεδίασε το φάντασμα μόνο αν ο pacman είναι ζωντανός (για να αποφύγουμε λάθος σχεδίαση όταν εκτελείται η pacman.death())
                
                if ghost.show_points:
                    elapsed = time.time() - ghost.points_start_time
                    if elapsed < ghost.points_duration:
                        screen.blit(ghost.points_frame, (ghost.points_x, ghost.points_y))                                              
                    else:
                        ghost.show_points = False
        if pacman.score>=10000 and pacman.life_bonus==False: #Aν ο pacman κάνει score 10000 τότε κερδίζει μια ζωή
            for i in range(0,11):
                pygame.mixer.Channel(i).pause()              
            pacman.lives+=1
            pacman.life_bonus=True #Θέτουμε True τη σημαία life_bonus για να αποφύγουμε πολλαπλό trigger
            bonus_life_sound  = pygame.mixer.Sound("Assets/Sounds/bonus-life.mp3")
            pygame.mixer.Channel(9).play(bonus_life_sound, loops=0) #Aναπαραγωγή του ήχου bonus life
            for i in range(0,11):
                pygame.mixer.Channel(i).unpause()    
   
        if maze.total_dots==0: #Aν ο pacman κατανάλωσε όλες τις κουκίδες τότε
    
            new_level(stats, df_visits, df_trans, df_times) #Σχεδίασε τη νέα πίστα
      

        
        show_scores(pacman,screen) #Εμφάνισε score και τις άλλες πληροφορίες στη βάση της οθόνης
    
        pygame.display.flip() #Ανανέωσε την οθόνη
    
        clock.tick(60) #Θέσε την τιμή 60 για τα frames per second του παιχνιδιού
        if pacman.begin_message: #Aν η σημαία είναι True    
            show_ready_message(pacman,stats) #εμφάνισε το μήνυμα Ready!            
    else:  
        draw_text_centered("PAUSED", HEIGHT//2, title_font, YELLOW) #Σχεδιάζουμε το μήνυμα "PAUSED"  
       
pygame.quit()
save_stats(stats, pacman.level) #αποθήκευσε τα στατιστικά αν ο χρήστης κάνει έξοδο από το παιχνίδι
sys.exit()

