import time

class time:

    def WaitMinutes(Minutes):
        time.sleep(Minutes * 60)

    def WaitSeconds(Seconds):
        time.sleep(Seconds)
    
    def WaitMiliSeconds(MiliSeconds):
        time.sleep(MiliSeconds / 1000)
    
    def WaitMicroSeconds(MicroSeconds):
        time.sleep(MicroSeconds / 1e+6)
    
    def WaitNanoSeconds(NanoSeconds):
        time.sleep(NanoSeconds / 1e+9)
