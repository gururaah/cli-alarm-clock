import datetime
import time
import threading
import sys

class AlarmClock:
    def __init__(self):
        self.alarms = []
        self.running = True
        self.lock = threading.Lock()
        self.is_ringing = False

    def add_alarm(self, alarm_time_str, label="Alarm"):
        try:
            alarm_time = datetime.datetime.strptime(alarm_time_str, "%H:%M").time()
            with self.lock:
                self.alarms.append({"time": alarm_time, "label": label, "active": True})
            print(f"\n[SUCCESS] Alarm set for {alarm_time_str} ({label})")
        except ValueError:
            print("\n[ERROR] Invalid time format! Please use HH:MM in 24-hour format (e.g., 14:30).")

    def list_alarms(self):
        with self.lock:
            if not self.alarms:
                print("\n[INFO] No active alarms set.")
                return
            print("\n--- Current Alarms ---")
            for idx, alarm in enumerate(self.alarms, 1):
                status = "Active" if alarm["active"] else "Inactive"
                print(f"{idx}. Time: {alarm['time'].strftime('%H:%M')} | Label: {alarm['label']} | Status: {status}")
            print("----------------------\n")

    def trigger_alarm(self, alarm):
        with self.lock:
            self.is_ringing = True

        print("\n\n" + "="*50)
        print(f"🚨 WEE-WOO WEE-WOO! ALARM RINGING! [{alarm['label']}] 🚨")
        print("="*50)
        print("👉 Press 'd' + Enter to Dismiss")
        print("👉 Press 's' + Enter to Snooze (5 mins)")
        print("="*50)

        # Flag to control continuous beeping until user responds
        stop_beeping = threading.Event()

        def beep_loop():
            while not stop_beeping.is_set():
                try:
                    import winsound
                    winsound.Beep(2500, 500) # Beep for 500ms
                except Exception:
                    print("\a", end="")
                time.sleep(0.3) # Gap between beeps

        # Start beeping in background thread
        beepper_thread = threading.Thread(target=beep_loop, daemon=True)
        beepper_thread.start()
        
        try:
            while True:
                action = input("Enter choice ('d' / 's'): ").strip().lower()
                
                if action == 'd':
                    stop_beeping.set() # Stop the beep loop
                    with self.lock:
                        alarm['active'] = False
                        self.is_ringing = False
                    print("[INFO] Alarm dismissed successfully.\n")
                    break
                elif action == 's':
                    stop_beeping.set() # Stop the beep loop
                    now = datetime.datetime.now()
                    new_time = (now + datetime.timedelta(minutes=5)).time()
                    with self.lock:
                        alarm['time'] = new_time
                        self.is_ringing = False
                    print(f"[INFO] Alarm snoozed to {new_time.strftime('%H:%M')}\n")
                    break
                else:
                    print("[INVALID] Please type 'd' to dismiss or 's' to snooze.")
        finally:
            stop_beeping.set()

    def check_alarms(self):
        while self.running:
            current_time = datetime.datetime.now().time().replace(second=0, microsecond=0)
            
            with self.lock:
                if self.is_ringing:
                    time.sleep(1)
                    continue
                alarms_snapshot = list(self.alarms)
                
            for alarm in alarms_snapshot:
                if alarm["active"] and alarm["time"].replace(second=0, microsecond=0) == current_time:
                    self.trigger_alarm(alarm)
                    break
                    
            time.sleep(10)

    def start(self):
        t = threading.Thread(target=self.check_alarms, daemon=True)
        t.start()

        print("=== Python CLI Alarm Clock (Thread-Safe) ===")
        while self.running:
            if self.is_ringing:
                time.sleep(0.5)
                continue

            print("\nOptions:")
            print("1. Set Alarm (HH:MM)")
            print("2. List Alarms")
            print("3. Exit")
            
            choice = input("Select an option (1-3): ").strip()
            
            if self.is_ringing:
                continue

            if choice == '1':
                t_str = input("Enter alarm time in HH:MM (24-hour format): ").strip()
                label = input("Enter alarm label (optional): ").strip() or "Alarm"
                self.add_alarm(t_str, label)
            elif choice == '2':
                self.list_alarms()
            elif choice == '3':
                print("Exiting Alarm Clock. Goodbye!")
                self.running = False
                break
            else:
                if choice:
                    print("[INVALID] Choose between 1, 2, or 3.")

if __name__ == "__main__":
    clock = AlarmClock()
    clock.start()