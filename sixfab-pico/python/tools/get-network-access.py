from pico_lte.core import PicoLTE
from pico_lte.utils.atcom import ATCom
from pico_lte.common import debug

debug.set_level(0)

atcom = ATCom()
picoLTE = PicoLTE()

atcom.send_at_comm("AT+CREG=2", None, None, 60)

debug.debug("Registering network")
picoLTE.network.register_network()

debug.debug("PDP ready")
picoLTE.network.get_pdp_ready()

result = atcom.send_at_comm("AT+CREG?", None, None, 60)
print("Network type is " + result["response"][0].split(",")[4])