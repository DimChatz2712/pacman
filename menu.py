import pygame
import time
from constants import *
import matplotlib.pyplot as plt #Φόρτωση των απαραίτητων βιβλιοθηκών
import pandas as pd
import os, json
import seaborn as sns 
import io
import sys

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man by PyGame-Over") #Τίτλος του παραθύρου
title_font = pygame.font.Font(None, 60) #Ορισμός διαφορετικών fonts
menu_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 24)
small_two_font = pygame.font.Font(None, 35)

def fig_to_surface(fig): #Μετατροπή του Matplotlib Figure σε PyGame Surface
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img = pygame.image.load(buf, 'heatmap').convert()
    return img

def load_stats(stats, level): #Φόρτωση των στατιστικών για την τρέχουσα πίστα level από το αντίστοιχο .json αρχείο
    fn = stats_filename_for_level(level)
    if not os.path.exists(fn):
        return
    with open(fn, "r") as f:
        data = json.load(f)
    stats.visit_count = data["visit_count"]
    stats.transition_counts.clear()
    for key, inner in data["transition_counts"].items():
        x, y = map(int, key.split(","))
        for ik, cnt in inner.items():
            nx, ny = map(int, ik.split(","))
            stats.transition_counts[(x,y)][(nx,ny)] = cnt
    stats.playing_times = data.get("playing_times", [])
    stats.survival_times = data.get("survival_times", [])
            
def stats_filename_for_level(level): #Δημιουργία του filename του json για το αντίστοιχο level
    return f"Statistics/stats_level{level}.json"

def save_stats(stats, level): #Αποθήκευση των στατιστικών για την τρέχουσα πίστα level από το αντίστοιχο .json αρχείο
    fn = stats_filename_for_level(level)
    data = {
        "visit_count": stats.visit_count,
        "transition_counts": {
            f"{x},{y}": {f"{nx},{ny}": cnt
                         for (nx,ny), cnt in inner.items()}
            for (x,y), inner in stats.transition_counts.items()
        },
        "playing_times": stats.playing_times,
        "survival_times": stats.survival_times
    }   
    with open(fn, "w") as f:
        json.dump(data, f)

def draw_text_centered(text, y, font, color=WHITE): #Εμφάνιση του κειμένου στη μέση της οθόνης στο ύψος y με χρώμα color
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    screen.blit(rendered, rect) 

def show_menu(maze,stats,pacman1, pacman2): #Εμφάνιση του κυρίως μενού
    pygame.event.clear()
    menu_active = True #Θέσε τη σημαία menu_active σε Τrue
    blink = True #Σημαία για το τρεμόπαιγμα του μηνύματος
    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα του μηνύματος
    blink_interval = 500 #Χρονικό διάστημα σε ms
    menu_music  = pygame.mixer.Sound("Assets/Sounds/background.mp3") #Αρχείο μουσικής παρασκηνίου
    pygame.mixer.Channel(0).play(menu_music, loops=-1) #Συνεχόμενη αναπαραγωγή της μουσικής παρασκηνίου
    pygame.mixer.Channel(0).set_volume(1) #Μέγιστη ένταση της μουσικής για το κανάλι 0 της μουσικής παρασκηνίου
    while menu_active: #Όσο η σημαία menu_active είναι True εμφάνισε το μενού
        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα

        draw_text_centered("PAC-MAN", 100, title_font, YELLOW) #Εμφάνισε τις επιλογές του μενού στις κατάλληλες θέσεις
        draw_text_centered("by PyGame-Over Team", 150, small_font, YELLOW)
        draw_text_centered("1 - Single Player", 250, menu_font, WHITE)
        draw_text_centered("2 - Two Players", 300, menu_font, WHITE)
        draw_text_centered("K - Controls", 350, menu_font, WHITE)
        draw_text_centered("H - High Scores", 400, menu_font, WHITE)
        draw_text_centered("C - Cheats", 450, menu_font, WHITE)
        draw_text_centered("S - Heatmaps", 500, menu_font, WHITE)
        draw_text_centered("T - Time statistics", 550, menu_font, WHITE)

        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα του μηνύματος "Press Q to Quit" ανά 500ms
        if current_time - blink_timer > blink_interval:
            blink = not blink
            blink_timer = current_time
        if blink:
            draw_text_centered("Press Q to Quit", HEIGHT - 50, small_font, YELLOW) #Εμφάνισε το μήνυμα 

        pygame.display.flip() #Ανανέωσε την οθόνη

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: #Έξοδος του παιχνιδιού (Κλείσιμο του παραθύρου)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: #Αν πατηθεί το πλήκτρο 1
                    menu_active = False  #Θέσε τη σημαία σε False
                    screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
                    pygame.display.flip() #Ανανέωσε την οθόνη
                    pacman1.player_name = prompt_player_name(screen, menu_font, 1) #Ζήτησε από τον παίκτη 1 να δώσει το όνομά του
                    stats.number_of_players=1
                    pygame.event.clear()
                    pygame.mixer.Channel(0).fadeout(2200) #Κάνε fade τη μουσική παρασκηνίου σε 2,2 sec
                    time.sleep(2) #Κάνε παύση 2 sec
                elif event.key == pygame.K_2: #Αν πατηθεί το πλήκτρο 1
                    menu_active = False  #Θέσε τη σημαία σε False
                    screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
                    pygame.display.flip() #Ανανέωσε την οθόνη
                    pacman1.player_name = prompt_player_name(screen, menu_font, 1) #Ζήτησε από τους παίκτες 1 και 2 να δώσουν το όνομά τους
                    screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
                    pygame.display.flip() #Ανανέωσε την οθόνη
                    pacman2.player_name = prompt_player_name(screen, menu_font, 2)
                    stats.number_of_players=2
                    pygame.event.clear()
                    pygame.mixer.Channel(0).fadeout(2200) #Κάνε fade τη μουσική παρασκηνίου σε 2,2 sec
                    time.sleep(2) #Κάνε παύση 2 sec
                elif event.key == pygame.K_k: #Αν πατηθεί το πλήκτρο k
                    show_controls() #Εμφάνισε τα cοntrols
                elif event.key == pygame.K_h: #Αν πατηθεί το πλήκτρο h
                    show_high_scores(stats) #Εμφάνισε τα high scores    
                elif event.key == pygame.K_c: #Αν πατηθεί το πλήκτρο c
                    show_cheats() #Εμφάνισε τα cheats                    
                elif event.key == pygame.K_s: #Αν πατηθεί το πλήκτρο s
                    show_heatmaps(maze,stats) #Εμφάνισε τα στατιστικά heatmaps
                elif event.key == pygame.K_t: #Αν πατηθεί το πλήκτρο t
                    show_time_statistics(stats) #Εμφάνισε τα στατιστικά χρόνου                                    
                elif event.key == pygame.K_q: #Αν πατηθεί το πλήκτρο q
                    pygame.quit() #Έξοδος από το παιχνίδι
                    sys.exit()

def prompt_player_name(screen, font, player_num):  #Συνάρτηση στην οποία ο παίκτης δίνει το όνομά του
    name = "" #Αρχικοποίηση ονόματος
    clock = pygame.time.Clock()

    prompt_text = f"Enter name for Player {player_num}:" #Μηνύμα προτροπής προς τον παίκτη να εισάγει το όνομά του
    prompt_surf = font.render(prompt_text, True, YELLOW)
    prompt_rect = prompt_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)) #Υπολογισμός ορθογωνίου μηνύματος προτροπής
    screen.blit(prompt_surf, prompt_rect)#Εμφάνιση μηνύματος
    pygame.display.update(prompt_rect) #Ανανέωση της οθόνης μόνο στο ορθογώνιο μηνύματος για να αποφύγουμε το flashing 
                                        #κατά την ανανέωση
   
    name_rect = pygame.Rect(0, 0, 400, font.get_height() + 10) #Υπολογισμός ορθογωνίου πεδίου εισαγωγής του ονόματος
    name_rect.center = (WIDTH//2, HEIGHT//2) #Κεντράρισμα στο μέσον της οθόνης

    while True:
        
        screen.fill(BLACK, name_rect) #Καθάρισμα μόνο του ορθογωνίου πεδίου εισαγωγής του ονόματος

        name_surf = font.render(name, True, WHITE)
        name_surf_rect = name_surf.get_rect(center=name_rect.center)
        screen.blit(name_surf, name_surf_rect) #Εμφάνιση του ορθογωνίου πεδίου εισαγωγής του ονόματος

        pygame.display.update(name_rect) #Ανανέωση της οθόνης μόνο στο ορθογώνιο πεδίου εισαγωγής για να αποφύγουμε το flashing 
                                            #κατά την ανανέωση
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #'Εξοδος αν ο χρήστης κλείσει το παράθυρο
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                key_sound  = pygame.mixer.Sound("Assets/Sounds/dot.mp3") #Αρχείο ήχου για να πάτημα πλήκτρου
                if not pygame.mixer.Channel(5).get_busy(): #Αν δεν αναπαράγεται ήδη ο ήχος

                    pygame.mixer.Channel(5).play(key_sound, loops=0)
                if event.key == pygame.K_RETURN: #Αν πατηθεί το πλήκτρο ENTER επέστρεψε το όνομα
                    screen.fill(BLACK, name_rect)
                    name_surf = font.render("ACCEPTED", True, RED) #Εμφάνιση του μηνύματος ACCEPTED! με κόκκινο χρώμα
                    name_surf_rect = name_surf.get_rect(center=name_rect.center)
                    screen.blit(name_surf, name_surf_rect) #Εμφάνιση του ορθογωνίου πεδίου εισαγωγής του ονόματος
                    pygame.display.update(name_rect) #Ανανέωση της οθόνης μόνο στο ορθογώνιο πεδίου εισαγωγής 
                    time.sleep(1)
                                
                    return name or f"Player{player_num}" #Αν το name είναι κενό τότε δίνεται το όνομα PLayer1 ή Player2

                elif event.key == pygame.K_BACKSPACE: #Αν πατηθεί το BACKSPACE τότε μείωσε κατά 1 χαρακτήρα το string ονόματος
                    name = name[:-1]

                else:
                    
                    if len(name) < 10 and len(event.unicode) == 1 and event.unicode.isprintable(): #Αποφεύγουμε controls χαρακτήρες
                        name += event.unicode                               #και καθορίζουμε μέχρι 10 χαρακτήρες μήκος του ονόματος

        clock.tick(30)

def show_heatmaps(maze,stats): #Εμφάνισε τα στατιστικά του παιχνιδιού 
    current_level=1 #Θέσε τον μετρητή πίστας αρχικά στο 1
    blink = True #Σημαία για το τρεμόπαιγμα
    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα
    blink_interval = 500 #Χρονικό διάστημα σε ms

    rows = len(maze.maze_layout) #Υπολογισμός αριθμού γραμμών και στηλών
    cols = len(maze.maze_layout[0])
   
    load_stats(stats, current_level) #Φόρτωση των στατιστικών για την πίστα current_level
    
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
    df_trans = pd.DataFrame.from_records(records)  #φτιάχνουμε το dataFrame df_trans μέσω της panda.DateFrame()
    top_tiles = (
    df_visits
      .stack()                      #σειριακής μορφής: index=(y,x), value=visits
      .reset_index(name='visits')   #dataframe με στήλες ['level_0','level_1','visits']
      .rename(columns={'level_0':'y','level_1':'x'})
      .nlargest(10, 'visits')
)
          
    fig, ax = plt.subplots(figsize=(6,6), dpi=100) #Δημιουργία του figure σε Matplotlib

    new_vmax = 10000 #Oρισμός μέγιστου αριθμού επισκέψεων για το heatmap
    sns.heatmap(
    df_visits,
    cmap='Reds', #Επιλογή κόκκινου χρώματος
    vmin=0, #Ελάχιστη τιμή
    vmax=new_vmax, #Μέγιστη τιμή
    cbar_kws={'ticks':[0, new_vmax//2, new_vmax]} #Καθορισμός εύρους ύψους διαστημάτων διαγράμματος
)
    ax.axis('on') #Εμφάνιση αξόνων
    ax.set_title("Pac-Man Visit Heatmap of level "+str(current_level)) #Τίτλος του heatmap
    
    heat_surf = fig_to_surface(fig) #Μετατροπή του lib Figure σε PyGame Surface
    plt.close(fig)

    stats_active = True #Θέσε τη σημαία stats_active σε True

    while stats_active: #Όσο η σημαία stats_active είναι Τrue 
        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
        draw_text_centered("Heatmaps", 50, title_font, YELLOW) #Εμφάνισε τoν τίτλο του μενού των στατιστικών
        screen.blit(heat_surf, ((WIDTH - heat_surf.get_width())//2, 110)) #Εμφάνισε το γράφημα Heatmap

        y0 = 140 + heat_surf.get_height() + 20 
        draw_text_centered("Top 5 tiles:", y0, menu_font, YELLOW) #Εμφάνισε τα 5 κορυφαία σε επισκέψεις πλακίδια
        for i, row in enumerate(top_tiles.head(5).itertuples(), start=1):
            text = f"{i}. ({row.x},{row.y}) -> {row.visits}"
            draw_text_centered(text, y0+10+ + i*30, small_font, YELLOW) #Εμφάνιση του καθενός στο αντίστοιχο ύψος
                
        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα των μηνυμάτων
        if current_time - blink_timer > blink_interval:
            blink = not blink
            blink_timer = current_time
        if blink:
            draw_text_centered("Press 1–9 to switch level, B to go back", HEIGHT - 50, small_font, YELLOW)

        current_level_new=handle_keys_show_statistics() #Έλεγχος αν πατήθηκε κάποιο πλήκτρο για την επιλογή πίστας
        if current_level_new!=current_level and current_level_new is not None: #Αν έχει επιλεχθεί κάποιο πλήκτρο και είναι διαφορετικό από την current_level
            current_level=current_level_new
            load_stats(stats, current_level) #Φόρτωση στατιστικών για την πίστα current_level
                                             #Δημιουργούμε παρακάτω ξανά τα στατιστικά τώρα όμως για την νέα επιλεγμένη πίστα
            num_rows = len(stats.visit_count) #Υπολογισμός μέγιστου αριθμού γραμμών και στηλών
            num_cols = len(stats.visit_count[0])
            df_visits = pd.DataFrame(stats.visit_count, #φτιάχνουμε το dataFrame df_visits μέσω της panda.DateFrame()
                                     index=range(num_rows), #κάθε γραμμή=y, στήλη=x
                                     columns=range(num_cols)) # H stats.visit_count είναι λίστα λιστών: rows × cols
            records = [] #Μεταβάσεις tile→tile
            for (x,y), inner in stats.transition_counts.items():
                for (nx,ny), cnt in inner.items():
                    records.append({
                        'from_x': x, 'from_y': y,
                        'to_x': nx, 'to_y': ny,
                        'count': cnt
                    })
            df_trans = pd.DataFrame.from_records(records) #φτιάχνουμε το dataFrame df_trans μέσω της panda.DateFrame()
            top_tiles = (
            df_visits
              .stack()                      #σειριακής μορφής: index=(y,x), value=visits
              .reset_index(name='visits')   #dataframe με στήλες ['level_0','level_1','visits']
              .rename(columns={'level_0':'y','level_1':'x'})
              .nlargest(10, 'visits')
        )
                  
            fig, ax = plt.subplots(figsize=(6,6), dpi=100) #Δημιουργία του figure σε Matplotlib 
            new_vmax = 10000 #Oρισμός μέγιστου αριθμού επισκέψεων για το heatmap
            sns.heatmap(
            df_visits,
            cmap='Reds', #Επιλογή κόκκινου χρώματος
            vmin=0, #Ελάχιστη τιμή
            vmax=new_vmax, #Μέγιστη τιμή
            cbar_kws={'ticks':[0, new_vmax//2, new_vmax]} #Καθορισμός εύρους ύψους διαστημάτων διαγράμματος
        )
            ax.axis('on') #Εμφάνιση αξόνων
            ax.set_title("Pac-Man Visit Heatmap of level "+str(current_level)) #Τίτλος του heatmap           
            heat_surf = fig_to_surface(fig) #Μετατροπή του Matplotlib Figure σε PyGame Surface
            plt.close(fig)

        pygame.display.flip() #Ανανέωσε την οθόνη

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Έξοδος του παιχνιδιού (Κλείσιμο του παραθύρου)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b: #Αν πατηθεί το πλήκτρο b
                    stats_active = False #Θέσε τη σημαία σε False ώστε να γίνει έξοδος από το μενού στατιστικών

def show_time_statistics(stats):
    current_level=1
    blink=True
    blink_timer=pygame.time.get_ticks()
    blink_interval=500

    stats_active=True
    while stats_active:
        
        load_stats(stats, current_level)
        playing=stats.playing_times or []
        surviving=getattr(stats, 'survival_times', []) or []


        df=pd.DataFrame({
            'time': playing + surviving,
            'type': ['playing'] * len(playing) + ['survival'] * len(surviving)
        })
        means=df.groupby('type')['time'].mean()
        total_playing=sum(playing)


        fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
        x_p = list(range(1, len(playing) + 1))
        x_s = list(range(1, len(surviving) + 1))
        if playing:
            ax.plot(x_p, playing, marker='o', label='Playing time')
        if surviving:
            ax.plot(x_s, surviving, marker='o', label='Survival time')
        ax.set_xlabel("Attempt")
        ax.set_ylabel("Time (sec)")
        ax.set_title(f"Level {current_level} Times")
        ax.legend()
        fig.tight_layout()


        surf = fig_to_surface(fig)
        plt.close(fig)

        screen.fill(BLACK)
        draw_text_centered("Time Statistics", 50, title_font, YELLOW)
        screen.blit(surf, ((WIDTH - surf.get_width()) // 2, 100))


        y0 = 140 + surf.get_height() + 20
        draw_text_centered(f"Mean playing time: {means.get('playing', 0):.2f} sec",
                           y0, small_font, (31, 119, 180))
        draw_text_centered(f"Mean survival time: {means.get('survival', 0):.2f} sec",
                           y0 + 30, small_font, (255, 127, 14))
        draw_text_centered(f"Total playing time: {total_playing:.2f} sec",
                           y0 + 60, small_font, YELLOW)


        if pygame.time.get_ticks() - blink_timer > blink_interval:
            blink = not blink
            blink_timer = pygame.time.get_ticks()
        if blink:
            draw_text_centered("Press 1–9 to switch level, B to go back", HEIGHT - 50, small_font, YELLOW)
            

        pygame.display.flip()

 
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_b:
                    stats_active = False
                    break
                if pygame.K_1 <= e.key <= pygame.K_9:
                    current_level = e.key - pygame.K_0
                    break
                    
def show_cheats(): #Eμφάνισε το μενού των cheats
    blink = True #Σημαία για το τρεμόπαιγμα
    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα
    blink_interval = 500 #Χρονικό διάστημα σε ms
    cheats_active = True #Θέσε τη σημαία cheats_active σε True

    while cheats_active: #Όσο η σημαία cheats_active είναι Τrue 
        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
        draw_text_centered("Game Cheats", 100, title_font, YELLOW) #Εμφάνισε τoν τίτλο του μενού των cheats        
        draw_text_centered("N - Next level", 250, menu_font, WHITE)
        draw_text_centered("A - Show path of each ghost", 300, menu_font, WHITE)
        draw_text_centered("R - Show region of pac man", 350, menu_font, WHITE)
        draw_text_centered("L - Infinite lives", 400, menu_font, WHITE)
        draw_text_centered("F - Infinite ammunition", 450, menu_font, WHITE)
        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα των μηνυμάτων
        if current_time - blink_timer > blink_interval:
            blink = not blink
            blink_timer = current_time
        if blink:
            draw_text_centered("Press B to go back", HEIGHT - 50, small_font, YELLOW)
        pygame.display.flip() #Ανανέωσε την οθόνη

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Έξοδος του παιχνιδιού (Κλείσιμο του παραθύρου)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b: #Αν πατηθεί το πλήκτρο b
                    cheats_active = False #Θέσε τη σημαία σε False ώστε να γίνει έξοδος από το μενού cheats

def show_controls(): #Eμφάνισε το μενού των controls
    blink = True #Σημαία για το τρεμόπαιγμα
    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα
    blink_interval = 500 #Χρονικό διάστημα σε ms
    controls_active = True #Θέσε τη σημαία cheats_active σε True

    while controls_active: #Όσο η σημαία controls_active είναι Τrue 
        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
        draw_text_centered("Game Controls", 100, title_font, YELLOW) #Εμφάνισε τoν τίτλο του μενού των controls        
        draw_text_centered("Arrows - Move Pacman", 250, menu_font, WHITE)
        draw_text_centered("SPACE - Shoot bullet", 300, menu_font, WHITE)
        draw_text_centered("P - Pause game", 350, menu_font, WHITE)
        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα των μηνυμάτων
        if current_time - blink_timer > blink_interval:
            blink = not blink
            blink_timer = current_time
        if blink:
            draw_text_centered("Press B to go back", HEIGHT - 50, small_font, YELLOW)
        pygame.display.flip() #Ανανέωσε την οθόνη

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Έξοδος του παιχνιδιού (Κλείσιμο του παραθύρου)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b: #Αν πατηθεί το πλήκτρο b
                    controls_active = False #Θέσε τη σημαία σε False ώστε να γίνει έξοδος από το μενού controls
                    
def show_high_scores(stats): #Eμφάνισε το μενού των high scores
    blink = True #Σημαία για το τρεμόπαιγμα
    blink_timer = pygame.time.get_ticks() #Μετρητής χρόνου για το τρεμόπαιγμα
    blink_interval = 500 #Χρονικό διάστημα σε ms
    high_scores_active = True #Θέσε τη σημαία high_scores_active σε True

    while high_scores_active: #Όσο η σημαία controls_active είναι Τrue 
        screen.fill(BLACK) #Καθάρισε την οθόνη με μαύρο χρώμα
        draw_text_centered("Game Top 10 Players", 100, title_font, YELLOW) #Εμφάνισε τoν τίτλο του μενού των high scores

        top10 = sorted(stats.high_scores, key=lambda entry: entry[1], reverse=True)[:10]
        y = 200
        for name, score in top10:
            text_name=f"{name}"
            text_score=f"{score}"            
            y += 50
            draw_text(text_name, (WIDTH//2)-150,y, menu_font, WHITE) #Εμφάνισε τα ονόματα των παικτών       
            draw_text(text_score, (WIDTH//2)+50,y, menu_font, RED) #Εμφάνισε τα high scores 
        current_time = pygame.time.get_ticks() #Τρεμόπαιγμα των μηνυμάτων
        if current_time - blink_timer > blink_interval:
            blink = not blink
            blink_timer = current_time
        if blink:
            draw_text_centered("Press B to go back", HEIGHT - 50, small_font, YELLOW)
        pygame.display.flip() #Ανανέωσε την οθόνη

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Έξοδος του παιχνιδιού (Κλείσιμο του παραθύρου)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b: #Αν πατηθεί το πλήκτρο b
                    high_scores_active = False #Θέσε τη σημαία σε False ώστε να γίνει έξοδος από το μενού των high scores
                    
def draw_text(text, x, y, font, color=WHITE): #Εμφάνισε το κείμενο text στην οθόνη στη θέση x,y
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))
    
def handle_keys_show_statistics(): #Μέθοδος για τον έλεγχο πλήκτρων στο μενού για την επιλογή πίστας προς εμφάνιση των στατιστικών της
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: #Aν πατηθεί το πλήκτρο 1   
            return 1 #Επέστρεψε το 1 (πίστα 1)
        elif keys[pygame.K_2]:#Ομοίως για το πλήκτρο 2
            return 2 #Επέστρεψε το 2 (πίστα 2)
        if keys[pygame.K_3]: #Aν πατηθεί το πλήκτρο 3   
            return 3 #Επέστρεψε το 1 (πίστα 3)
        elif keys[pygame.K_4]:#Ομοίως για το πλήκτρο 4
            return 4 #Επέστρεψε το 2 (πίστα 4)
        if keys[pygame.K_5]: #Aν πατηθεί το πλήκτρο 5   
            return 5 #Επέστρεψε το 1 (πίστα 5)
        elif keys[pygame.K_6]:#Ομοίως για το πλήκτρο 6
            return 6 #Επέστρεψε το 2 (πίστα 6)
        if keys[pygame.K_7]: #Aν πατηθεί το πλήκτρο 7   
            return 7 #Επέστρεψε το 1 (πίστα 7)
        elif keys[pygame.K_8]:#Ομοίως για το πλήκτρο 8
            return 8 #Επέστρεψε το 2 (πίστα 8)
        
       