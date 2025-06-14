import pygame
WIDTH, HEIGHT = 896, 1050 #Διαστάσεις παραθύρου

WHITE = (255, 255, 255) #Τιμές χρωμάτων
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE=(0,0,200)
LIGHT_BLUE=(0,150,140)
PACMAN_LIVES=3 #Ζωές του pacman
POWER_UP_EARTHQUAKE=10 #Φορές που θα γίνεται το εφέ του σεισμού στην κατανάλωση power up κουκίδας
GHOSTS_DUNGEON_POSITION=[12,12] #Θέση των φαντασμάτων μέσα στη φυλακή
PACMAN_INITIAL_POSITION=[14,20] #Αρχική θέση του pacman
WALL_COLORS=[LIGHT_BLUE,WHITE,YELLOW, RED, GREEN,BLUE,LIGHT_BLUE,YELLOW,RED] #Χρώματα που επιλέγονται αντίστοιχα για το κάθε level
TILE_SIZE=32
CHASING_TIME=9 #Αριθμός που χρησιμοποιείται για να υπολογίζεται το χρονικό διάστημα που ο pacman είναι κυνηγός (ο χρόνος μειώνεται ανάλογα όσο αυξάνει το level)

MENU_HEIGHT=200
MENU_WIDTH=WIDTH//3

# maze_layout=[#Ο πίνακας που αντιστοιχεί στην πίστα μας, 0 διάδρομος ελεύθερος, 1 τοίχος, 9 ελεύθερος μη προσπελάσιμος χώρος, 8 κενός χώρος που δεν έχει ούτε 
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  #κουκίδες #7 πόρτα σπιτιού φσαντασμάτων #6 teleport ((level1.npy))
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 2, 1, 9, 9, 1, 0, 0, 0, 0, 1, 9, 9, 9, 9, 9, 9, 1, 0, 0, 0, 0, 1, 9, 9, 1, 2, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 8, 8, 8 ,8, 8, 8, 8, 8, 8, 8, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 8, 1, 1, 7, 7, 7, 7, 1, 1, 8, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 8, 1, 9, 9, 9, 9, 9, 9, 1, 8, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1, 9, 9, 9, 9, 9, 9, 1, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 2, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 2, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# ]

# maze_layout=[#Ο πίνακας που αντιστοιχεί στην πίστα μας, 0 διάδρομος ελεύθερος, 1 τοίχος, 9 ελεύθερος μη προσπελάσιμος χώρος, 8 κενός χώρος που δεν έχει ούτε 
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  #κουκίδες #7 πόρτα σπιτιού φσαντασμάτων (level2.npy)
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 2, 1, 9, 9, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 9, 9, 1, 2, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 8, 8, 8 ,8, 8, 8, 8, 8, 8, 8, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 8, 1, 1, 7, 7, 7, 7, 1, 1, 8, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 8, 1, 9, 9, 9, 9, 9, 9, 1, 8, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [6, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1, 9, 9, 9, 9, 9, 9, 1, 8, 0, 0, 0, 0, 0, 0, 0, 0, 6],
#     [1, 0, 1, 1, 1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 1, 1, 1, 8, 1, 1, 1, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 2, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 2, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# ]

tile_size = 32  # Μέγεθος του πλακιδίου
dot_image = pygame.image.load("Assets/Sprites/dot.png") #Φόρτωση της εικόνας της κουκίδας
power_dot_image = pygame.image.load("Assets/Sprites/power_dot.png") #Φόρτωση της εικόνας της power up κουκίδας
ready_message_image=pygame.image.load("Assets/Sprites/ready.png") #Φόρτωση της εικόνας για το μήνυμα "Ready!"
sprite_sheet_bullets = pygame.image.load("Assets/Sprites/amunition.png") #Φόρτωση της εικόνας της σφαίρας που θα δείχνει πόσες σφαίρες έχουν απομείνει

sprite_sheet_bullets_frames = [#Δημιουργία σκηνής για τη σφαίρα
     sprite_sheet_bullets.subsurface(pygame.Rect(0, 0, 32, 32))
 ]

sprite_sheet_levels = pygame.image.load("Assets/Sprites/levels.png")#φόρτωση του spritesheet για τα εικονίδια των πιστών
level_frames = [ 
    sprite_sheet_levels.subsurface(pygame.Rect(0, 0, 32, 32)),  #sprite πρώτης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(32, 0, 32, 32)), #sprite δεύτερης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(64, 0, 32, 32)), #sprite τρίτης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(96, 0, 32, 32)), #sprite τέταρτης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(128, 0, 32, 32)),#sprite πέμπτης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(160, 0, 32, 32)),#sprite έκτης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(192, 0, 32, 32)),#sprite έβδομης πίστας
    sprite_sheet_levels.subsurface(pygame.Rect(224, 0, 32, 32)) #sprite όγδοης πίστας
]

sprite_sheet_ghost_points = pygame.image.load("Assets/Sprites/ghost_points.png") #φόρτωση των εικονιδίων για τους αριθμούς με τους πόντους 
ghost_points_frames = [                                                          #κάθε φορά που καταναλώνεται ένα φάντασμα από τον pacman
    sprite_sheet_ghost_points.subsurface(pygame.Rect(0, 0, 32, 32)),  #Αριθμός 200
    sprite_sheet_ghost_points.subsurface(pygame.Rect(32, 0, 32, 32)), #Αριθμός 400
    sprite_sheet_ghost_points.subsurface(pygame.Rect(64, 0, 32, 32)), #Αριθμός 800
    sprite_sheet_ghost_points.subsurface(pygame.Rect(96, 0, 32, 32))  #Αριθμός 1600  
]