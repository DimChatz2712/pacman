import pygame

from constants import WIDTH, HEIGHT, WHITE, BLACK, RED, LIGHT_BLUE , BLUE, YELLOW, GREEN, WALL_COLORS     
  
class Maze: #Δημιουργία του αντικειμένου Maze
    
    def __init__(self, maze_layout, tile_size, dots): #Δημιουργία του κονστράκτορα του αντικειμένου
        self.maze_layout = maze_layout
        self.tile_size = tile_size
        self.dots = dots
        self.width = len(maze_layout[0])  #Στήλες από τον πίνακα maze_layout
        self.height = len(maze_layout)  #ΓραμμέςΣ από τον πίνακα maze_layout
        self.total_dots=0 #Μεταβλητή που αντιστοιχεί στον συνολικό αριθμό κουκίδων της πίστας

        for y in range(len(self.maze_layout)): 
            for x in range(len(self.maze_layout[y])):  
                if self.maze_layout[y][x] == 0: #αν υπάρχει στη θέση x, y απλή κουκίδα
                    self.dots[y][x] = 1
                    self.total_dots+=1 #Αποθήκευση κάθε κουκίδας στην total_dots
                if self.maze_layout[y][x] == 2:#αν υπάρχει στη θέση x, y power up κουκίδα
                    self.dots[y][x] = 2  
                    self.total_dots+=1 #Αποθήκευση και της power up κουκίδας στην total_dots
        
    def draw(self, screen, pacman): #Σχεδιασμός της πίστας με βάση την κωδικοποίηση του maze_layout   
       for row in range(self.height): #Σάρωση με βάση τις συντεταγμένες πλακιδίων και όχι pixels
           for col in range(self.width):              
                  
                if self.maze_layout[row][col] == 1:
                    pygame.draw.rect(screen, WALL_COLORS[pacman.level-1], pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μπλέ χρώμα του τοίχου
                elif self.maze_layout[row][col] == 9:
                    pygame.draw.rect(screen, BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μπλέ χρώμα των περιοχων που δεν είναι προσβάσιμες
                elif self.maze_layout[row][col] == 7:
                    pygame.draw.rect(screen, GREEN, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός της πόρτας του σπιτιού των φαντασμάτων 
                elif self.maze_layout[row][col] == 6:
                    pygame.draw.rect(screen, BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός της πόρτας του σπιτιού των φαντασμάτων                
                else:
                    pygame.draw.rect(screen,BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μαύρο χρώμα του διαδρόμου
        
    def draw_maze_and_dots(self,screen,dot_image,power_dot_image,pacman):
        self.draw(screen,pacman)
        for row in range(len(self.dots)):  #Σχεδίασε τις κουκίδες στην οθόνη σύμφωνα με τον πίνακα dots
            for col in range(len(self.dots[row])):
                if self.dots[row][col] == 1:  #Υπάρχει απλή κουκίδα
                    screen.blit(dot_image, (col * self.tile_size , row * self.tile_size )) #Σχεδίασε την κουκίδα
                if self.dots[row][col] == 2:  #Υπάρχει power up κουκίδα
                    screen.blit(power_dot_image, (col * self.tile_size , row * self.tile_size  )) #Σχεδίασε την power up κουκίδα
   
    def update_maze(self): #Ανανέωση της dots σύμφωνα με την υπάρχουσα maze_layout
        for y in range(len(self.maze_layout)): 
            for x in range(len(self.maze_layout[y])):  
                if self.maze_layout[y][x] == 0: #αν υπάρχει στη θέση x, y απλή κουκίδα
                    self.dots[y][x] = 1
                    self.total_dots+=1 #Αποθήκευση κάθε κουκίδας στην total_dots
                if self.maze_layout[y][x] == 2:#αν υπάρχει στη θέση x, y power up κουκίδα
                    self.dots[y][x] = 2  
                    self.total_dots+=1 #Αποθήκευση και της power up κουκίδας στην total_dots
                    
    def invert_draw(self, screen): #Σχεδιασμός της πίστας με βάση την κωδικοποίηση του maze_layout   
       for row in range(self.height): #Σάρωση με βάση τις συντεταγμένες πλακιδίων και όχι pixels
           for col in range(self.width):              
                  
                if self.maze_layout[row][col] == 1:
                    pygame.draw.rect(screen, RED, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μπλέ χρώμα του τοίχου
                elif self.maze_layout[row][col] == 9:
                    pygame.draw.rect(screen, BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μπλέ χρώμα των περιοχων που δεν είναι προσβάσιμες
                elif self.maze_layout[row][col] == 7:
                    pygame.draw.rect(screen, GREEN, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός της πόρτας του σπιτιού των φαντασμάτων 
                elif self.maze_layout[row][col] == 6:
                    pygame.draw.rect(screen, BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός της πόρτας του σπιτιού των φαντασμάτων                
                else:
                    pygame.draw.rect(screen,BLACK, pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size))  #Σχεδιασμός με μαύρο χρώμα του διαδρόμου
                    
    def invert_draw_maze_and_dots(self,screen,dot_image,power_dot_image):

        for row in range(len(self.dots)):  #Σχεδίασε τις κουκίδες στην οθόνη σύμφωνα με τον πίνακα dots
            for col in range(len(self.dots[row])):
                if self.dots[row][col] == 1:  #Υπάρχει απλή κουκίδα
                    screen.blit(dot_image, (col * self.tile_size , row * self.tile_size )) #Σχεδίασε την κουκίδα
                if self.dots[row][col] == 2:  #Υπάρχει power up κουκίδα
                    screen.blit(power_dot_image, (col * self.tile_size , row * self.tile_size  )) #Σχεδίασε την power up κουκίδα
                    
    def recount_total_dots(self):
        self.total_dots=0
        for y in range(len(self.maze_layout)): 
            for x in range(len(self.maze_layout[y])):  
                if self.dots[y][x] == 1: #αν υπάρχει στη θέση x, y απλή κουκίδα
                    
                    self.total_dots+=1 #Αποθήκευση κάθε κουκίδας στην total_dots
                if self.dots[y][x] == 2 :#αν υπάρχει στη θέση x, y power up κουκίδα
                     
                    self.total_dots+=1 #Αποθήκευση και της power up κουκίδας στην total_dots
        
       