import requests
import socket
import os

# --- 1. DICCIONARIO DE INTELIGENCIA Y REMEDIACIÓN ---
# Aquí asociamos técnica con ayuda humana.
MANUAL_REMEDIACION = {
    21: {
        "servicio": "FTP (Archivos)",
        "riesgo": "ALTO 🟠",
        "instruccion": "📁 *Manual rápido:* Alguien podría ver tus archivos. Si usas un disco duro en red (NAS), entra en su panel de control y cambia el acceso a 'SFTP' o usa servicios como Google Drive."
    },
    22: {
        "servicio": "SSH (Acceso Técnico)",
        "riesgo": "MEDIO 🟡",
        "instruccion": "🔑 *Manual rápido:* Este puerto permite controlar tu equipo por código. Si no eres informática, pide a tu técnico que lo cierre o que use 'Llaves SSH' en lugar de contraseñas."
    },
    80: {
        "servicio": "HTTP (Panel del Router)",
        "riesgo": "ALTO 🟠",
        "instruccion": "🌐 *Manual rápido:* Tu router es visible desde internet. Accede a la web de tu router (suele ser 192.168.1.1) y desactiva la 'Gestión Remota' o 'WAN Management'."
    },
    8080: {
        "servicio": "Cámara IP / Videovigilancia",
        "riesgo": "CRÍTICO 🔴",
        "instruccion": "🎥 *Manual rápido:* ¡Tus cámaras podrían ser públicas! Entra en la App de la cámara, busca 'Configuración de Red' y desactiva 'UPnP'. Cambia siempre la contraseña de fábrica."
    },
    3389: {
        "servicio": "Escritorio Remoto (Windows)",
        "riesgo": "CRÍTICO 🔴",
        "instruccion": "💻 *Manual rápido:* Alguien podría entrar en tu PC. Ve a *Configuración > Sistema > Escritorio remoto* y pulsa 'Desactivar'. Usa una VPN si necesitas teletrabajar."
    },
    9100: {
        "servicio": "Impresora en Red",
        "riesgo": "BAJO 🔵",
        "instruccion": "🖨️ *Manual rápido:* Tu impresora es visible. Ve al menú de la impresora, busca 'Servicios Web' y desactiva la impresión remota o AirPrint si solo imprimes desde dentro de la oficina."
    }
}

# --- 2. FUNCIONES TÉCNICAS ---

def obtener_ip_publica():
    try:
        respuesta = requests.get('https://api.ipify.org?format=json')
        return respuesta.json()['ip']
    except Exception as e:
        return f"Error: {e}"

def escanear_puerto(ip, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.settimeout(2)
    resultado = cliente.connect_ex((ip, puerto))
    cliente.close()
    return resultado == 0

def enviar_alerta_telegram(mensaje):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TOKEN or not CHAT_ID:
        print("⚠️ Error: Faltan credenciales de Telegram.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

# --- 3. LÓGICA DE AUDITORÍA ---

def ejecutar_auditoria():
    mi_ip = obtener_ip_publica()
    print(f"Iniciando escaneo profesional en: {mi_ip}")
    
    hallazgos = []
    
    for puerto in MANUAL_REMEDIACION.keys():
        if escanear_puerto(mi_ip, puerto):
            info = MANUAL_REMEDIACION[puerto]
            # Creamos un bloque de texto formateado para cada hallazgo
            alerta = (
                f"🚨 *PUERTO ABIERTO:* {puerto}\n"
                f"🔹 *Servicio:* {info['servicio']}\n"
                f"🚩 *Riesgo:* {info['riesgo']}\n"
                f"{info['instruccion']}\n"
            )
            hallazgos.append(alerta)

    if hallazgos:
        mensaje_final = f"⚠️ *NETSENTINEL: INFORME DE RIESGOS*\nIP auditada: `{mi_ip}`\n\n"
        mensaje_final += "\n---\n".join(hallazgos)
        enviar_alerta_telegram(mensaje_final)
    else:
        enviar_alerta_telegram(f"✅ *NetSentinel:* Escaneo completado en `{mi_ip}`. Tu red es un búnker, ¡todo seguro!")

# Ejecución
if __name__ == "__main__":
    ejecutar_auditoria()