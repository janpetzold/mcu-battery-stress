from pico_lte.core import PicoLTE
from pico_lte.utils.atcom import ATCom

picoLTE = PicoLTE()
atcom = ATCom()

result = atcom.send_at_comm("AT+QLTS=0")
print(result["response"][0].split(": ")[1])