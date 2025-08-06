from __future__ import print_function
import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Escopo necessário para acessar e modificar o Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def autenticar_google():
    """Autentica no Google e retorna as credenciais."""
    creds = None
    # Verifica se já existe um token salvo
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Se não houver credenciais válidas, faz login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Usa o arquivo credentials.json que você baixou do Google Cloud
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva as credenciais para futuras execuções
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def listar_eventos():
    """Lista os próximos eventos do Google Agenda."""
    service = build('calendar', 'v3', credentials=autenticar_google())
    agora = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC

    eventos_resultado = service.events().list(
        calendarId='primary', timeMin=agora,
        maxResults=10, singleEvents=True,
        orderBy='startTime'
    ).execute()

    eventos = eventos_resultado.get('items', [])

    if not eventos:
        print('Nenhum evento futuro encontrado.')
    for evento in eventos:
        inicio = evento['start'].get('dateTime', evento['start'].get('date'))
        print(inicio, evento['summary'])

def criar_evento(titulo, data_inicio, data_fim):
    """Cria um novo evento no Google Agenda."""
    service = build('calendar', 'v3', credentials=autenticar_google())
    evento = {
        'summary': titulo,
        'start': {'dateTime': data_inicio, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': data_fim, 'timeZone': 'America/Sao_Paulo'},
    }

    evento = service.events().insert(calendarId='primary', body=evento).execute()
    print(f"Evento criado: {evento.get('htmlLink')}")

if __name__ == '__main__':
    # Lista eventos já existentes
    listar_eventos()

    # Cria um evento de teste
    criar_evento(
        "Evento de Teste GPT",
        "2025-08-06T18:00:00",  # Data/hora de início
        "2025-08-06T19:00:00"   # Data/hora de fim
    )
