import rumps
import pync
from playsound3 import playsound

class PomodoroApp(object):
    def __init__(self):
        self.config = {
            "app_name":       "Pomodoro",
            "start":          "Start",
            "pause":          "Pause",
            "continue":       "Continue",
            "break":          "Break",
            "stop":           "Stop",
            "Mute/Un-Mute":   "Mute/Un-Mute",
            "break_message":  "Break time",
            "interval": 1500,               # 25 minutes
            "interval_break": 300,          # 5 minutes
            "interval_long_break": 900,     # 15 minutes
            "interval_count": 0,
            "is_muted": False               # Mute state flag
        }
        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)
        self.interval = self.config["interval"]
        self.interval_break = self.config["interval_break"]
        self.interval_long_break = self.config["interval_long_break"]
        self.set_up_menu()
        
        self.start_pause_button = rumps.MenuItem(title=self.config["start"], callback=self.start_timer)
        self.break_pause_button = rumps.MenuItem(title=self.config["break"], callback=self.break_timer)
        self.mute_button = rumps.MenuItem(title=self.config["Mute/Un-Mute"], callback=self.toggle_mute)
        self.stop_button = rumps.MenuItem(title=self.config["stop"], callback=None)
        
        self.app.menu = [self.start_pause_button, self.break_pause_button, self.mute_button, self.stop_button]
    
    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = ("♠︎♣︎♥︎♦︎ - " + str(self.config["interval_count"])) 
        
    def toggle_mute(self, sender):
        self.config["is_muted"] = not self.config["is_muted"]
        sender.title = "Un-Mute" if self.config["is_muted"] else "Mute"
    
    def on_tick(self, sender):
        time_left = sender.end - sender.count
        mins = time_left // 60 if time_left >= 0 else time_left // 60 + 1
        secs = time_left % 60 if time_left >= 0 else (-1 * time_left) % 60
        
        if mins == 0 and time_left < 0:
            # Only increment if the completed timer was a work interval
            if sender.end == self.interval: 
                self.config["interval_count"] += 1 
                pync.notify('Time for a Break!', title='Pomodoro Timer')
            else:
                pync.notify('Back to the keys', title='Pomodoro Timer')
            # Handle audio safely and respect mute toggle
            if not self.config["is_muted"]:
                try:
                    playsound('smash_spike.wav')
                except Exception:
                    pass # Fail silently if audio is missing
            
            # going back to menu
            self.stop_timer(sender)
            self.stop_button.set_callback(None)   
        else:
            self.stop_button.set_callback(self.stop_timer)
            # Modern string formatting
            self.app.title = f'{mins:2d}:{secs:02d}'
        sender.count += 1

    ## working timer
    def start_timer(self, sender):
        self.break_pause_button.set_callback(None)
        if sender.title.lower().startswith(("start", "continue")):
            if sender.title == self.config["start"]:
                self.timer.count = 0
                self.timer.end = self.interval 
            sender.title = self.config["pause"]
            self.timer.start()
        else:
            sender.title = self.config["continue"]
            self.timer.stop()
        
    ## break period
    def break_timer(self, sender):
        self.start_pause_button.set_callback(None)
        if sender.title.lower().startswith(("break", "continue")):
            if sender.title == self.config["break"]:
                self.timer.count = 0
                
                # --- LONG BREAK LOGIC ---
                completed_sessions = self.config["interval_count"]
                
                # If we've completed a multiple of 4 sessions, take a long break
                if completed_sessions > 0 and completed_sessions % 4 == 0:
                    self.timer.end = self.interval_long_break
                    pync.notify('Time for a long break!', title='Pomodoro Timer')
                else:
                    self.timer.end = self.interval_break
                # ------------------------
                    
            sender.title = self.config["pause"]
            self.timer.start()
        else:
            sender.title = self.config["continue"]
            self.timer.stop()

    def stop_timer(self, sender):
        self.set_up_menu()
        self.stop_button.set_callback(None)
        self.start_pause_button.title = self.config["start"]
        self.start_pause_button.set_callback(self.start_timer)
        self.break_pause_button.title = self.config["break"]
        self.break_pause_button.set_callback(self.break_timer)

    def run(self):
        self.app.run()

## running the show
if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
