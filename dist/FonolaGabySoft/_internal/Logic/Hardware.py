import uuid

class RecolectorHardware:
    def obtener_datos(self):
        # Obtiene la dirección MAC de la placa de red principal
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        # Formatear MAC (XX:XX:XX:XX:XX:XX)
        mac_address = ':'.join(mac_num[i:i+2] for i in range(0, 11, 2))
        return {"mac": mac_address}