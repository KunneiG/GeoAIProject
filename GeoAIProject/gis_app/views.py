import json
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

def index(request):
    return render(request, 'gis_app/index.html')

def get_data(request):
    # Отдаем JSON файл с данными
    file_path = os.path.join(settings.BASE_DIR, 'gis_app', 'static', 'gis_app', 'data.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)

@csrf_exempt # Для простоты лабораторной отключаем строгую проверку CSRF (в продакшене так нельзя!)
def ask_ai(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body)
            question = req_data.get('question')
            context_objects = req_data.get('context', [])

            if not question:
                return JsonResponse({'error': 'Пустой вопрос'}, status=400)
            # ID от яндекса
            IAM_TOKEN = 't1.9euelZrGzpCQmseKypnGyZCRmYuaju3rnpWakJudzMvLnJqZx8iKyceSiczl8_c2SWQn-e9UJyJ7_N3z93Z3YSf571QnInv8zef1656VmpfMx8zIkcmRlZSazIzKx5mK7_zN5_XrnpWakJKJnc-Zjs3JmpCejseNx8rv_cXrnpWal8zHzMiRyZGVlJrMjMrHmYo.A3TY3atWzxS9eCBMdwfN6P-v6saJejzs972UIOMvoAUp38a2brW9xlwKo2TdXF0Rj-RDVulzo3HTyHjl1xSXAQ'
            FOLDER_ID = 'b1g9idkbb77lhceuop73'

            # Формируем контекст для ИИ (переводим объекты в компактную строку)
            context_str = "\n".join([f"{o['name']} (Тип: {o['type']}, Адрес: {o['address']})" for o in context_objects])

            # Формируем промпт
            prompt = f"""Ты — ГИС-ассистент. Отвечай кратко, используя только предоставленные данные.
Данные об объектах на карте:
{context_str}

Вопрос пользователя: {question}"""

            # Запрос к YandexGPT
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Bearer {IAM_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
                "messages": [
                    {"role": "system", "text": "Ты — ГИС-ассистент."},
                    {"role": "user", "text": prompt}
                ],
                "temperature": 0.3,
                "maxTokens": 500
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            # Обработка ошибок API
            if response.status_code != 200:
                return JsonResponse({'error': f'Ошибка API Yandex: {response.status_code} - {response.text}'}, status=500)

            res_json = response.json()
            answer_text = res_json['result']['alternatives'][0]['message']['text']

            return JsonResponse({'answer': answer_text})

        except requests.exceptions.Timeout:
            return JsonResponse({'error': 'Таймаут при запросе к ИИ'}, status=504)
        except Exception as e:
            return JsonResponse({'error': f'Внутренняя ошибка: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Метод не разрешен'}, status=405)