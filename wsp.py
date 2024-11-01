import boto3
import threading
import time
import requests
from flask import Flask, send_file, request, jsonify, after_this_request
import os, glob
from openai import OpenAI
import re
from datetime import datetime, timezone
import uuid

# Configuración de credenciales
whatsapp_business_token = ''
whatsapp_business_id = ''
WEBHOOK_VERIFY_TOKEN = ''
app = Flask(__name__)

# Configuración de AWS Polly
polly_client = boto3.client('polly', region_name='sa-east-1')

def synthesize_speech(text):
    ssml_text = f"""
    <speak>
        <prosody rate="medium" pitch="medium">
            {text}
        </prosody>
    </speak>
    """
    response = polly_client.synthesize_speech(
        Text=ssml_text,
        TextType='ssml',
        VoiceId='Miguel',  # O cualquier otra voz que prefieras
        OutputFormat='mp3'
    )
    return response['AudioStream'].read()

def save_audio_locally(audio_data, filename):
    path = os.path.join('/home/ubuntu/llamadas', filename)  # Ruta absoluta al archivo
    with open(path, 'wb') as audio_file:
        audio_file.write(audio_data)
        
        
def format_phone_number(phone_number):
    # Que el número sea una cadena
    phone_number = str(phone_number)

    # Eliminar cualquier carácter no numérico
    phone_number = re.sub(r'\D', '', phone_number)

    # Eliminar el '9' si está presente después del código de país
    if phone_number.startswith('549'):
        phone_number = phone_number[:2] + phone_number[3:]

    return phone_number

@app.route('/audio/<filename>')
def audio(filename):
    # Ruta completa del archivo de audio
    file_path = os.path.join('/home/ubuntu/llamadas', filename)
    
    # Verifica si el archivo existe antes de intentar enviarlo
    if os.path.exists(file_path):
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
                print(f"Archivo {file_path} eliminado después de la descarga.")
            except Exception as e:
                print(f"Error al eliminar el archivo {file_path}: {e}")
            return response
        
        return send_file(file_path, mimetype='audio/mpeg')
    else:
        return "Archivo no encontrado", 404

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Log para verificar si GET se recibe correctamente
        print(f"Recibido GET: verify_token={verify_token}, challenge={challenge}")
        
        if verify_token == WEBHOOK_VERIFY_TOKEN:
            return challenge  # Confirma el desafío si el token es correcto
        else:
            print("Token de verificación no coincide.")
            return 'Token de verificación incorrecto', 403

    if request.method == 'POST':
        data = request.json
        
        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            message_value = changes.get("value", {})
            messages = message_value.get("messages", [])
            
            # No hacer nada si no hay mensajes
            if not messages:
                return jsonify(status="ok"), 200  

            message = messages[0]
            
            print("Mensaje recibido:", message)
            
            #Sacar el numero
            original_number = message["from"]
            #Formatearlo para sacarle el 9
            sender_id = format_phone_number(original_number)
            
	    
            # Verificación de tiempo para evitar mensajes antiguos
            timestamp = message.get("timestamp")
            if timestamp:
                message_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
                time_difference = (current_time - message_time).total_seconds()

                # Ignorar mensajes que tienen más de 1 minuto
                if time_difference > 60:
                    return jsonify(status="ok"), 200

            # Obtener el texto del mensaje
            text = message.get("text", {}).get("body", "")

            if text:
                response_text = get_openai_response(text)
                
                # Crear un identificador único para el archivo de audio
                unique_filename = f'audio_message_{uuid.uuid4()}.mp3'
                
                # Crea un hilo para sintetizar y guardar el audio
                audio_thread = threading.Thread(target=synthesize_and_save_audio, args=(response_text, unique_filename,))
                audio_thread.start()  # Inicia el hilo
                audio_thread.join()  # Espera a que el hilo termine
                
                send_whatsapp_audio(sender_id, unique_filename)
		
            return jsonify(status="ok"), 200

        except KeyError as e:
            return jsonify(status="error", error=f"Missing key: {str(e)}"), 500

        except Exception as e:
            return jsonify(status="error", error=str(e)), 500

def get_openai_response(user_message):
    client = OpenAI(
        api_key='',
    )

    # Agregar un contexto específico para respuestas en jerga argentina
    custom_prompt = f"""
    Actúa como un hablante nativo argentino. Usa jerga argentina y expresiones coloquiales en tus respuestas. 
    El mensaje del usuario es: "{user_message}"
    Responde de manera amistosa y con un toque local.
    """

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": custom_prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print("Mensaje de ChatGPT:", response.choices[0].message.content)
    return response.choices[0].message.content

# Función para sintetizar el audio en un hilo
def synthesize_and_save_audio(message, unique_filename):
    audio_data = synthesize_speech(message)  # Sintetiza el audio
    save_audio_locally(audio_data, unique_filename)  # Guarda el audio localmente

def send_whatsapp_audio(to_number, audio_filename):

    audio_url = f'http://url_de_tu_servidor:5000/audio/{audio_filename}'
    
    # Verifica si el archivo existe antes de enviar
    if not os.path.exists(audio_filename):
        print(f"El archivo {audio_filename} no existe, abortando envío.")
        return
    
    send_message_payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "audio",
        "audio": {
            "link": audio_url
        }
    }

    headers = {
        "Authorization": f"Bearer {whatsapp_business_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f'https://graph.facebook.com/v18.0/{whatsapp_business_id}/messages',
        json=send_message_payload,
        headers=headers
    )

    if response.status_code == 200:
        print("Mensaje enviado exitosamente")
        
    else:
        print("Error al enviar el mensaje:", response.text)

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    time.sleep(2)
