import threading
import time

class TTimer:
    def __init__(self, Interval=1000, Enabled=False, OnTimer=None):
        """
        Interval : 觸發間隔ms.（毫秒）
        Enabled  : 是否啟動定時器
        OnTimer  : 事件回呼函式 (void func())
        """
        self.Interval = Interval
        self.Enabled = Enabled
        self.OnTimer = OnTimer
        self._thread = None
        self._stop_event = threading.Event()

        if self.Enabled:
            self.Start()

    # ------------------------------------------------------
    def Start(self):
        """啟動定時器"""
        if self._thread and self._thread.is_alive():
            return  # 已在執行中
        self.Enabled = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ------------------------------------------------------
    def Stop(self):
        """停止定時器"""
        self.Enabled = False
        self._stop_event.set()

    # ------------------------------------------------------
    def _run(self):
        """內部執行迴圈"""
        interval = self.Interval / 1000.0
        next_time = time.perf_counter()
        while not self._stop_event.is_set():
            now = time.perf_counter()
            if now >= next_time:
                next_time += interval
                if self.OnTimer:
                    try:
                        self.OnTimer()
                    except Exception as e:
                        print(f"[TTimer Error] {e}")
            time.sleep(0.0005)  # 減少 CPU 負擔

    # ------------------------------------------------------
    def Execute(self):
        """封裝主程式迴圈（模擬應用程式主執行緒）"""
        print("TTimer is running... Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.Stop()
            print("TTimer stopped.")
        except Exception as e:
            self.Stop()
            print(f"[TTimer MainLoop Error] {e}")
        finally:
            self.Stop()

    # ------------------------------------------------------
    def __del__(self):
        self.Stop()



# ================================================================================
# [使用範例]
import time
#from TTimer import TTimer  # 假設存成 TTimer.py

def OnTimerEvent():
    print(f"[1] Tick: {time.time():.6f}")


def OnTimerEvent2():
    print(f"[2] Tick: {time.time():.6f}")

# ================================================================================
if __name__ == "__main__":
    Timer1 = TTimer(Interval=5, Enabled=True, OnTimer=OnTimerEvent)
    Timer2 = TTimer(Interval=5, Enabled=True, OnTimer=OnTimerEvent2)

    print("Timers running... Press Ctrl+C to stop.")
    try:
        while True:
            print("****** Main Loop ******");
            time.sleep(0.1)
    except KeyboardInterrupt:
        Timer1.Stop()
        Timer2.Stop()