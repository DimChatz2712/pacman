import pygame #Imports των βιβλιοθηκών
import heapq
import random
import math
import time
from q_learning import QAgent
import numpy as np
from constants import WIDTH, HEIGHT

BLUE_GHOST   = (1,   254, 254) #Χρώματα για τα βέλη του μονοπατιού των φαντασμάτων
ORANGE_GHOST = (254, 182,  81)
PURPLE_GHOST = (254, 181, 254)
RED_GHOST    = (254,   0,   1)
GHOST_COLORS=[RED_GHOST,PURPLE_GHOST,BLUE_GHOST,ORANGE_GHOST] #Πίνακας στον οποίο αποθηκεύουμε τα παραπάνω χρώματα

ACTIONS = [(1,0), (-1,0), (0,1), (0,-1)]

def heuristic(a, b): #Συναρτήσεις του A* αλγόριθμου -  # Manhattan distance heuristic https://idm-lab.org/intro-to-ai/problems/solutions-Heuristic_Search.pdf
  
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(maze, pos):
    x, y = pos
    neighbors = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
            if maze[ny][nx] != 1:  # Η μοναδική τιμή 1 είναι τοίχος
                neighbors.append((nx, ny))
    return neighbors

def a_star(maze, start, goal, heur=heuristic): #A* αλγόριθμος https://en.wikipedia.org/wiki/A*_search_algorithm
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            break

        for neighbor in get_neighbors(maze, current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heur(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    if goal not in came_from:
        return None #Δεν βρέθηκε μονοπάτι

    path = [goal] #Ανακατασκεύασε το μονοπάτι από την αρχή μέχρι να επιτευχθεί ο στόχος
    cur = goal
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

class Ghost: #Δημιουργία του αντικειμένου Ghost

    def __init__(self, x, y, screen_width, screen_height, tile_size,speed, id_ghost):
        self.alive=True #Σημαία ότι το φάντασμα είναι ζωντανό
        self.frame_repeater=0 #Μετρητής που χρησιμεύει για την επανάληψη της σκηνής
        self.x = x #Οριζόντια συντεταγμένη σε pixels  #Ιδιότητες αντικειμένου
        self.y = y #Κάθετη  συντεταγμένη σε pixels
        self.initial_x=x #Αρχική θέση του sprite
        self.initial_y=y
        self.hunter=True #Σημαία που δείχνει αν το φάντασμα είναι κυνηγός
        self.state = "prison_move" #κατάσταση του φαντάσματος αρχικοποίηση εντός της φυλακής
        self.prison_timer = 0  # Μετρητής χρόνου στη φυλακή
        self.direction = pygame.Vector2(1, 0)  # ξεκινάει να κινείται δεξιά
        self.change_direction_timer = 0  # κάθε λίγο αλλάζει δεξιά/αριστερά
        self.show_arrow=False #σημαία για την εμφάνιση του μονοπατιού του φαντάσματος
        self.spawn_timer = 0 # μετράει πόσα frames έχει μείνει μέσα στη φυλακή πριν μπορέσει να ξεκινήσει τη διαδικασία εξόδου.
        self.exit_timer  = 0 # μόλις περάσει το spawn delay, ξεκινά να μετράει πόσα frames χρειάζεται ακόμα για να βγει από τη φυλακή.       
        self.spawn_delay = (id_ghost - 1) * 120  # 0s, 2s, 4s, 6s καθορισμός spawn delay (frames) αναλόγως του ghost.id
        self.exit_delay  = 180  # καθορισμός πόσες frames θέλει για έξοδο μετά το spawn ~3 δευτερόλεπτα
        self.speed = speed #Κίνηση sprite σε pixels
        self.direction = pygame.Vector2(1, 0)  #Aρχική κατεύθυνση οριζόντια δεξιά   
        self.next_direction = self.direction  #Επόμενη κατεύθυνση 
        self.screen_width = screen_width #Πλάτος παραθύρου σε pixels
        self.screen_height = screen_height #Υψος παραθύρου σε pixels
        self.id=id_ghost #Αναγνωριστικό id φαντάσματος
        self.tile_size = tile_size #Μέγεθος πλακιδίου        
        self.current_path = [] #αποθηκεύει τη λίστα των tile (x,y)
        self.path_color = (255, 0, 0) #χρώμα μονοπατιού αρχικοποίηση σε κόκκινο χρώμα
        max_offset = 10 #Καθορισμός μέγιστου offset
        self.max_off = max_offset
        num_states = (2*max_offset+1)**2 * 2  #dx×dy×power-flag 
        self.rl_agent = QAgent(num_states, num_actions=4)
        self.show_points = False #Σημαία για την απεικόνιση των πόντων όταν φαγωθεί κάποιο φάντασμα
        self.points_frame = None #Μετρητής που αντιστοιχεί στο frame των πόντων
        self.points_start_time = 0.0 #Αρχικοποίηση του μετρητή χρόνου απεικόνισης των πόντων
        self.points_duration = 2.0  #Χρόνος που δείχνονται οι πόντοι
        self.points_x=0 #H θέση απεικόνισης των πόντων (αλλιώς η θέση που είχε το φάντασμα όταν φαγώθηκε)
        self.points_y=0
         
        if id_ghost==1:  #Έλεγχος ποια εικόνα θα φορτωθεί ανάλογα το φάντασμα                
            self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_red.png").convert_alpha() #κόκκινο φάντασμα
        else:
            if id_ghost==2:
                self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_purple.png").convert_alpha() #μωβ φάντασμα
            else:
                if id_ghost==3:
                    self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_blue.png").convert_alpha() #μπλέ φάντασμα
                else:
                    if id_ghost==4:
                        self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_orange.png").convert_alpha() #πορτοκαλί φάντασμα
        
        self.frames = [  #Δημιουργία των σκηνών του φαντάσματος
            self.sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32)), 
            self.sprite_sheet.subsurface(pygame.Rect(32, 0, 32, 32)),  
            self.sprite_sheet.subsurface(pygame.Rect(64, 0, 32, 32)),  
            self.sprite_sheet.subsurface(pygame.Rect(96, 0, 32, 32)), 
            self.sprite_sheet.subsurface(pygame.Rect(128, 0, 32, 32)),  
            self.sprite_sheet.subsurface(pygame.Rect(160, 0, 32, 32)),   
            self.sprite_sheet.subsurface(pygame.Rect(192, 0, 32, 32)),  
            self.sprite_sheet.subsurface(pygame.Rect(224, 0, 32, 32))            
        ]
        
        self.current_frame = self.get_frame_rotation() #Υπολογισμός κατεύθυνσης   
        self.animation_speed = 3 #Ταχύτητα ανανέωσης της σκηνής
        self.frame_counter = self.get_frame_rotation() #Υπολογισμός τρέχουσας σκηνής        
        self.rotated_frames = self.frames.copy() #Αποθήκευση περιστραμένων σκηνών
        
    @property 
    def position(self): #Μέθοδος για την αποθήκευση της τρέχουσας θέσης του φαντάσματος
        return pygame.Vector2(self.x, self.y)
    
    @position.setter
    def position(self, value): #Μέθοδος για την τροποποίηση της τρέχουσας θέσης του φαντάσματος
        self.x = value.x
        self.y = value.y
    
    def get_rl_state(self, pacman): #Υπολόγισε το r1_state
        dx = int((pacman.x - self.x) // self.tile_size) #Yπολόγισε σε πλακίδια τη διαφορά θέσης φαντάσματος - pacman
        dy = int((pacman.y - self.y) // self.tile_size)
        
        dx = max(-self.max_off, min(self.max_off, dx)) #περιορισμός σε [-max_off, +max_off] 
        dy = max(-self.max_off, min(self.max_off, dy))
        power = 1 if pacman.hunter else 0 #Παράμετρος αν ο pacman είναι κυνηγός ή όχι        
        W = 2*self.max_off+1
        return ((dx + self.max_off) * W + (dy + self.max_off)) * 2 + power #Επιστροφή του r1_state 
    
    def collided_with_pacman(self, pacman): #Συνάρτηση για τον υπολογισμό αν υπάρχει σύγκρουση με τον pacman
        return pacman.check_ghost_collision(self)

    def update_astar_direction(self, pacman, maze):
        ghost_tile = (int(self.x // self.tile_size), int(self.y // self.tile_size)) #υπολογισμός της θέσης του φαντάσματος σε πλακίδια
        pacman_tile = (int(pacman.x // self.tile_size), int(pacman.y // self.tile_size)) #ομοίως υπολογισμός της θέσης του pacman
        prison_door_tile = (13, 9) #Οι συντεταγμένες της πόρτας της φυλακής (σπιτιού) των φαντασμάτων    
        if self.state == "prison_move": #Πρώτη κατάσταση των φαντασμάτων που πηγαίνουν πέρα δώθε
            if not pygame.mixer.Channel(7).get_busy():
                laughing_ghost_sound  = pygame.mixer.Sound("Assets/Sounds/laughing-ghost.mp3")
                pygame.mixer.Channel(7).play(laughing_ghost_sound, loops=0) #Αναπαραγωγή ήχου γέλιου όσο είναι σε αυτή την κατάσταση
                pygame.mixer.Channel(7).set_volume(0.6) #Χαμήλωμα της έντασης του καναλιού             
            self.spawn_timer += 1# Αύξηση spawn_timer                
            if self.spawn_timer < self.spawn_delay:# Αν δεν έχουμε φτάσει ακόμα στο spawn_delay                
                self.change_direction_timer += 1 #Εκτέλεση οριζόντιας κίνησης
                if self.change_direction_timer > 30:
                    self.direction.x *= -1
                    self.change_direction_timer = 0
                self.next_direction = self.direction
                return                
            self.exit_timer += 1#Όταν περάσει το spawn_delay, αρχίζουμε το exit_timer               
            if self.exit_timer < self.exit_delay: #Μέχρι να φτάσει ο χρόνος του exit_delay, συνεχίζεται η οριζόντια κίνηση
                self.change_direction_timer += 1
                if self.change_direction_timer > 30:
                    self.direction.x *= -1
                    self.change_direction_timer = 0
                self.next_direction = self.direction
                return                
            self.state = "prison_exit"#Μόλις περάσουν και τα δύο delays, πηγαίνουμε στην έξοδο
           
        elif self.state == "prison_exit": #Κατάσταση που τα φαντάσματα κινούνται προς την έξοδο
            path = a_star(maze.maze_layout, ghost_tile, prison_door_tile)
            if path and len(path) > 1:
                next_tile = path[1]
                dx = next_tile[0] - ghost_tile[0]
                dy = next_tile[1] - ghost_tile[1]
                self.next_direction = pygame.Vector2(dx, dy)            
            if self.y==prison_door_tile[1]*self.tile_size: #Μόλις το φάντασμα φτάσει στην έξοδο από την πόρτα
                self.state = "hunt" #Άλλαξε σε κατάσταση hunt
            else: #Αν δεν έχει φτάσει στην έξοδο τότε
                opening_door_sound  = pygame.mixer.Sound("Assets/Sounds/opening-door.mp3")
                if not pygame.mixer.Channel(8).get_busy(): #Αν δεν παίζει ήδη ο ήχος ανοίγματος πόρτας
                    pygame.mixer.Channel(8).play(opening_door_sound, loops=0) #Κάνε αναπαραγωγή του ήχου ανοίγματος πόρτας
                    pygame.mixer.Channel(8).set_volume(0.5)
                self.next_direction = pygame.Vector2(0, -1) #Ανοδική πορεία για την έξοδο
                self.x = (int(self.x // self.tile_size)*self.tile_size) #Τοποθέτηση πάνω στο grid όταν αρχίζει η ανοδική κίνηση για να βγει από τη φυλακή                                                                       #Διορθώνουμε την x συντεταγμένη για να αποφύγουμε το collision με τον τοίχο λόγω offset από το speed (4 px)                            
        
    def move(self, pacman, maze):        
        if self.state!="hunt": #Aν το φάντασμα δεν έχει βγει από τη φυλακή
            self.update_astar_direction(pacman, maze)       
            new_x = self.x + self.next_direction.x * self.speed
            new_y = self.y + self.next_direction.y * self.speed        
            if not self.check_collision(new_x, new_y, maze):
                self.direction = self.next_direction       
            new_x = self.x + self.direction.x * self.speed
            new_y = self.y + self.direction.y * self.speed            
            self.update_astar_direction(pacman, maze) #Υπολόγισε βέλτιστο μονοπάτι αν δεν υπάρχουν collisions  με τοίχο
            if not self.check_collision(new_x, new_y, maze):                              
                    self.x = new_x
                    self.y = new_y
            else:
                self.update_astar_direction(pacman, maze) #Υπολόγισε βέλτιστο μονοπάτι αν δεν υπάρχουν collisions  με τοίχο
        else: #Το φάντασμα έχει βγει από τη φυλακή                
                mod_x = self.x % self.tile_size #Ελέχουμε αν υπάρχει μετατόπιση του sprite σε σχέση με το tile grid
                mod_y = self.y % self.tile_size        
                if mod_x < self.speed and mod_y < self.speed: #Aν το sprite δεν βρίσκεται πάνω στο tile grid                    
                    
                    tile_x = int(self.x // self.tile_size) #Υπολόγισε τις σωστές συντεταγμένες (σε πλακίδια) για να είναι στο grid
                    tile_y = int(self.y // self.tile_size)
                    self.x = tile_x * self.tile_size #Τοποθέτησε το sprite στη θέση αυτή (πάνω στο grid)
                    self.y = tile_y * self.tile_size
            
                    s = self.get_rl_state(pacman) #Αποθήκευσε το παλιό state
            
                    pacman_tile = (int(pacman.x // self.tile_size), int(pacman.y // self.tile_size)) #Υπολογισμός της θέσης του pacman σε πλακίδια
                    ghost_tile = (int(self.x // self.tile_size), int(self.y // self.tile_size)) #υπολογισμός της θέσης του φαντάσματος σε πλακίδια
                    if self.id == 1: #Ανάλογα με ποιο φάντασμα είναι, υπολόγισε την αντίστοιχη θέση που στοχεύει να πάει το φάντασμα
                        if abs(ghost_tile[0]-int(pacman.x//self.tile_size))<=4 and abs(ghost_tile[1]-int(pacman.y//self.tile_size))<=4:
                            target=pacman_tile                    
                        else:                                                   
                            target = (int(pacman.x // self.tile_size)+6*pacman.direction.x, int(pacman.y // self.tile_size))               
                    elif self.id == 2:
                        if abs(ghost_tile[0]-int(pacman.x//self.tile_size))<=4 and abs(ghost_tile[1]-int(pacman.y//self.tile_size))<=4:
                            target=pacman_tile
                        else:                                
                            target = (int(pacman.x // self.tile_size), int(pacman.y // self.tile_size)-6*pacman.direction.y)                          
                    elif self.id == 3:
                        if abs(ghost_tile[0]-int(pacman.x//self.tile_size))<=4 and abs(ghost_tile[1]-int(pacman.y//self.tile_size))<=4:
                            target=pacman_tile
                        else:             
                            target = (int(pacman.x // self.tile_size)-6*pacman.direction.x, int(pacman.y // self.tile_size))
                    elif self.id == 4:
                        if abs(ghost_tile[0]-int(pacman.x//self.tile_size))<=4 and abs(ghost_tile[1]-int(pacman.y//self.tile_size))<=4:
                            target=pacman_tile
                        else:             
                            target = (int(pacman.x // self.tile_size), int(pacman.y // self.tile_size)+6*pacman.direction.y)
                    path = a_star(maze.maze_layout, (tile_x, tile_y), target) #Υπολόγισε το βέλτιστο μονοπάτι με Α*
            
                    if path and len(path) > 1: 
                        dx_astar = path[1][0] - tile_x
                        dy_astar = path[1][1] - tile_y
                        self.current_path=path #Καταχώρησε το βέλτιστο μονοπάτι στο current_path (Για απεικόνιση με το πλήκτρο Α)
                        try:
                            astar_idx = ACTIONS.index((dx_astar, dy_astar)) #Υπολόγισε το astar_idx
                        except ValueError:
                            astar_idx = None
                    else:
                        astar_idx = None
                                
                    q_vals = self.rl_agent.Q[s] #Υπολόγισε τα Q-values και πρόσθεσε bonus στο A* action
                    q_bias = q_vals.copy()
                    if astar_idx is not None:
                        q_bias[astar_idx] += 1  # Ρύθμιση του q_bias (πόσο αξιόπιστος είναι ο A*)
                                         
                    a = int(np.argmax(q_bias)) #Επιλογή του τελικού action
                    self.next_direction = pygame.Vector2(*ACTIONS[a]) #Αλλαγή κατεύθυνσης με βάση το action
            
                    self._last_state = s #Αποθήκευση του τελευταίου state και του action που υπολογίστηκε
                    self._last_action = a            
                
                nx = self.x + self.next_direction.x * self.speed #Υπολογισμός νέας θέσης
                ny = self.y + self.next_direction.y * self.speed
                if not self.check_collision(nx, ny, maze): #Αλλαγή κατεύθυνση αν δεν υπάρχει σύγκρουση με τοίχο
                    self.direction = self.next_direction            
                    
                    if hasattr(self, '_last_state'): #RL learning update
                        
                        s2 = self.get_rl_state(pacman) #Μικρό αρνητικό bonus για κάθε βήμα                        
                        r = -1  
                        self.rl_agent.learn(self._last_state, self._last_action, r, s2) #Πρόσθεση του bonus
                        del self._last_state, self._last_action #Διαγραφή των τελευταίων action και state
            
                new_x = self.x + self.direction.x * self.speed #Yπολογισμός ξανά της νέας θέσης
                new_y = self.y + self.direction.y * self.speed            
                
                if new_x <= 0 and self.direction == pygame.Vector2(-1, 0): #Αν το φάντασμα βρίσκεται σε θύρα teleport
                    new_x = self.screen_width - self.tile_size #Κάνε ανάλογα μεταφορά αν βρίσκεται αριστερά
                elif new_x >= self.screen_width - self.tile_size and self.direction == pygame.Vector2(1, 0): #ή δεξιά
                    new_x = 0
            
                if not self.check_collision(new_x, new_y, maze): #Αν δεν υπάρχει σύγκρουση με τοίχο βάλε το sprite στην νέα θέση
                    self.x = new_x
                    self.y = new_y   
    
    def check_collision(self, new_x, new_y, maze): #Έλεγχος κίνησης του sprite
        corners = [ #Δημιουργία πίνακα που περιέχει τις συντεταγμένες ενός tile
            (new_x, new_y),                              # Πάνω αριστερά
            (new_x + 31, new_y),                         # Πάνω δεξιά
            (new_x, new_y + 31),                         # Κάτω αριστερά
            (new_x + 31, new_y + 31)                     # Κάτω δεξιά
        ]

        for corner_x, corner_y in corners:
            ghost_tile_x = int(corner_x // self.tile_size)  #Yπολογισμός της θέσης του αντικειμένου σε tiles με βάση τον πίνακα corners
            ghost_tile_y = int(corner_y // self.tile_size)

            if ghost_tile_x < 0 or ghost_tile_y < 0 or ghost_tile_y >= len(maze.maze_layout) or ghost_tile_x >= len(maze.maze_layout[0]):
                return True  #Όταν είναι εκτός ορίων του corners τότε θεωρούμε ότι υπάρχει σύγκρουση

            if maze.maze_layout[ghost_tile_y][ghost_tile_x] == 1: #Σύγκρουση αν υπάρχει τοίχος
                return True
        return False   #Δεν υπάρχει σύγκρουση
    
    def update_animation(self): #Ανανέωση σκηνών λόγω κίνησης
        angle = self.get_frame_rotation() #Υπολογισμός της σκηνής του sprite που αντιστοιχεί στην συγκεκριμένη κατεύθυνση      
        
        if self.direction.length() > 0: #Ανανέωση σκηνής μόνο όταν υπάρχει κίνηση
            self.frame_repeater+=1 #Αύξησε το μετρητή frame_repeater κατά 1
            if self.frame_counter == angle: #Αν ο μετρητής τρέχουσας σκηνής είναι ίσος με τη σκηνή που αντιστοιχεί στη συγκεκριμένη κατεύθυνση
                if self.frame_repeater==12: #Αν ο μετρητής frame_repeater είναι ίσος με 12
                    self.frame_counter +=1 #Προχώρησε στην επόμενη σκηνή
                    self.frame_repeater=0 #Μηδένισε τον frame_repeater   
            else: #Αν ο μετρητής τρέχουσας σκηνής δεν είναι ίσος με τη σκηνή που αντιστοιχεί στη συγκεκριμένη κατεύθυνση
                if self.frame_repeater==12: #Αν ο μετρητής frame_repeater είναι ίσος με 12
                    self.frame_counter=angle #Θέσε τον μετρητή τρέχουσας σκηνής σύμφωνα με τη σκηνή που αντιστοιχεί στη συγκεκριμένη κατεύθυνση
                    self.frame_repeater=0 #Μηδένισε τον frame_repeater
            self.current_frame = self.frame_counter #Απόδοση τρέχουσας σκηνής με βάση τον μετρητή            
            
    def get_frame_rotation(self): #Υπολογισμός της σκηνής του sprite που αντιστοιχεί στην συγκεκριμένη κατεύθυνση 
        if self.direction == pygame.Vector2(1, 0):
            return 0    #Δεξιά κατεύθυνση
        elif self.direction == pygame.Vector2(-1, 0):
            return 2  #Αριστερή κατεύθυνση
        elif self.direction == pygame.Vector2(0, -1):
            return 4   #Πάνω κατεύθυνση
        elif self.direction == pygame.Vector2(0, 1):
            return 6  #Κάτω κατεύθυνση
        return 0
            
    def change_skin(self, value, id_ghost): #Αλλαγή skin του φαντάσματος με το συγκεκριμένο id_ghost
        if value is False: #Αν η value είναι False 
            if id_ghost==1: #Ελεγχος για ποιο φάντασμα πρόκειται     
                self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_red.png") #Άλλαξε και βάλε το skin κυνηγού για το κόκκινο φάντασμα
            else:
                if id_ghost==2:
                    self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_purple.png") #Άλλαξε και βάλε το skin κυνηγού για το μωβ φάντασμα
                else:
                    if id_ghost==3:
                       self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_blue.png") #Άλλαξε και βάλε το skin κυνηγού για το μπλε φάντασμα
                    else:
                        if id_ghost==4:
                            self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_orange.png") #Άλλαξε και βάλε το skin κυνηγού για το πορτοκαλί φάντασμα
        else: #Αν η value είναι True
            self.sprite_sheet = pygame.image.load("Assets/Sprites/ghost_chased.png") #Άλλαξε και βάλε το skin θηράματος            
            
        self.frames = [ #Δημιουργία των σκηνών του φαντάσματος
        self.sprite_sheet.subsurface(pygame.Rect(0, 0, 32, 32)), 
        self.sprite_sheet.subsurface(pygame.Rect(32, 0, 32, 32)), 
        self.sprite_sheet.subsurface(pygame.Rect(64, 0, 32, 32)),   
        self.sprite_sheet.subsurface(pygame.Rect(96, 0, 32, 32)),  
        self.sprite_sheet.subsurface(pygame.Rect(128, 0, 32, 32)),  
        self.sprite_sheet.subsurface(pygame.Rect(160, 0, 32, 32)),  
        self.sprite_sheet.subsurface(pygame.Rect(192, 0, 32, 32)), 
        self.sprite_sheet.subsurface(pygame.Rect(224, 0, 32, 32))           
    ]
        self.rotated_frames = self.frames.copy() #Αποθήκευσε τις περιστραμένες σκηνές
        
    def trigger_show_points(self, ghost_points_frames, ghosts_eaten): #Aπεικόνιση των πόντων όταν τρώγεται ένα φάντασμα
        
        self.show_points= True #Θέσε τη σημαία σε True για να εμφανιστούν οι πόντοι
        self.points_frame= ghost_points_frames[ghosts_eaten-1] #Απεικόνιση του κατάλληλου frame που αντιστοιχούν στους πόντους
        self.points_start_time = time.time() #Καταγραφή του χρόνου που φαγώθηκε το φάντασμα
        self.points_x=self.x #Aποθήκευσε τη θέση που είχε το φάντασμα όταν φαγώθηκε
        self.points_y=self.y

    def draw(self, screen): #Σχεδίασε το φάντασμα στην οθόνη

        self.update_animation()
        screen.blit(self.rotated_frames[self.current_frame], (self.x, self.y))          
              
    def revive(self, ghost): #Ζωντάνεψε το φάντασμα στην αρχική του θέση
        ghost.alive=True #Θέσε τη σημαία alive σε True
        ghost.x=ghost.initial_x #Αρχικοποίηση των ιδιοτήτων του αντικειμένου ξανά
        ghost.y=ghost.initial_y
        ghost.current_path=[] 
        ghost.state="prison_move"
        ghost.prison_timer = 0  # Μετρητής χρόνου στη φυλακή
        ghost.direction = pygame.Vector2(1, 0)  # ξεκινάει να κινείται δεξιά
        ghost.change_direction_timer = 0  # κάθε λίγο αλλάζει δεξιά/αριστερά
        ghost.spawn_timer = 0 # μετράει πόσα frames έχει μείνει μέσα στη φυλακή πριν μπορέσει να ξεκινήσει τη διαδικασία εξόδου.
        ghost.exit_timer  = 0 # μόλις περάσει το spawn delay, ξεκινά να μετράει πόσα frames χρειάζεται ακόμα για να βγει από τη φυλακή.
                  
    def draw_path(self, surface): #Σχεδίασε το μονοπάτι του φαντάσματος
        if self.show_arrow:
            if not self.current_path or len(self.current_path) < 2:
                return
            self.path_color=GHOST_COLORS[self.id-1] #Χρησιμοποιήσε αντίστοιχο χρώμα ανάλογα με το ghost.id
            for (tx1, ty1), (tx2, ty2) in zip(self.current_path, self.current_path[1:]): #Εμφάνιση γραμμής μονοπατιού
                x1 = tx1 * self.tile_size + self.tile_size // 2
                y1 = ty1 * self.tile_size + self.tile_size // 2
                x2 = tx2 * self.tile_size + self.tile_size // 2
                y2 = ty2 * self.tile_size + self.tile_size // 2
                pygame.draw.line(surface, self.path_color, (x1+self.id*2, y1+self.id*2), (x2+self.id*2, y2+self.id*2), 2) #Εμφάνισε τη γραμμή του path
                
                dx, dy = x2 - x1, y2 - y1 #Κατασκευή κεφαλής βέλους
                length = max((dx*dx + dy*dy)**0.5, 1)
                ux, uy = dx/length, dy/length
                for angle in (135, -135): #Υπολογίζουμε από γωνία +135 έως -135 μοίρες
                    rad = math.radians(angle) #Μετατροπή σε ακτίνια από μοίρες
                    rx = ux*math.cos(rad) - uy*math.sin(rad)
                    ry = ux*math.sin(rad) + uy*math.cos(rad)
                    ex = x2 + rx * 8
                    ey = y2 + ry * 8                    
                    pygame.draw.line(surface, self.path_color, (x2+self.id*2, y2+self.id*2), (ex+self.id*2, ey+self.id*2), 2) #Εμφάνισε την κεφαλή του βέλους 
            
                