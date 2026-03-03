import requests
import socket
import os

# --- 1. DEFINICIÓN DE FUNCIONES ---

def obtener_ip_publica():
    try:
        respuesta = requests.get('https://api.ipify.org?format=json')
        datos = respuesta.json()
        return datos['ip']
    except Exception as e:
        return f"Error al obtener la IP: {e}"

def escanear_puerto(ip, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.settimeout(2)
    resultado = cliente.connect_ex((ip, puerto))
    if resultado == 0:
        estado = "ABIERTO"
    else:
        estado = "CERRADO"
    cliente.close()
    return estado

def enviar_alerta_telegram(mensaje):
    # Tus credenciales
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    if not TOKEN or not CHAT_ID:
        print("⚠️ Error: No se encontraron las credenciales de Telegram.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        respuesta = requests.post(url, data=payload)
        if respuesta.status_code == 200:
            print("📱 Mensaje de Telegram enviado con éxito.")
        else:
            print(f"❌ Error al enviar a Telegram: {respuesta.text}")
    except Exception as e:
        print(f"⚠️ Error de conexión con Telegram: {e}")

def ejecutar_auditoria(ip, puertos):
    print(f"\n--- Iniciando Auditoría en {ip} ---")
    hallazgos = []
    for puerto, servicio in puertos.items():
        print(f"Revisando {servicio} (Puerto {puerto})...", end=" ", flush=True)
        estado = escanear_puerto(ip, puerto)
        if estado == "ABIERTO":
            print("🚨 ¡ALERTA!")
            hallazgos.append(f"⚠️ PUERTO ABIERTO: {puerto} ({servicio})")
        else:
            print("✅ Seguro")
    return hallazgos

# --- 2. EJECUCIÓN DEL PROGRAMA ---

# Configuramos puertos
puertos_criticos = {
    21: "FTP", 22: "SSH", 23: "Telnet", 
    80: "HTTP", 443: "HTTPS", 3389: "RDP"
}

# Iniciamos proceso
mi_ip = obtener_ip_publica()
print(f"Tu IP pública detectada es: {mi_ip}")

# Enviamos un mensaje de inicio para probar el bot
enviar_alerta_telegram(f"🔍 *NetSentinel activado*\nIniciando escaneo en IP: `{mi_ip}`")

# Escaneamos
resultados = ejecutar_auditoria(mi_ip, puertos_criticos)

# Reportamos resultados
if resultados:
    mensaje_alerta = "🚨 *¡ALERTA DE VULNERABILIDAD!* 🚨\n\n"
    mensaje_alerta += f"Se detectaron puertos abiertos en: `{mi_ip}`\n\n"
    for h in resultados:
        mensaje_alerta += f"{h}\n"
    enviar_alerta_telegram(mensaje_alerta)
else:
    print("\n✅ Todo seguro. No hay hallazgos.")
    enviar_alerta_telegram("✅ *Escaneo finalizado*: Tu red está limpia y protegida.")