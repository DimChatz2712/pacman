import pygame
from constants import WIDTH

class Bullet: #Δημιουργία του αντικειμένου Bullet
    def __init__(self, x, y, screen_width, screen_height, maze_layout, tile_size, direction):
        self.x = x #Οριζόντια συντεταγμένη σε pixels  #Ιδιότητες αντικειμένου
        self.y = y #Κάθετη  συντεταγμένη σε pixels
        self.speed = 20 #Κίνηση sprite σε pixels
        self.direction = direction  #Τρέχουσα κατεύθυνση
        self.next_direction = self.direction  #Επόμενη κατεύθυνση
        self.screen_width = screen_width #Πλάτος παραθύρου σε pixels
        self.screen_height = screen_height #Υψος παραθύρου σε pixels
        self.maze_layout=maze_layout
        self.tile_size = tile_size #Μέγεθος πλακιδίου 
        sprite_sheet = pygame.image.load("Assets/Sprites/bullet.png") #Φόρτωση εικόνας σφαίρας
        self.frames = [ #Σκηνή σφαίρας
            sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32))
        ]       
        self.current_frame = 0 #Τρέχουσα σκηνή
        self.animation_speed = 3 #Ταχύτητα ανανέωσης της σκηνής
        self.frame_counter = 0 #Μετρητής σκηνής
        self.explosion_frames = [] #Πίνακας σκηνών έκρηξης
        self.is_exploding = False #Σημαία ότι η σφαίρα εκρήγνυται
        self.explode_timer = 0 #Μετρητής χρόνου έκρηξης
        self.rotated_frames = self.frames.copy() #Αποθήκευση περιστραμένων σκηνών
        self.destroyed = False #Σημαία ότι η σφαίρα καταστράφηκε

    @property #Μέθοδος για την αποθήκευση της τρέχουσας θέσης της σφαίρας
    def position(self):
        return pygame.Vector2(self.x, self.y)

    @position.setter  #Μέθοδος για την τροποποίηση της τρέχουσας θέσης της σφαίρας
    def position(self, value):
        self.x = value.x
        self.y = value.y
        
    @property
    def destroyed(self): #Μέθοδος για την αποθήκευση της σημαίας destroyed       
        return self.destroyed
    
    @destroyed.setter #Μέθοδος για την τροποποίηση της σημαίας destroyed       
    def destroyed(self, value):
        self.destoyed = value

    def move(self, screen): #Κίνηση του αντικειμένου 
        if self.is_exploding:
            return  #Σταμάτησε την κίνηση αν η σφαίρα εκρήγνυται

        new_x = self.x + self.next_direction.x * self.speed #Υπολογισμός νέας θέσης της σφαίρας
        new_y = self.y + self.next_direction.y * self.speed
       
        if not self.check_collision(new_x, new_y, screen): #Αν δεν υπάρχει σύγκρουση συνέχισε την κίνηση
            self.x = new_x
            self.y = new_y

    def check_collision(self, new_x, new_y, screen): #Έλεγχος σύγκρουσης της σφαίρας
        corners = [ #Δημιουργία πίνακα που περιέχει τις συντεταγμένες ενός tile
            (new_x, new_y),         #Πάνω αριστερά                             
            (new_x + 31, new_y),    #Πάνω δεξιά                        
            (new_x, new_y + 31),    #Κάτω αριστερά                        
            (new_x + 31, new_y + 31) #Κάτω δεξιά                    
        ]
        outbound=False
        
        for corner_x, corner_y in corners:
            tile_x = int(corner_x // self.tile_size) #Yπολογισμός της θέσης του αντικειμένου σε tiles με βάση τον πίνακα corners
            tile_y = int(corner_y // self.tile_size)

            if tile_x < 0 or tile_y < 0 or tile_y >= len(self.maze_layout) or tile_x >= len(self.maze_layout[0]):
                return True   #Όταν είναι εκτός ορίων του corners τότε θεωρούμε ότι υπάρχει σύγκρουση
            if new_x<=self.tile_size-self.speed or new_x>=WIDTH-self.tile_size+self.speed:                
                outbound=True
            
            if self.maze_layout[tile_y][tile_x] == 1 or (new_x<=20 or new_x>=872):
             
                if not self.is_exploding: #Αν υπάρχει σύγκρουση με τοίχο φόρτωσε τις σκηνές έκρηξης
                    sprite_sheet = pygame.image.load("Assets/Sprites/bullet2.png")
                    self.explosion_frames = [ #Δημιουργία των σκηνών έκρηξης
                        sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32)),
                        sprite_sheet.subsurface(pygame.Rect(32, 0, 32, 32))
                    ]
                    self.is_exploding = True #Θέσε τη σημαία σε True ότι η σφαίρα εκρήγνυται 

                    if corner_y % 32==0:  #Έλεγξε αν η σκηνή έκρηξης είναι τοποθετημένη καθ ύψος στο πλέγμα των πλακιδίων (tile grid)
                        if self.direction == pygame.Vector2(1, 0):
                            tile_x-=1 #κατεύθυνση δεξιά, μείωσε συντεταγμένη x
                        else:
                            tile_x+=1 #κατεύθυνση αριστερή, αύξησε συντεταγμένη x
                    if corner_x % 32==0:  #Έλεγξε αν η σκηνή έκρηξης είναι τοποθετημένη κατά μήκος στο πλέγμα των πλακιδίων (tile grid)
                        if self.direction == pygame.Vector2(0, 1):                        
                            tile_y-=1 #κατεύθυνση κάτω, μείωσε συντεταγμένη y 
                        else:
                            tile_y+=1 #κατεύθυνση πάνω, αύξησε συντεταγμένη y
                    self.x=tile_x*32 #Υπολόγισε τη θέση 
                    self.y=tile_y*32                                                 
                    self.explode_timer = pygame.time.get_ticks()  #Ξεκίνησε τον μετρητή χρόνου για την έκρηξη
                    explosion_sound  = pygame.mixer.Sound("Assets/Sounds/explosion.mp3")
                    pygame.mixer.Channel(2).play(explosion_sound, loops=0)
                return True #Υπάρχει σύγκρουση σφαίρας με τοίχο
        return False #Δεν υπάρχει σύγκρουση σφαίρας με τοίχο
    
    def check_ghost_collision(self, ghost): #Έλεγχος αν υπάρχει σύγκρουση με φάντασμα
        bullet_tile_x = self.x #Παρούσα θέση της σφαίρας
        bullet_tile_y = self.y 
        bullet_rect = pygame.Rect(bullet_tile_x, bullet_tile_y, self.tile_size, self.tile_size) #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση της σφαίρας
        ghost_rect = pygame.Rect(ghost.x, ghost.y, self.tile_size, self.tile_size) #Υπολόγισε το πλακίδιο σύμφωνα με τη θέση του φαντάσματος
        if bullet_rect.colliderect(ghost_rect) and ghost.alive==True: #Αν υπάρχει σύγκρουση των πλακιδίων και το φάντασμα είναι ζωντανό
            if not self.is_exploding: #Αν υπάρχει σύγκρουση με φάντασμα φόρτωσε τις σκηνές έκρηξης
                sprite_sheet = pygame.image.load("Assets/Sprites/bullet2.png")
                self.explosion_frames = [ #Δημιουργία των σκηνών έκρηξης
                    sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32)),
                    sprite_sheet.subsurface(pygame.Rect(32, 0, 32, 32))
                ]
                self.is_exploding = True #Θέσε τη σημαία σε True ότι η σφαίρα εκρήγνυται  
                self.explode_timer = pygame.time.get_ticks()  #Ξεκίνησε τον μετρητή χρόνου για την έκρηξη            
            return True #Υπάρχει σύγκρουση        
        else:
            return False #Δεν υπάρχει σύγκρουση
        
    def get_rotation_angle(self): #Υπολογισμός της κατεύθυνσης της σφαίρας
        if self.direction == pygame.Vector2(1, 0):
            return 0    
        elif self.direction == pygame.Vector2(-1, 0):
            return 180  
        elif self.direction == pygame.Vector2(0, -1):
            return 90   
        elif self.direction == pygame.Vector2(0, 1):
            return 270  
        return 0

    def draw(self, screen): #Σχεδιασμός της σφαίρας στην οθόνη
        if self.is_exploding: #Η σφαίρα εκρήγνυται
            
            elapsed_time = pygame.time.get_ticks() - self.explode_timer #Υπολογισμός της χρονικής διαφοράς που συμβαίνει η έκρηξη
            frame_index = (elapsed_time // 500) % 2  # Άλλαξε σκηνή κάθε μισό δευτερόλεπτο

            if elapsed_time >= 1000:  #Μετά από 1 δευτερόλεπτο απεικόνισης της έκρηξης θέσε τη σημαία destroyed σε True. Η σφαίρα δεν υπάρχει πια.
                self.destroyed = True
            else: #Αν δεν έχει περάσει 1 δευτερόλεπτο τότε σχεδίασε τη τρέχουσα σκηνή της σφαίρας
                screen.blit(self.explosion_frames[frame_index], (self.x, self.y))
        else: #Αν η σφαίρα δεν εκρήγνυται τότε
            angle = self.get_rotation_angle() #Υπολόγισε την κατεύθυνση
            self.rotated_frames = [pygame.transform.rotate(frame, angle) for frame in self.frames] #Αποθήκευσε την περιστραμένη σκηνή στον πίνακα rotated_frames
            screen.blit(self.rotated_frames[0], (self.x, self.y)) #Σχεδίασε τη σφαίρα 
