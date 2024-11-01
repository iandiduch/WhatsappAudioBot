
# WhatsApp Audio Bot con Meta Business, OpenAI y AWS Polly

Este proyecto es una aplicación que integra la API de WhatsApp Business, OpenAI, y AWS Polly para proporcionar respuestas automáticas a través de WhatsApp, incluyendo la conversión de texto a voz. La aplicación utiliza Flask como servidor web para manejar solicitudes y webhooks.

## Requisitos Previos

### 1. Cuentas Necesarias

- **Meta Business (WhatsApp API)**: Necesitas una cuenta de WhatsApp Business para enviar y recibir mensajes. Puedes registrarte en [Meta Business](https://business.facebook.com/).
- **OpenAI API**: Para generar respuestas automáticas, necesitas una cuenta en OpenAI. Regístrate y obtén una clave API en [OpenAI](https://platform.openai.com/).
- **AWS (Amazon Polly)**: AWS Polly se usa para convertir texto a voz. Necesitas una cuenta de AWS para utilizar este servicio. Puedes registrarte en [AWS](https://aws.amazon.com/) y generar una clave de acceso y secret key en el panel IAM.
- **AWS EC2**: AWS EC2 para correr el script de python.

### 2. Configuración de Credenciales

Asegúrate de tener los siguientes valores de configuración para las credenciales:
- **Meta (WhatsApp API)**:
  - `whatsapp_business_token`: Token de acceso para tu API de WhatsApp Business.
  - `whatsapp_business_id`: ID de tu cuenta de WhatsApp Business.
  - `WEBHOOK_VERIFY_TOKEN`: Token de verificación para tu webhook.
- **OpenAI**: Clave de API de OpenAI.
- **AWS Polly**:
  - Configura las credenciales de AWS (Access Key y Secret Access Key) y especifica la región con el comando aws configure.

## Instalación

1. **Clona el Repositorio**:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. **Instala las Dependencias**:
   Este proyecto requiere varias dependencias que puedes instalar con `pip`:
   ```bash
   pip install boto3 flask requests openai
   ```

## Configuración

1. **Variables de Configuración**:
   En el archivo `wsp.py`, actualiza las variables de configuración con tus credenciales:
   
   ```python
   whatsapp_business_token = 'TU_TOKEN'
   whatsapp_business_id = 'TU_ID'
   WEBHOOK_VERIFY_TOKEN = 'TU_TOKEN_VERIFICACION'
   ```

2. **Configurar AWS Credenciales**:
   Puedes configurar las credenciales de AWS utilizando la CLI de AWS o guardando tus credenciales en el archivo `~/.aws/credentials`:
   ```plaintext
   [default]
   aws_access_key_id = TU_ACCESS_KEY
   aws_secret_access_key = TU_SECRET_KEY
   region = sa-east-1
   ```

3. **Ejecuta la Aplicación**:
   Inicia el servidor Flask ejecutando:
   ```bash
   python wsp.py
   ```

4. **Configurar Webhook en Meta Business**:
   - Dirígete a la configuración de tu aplicación en Meta Business.
   - Configura la URL de tu webhook apuntando a tu servidor y utiliza el `WEBHOOK_VERIFY_TOKEN` para la verificación.
   - IMPORTANTE QUE TU SERVIDOR DONDE EJECUTES EL SCRIPT TIENE QUE TENER CERTIFICADO HTTPS PARA QUE EL WEBHOOK DE META FUNCIONE, SI NO LO TIENES PUEDES UTILIZAR NGROK PARA HACER TUS ENDPOINTS HTTPS.

## Costos

- **Meta Business (WhatsApp API)**: Meta puede cobrar por los mensajes enviados y recibidos según el tipo y volumen de mensajes.
- **OpenAI API**: La API de OpenAI cobra por cada solicitud de generación de texto. Consulta los precios actualizados en [OpenAI Pricing](https://platform.openai.com/pricing).
- **AWS Polly**: AWS Polly cobra por el uso de texto a voz (TTS) en función del número de caracteres convertidos. Consulta los precios en [AWS Polly Pricing](https://aws.amazon.com/polly/pricing/).
- **AWS EC2**: El servidor EC2 cobra por las horas en linea.

> **Nota**: Asegúrate de configurar alertas de uso en AWS y OpenAI para evitar cargos inesperados.
