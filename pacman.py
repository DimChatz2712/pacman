import pygame
import threading
import time
from constants import BLACK,POWER_UP_EARTHQUAKE,WIDTH, HEIGHT, YELLOW #Εισαγωγή σταθερής μεταβλητής για τη διάρκεια του εφέ του σεισμού στην κατανάλωση power up κουκίδας

class Pacman:  #Δημιουργία του αντικειμένου Pacman

    
    @staticmethod
    def _direction_from_keys(keys): #Θα τη χρησιμοποιήσουμε στο unitest για τον έλεγχο των πλήκτρων
        dx = dy = 0 #μετατρέπει ένα keys = pygame.key.get_pressed() σε vector κατεύθυνσης
        if keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_DOWN]:  dy += 1
        return pygame.Vector2(dx, dy)

    def __init__(self, x, y, screen_width, screen_height, tile_size):
        self.x = x #Οριζόντια συντεταγμένη σε pixels  #Ιδιότητες αντικειμένου
        self.y = y #Κάθετη  συντεταγμένη σε pixels
        self.speed = 4 #Κίνηση sprite σε pixels
        self.lives= 2 #Ζωές του pacman
        self.alive=True#Σημαία ότι ο pacman είναι ζωντανός
        self.begin_message=True #σημαία για τον έλεγχο εμφάνισης του μηνύματος "Ready!"
        self.direction = pygame.Vector2(0, -1) #Aρχική κατεύθυνση κάτω
        self.next_direction = self.direction #Επόμενη κατεύθυνση
        self.hunter= False #Σημαία ότι ο pacman είναι κυνηγός (έχει καταναλώσει power up κουκίδα)
        self.hunting_start_time=0.0 #Αρχικοποίηση του χρόνου που ο pacman είναι κυνηγός
        self.score= 0 #Σκορ
        self.screen_width = screen_width #Πλάτος παραθύρου σε pixels
        self.screen_height = screen_height #Υψος παραθύρου σε pixels
        self.level=1 #Τρέχουσα πίστα
        self.ghosts_eaten=0 #Φαντάσματα που έχει φάει ο pacman αφού κατανάλωσε μια power up κουκίδα
        self.ate_a_dot=False #Σημαία ότι έφαγε μια κουκίδα για να αποφύγουμε το πολλαπλό trigger
        self.ammunition=300 #Πυρομαχικά που έχει ο pacman
        self.infinite_lives=False #Σημαία για απεριόριστες ζωές
        self.infinite_ammunition=False #Σημαία για απεριόριστα πυρομαχικά
        self.tile_size = tile_size #Μέγεθος πλακιδίου        
        self.player_name='' #Αρχικοποίηση ονόματος παίκτη
        self.id=1 #Χαρακτηριστικό του παίκτη
        self.dots=[] #Aποθηκεύουμε τις κουκίδες της πίστας όταν χάνει τη ζωή του ο pacman 
        self.maze_layout=[] #Aποθηκεύουμε την πίστα όταν χάνει τη ζωή του ο pacman
        self.life_bonus=False #Σημαία για τον καθορισμό του life bonus για την αποφυγή πολλαπλού trigger
        self.show_pacman_region=False #Σημαία για την απεικόνιση του κύκλου περιοχής του pacman


        sprite_sheet = pygame.image.load("Assets/Sprites/pacman_sprites.png").convert_alpha()#Φόρτωση εικόνας pacman

        self.frames = [#Δημιουργία των σκηνών του  pacman
            sprite_sheet.subsurface(pygame.Rect(64, 0, 32, 32)), #κλειστό στόμα
            sprite_sheet.subsurface(pygame.Rect(32, 0, 32, 32)), #μισόκλειστο στόμα
            sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32)),  #ανοικτό στόμα
        ]
        
        self.current_frame = 0 #Τρέχουσα σκηνή
        self.animation_speed = 3 #Ταχύτητα ανανέωσης της σκηνής
        self.frame_counter = 0 #Μετρητής τρέχουσας σκηνής
        self.rotated_frames = self.frames.copy()#Αποθήκευση περιστραμένων σκηνών του sprite
        
    @property
    def position(self): #Μέθοδος που επιστρέφει τη θέση του αντικειμένου
        return pygame.Vector2(self.x, self.y)
            
    @position.setter #Μέθοδος για τροποποίηση της θέση του αντικειμένου
    def position(self, value):
        self.x = value.x #Οριζόντια θέση
        self.y = value.y #Κάθετη θέση
        
    @property
    def hunting(self): #Μέθοδος που επιστρέφει τη σημαία hunter
        return self.hunter    
           
    @hunting.setter
    def hunting(self, value): #Μέθοδος για τροποποίηση της σημαίας hunter
         self.hunter = value
         
    def handle_keys(self,ghosts): #Μέθοδος για τον έλεγχο πλήκτρων
      if self.alive:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]: #Υπολογισμός κατεύθυνσης
            self.next_direction = pygame.Vector2(0, -1)
            return False
        elif keys[pygame.K_DOWN]:
            self.next_direction = pygame.Vector2(0, 1)
            return False
        elif keys[pygame.K_LEFT]:
            self.next_direction = pygame.Vector2(-1, 0)
            return False
        elif keys[pygame.K_RIGHT]:
            self.next_direction = pygame.Vector2(1, 0)
            return False         
        elif keys[pygame.K_SPACE]: #Εκτόξευση σφαίρας με SPACE και επιστροφή True   
            if self.ammunition>0: #Εφόσον υπάρχουν πυρομαχικά
                return True 
            
    def move(self, maze): #Κίνηση του αντικειμένου

        if self.alive: #Αν είναι ζωντανός
            new_x = self.x + self.next_direction.x * self.speed  #Υπολογισμός νέας θέσης (new_X,new_y)
            new_y = self.y + self.next_direction.y * self.speed
    
            if not self.check_collision(new_x, new_y, maze):
                self.direction = self.next_direction #Αλλαγή κατεύθυνσης αν δεν υπάρχει σύγκρουση με τοίχο
    
            new_x = self.x + self.direction.x * self.speed #Yπολόγισε τη νέα θέση σύμφωνα με την νέα κατεύθυνση και ταχύτητα
            new_y = self.y + self.direction.y * self.speed
    
            if not self.check_collision(new_x, new_y, maze): #Όταν δεν υπάρχει σύγκρουση με τοίχο τότε θέσε την νέα θέση που υπολόγισες πριν
                if new_x<=31 and new_x>=0 and self.direction==pygame.Vector2(-1,0): #Αν ο pacman βρίσκεται εντός θύρας μεταφοράς τότε μετακίνησέ τον στην άλλη πλευρά της πίστας
                    new_x=WIDTH-32                                                  #από αριστερή πλευρά σε δεξιά
                else:                    
                   if new_x<=WIDTH-32 and new_x>=WIDTH-36 and self.direction==pygame.Vector2(1,0): #από δεξιά σε αριστερή πλευρά
                       new_x=4
        
                self.x = new_x #Μετακίνηση τον pacman στη νέα θέση (new_X,new_y)
                self.y = new_y
            else:
                self.frame_counter = 0 #Όταν υπάρχει σύγκρουση να φαίνεται η πρώτη σκηνή του sprite

    def check_collision(self, new_x, new_y, maze): #Έλεγχος κίνησης του sprite       
        corners = [ #Δημιουργία πίνακα που περιέχει τις συντεταγμένες ενός tile
           (new_x, new_y),                              # Πάνω αριστερά
           (new_x + 31, new_y),                         # Πάνω δεξιά
           (new_x, new_y + 31),                         # Κάτω αριστερά
           (new_x + 31, new_y + 31)                     # Κάτω δεξιά
        ]

        for corner_x, corner_y in corners:
            pacman_tile_x = int(corner_x // self.tile_size) #Yπολογισμός της θέσης του αντικειμένου σε tiles με βάση τον πίνακα corners
            pacman_tile_y = int(corner_y // self.tile_size)

            if pacman_tile_x < 0 or pacman_tile_y < 0 or pacman_tile_y >= len(maze.maze_layout) or pacman_tile_x >= len(maze.maze_layout[0]):
                return True  #Όταν είναι εκτός ορίων του corners τότε θεωρούμε ότι υπάρχει σύγκρουση

            if maze.maze_layout[pacman_tile_y][pacman_tile_x] == 1 or maze.maze_layout[pacman_tile_y][pacman_tile_x] == 7 : #Σύγκρουση αν υπάρχει τοίχος στη θέση αυτή
                return True

        return False #Δεν υπάρχει σύγκρουση με τοίχο 
    
    def check_dot_collision(self, maze,screen, ghosts, chasing_time): #Έλεγχος αν υπάρχει σύγκρουση με κουκίδα 
            pacman_tile_x = self.x 
            pacman_tile_y = self.y 

            pacman_rect = pygame.Rect(pacman_tile_x, pacman_tile_y, self.tile_size, self.tile_size)  #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση του pacman
            for col in range(len(maze.dots)): #Σάρωση του πίνακα dots
                for row in range(len(maze.dots[col])):  
                    dot_x = col * self.tile_size
                    dot_y = row * self.tile_size
                    dot_rect = pygame.Rect(dot_x, dot_y, self.tile_size, self.tile_size) #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση της κουκίδας που σαρώθηκε

                    if pacman_rect.colliderect(dot_rect) and maze.dots[row][col] == 1 and self.ate_a_dot==False: #Αν υπάρχει σύγκρουση με απλή κουκίδα και η σημαία ate_a_dot είναι False
                      
                        self.ate_a_dot=True #θέσε τη σημαία σε True                 
                        points=10 #Οι πόντοι είναι 10 για την απλή κουκίδα
                        self.score= self.score+points  #Αύξησε το σκορ
                        threading.Thread(target=self.remove_dots, args=(maze, col, row, screen, False, chasing_time),daemon=True).start() #Κάνε thread για την αφαίρεση της κουκίδας (Χρησιμεύει για να μην αφαιρείται
                                                                                                               #η κουκίδα πολύ γρήγορα πριν φτάσει ο pacman πάνω της.)
                    
                    if pacman_rect.colliderect(dot_rect) and maze.dots[row][col] == 2 and self.ate_a_dot==False: #Αν υπάρχει σύγκρουση με power up κουκίδα και η σημαία ate_a_dot είναι False                                       
                        power_up_sound  = pygame.mixer.Sound("Assets/Sounds/power-up.mp3") #αρχείο κατανάλωσης power up κουκίδας
                        pygame.mixer.Channel(6).play(power_up_sound, loops=0) #Κάνε αναπαραγωγή του ήχου κατανάλωσης power up κουκίδας
                        pygame.mixer.Channel(0).pause() #Προσωρινή παύση της μουσικής παρασκηνίου
                        self.ate_a_dot=True #θέσε τη σημαία σε True
                        points=50 #Οι πόντοι είναι 50 για την power up κουκίδα
                        self.score= self.score+points #Αύξησε το σκορ
                        self.ghosts_eaten=0
                        threading.Thread(target=self.remove_dots, args=(maze, col, row, screen, True, chasing_time),daemon=True).start() #Κάνε thread για την αφαίρεση της κουκίδας (Χρησιμεύει για να μην αφαιρείται
                        self.hunter=True #O pacman τώρα είναι κυνηγός. Θέσε True τη σημαία                     #η κουκίδα πολύ γρήγορα πριν φτάσει ο pacman πάνω της)
                        self.hunting_start_time=time.time() #Καταχώρησε την τρέχουσα χρονική στιγμή που καταναλώθηκε η power up κουκίδα
                        for ghost in ghosts: #Άλλαξε το skin των φαντασμάτων σε θήραμα
                            ghost.change_skin(True, ghost.id)
                            ghost.hunter=False #Θέσε τα φαντάσματα ως θηράματα                          
                        
    def earthquake(self,screen, duration): #Δημιουργία του εφέ σεισμού
        update_rect = pygame.Rect(0, 0, WIDTH, HEIGHT-200)       
        for i in range(duration): #Για την αντίστοιχη τιμή duration κάνε ρτόσες φορές scroll την οθόνη κατά την αντίστοιχη διεύθυνση και μετά κάνε παύση για 5 χιλιοστά του δευτερολέπτου
            
            screen.scroll(3,0)
            time.sleep(0.005)
            pygame.display.update(update_rect)  #Ανανέωσε την οθόνη
             
            screen.scroll(-3,0)
            time.sleep(0.005)
            pygame.display.update(update_rect)
            
            screen.scroll(0,3)
            time.sleep(0.005)
            pygame.display.update(update_rect) 
             
            screen.scroll(0,-3)
            time.sleep(0.005)
            pygame.display.update(update_rect)
                                  
    def check_ghost_collision(self, ghost):  #Έλεγχος αν υπάρχει σύγκρουση με φάντασμα

        pacman_tile_x = self.x 
        pacman_tile_y = self.y 
        pacman_rect = pygame.Rect(pacman_tile_x, pacman_tile_y, self.tile_size, self.tile_size) #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση του pacman
        ghost_rect = pygame.Rect(ghost.x, ghost.y, self.tile_size, self.tile_size) #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση του φαντάσματος
        if pacman_rect.colliderect(ghost_rect) and ghost.alive==True and self.alive==True: #Αν υπάρχει σύγκρουση των πλακιδίων και το φάντασμα είναι ζωντανό και ο pacman είναι ζωντανός
            
            return True #Υπάρχει σύγκρουση
        else:
            return False #Δεν υπάρχει σύγκρουση
        
    def remove_dots(self,maze , row, col, screen, power, chasing_time): #Αφαίρεση κουκίδας
        time.sleep(0.1) #Παύση για 10 δέκατα του δευτερολέπτου
        maze.dots[col][row] = 0  #Αφαίρεσε την κουκίδα από τον πίνακα dots
        maze.total_dots=maze.total_dots-1
        dot_sound  = pygame.mixer.Sound("Assets/Sounds/dot.mp3") #Αρχείο ήχου κατανάλωσης απλής κουκίδας
        if not pygame.mixer.Channel(5).get_busy(): #Αν δεν αναπαράγεται ήδη ο ήχος

            pygame.mixer.Channel(5).play(dot_sound, loops=0) #Αναπαραγωγή του ήχου για την κατανάλωση απλής κουκίδας
            pygame.mixer.Channel(5).set_volume(0.4) #Χαμήλωμα της έντασης ώστε να μην είναι εκνευριστικός ο ήχος λόγω της επανάληψης
        self.ate_a_dot=False #Κατέβασε τη σημαία ate_a_dot
        if power: #Αν η κουκίδα είναι power up
            self.earthquake(screen,POWER_UP_EARTHQUAKE) #Κάνε το εφέ σεισμού για τόσες φορές όσες είναι η POWER_UP_EARTHQUAKE (προσωρινά απενεργοποιημένο)

            chasing_sound  = pygame.mixer.Sound("Assets/Sounds/chasing.mp3")  #Αρχείο ήχου κυνηγητού φαντασμάτων - δραματική μουσική 
            pygame.mixer.Channel(4).play(chasing_sound, loops=0) #Αναπαραγωγή του ήχου κυνηγητού των φαντασμάτων από τον pacman
            pygame.mixer.Channel(4).fadeout(chasing_time*1000) #Σταμάτησε τον ήχο μετά από αντίστοιχα δευτερόλεπτα σύμφωνα με το CHASING_TIME
   
                                   
    def update_animation(self): #Ανανέωση σκηνών λόγω κίνησης
        if self.alive:
            if  self.direction.length() > 0: #Ανανέωση σκηνής μόνο όταν υπάρχει κίνηση 
                self.frame_counter += 1
                if self.frame_counter >= self.animation_speed: #Ο μετρητής που δείχνει τη σκηνή παίρνει τιμές 0-3
                    self.frame_counter = 0
                    self.current_frame = (self.current_frame + 1) % len(self.frames) #Αποθήκευση της τρέχουσας σκηνής
       
                angle = self.get_rotation_angle() #Υπολογισμός κατεύθυνσης
                self.rotated_frames = [pygame.transform.rotate(frame, angle) for frame in self.frames] #Περιστροφή σκηνών και αποθήκευσή τους            

    def get_rotation_angle(self):
        if self.direction == pygame.Vector2(1, 0):
            return 0   #Δεξιά κατεύθυνση
        elif self.direction == pygame.Vector2(-1, 0):
            return 180 #Αριστερή κατεύθυνση
        elif self.direction == pygame.Vector2(0, -1):
            return 90  #Πάνω κατεύθυνση
        elif self.direction == pygame.Vector2(0, 1):
            return 270 #Κάτω κατεύθυνση
        return 0
    
    def death(self, screen, killer_ghost, ghosts,maze): #Θάνατος του pacman
        killer_ghost.x= killer_ghost.x - killer_ghost.direction.x * killer_ghost.speed #Yπολόγισε τη θέση του φαντάσματος που έφαγε τον pacman
        killer_ghost.y= killer_ghost.y - killer_ghost.direction.y * killer_ghost.speed
        self.alive = False #Θέσε τη σημαία alive σε False
        time.sleep(0.3)
        for channel in range(1,10):
            pygame.mixer.Channel(channel).fadeout(50) #Κάνε στοπ τους ήχους από όλα τα κανάλια πλην του παρασκηνίου
        pygame.mixer.Channel(0).pause() #Κάνε προσωρινη παύση της μουσικής παρασκηνίου
        lost_life_sound  = pygame.mixer.Sound("Assets/Sounds/lost_life.mp3") #Αρχείο μουσικής απώλειας ζωής
        pygame.mixer.Channel(4).play(lost_life_sound, loops=2) #Κάνε αναπαραγωγή του ήχου ότι ο pacman έχασε τη ζωή του
        pygame.mixer.Channel(4).set_volume(1)
        # pygame.mixer.Channel(4).fadeout(4000)
        threading.Timer(4.0, pygame.mixer.Channel(4).stop).start() #Φτιάξε άλλο thread και κάνε παύση τον ήχο μετά από 4 δευτερόπεπτα
        for i in range(1,4): #Περιστροφή του pacman για 3 φορές όλων των frames
                self.draw(screen)
        
                current_direction=self.get_rotation_angle() #Aνάλογα με την κατεύθυνση του pacman υπολόγισε αντίστοιχες διαστάσεις για το κουτί σβησίματος περιοχής
                if current_direction==0:  #Δεξιά κατεύθυνση
                     offset_x=2
                     offset_y=1
                     directions = [270, 180, 90, 0]
                elif current_direction==180: #Αριστερή κατεύθυνση
                     offset_x=2
                     offset_y=1
                     directions = [90, 0, 270, 180]
                elif current_direction==90: #Πάνω κατεύθυνση
                     offset_x=1
                     offset_y=2
                     directions = [0, 270, 180, 90]             
                elif current_direction==270: #Kάτω κατεύθυνση
                     offset_x=1
                     offset_y=2
                     directions = [180, 90, 0, 270]
                for angle in directions:
                 
                    tile_x = int(self.x // self.tile_size) 
                    tile_y = int(self.y // self.tile_size)
                                    
                    clear_rect = pygame.Rect(tile_x * self.tile_size, tile_y * self.tile_size, self.tile_size*offset_x, self.tile_size*offset_y) #Υπολογισμός κουτιού για το
                                                                                                            #σβήσιμο του pacman πριν τον σχεδιασμό των περιστραμένων frames
                    pygame.draw.rect(screen, BLACK, clear_rect) #Κάνε καθαρισμό με μαύρο χρώμα
                    pygame.display.update(clear_rect) #Ανανέωσε την οθόνη μόνο για τη συγκεκριμένη περιοχή
                    maze.draw(screen,self) #Σχεδίασε την πίστα ώστε αν έχει σβηστεί κάποιο κόμματι της να ξανασχεδιαστεί στην οθόνη
       
                    self.rotate(angle)
                    screen.blit(self.rotated_frames[1], (self.x, self.y)) #Σχεδίασε μόνο την περιστραμένη σκηνή
                    for ghost in ghosts:
                        ghost.draw(screen)
        
                    pygame.display.update(clear_rect)#Ανανέωσε την οθόνη μόνο για τη συγκεκριμένη περιοχή
                    time.sleep(0.3) #Κάνε παύση για 0.3 sec

    def draw(self, screen):  #Σχεδιασμός του αντικειμένου pacman στην οθόνη με βάση τις συντεταγμένες και τις περιστραμένες σκηνές
        if self.alive:
            self.update_animation()
            screen.blit(self.rotated_frames[self.current_frame], (self.x, self.y)) 
            if self.show_pacman_region:
                radius = self.tile_size * 4 #Μέγεθος ακτίνας περιοχής του pacman
                
                center_x = self.x + self.tile_size // 2 #Υπολογισμός συντεταγμένων σε πλακίδια 
                center_y = self.y + self.tile_size // 2
                
                pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius, 2) #απεικόνιση στην οθόνη του κύκλου περιοχής του pacman
           
    def rotate(self, angle):        
        self.rotated_frames = [pygame.transform.rotate(frame, angle) for frame in self.frames] #Περιστροφή σκηνών και αποθήκευσή τους  
