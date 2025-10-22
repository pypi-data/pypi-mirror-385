# -*- coding: utf-8 -*-
"""Привет!\nВ этой библиотеке Вы увидите некоторые функции [бота Флореста](https://t.me/postbotflorestbot).\nМои социальные сети: [тык](https://taplink.cc/florestone4185)"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os, re
import random, requests
import aiohttp
import asyncio
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as Service1
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm.asyncio import tqdm
import numpy
import cv2
from yoloface import face_analysis
from telethon.sync import TelegramClient
from mcstatus import JavaServer, BedrockServer
from g4f.client import Client, AsyncClient
from g4f.Provider import OIVSCodeSer2, Blackbox, Chatai, LegacyLMArena, PollinationsAI, RetryProvider, ARTA, PollinationsImage
from g4f.Provider import Together
from phub import Client as PHClient, Quality
from yt_dlp import YoutubeDL
import torch
from whisper import load_model
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import librosa
from typing import Dict, Any, Optional, List

class VkUser:
    """ООП-модель пользователя ВКонтакте с доступом ко всем метаданным."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    # 🔹 Основные данные
    @property
    def id(self) -> int:
        return self._data.get("id")

    @property
    def first_name(self) -> str:
        return self._data.get("first_name", "")

    @property
    def last_name(self) -> str:
        return self._data.get("last_name", "")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def domain(self) -> str:
        return self._data.get("domain", "")

    @property
    def profile_url(self) -> str:
        return f"https://vk.com/{self.domain or 'id' + str(self.id)}"

    # 🔹 Демография
    @property
    def sex(self) -> str:
        return {1: "женский", 2: "мужской"}.get(self._data.get("sex"), "не указан")

    @property
    def bdate(self) -> Optional[str]:
        return self._data.get("bdate")

    @property
    def city(self) -> Optional[str]:
        return self._data.get("city", {}).get("title")

    @property
    def country(self) -> Optional[str]:
        return self._data.get("country", {}).get("title")

    @property
    def home_town(self) -> Optional[str]:
        return self._data.get("home_town")

    # 🔹 Социальные данные
    @property
    def followers(self) -> int:
        return self._data.get("followers_count", 0)

    @property
    def status(self) -> str:
        return self._data.get("status", "")

    @property
    def about(self) -> str:
        return self._data.get("about", "")

    @property
    def relation(self) -> str:
        relations = {
            0: "не указано", 1: "не женат/не замужем", 2: "есть друг/подруга",
            3: "помолвлен(а)", 4: "в браке", 5: "всё сложно",
            6: "в активном поиске", 7: "влюблён(а)", 8: "в гражданском браке"
        }
        return relations.get(self._data.get("relation"), "не указано")

    # 🔹 Контакты
    @property
    def mobile_phone(self) -> Optional[str]:
        return self._data.get("mobile_phone")

    @property
    def home_phone(self) -> Optional[str]:
        return self._data.get("home_phone")

    @property
    def site(self) -> Optional[str]:
        return self._data.get("site")

    @property
    def photo(self) -> str:
        return self._data.get("photo_max_orig", "")

    # 🔹 Образование и работа
    @property
    def university(self) -> str:
        return self._data.get("university_name", "")

    @property
    def faculty(self) -> str:
        return self._data.get("faculty_name", "")

    @property
    def graduation(self) -> Optional[int]:
        return self._data.get("graduation")

    @property
    def schools(self) -> List[Dict[str, Any]]:
        return self._data.get("schools", [])

    @property
    def career(self) -> List[Dict[str, Any]]:
        return self._data.get("career", [])

    @property
    def occupation(self) -> Optional[str]:
        occ = self._data.get("occupation")
        return occ.get("name") if occ else None

    # 🔹 Интересы
    @property
    def interests(self) -> str:
        return self._data.get("interests", "")

    @property
    def activities(self) -> str:
        return self._data.get("activities", "")

    @property
    def music(self) -> str:
        return self._data.get("music", "")

    @property
    def movies(self) -> str:
        return self._data.get("movies", "")

    @property
    def books(self) -> str:
        return self._data.get("books", "")

    @property
    def games(self) -> str:
        return self._data.get("games", "")

    @property
    def quotes(self) -> str:
        return self._data.get("quotes", "")

    # 🔹 Приватные и доп. поля
    @property
    def personal(self) -> Dict[str, Any]:
        return self._data.get("personal", {})

    @property
    def connections(self) -> Dict[str, Any]:
        return self._data.get("connections", {})

    # 🔹 Удобный вывод
    def summary(self) -> str:
        return (
            f"👤 {self.full_name}\n"
            f"Пол: {self.sex}\n"
            f"Дата рождения: {self.bdate or '—'}\n"
            f"Город: {self.city or '—'}, Страна: {self.country or '—'}\n"
            f"Статус: {self.status}\n"
            f"О себе: {self.about}\n"
            f"Подписчиков: {self.followers}\n"
            f"Профиль: {self.profile_url}"
        )


class ImageFormat:
    """Введите формат изображения. Поддерживаются: `.jpg`, `.webp`, `.gif`, `.bmp`, `.png`."""
    def __init__(self, format_: str):
        """Введите формат изображения. Поддерживаются: `.jpg`, `.webp`, `.gif`, `.bmp`, `.png`."""
        self.format_ = format_
        if format_ in ['.jpg', '.webp', '.gif', '.bmp', '.png']:
            return
        else:
            raise Exception("Неизвестный формат изображения.")

class RTMPServerInit:
    def __init__(self, url: str, key: str, user: str = None, password: str = None):
        """Ну, короче, инициализация класса для rtmp_livestream().\nurl: ссылОЧКА на RTMP. Пример: `rtmp://live.twitch.tv/app`.\nkey: ключ потока.\nuser: имя пользователя. Нигде не используется.\npassword: пароль. Нигде не используется."""
        self.key = key
        self.user = user
        self.password = password
        if url.startswith('rtmps://'):
            if not all([user, password]):
                self.url = url
            else:
                self.url = url.replace('rtmps://', f'rtmps://{user}:{password}@')
        else:
            if not all([user, password]):
                self.url = url
            else:
                self.url = url.replace('rtmp://', f'rtmp://{user}:{password}@')

class FaceInfo:
    def __init__(self, info: dict):
        self.info = info
    @property
    def gender(self):
        """Возвращаем пол человека на фотографии."""
        return self.info.get('gender')
    @property
    def race(self):
        """Возвращаем расу человека на фотографии."""
        return self.info.get('race')
    @property
    def age(self):
        """Возвращаем возраст человека на фотографии."""
        return self.info.get('age')
    @property
    def emotion(self):
        """Возвращаем эмоцию человека на фотографии."""
        return self.info.get('emotion')

class KworkOffer:
    def __init__(self, data: dict):
        self._data = data

    # Основные свойства для прямого доступа к простым полям
    @property
    def id(self) -> int:
        """ID оффера"""
        return self._data.get('id', 0)

    @property
    def status(self) -> str:
        """Статус оффера"""
        return self._data.get('status', '')

    @property
    def name(self) -> str:
        """Название оффера"""
        return self._data.get('name', '')

    @property
    def description(self) -> str:
        """Описание оффера"""
        return self._data.get('description', '')

    @property
    def price_limit(self) -> float:
        """Лимит цены"""
        return float(self._data.get('priceLimit', '0.00'))

    @property
    def possible_price_limit(self) -> int:
        """Возможный лимит цены"""
        return self._data.get('possiblePriceLimit', 0)

    @property
    def max_days(self) -> int:
        """Максимальная длительность выполнения в днях"""
        return int(self._data.get('max_days', '0'))

    @property
    def time_left(self) -> str:
        """Оставшееся время до истечения"""
        return self._data.get('timeLeft', '')

    @property
    def is_active(self) -> bool:
        """Активен ли оффер"""
        return self._data.get('isWantActive', False)

    @property
    def is_archived(self) -> bool:
        """Заархивирован ли оффер"""
        return self._data.get('isWantArchive', False)

    # Доступ к данным пользователя
    @property
    def user_id(self) -> int:
        """ID пользователя"""
        return self._data.get('user', {}).get('USERID', 0)

    @property
    def username(self) -> str:
        """Имя пользователя"""
        return self._data.get('user', {}).get('username', '')

    @property
    def user_profile_url(self) -> str:
        """URL профиля пользователя"""
        return self._data.get('wantUserGetProfileUrl', '')

    # Доступ к датам
    def get_date(self, date_type: str) -> str:
        """
        Получить дату из wantDates по типу (create, active, expire, reject)
        """
        return self._data.get('wantDates', {}).get(f'date{date_type.capitalize()}', '')

    @property
    def date_create(self) -> str:
        """Дата создания оффера"""
        return self.get_date('create')

    @property
    def date_active(self) -> str:
        """Дата активации оффера"""
        return self.get_date('active')

    @property
    def date_expire(self) -> str:
        """Дата истечения оффера"""
        return self.get_date('expire')

    # Доступ к статусу (altStatusHint)
    @property
    def status_color(self) -> str:
        """Цвет статуса"""
        return self._data.get('altStatusHint', {}).get('color', '')

    @property
    def status_title(self) -> str:
        """Название статуса"""
        return self._data.get('altStatusHint', {}).get('title', '')

    # Доступ к данным о бейджах пользователя
    def get_user_badges(self) -> list[dict]:
        """Список бейджей пользователя"""
        return self._data.get('user', {}).get('badges', [])

    @property
    def user_badge_titles(self) -> list[str]:
        """Список названий бейджей пользователя"""
        return [badge.get('badge', {}).get('title', '') for badge in self.get_user_badges()]

    # Доступ к статистике
    @property
    def wants_count(self) -> int:
        """Количество офферов пользователя"""
        return int(self._data.get('user', {}).get('data', {}).get('wants_count', '0'))

    @property
    def wants_hired_percent(self) -> int:
        """Процент нанятых по офферам"""
        return int(self._data.get('user', {}).get('data', {}).get('wants_hired_percent', '0'))

    # Доступ к категориям и просмотрам
    @property
    def category_id(self) -> str:
        """ID категории"""
        return self._data.get('category_id', '')

    @property
    def views(self) -> int:
        """Количество просмотров"""
        return int(self._data.get('views_dirty', '0'))

    # Доступ к доступным длительностям
    @property
    def available_durations(self) -> list[int]:
        """Список доступных длительностей выполнения"""
        return self._data.get('availableDurations', [])

    # Метод для проверки, есть ли портфолио
    @property
    def has_portfolio(self) -> bool:
        """Доступно ли портфолио"""
        return self._data.get('hasPortfolioAvailable', False)
    
    @property
    def url(self) -> str:
        """Ссылка на кворк."""
        return f'https://kwork.ru/projects/{self.id}'
    
    @property
    def dictify(self) -> dict:
        """Возвращаем словарь с кворком."""
        return self._data

class Resolution:
    def __init__(self, data: dict):
        self.data = data
    @property
    def height(self) -> int:
        """Возвращает высоту изображения."""
        return self.data.get('height')
    @property
    def width(self) -> int:
        """Возвращает ширину изображения."""
        return self.data.get('width')
    @property
    def orientation(self):
        """Возвращает ориентацию.\n0 - горизонтальная, 1 - вертикальная, 2 - квадратная."""
        if self.width > self.height:
            return 0
        elif self.width < self.height:
            return 1
        else:
            return 2

class YandexImage:
    def __init__(self, image: dict):
        self.image = image
    def get_image(self) -> bytes:
        """Изображение в байтах."""
        return self.image.get('data')
    def get_url(self) -> str:
        """Ссылка на изображение."""
        return self.image.get('url')
    def get_resolution(self) -> Resolution:
        """Возвращает высоту, ширину и ориентацию изображения."""
        image = Image.open(io.BytesIO(self.get_image()))
        resolution = image.size
        return Resolution({"width":resolution[0], 'height':resolution[1]})
    def get_size_mb(self):
        """Возвращает размер картинки в MB."""
        bytes_size = len(self.get_image()) 
        mbs = bytes_size / (1024 * 1024)
        return mbs
    def get_format(self):
        """Возвращает формат изображения."""
        image = Image.open(io.BytesIO(self.get_image()))
        return image.format.lower()
    def download(self, dir: str, name: str = None):
        """Просто скачаем локально.\ndir: директория. Если она не существует, мы создадим ее.\nname: имя изображения. Оно будет сгенерировано автоматически, если не указано."""
        if not os.path.exists(dir):
            os.mkdir(dir)
        if name:
            file = open(os.path.join(dir, f'{name}.jpg'), 'wb')
            file.write(self.get_image())
            file.close()
        else:
            r = random.random()
            file = open(os.path.join(dir, f'{r}.jpg'), 'wb')
            file.write(self.get_image())
            file.close()

class InitPornHubAccount:
    """Класс для инициализации вашего аккаунта PornHub. Удобно и быстро.\nemail: введите почту, к которой привязан ваш аккаунт.\npassword: введите пароль от вашей учётной записи."""
    def __init__(self, email: str, password: str):
        """Класс для инициализации вашего аккаунта PornHub. Удобно и быстро.\nemail: введите почту, к которой привязан ваш аккаунт.\npassword: введите пароль от вашей учётной записи."""
        self.email = email
        self.password = password
    @property
    def get_user(self):
        return self.email
    
    @property
    def get_password(self):
        return self.password
        

class Cripto():
    """Класс со списком криптовалют, которые доступны для функции `crypto_price`.\nBITKOIN, USDT, DOGECOIN, HAMSTERCOIN"""
    BITKOIN = 'bitcoin'
    USDT = 'tether'
    DOGE = 'dogecoin'
    HMSTR = 'hamster'

class FunctionsObject:
    def __init__(self, proxies: dict = {}, html_headers: dict = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'}, google_api_key: str = "", gigachat_key: str = "", gigachat_id: str = "", username_mail: str = "", mail_passwd: str = "", speech_to_text_key: str = None, vk_token: str = None, rcon_ip: str = None, rcon_port: int = None, rcon_password: str = None, whisper_model: str = None):
        """Привет. Именно в данном классе находятся ВСЕ функции бота. Давай я объясню смысл параметров?\nproxies: прокси, которые используются при HTTPS запросах к сайтам.\nhtml_headers: заголовки HTTPS запросов.\ngoogle_api_key: апи ключ гугла. Получить его можно [здесь](https://console.google.com/)\ngigachat_key: ключ от GigaChat (ПАО "СберБанк")\ngigachat_id: ID от GigaChat.\nusername_mail: ваша электронная почта.\nmail_passwd: ваш API-ключ от SMTP сервера.\nspeech_to_text_key: API ключ от Google Speech To Text. Необязательно.\nvk_token: токен для работы с VK API от вашего аккаунта.\nrcon_ip: IP адрес сервера, к которому нужно подключиться.\nrcon_port: порт удаленного администрирования RCON, по умолчанию, 25575.\nrcon_password: пароль для доступа к RCON. Храните его в надежном месте.\nwhisper_model: модель для распознаватора речи и создания субтитров. К примеру, tiny."""
        print(f'Объект класса был успешно запущен.')
        self.proxies = proxies
        self.headers = html_headers
        self.google_key = google_api_key
        self.gigachat_key = gigachat_key
        self.client_id_gigachat = gigachat_id
        self.username_mail = username_mail
        self.mail_passwd = mail_passwd
        self.speech_to_text_key = speech_to_text_key
        self.token_of_vk = vk_token
        self.client_for_gpt = Client()
        self.detector = face_analysis()
        if all([rcon_ip, rcon_port, rcon_password]):
            from mcrcon import MCRcon
            self.rcon_server = MCRcon(rcon_ip, rcon_password, rcon_port)
            print(f'RCON сервер инициализирован и готов к запуску.')
        else:
            self.rcon_server = None
        if whisper_model:
            self.whisper = load_model(whisper_model, torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
        else:
            self.whisper = None
    def generate_image(self, prompt: str) -> bytes:
        """Данная функция генерирует картинки с помощью GigaChat.\nprompt: запрос, по которому надо сгенерировать изображение."""
        import requests, re, urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if self.gigachat_key and self.client_id_gigachat:
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            payload={
                'scope': 'GIGACHAT_API_PERS'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': f'{self.client_id_gigachat}',
                'Authorization': f'Basic {self.gigachat_key}'
            }

            response = requests.request("POST", url, headers=headers, data=payload, verify=False, proxies=self.proxies)

            access_token = response.json()['access_token']

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }

            data = {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "system",
                        "content": "Glory to Florest."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "function_call": "auto"
            }

            patterns = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

            response = requests.post(
                'https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
                headers=headers,
                json=data,
                verify=False,
                proxies=self.proxies
            )
            json = response.json()
            matches = re.search(patterns, json['choices'][0]['message']['content'])
            if not matches:
                return f"Нельзя нарисовать что-либо по данному запросу. Причина: {json['choices'][0]['message']['content']}"
            else:
                req_img = requests.get(f"https://gigachat.devices.sberbank.ru/api/v1/files/{matches}/content", headers={'Accept': 'application/jpg', "Authorization":f"Bearer {access_token}"}, verify=False, stream=True, proxies=self.proxies)
                return req_img.content
        else:
            return "Нужно указать параметр `gigachat_key` и `gigachat_id` в настройках класса для работы с этой функцией."
    def ai(self, prompt: str, is_voice: bool = False):
        """Используем GigaChat.\nprompt: что тебе нужно от нейросетки.\nis_voice: записать-ли нам голосовуху?"""
        import requests, json, gtts, io
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if self.gigachat_key and self.client_id_gigachat:
            if not is_voice:
                url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

                payload={
                    'scope': 'GIGACHAT_API_PERS'
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'RqUID': f'{self.client_id_gigachat}',
                    'Authorization': f'Basic {self.gigachat_key}'
                }

                response = requests.request("POST", url, headers=headers, data=payload, verify=False, proxies=self.proxies)

                access_token = response.json()['access_token']

                url1 = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

                payload1 = json.dumps({
                    "model": "GigaChat",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "repetition_penalty": 1
                })
                headers1 = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                }

                response1 = requests.request("POST", url1, headers=headers1, data=payload1, verify=False, proxies=self.proxies)
                return response1.json()
            else:
                url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

                payload={
                    'scope': 'GIGACHAT_API_PERS'
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'RqUID': f'{self.client_id_gigachat}',
                    'Authorization': f'Basic {self.gigachat_key}'
                }

                response = requests.request("POST", url, headers=headers, data=payload, verify=False, proxies=self.proxies)

                access_token = response.json()['access_token']

                url1 = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

                payload1 = json.dumps({
                    "model": "GigaChat",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "stream": False,
                    "repetition_penalty": 1
                })
                headers1 = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                }

                response1 = requests.request("POST", url1, headers=headers1, data=payload1, verify=False, proxies=self.proxies)
                buffer = io.BytesIO()
                gtts.gTTS(response1.json()['choices'][0]['message']['content'], lang='ru', lang_check=False).write_to_fp(buffer)
                return buffer.getvalue()
        else:
            return "Нужно указать параметр `gigachat_key` и `gigachat_id` в настройках класса для работы с этой функцией."
        
    def deanon(self, ip: str) -> list:
        """Деанончик по IP.\nВы сами принимаете на себя ответственность за использование данной функции.\nip: дай айпи, тварюка."""
        import requests
        r = requests.get(f'http://ip-api.com/json/{ip}?lang=ru', proxies=self.proxies, headers=self.headers).json()
        results = []
        for key, value in r.items():
            results.append(f'{key.title()}: {value}')
        return results
    def download_video(self, url: str):
        """Данная функция качает видео с YouTube с помощью URL.\nurl: ссылка на видео."""
        from pytubefix import YouTube
        from tqdm import tqdm as sync_tqdm

        yt_obj = YouTube(url, proxies=self.proxies)

        if yt_obj.age_restricted:
            return 'На видео наложены возрастные ограничения.'    
        else:
            import io
            buffer = io.BytesIO()
            stream = yt_obj.streams.get_lowest_resolution()
            pbar = sync_tqdm(total=stream.filesize, desc=f'Скачивание "{yt_obj.title}"..', unit='B', unit_scale=True, dynamic_ncols=True)
            def progress(stream, chunk, bytes_remaining):
                pbar.update(len(chunk)) # Обновление прогресс-бар
            yt_obj.register_on_progress_callback(progress)
            stream.stream_to_buffer(buffer)
            pbar.close()
            return buffer.getvalue()
    def search_videos(self, query: str):
        """Функция для поиска видео по запросу и дальнейшего его закачивания.\nquery: запрос, по которому надо искать видео."""
        from pytubefix import Search
        from tqdm import tqdm as sync_tqdm

        search = Search(query, proxies=self.proxies)
        videos = search.videos

        if len(videos) == 0:
            return 'Видео по запросу не существует.'
        else:
            video = videos[0]
            if video.age_restricted:
                return 'На видео, которое мы нашли первым присутствуют возрастные ограничение. Его скачивание невозможно.'  
            else:
                import io
                buffer = io.BytesIO()
                stream = video.streams.get_lowest_resolution()
                pbar = sync_tqdm(total=stream.filesize, desc=f'Скачивание "{video.title}"..', unit='B', unit_scale=True, dynamic_ncols=True)
                def progress(stream, chunk, bytes_remaining):
                    pbar.update(len(chunk)) # Обновление прогресс-бара
                video.register_on_progress_callback(progress)
                stream.stream_to_buffer(buffer)
                pbar.close()
                return buffer.getvalue()
    def create_demotivator(self, top_text: str, bottom_text: str, photo: bytes, font: str):
        """Создайте демотиватор с помощью данной фичи!\ntop_text: верхний текст.\nbottom_text: нижний текст.\nphoto: ваша фотография в bytes.\nfont: ваш шрифт. Пример: `times.ttf`."""
        import io
        image = io.BytesIO(photo)
        from PIL import Image, ImageOps, ImageDraw, ImageFont
        img = Image.new('RGB', (1280, 1024), color='black')
        img_border = Image.new('RGB', (1060, 720), color='#000000')
        border = ImageOps.expand(img_border, border=2, fill='#ffffff')
        user_img = Image.open(image).convert("RGBA").resize((1050, 710))
        (width, height) = user_img.size
        img.paste(border, (111, 96))
        img.paste(user_img, (118, 103))
        drawer = ImageDraw.Draw(img)
        font_1 = ImageFont.truetype(font=font, size=80, encoding='UTF-8')
        text_width = font_1.getlength(top_text)

        while text_width >= (width + 250) - 20:
            font_1 = ImageFont.truetype(font=font, size=80, encoding='UTF-8')
            text_width = font_1.getlength(top_text)
            top_size -= 1

        font_2 = ImageFont.truetype(font=font, size=60, encoding='UTF-8')
        text_width = font_2.getlength(bottom_text)

        while text_width >= (width + 250) - 20:
            font_2 = ImageFont.truetype(font=font, size=60, encoding='UTF-8')
            text_width = font_2.getlength(bottom_text)
            bottom_size -= 1

        size_1 = drawer.textlength(top_text, font=font_1)
        size_2 = drawer.textlength(bottom_text, font=font_2)

        drawer.text(((1280 - size_1) / 2, 840), top_text, fill='white', font=font_1)
        drawer.text(((1280 - size_2) / 2, 930), bottom_text, fill='white', font=font_2)

        result_here = io.BytesIO()

        img.save(result_here, 'JPEG')
    
        del drawer

        return result_here.getvalue()
    def photo_make_black(self, photo: bytes):
        """Сделать фото черно-белым.\nphoto: фото в `bytes`."""
        import io
        from PIL import Image
        your_photo = io.BytesIO(photo)

        image = Image.open(your_photo)
        new_image = image.convert('L')
        buffer = io.BytesIO()
        new_image.save(buffer, 'JPEG')
        return buffer.getvalue()
    def check_weather(self, city):
        """Проверить погоду в каком-либо городе.\ncity: город, или его координаты в виде словаря `{"lat":..., "lon":...}`.\nИспользуется бесплатный OpenMeteo API."""
        import requests
        if isinstance(city, str):
            try:
                d = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city}', proxies=self.proxies, headers=self.headers).json()
                lot = d["results"][0]["latitude"]
                lat = d['results'][0]['longitude']
                req = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lot}&longitude={lat}&current_weather=true', headers=self.headers, proxies=self.proxies)
                if req.status_code != 200:
                    return None
                else:
                    data = req.json()
                    temperature = data['current_weather']['temperature']
                    title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                    weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                    wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                    time1 = data['current_weather']['time']
                    wind = data['current_weather']['windspeed']
                    return {'temp':temperature, 'weather':weather, 'weather_code':data['current_weather']['weathercode'], 'wind_direction':wind_dir, 'time_of_data':time1, 'wind_speed':wind}
            except:
                return None
        elif isinstance(city, dict):
            try:
                try:
                    lat = city["lat"]
                    lon = city["lon"]
                    req = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true', headers=self.headers, proxies=self.proxies)
                except KeyError:
                    return f'Нужно составить словарь, согласно образцу, указанного в описании функции.'
                
                data = req.json()
                temperature = data['current_weather']['temperature']
                title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                time1 = data['current_weather']['time']
                wind = data['current_weather']['windspeed']
                return {'temp':temperature, 'weather':weather, 'weather_code':data['current_weather']['weathercode'], 'wind_direction':wind_dir, 'time_of_data':time1, 'wind_speed':wind}
            except:
                return None
        else:
            return 'Поддерживаемые типы данных: `str` для названия города и `dict` для координатов.'
    def create_qr(self, content: str):
        """Создать QR код.\ncontent: что будет нести в себе qr. ссылка, текст..."""
        import qrcode
        import io
        
        buffer = io.BytesIO()
        qr = qrcode.make(content)
        qr.save(buffer, scale=10)
        return buffer.getvalue()
    def get_charts(self):
        """Узнать чарты Я.Музыки."""
        import requests
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
            'Connection': 'keep-alive',
            'Referer': 'https://music.yandex.ru/chart',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'X-Current-UID': '403036463',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Retpath-Y': 'https://music.yandex.ru/chart',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        }

        params = {
            'what': 'chart',
            'lang': 'ru',
            'external-domain': 'music.yandex.ru',
            'overembed': 'false',
            'ncrnd': '0.23800355071570123',
        }
        result = []
        response = requests.get('https://music.yandex.ru/handlers/main.jsx', params=params, headers=headers, proxies=self.proxies)
        chart = response.json()['chartPositions']
        for track in chart[:10]:
            position = track['track']['chart']['position']
            title = track['track']['title']
            author = track['track']['artists'][0]['name']
            result.append(f"№{position}: {author} - {title}")
        return f'Чарты Яндекс Музыки на данный момент🔥\n🥇{result[0]}\n🥈{result[1]}\n🥉{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}\n{result[6]}\n{result[7]}\n{result[8]}\n{result[9]}'
    def generate_password(self, symbols: int = 15):
        """Сгенерировать пароль.\nsymbols: количество символов в пароле."""
        import string
        import random

        symbols_ascii = list(string.ascii_letters + string.digits)

        random.shuffle(symbols_ascii)

        return ''.join(symbols_ascii[:symbols])
    def text_to_speech(self, text: str, lang: str = 'ru'):
        """Из текста в речь на Python.\ntext: текст для озвучки.\nlang: язык для озвучки. По умолчанию, **русский**."""
        import gtts
        import io

        buffer = io.BytesIO()
        engine = gtts.gTTS(text, lang=lang)
        engine.write_to_fp(buffer)
        return buffer.getvalue()
    def information_about_yt_channel(self, url: str):
        """Узнать информацию о YouTube канале на Python.\nurl: ссылка на канал."""
        if not self.google_key:
            return 'Для использования данной функции нужно указать параметр `google_key` в конструктор класса.'
        else:
            import requests
            if '/channel/' in url:
                channel_id = url.split('/channel/')[-1].split('?')[0]
                params = {
                    "part": "snippet,statistics",
                    "id": channel_id,
                    "key": self.google_key
                }
            else:
                username = url.split('/@')[-1].split('?')[0]
                params = {
                    "part": "snippet,statistics",
                    "forHandle": f"@{username}",
                    "key": self.google_key
                }
            request = requests.get('https://www.googleapis.com/youtube/v3/channels', proxies=self.proxies, headers=self.headers, params=params)
            response = request.json()
            return response
    def crypto_price(self, crypto: str, currency: str = 'rub'):
        """Цена криптовалют.\ncrypto: крипта, которую нужно узнать. Для этого воспользуйтесь константами из класса `Cripto`.\ncurrency: валюта, в которой нужно получить результат. Доступно: `rub`, `usd` и `eur`."""
        import requests
        r = requests.get('https://api.coingecko.com/api/v3/simple/price', params={"ids":crypto, 'vs_currencies':currency}, proxies=self.proxies, headers=self.headers).json()
        if r == {}:
            return "Неправильная валюта, или криптовалюта."
        else:
            try:
                return r[crypto][currency]
            except:
                return "Произошла ошибка. Возможно, были преодолены лимиты API."
    def password_check(self, nickname: str) -> int:
        """Поиск сливов паролей по нику.\nnickname: ник для поиска.\nВозвращает `int`."""
        import requests
        req = requests.get(f'https://api.proxynova.com/comb?query={nickname}&start=0&limit=15', headers=self.headers, proxies=self.proxies)
        if req.status_code == 200:
            return req.json()['count']
    def generate_nitro(self, count: int):
        """Генерация нитро.\n(Ключи могут не работать, может потребоваться некоторое количество попыток)\ncount: количество ключей."""
        import random, string
        a = 0
        results = []
        while a < count:
            characters = string.ascii_uppercase + string.digits
            random_code = ''.join(random.choice(characters) for _ in range(15))
            formatted_code = '-'.join(random_code[i:i+4] for i in range(0, 15, 4))
            results.append(formatted_code)
        del a
        return results
    def fake_human(self):
        """Фейковый гражданин Российской Федерации. Без вопросов.\nАргументы отсутствуют.\nВозвращает словарь `dict`."""
        import faker as faker_
        from datetime import date

        faker = faker_.Faker('ru-RU')
        today = date.today()
        year_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[0])
        month_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[1])
        day_f = int(str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-")[2])
        age_t = today.year - year_f - ((today.month, today.day) < (month_f, day_f))

        return {"name":faker.name(), "age":age_t, "work_place":faker.company(), "work_class":faker.job().lower(), "address":f"Российская Федерация, {faker.address()}", "postal_code":faker.address()[-6:], 'telephone_number':faker.phone_number(), "useragent":faker.user_agent(), "number_card":faker.credit_card_number(), "provider_of_card":faker.credit_card_provider(), "expire_card":faker.credit_card_expire(), "inn":faker.businesses_inn(), "orgn":faker.businesses_ogrn()}
    def real_info_of_photo(self, photo: bytes):
        """С помощью данной функции можно узнать адрес, город, почтовый индекс по фотографии.\nphoto: фотография в `bytes`."""
        import io
        from PIL import Image
        import requests
        with Image.open(io.BytesIO(photo)) as img:
            metadata = img._getexif()
            if not metadata:
                return None
            gps_info = metadata.get(34853)
            if not gps_info:
                return None
            lat = gps_info[2]
            lon = gps_info[4]
            lat_ref = gps_info[3]
            latitude = (lat[0] + lat[1] / 60.0 + lat[2] / 3600.0)
            longitude = (lon[0] + lon[1] / 60.0 + lon[2] / 3600.0)
            datetime_original = metadata.get(36867)
            try:
                if lat_ref != 'E':
                    latitude = -latitude
                r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers=self.headers, proxies=self.proxies)
                json = r.json()
                return {"country":json["address"]["country"], "region":json["address"]["state"], "district":json["address"]["district"], 'city':json["address"]["city"], "full_address":json["display_name"], 'postcode':json["address"]["postcode"], 'datetime':datetime_original}
            except:
                if lat_ref != 'E':
                    latitude = -latitude
                longitude = -longitude
                r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers=self.headers, proxies=self.proxies)
                json = r.json()
                return {"country":json["address"]["country"], "region":json["address"]["state"], "district":json["address"]["district"], 'city':json["address"]["city"], "full_address":json["display_name"], 'postcode':json["address"]["postcode"], 'datetime':datetime_original}
    def bmi(self, weight: float, height: float):
        """Узнать ИМТ по весу и росту.\nweight: дай вес в кг.\nheight: дай рост в метрах. Пример: 1.76 (176 см)\nВозвращает `dict` при удаче. `None` при невозможности узнать ИМТ. Не указывайте 0, либо отрицательные числа в параметры.\nИсходный код на канале моего друга: [тык](https://t.me/pie_rise_channel_s_8395/1009)"""
        if weight == 0 or weight < 0:
            return None
        else:
            if height == 0 or height < 0:
                return None
            else:
                bmi = weight / (height ** 2)
                if bmi < 18.5:
                    return {"bmi":f'{bmi:.2f}', "status":"Недостаточный вес"}
                elif 18.5 <= bmi < 25:
                    return {"bmi":f'{bmi:.2f}', "status":"Нормальный вес"}
                elif 25 <= bmi < 30:
                    return {"bmi":f'{bmi:.2f}', "status":"Избыточный вес"}
                else:
                    return {"bmi":f'{bmi:.2f}', "status":"Ожирение"}
    def link_on_user(self, id: str):
        """Введи ID юзера.\nГде его можно узнать?\nСкачайте Ayugram с официального сайта разработчика, а затем зайдите в профиль к человеку. Внизу будет его ID.\nЛибо зайдите в @username_to_id_bot и нажмите на кнопку \"User\". Если пользователь не отображается, добавьте его в контакты и повторите попытку.\nid: ID пользователя в кавычках."""
        if len(id) > 10:
            return {'status':f'Пользовательский ID не может привышать 10 символов.', 'url':None}
        elif len(id) < 10:
            return {"status":f'Пользовательский ID не может быть меньше, чем 10 символов.', 'url':None}
        else:
            try:
                return {"status":"Успех!", "url":F"tg://openmessage?user_id={int(id)}"}
            except:
                return {"status":f'Пользовательский ID не может привышать 10 символов.', 'url':None}
    def send_mail(self, subject: str, body: str, recipient: str, service: str = 'smtp.mail.ru', service_port: int = 465):
        """Отправить письмо по почте, используя Python.\nТребуется указать username_mail и mail_passwd в настройках класса для работы.\nsubject: тема письма.\nbody: остальная часть письма.\nrecipient: получатель.\nservice: сервис-провайдер вашего SMTP сервера.\nservice_port: порт SMTP сервера."""
        if self.username_mail and self.mail_passwd:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import smtplib
            message = MIMEMultipart()
            message["From"] = self.username_mail
            message["To"] = recipient
            message["Subject"] = subject
 
            message.attach(MIMEText(body, "plain", 'utf-8'))
 
            with smtplib.SMTP_SSL(service, service_port) as server:
                server.login(self.username_mail, password=self.mail_passwd)
                server.sendmail(self.username_mail, recipient, message.as_string())
        else:
            return "Укажите параметр username_mail и mail_passwd в настройках класса."
    def parsing_site(self, url: str):
        """Парсинг сайта)))\nЧисто скинем HTML код.\nurl: ссылка на сайт.\nПри удаче возвращает `str`."""
        import requests
        try:
            req = requests.get(url, proxies=self.proxies, headers=self.headers)
            if req.status_code == 200:
                return req.text
            else:
                return None
        except:
            return None
    def google_photo_parsing(self, query: str):
        """Парсинг гугл фото.\nВозвращает список с ссылками на фотографии, если есть.\nquery: запрос."""
        import requests
        from bs4 import BeautifulSoup
        req = requests.get(f'https://www.google.com/search?q={query}&tbm=isch&imglq=1&isz=l&safe=unactive', proxies=self.proxies)
        soup = BeautifulSoup(req.text, 'html.parser')
        tags = soup.find_all('img', {'src':True})
        imgs_links = []
        for tag in tags:
            if 'https://' in tag['src']:
                imgs_links.append(tag['src'])
        return imgs_links
    def speech_to_text(self, file, language: str = 'ru-RU') -> str:
        """Из речи в текст. Поддерживаются аудиофайлы формата: `wav`, `flac`.\nfile: директория к файлу. Либо open(), или io.BytesIO().\nlanguage: код языка. К примеру, `en-US`.\nВозвращает `str`!"""
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        try:
            text = r.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return 'Ошибка распознавания текста.'
        except:
            return 'Неизвестная ошибка. Также могут быть проблемы с подключением.'
    def email_mass_send(self, recievers: list, title: str, body: str, service: str = 'smtp.mail.ru', service_port: int = 465):
        """Функция для массовой отправки сообщений.\nrecievers: список получателей. К примеру: ['...', '...', ...]\ntitle: заголовок письма.\nbody: остальной текст письма.\nservice: сервис, к примеру `smtp.mail.ru`.\nservice_port: порт SMTP-сервера, к примеру, 465."""
        if self.username_mail and self.mail_passwd:
            for email in recievers:
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                import smtplib
                message = MIMEMultipart()
                message["From"] = self.username_mail
                message["To"] = email
                message["Subject"] = title
    
                message.attach(MIMEText(body, "plain", 'utf-8'))
    
                with smtplib.SMTP_SSL(service, service_port) as server:
                    server.login(self.username_mail, password=self.mail_passwd)
                    server.sendmail(self.username_mail, email, message.as_string())
        else:
            return "Укажите параметр username_mail и mail_passwd в настройках класса."
    def alarm_clock(self, time_to_ring: str, sound):
        """Будильник на Python. Весело, не правда-ли?)\ntime_to_ring: время срабатывания будильника в формате ЧЧ:ММ:СС. К примеру, `16:45:43`.\nsound: директория к файлу со звуком для будильника, либо буфероподобные объекты. open(), io.BytesIO() и другие."""
        from os import environ
        environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        from pygame import mixer
        import time
        from colorama import Fore

        mixer.init()

        alarm_time = time.strptime(time_to_ring, "%H:%M:%S")
        hour = alarm_time.tm_hour
        minutes = alarm_time.tm_min
        seconds = alarm_time.tm_sec
        data = {'hour':hour, 'minutes':minutes, 'seconds':seconds}
        print(f'{Fore.GREEN}Будильник успешно запущен на {Fore.BLUE}{time_to_ring}.')
        while True:
            # Получаем текущее время
            current_time = time.localtime()
            hour_ = current_time.tm_hour
            minutes_ = current_time.tm_min
            seconds_ = current_time.tm_sec
            
            # Проверяем, наступило ли время будильника
            if {'hour':hour_, 'minutes':minutes_, 'seconds':seconds_} == data:
                print(f'{Fore.RED}ВНИМАНИЕ!!! БУДИЛЬНИК АКТИВИРОВАН, ПРОСЫПАЙТЕСЬ!!!')
                mixer.Sound(sound).play(loops=-1)
            else:
                pass
    def cpp_compiler(self, filename: str, filename_output: str):
        """Использование компилятора G++ в Python.\nПроверьте его наличие перед запуском программы.\nfilename: имя файла .cpp формата. Поставьте его в папку с .py документом.\nfilename_output: название выходного .exe файла."""
        import subprocess
        try:
            subprocess.run(['g++', f'{filename}', '-o', f'{filename_output}'])
            return True
        except:
            return False
    def python_exe_compiler(self, path_to_py: str, path_output: str, flags: str = None):
        """Из .py в .exe компилятор.\npath_to_py: путь к вашему .py файлу.\npath_output: куда сохранить .exe файл.\nflags: какие-нибудь флаги от PyInstaller. Необязательно."""
        import os
        if flags:
            os.chdir(path_output)
            c = os.system(f'pyinstaller --distpath "{path_output}" {flags} "{path_to_py}"')
            if c == 1:
                return False
            else:
                return True
        else:
            os.chdir(path_output)
            c = os.system(f'pyinstaller --distpath "{path_output}" "{path_to_py}"')
            if c == 1:
                return False
            else:
                return True
    def tracking_youtube_author(self, channel_url: str, token_of_bot: str, id: int):
        """Данная функция помогает отслеживать новый контент вашего любимого блогера на YouTube (видео, shorts, прямые трансляции) через уведомления, которые приходят к вам в переписку с вашим ботом, созданным в [BotFather](https://t.me/BotFather).\nchannel_url: ссылка на канал для отслеживания новых видео.\ntoken_of_bot: токен вашего бота, который можно узнать в BotFather.\nid: ID вашего аккаунта, в переписку с ботом будут отправляться уведомления."""
        import requests, time

        import pytubefix
        try:
            channel = pytubefix.Channel(channel_url, proxies=self.proxies)
        except:
            return "Данного канала не существует."


        last_video = channel.videos[0].watch_url
        last_short = channel.shorts[0].watch_url
        last_live = channel.live[0].watch_url

        while True:
            if channel.videos[0].watch_url == last_video:
                if channel.shorts[0].watch_url == last_short:
                    if channel.live[0].watch_url == last_live:
                        pass
                    else:
                        last_live = channel.live[0].watch_url
                        text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.live[0].title}\nСсылка: {channel.live[0].watch_url}'
                        requests.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxies=self.proxies)
                else:
                    last_short = channel.shorts[0].watch_url
                    text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.shorts[0].title}\nСсылка: {channel.shorts[0].watch_url}'
                    requests.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxies=self.proxies)
            else:
                last_video = channel.videos[0].watch_url
                text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.videos[0].title}\nСсылка: {channel.videos[0].watch_url}'
                requests.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxies=self.proxies)
            time.sleep(0.5)
    def searching_musics_vk(self, query: str, count: int = 3):
        """Поиск музыки по запросу с ВК.\nВозвращает список найденных песен.\nquery: запрос.\ncount: какое максимальное количество песен нужно отобразить в списке.\nЕсли не работает функция, то стоит откатить версию библиотеки vkpymusic: `pip install vkpymusic==3.0.0`."""
        if not self.token_of_vk:
            return "Необходимо в настройках класса указать токен от Вашего аккаунта в VK."
        else:
            from vkpymusic import Service, TokenReceiver
            service = Service('KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)', self.token_of_vk)
            songs = []
            for track in service.search_songs_by_text(query, count):
                songs.append(track.to_dict())
            return songs
    def get_last_post(self, query: str):
        """Последний посты из паблика.\nquery: название паблика.\nВернет словарь при удачном нахождении паблика."""
        import vk_api
        vk_session = vk_api.VkApi(token=self.token_of_vk)
        vk = vk_session.get_api()
        response = vk.groups.search(q=query, type='group', count=1)  # Используем groups.search
        response1 = vk.wall.get(owner_id=-int(response['items'][0]['id']), count=1)  # owner_id должен быть отрицательным для групп
        if response['count'] > 0:
                try:
                    post = response1['items'][0]
                    text = post.get('text', 'Текст отсутствует')  # Получаем текст поста, если есть
                    post_id = post['id']
                    owner_id = post['owner_id']
                    link = f"https://vk.com/wall{owner_id}_{post_id}"  # Формируем ссылку на пост
                    likes = response1['items'][0]['likes']['count']
                    views = response1['items'][0]['views']['count']
                    reposts = response1['items'][0]['reposts']['count']
                    return {"text":text, "post_id":post_id, "owner_id":owner_id, "link":link, 'views':views, 'reposts':reposts, 'likes':likes}
                except:
                    return None
        else:
            return None
    def image_text_recognition(self, img: bytes, lang: str = 'ru'):
        """Разбор текста на изображении, с помощью инструментов Google Cloud.\nimg: ваше изображение в bytes.\nlang: язык текста на изображении."""
        import requests, base64
        if not self.google_key:
            return 'Для работы с данной функцией необходим Ваш Google Cloud API ключ. Проверьте, что в разделе Enabled APIs & Services есть Vision AI API.'
        else:
            image = base64.b64encode(img).decode("utf-8")

            # Тело запроса
            request_body = {
                "requests": [
                    {
                        "image": {
                            "content": image
                        },
                        "features": [
                            {
                                "type": "LABEL_DETECTION",
                                "maxResults": 10
                            }
                        ],
                        "imageContext": {
		                    "languageHints": lang
		                }
                    }
                ]
            }

            # URL
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_key}"

            # Заголовки
            headers = {
                "Content-Type": "application/json"
            }

            # Запрос
            response = requests.post(url, headers=headers, json=request_body, proxies=self.proxies)
            return {"code":response.status_code, 'answer':response.json()}
    def rcon_send(self, command: str):
        """Команда для отправки команды на сервер через RCON.\nТребует rcon_ip, rcon_port и rcon_password в настройках FunctionsObject.\ncommand: команда с аргументами. Пример: `say Привет!`\nВозвращает `str`, ответ от сервера."""
        if not self.rcon_server:
            return 'RCON сервер не инициализирован.\nПроверьте, указали ли Вы нужные параметры в настройках класса.'
        else:
            self.rcon_server.connect()
            return self.rcon_server.command(command)
    def censor_faces_image(self, image: bytes, model: str = 'full', return_resolution: tuple[int] = None, block_size: int = 20):
        """Данная функция превращает лица на фото в пиксели, короче, цензура.\nimage: фотка в `bytes`. Пример: open('photo.jpg', 'rb').read()\nmodel: модель для распознавания лиц. `tiny` и `full`.\nreturn_resolution: выходное разрешение. По умолчанию, разрешение исходной фотографии.\nblock_size: резкость мозаики, по умолчанию 20.\nВозвращает bytes."""
        from tqdm import tqdm
        if return_resolution:
            img_pil = Image.open(io.BytesIO(image)).resize(return_resolution, Image.Resampling.LANCZOS)
            img = cv2.imdecode(numpy.frombuffer(image, numpy.uint8), cv2.IMREAD_COLOR)
            img = cv2.resize(img, return_resolution)
            _, boxes, confs = self.detector.face_detection(frame_arr=img, model=model)
            
            faces = [(x, y, w, h) for i, (x, y, w, h) in enumerate(boxes) if confs[i] > 0.5]
            if not faces:
                print(f'Лица не были найдены на фотографии.')
                return image
            else:
                for x, y, w, h in tqdm(faces, desc='Цензурим лица..', ncols=70):
                    region = (x, y, x + w, y + h)
                    region_img = img_pil.crop(region)
                    small_size = (max(int(w) // block_size, 1), h)
                    small_region = region_img.resize(small_size, Image.Resampling.NEAREST)
                    mosaic_region = small_region.resize((w, h), Image.Resampling.NEAREST)
                    img_pil.paste(mosaic_region, region)
                output = io.BytesIO()
                img_pil.save(output, format='JPEG')
                print(f'Готово!')
                return output.getvalue()
        else:
            img_pil = Image.open(io.BytesIO(image))
            img = cv2.imdecode(numpy.frombuffer(image, numpy.uint8), cv2.IMREAD_COLOR)        
            _, boxes, confs = self.detector.face_detection(frame_arr=img, model=model)
            
            faces = [(x, y, w, h) for i, (x, y, w, h) in enumerate(boxes) if confs[i] > 0.5]
            if not faces:
                print(f'Лица не были найдены на фотографии.')
                return image
            else:
                for x, y, w, h in tqdm(faces, desc='Цензурим лица..', ncols=70):
                    region = (x, y, x + w, y + h)
                    region_img = img_pil.crop(region)
                    small_size = (max(int(w) // block_size, 1), h)
                    small_region = region_img.resize(small_size, Image.Resampling.NEAREST)
                    mosaic_region = small_region.resize((w, h), Image.Resampling.NEAREST)
                    img_pil.paste(mosaic_region, region)
                output = io.BytesIO()
                img_pil.save(output, format='JPEG')
                print(f'Готово!')
                return output.getvalue()
    def minecraft_server_info(self, ip: str, port: int = None, type_: str = 'java'):
        """Информация о Minecraft-сервере.\nip: ip/host сервера, или домен. Также можно написать ip:port.\nport: порт сервера, необязателен.\ntype: java, или bedrock."""
        if type_ in ['java', 'bedrock']:
            try:
                if type_ == 'java':
                    if not port:
                        server = JavaServer(ip)
                    else:
                        server = JavaServer(ip, port)
                    latency = server.ping()
                    query = server.query()
                    status = server.status()
                    return {"latency":latency, 'query':{"query_motd":query.motd.to_ansi(), 'query_map':query.map, 'query_players_count':query.players.online, 'query_players_max':query.players.max, 'all_info':query.as_dict()}, 'status':{"query_motd":status.motd.to_ansi(), 'description':status.description, 'icon_of_server_base64':status.icon, 'query_players_count':query.players.online, 'query_players_max':query.players.max, 'version':status.version.name, 'all_info':status.as_dict()}}
                else:
                    if not port:
                        server = BedrockServer(ip)
                    else:
                        server = BedrockServer(ip, port)
                    status = server.status()
                    return {"status":status.as_dict()}
            except:
                return
        else:
            return
    def gpt_4o_req(self, prompt: str, max_tokens: int = 4096, proxy: str = None, image: bytes = None):
        """Фигня для доступа к GPT-4o-mini.\nprompt: сам запрос к нейронке.\nmax_tokens: количество символов в ответе. По умолчанию, 4096.\nproxy: прокси. По умолчанию, которые в FunctionsObject.\nimage: изображение в bytes. Для описания объектов на фото."""
        if not image:
            if not proxy:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', RetryProvider([Together, OIVSCodeSer2, Blackbox, Chatai, LegacyLMArena, PollinationsAI]), proxy=self.proxies.get('http'), max_tokens=max_tokens, web_search=True)
            else:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', RetryProvider([Together, OIVSCodeSer2, Blackbox, Chatai, LegacyLMArena, PollinationsAI]), proxy=proxy, max_tokens=max_tokens, web_search=True)
            return req.choices[0].message.content
        else:
            if not proxy:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', PollinationsAI, proxy=self.proxies.get('http'), max_tokens=max_tokens, web_search=True, image=image)
            else:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', PollinationsAI, proxy=proxy, max_tokens=max_tokens, web_search=True, image=image)
            return req.choices[0].message.content
    def flux_pro_gen(self, prompt: str, proxy: str = None):
        """Для генерации более лучших картинок через flux-pro.\nprompt: запрос для нейросети.\nproxy: прокси. По умолчанию, которые в настройках класса (если есть)."""
        if proxy:
            img = self.client_for_gpt.images.generate(prompt, 'flux-pro', Together, 'url', proxy)
        else:
            img = self.client_for_gpt.images.generate(prompt, 'flux-pro', Together, 'url', self.proxies.get('http'))
        urls = []
        for i in img.data:
            urls.append(i.url)
        return urls
    def add_watermark(self, text: str, image: bytes, font: str, position: tuple[int] = (10, 10)):
        """Функция для добавления водяного знака.\ntext: текст для водяного знака.\nimage: изображение в bytes.\nfont: путь к шрифту (пример: times.ttf)\nposition: где он должен находиться?"""
        # Открываем изображение
        base_image = Image.open(io.BytesIO(image)).convert("RGBA")
        
        # Создаем прозрачный слой для водяного знака
        watermark = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Настройки текста
        font = ImageFont.truetype(font, 40)  # Шрифт и размер
        text_color = (255, 255, 255, 100)  # R,G,B,Alpha (прозрачность)
        
        # Рисуем текст
        draw.text(position, text, fill=text_color, font=font)
        
        # Накладываем водяной знак
        result = Image.alpha_composite(base_image, watermark)
        
        # Сохраняем (конвертируем обратно в RGB для JPG)
        output = io.BytesIO()
        result.convert("RGB").save(output, 'JPEG')
        return output.getvalue()
    def deepseek_v3_0324(self, prompt: str, max_tokens: int = 4096, expression: str = 'auto', proxy: str = None):
        """Функция для бесплатного доступа к DeepSeek-v3-0324.\nprompt: запрос к нейросети.\nmax_tokens: максимально допустимое количество токенов в ответе.\nexpression: тон. Три режима: `auto`, `toxic`, `non-toxic`.\nproxy: прокси. По умолчанию, которые из класса."""
        if expression == 'auto':
            if proxy:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'deepseek-v3', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'deepseek-v3', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        elif expression == 'toxic':
            if proxy:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nЗапрос: "{prompt}"'}], 'deepseek-v3-0324', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nЗапрос: "{prompt}"'}], 'deepseek-v3-0324', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        elif expression == 'non-toxic':
            if proxy:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt + '\nnon-toxic'}], 'deepseek-v3', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt+ '\nnon-toxic'}], 'deepseek-v3', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        else:
            return 'expression указан неверно! auto, toxic, либо non-toxic!'
    def youtube_playlist_download(self, url: str, regime: str = 'audio') -> list[bytes]:
        """Функция для скачивания элементов из плейлиста с YouTube.\nurl: ссылка на плейлист.\nregime: что скачивать: аудио, или видео?\nВозвращает список, а точнее `list[bytes]` с видео."""
        from pytubefix import Playlist
        from tqdm import tqdm
        
        playlist = Playlist(url, proxies=self.proxies)
        videos: list[bytes] = []
        
        if regime == 'video':
            for video in tqdm(playlist.videos, 'Скачиваем видео..', ncols=70):
                buffer = io.BytesIO()
                if video.age_restricted:
                    continue
                video.streams.get_lowest_resolution().stream_to_buffer(buffer)
                videos.append(buffer.getvalue())
            return videos
        elif regime == 'audio':
            for audio in tqdm(playlist.videos, desc='Скачиваем аудио..', ncols=70):
                buffer = io.BytesIO()
                if audio.age_restricted:
                    continue
                audio.streams.get_audio_only().stream_to_buffer(buffer)
                videos.append(buffer.getvalue())
            return videos
        else:
            raise Exception('Ты неправильный режим указал. ТОЛЬКО VIDEO И AUDIO!')
    def pornhub_search(self, query: str, count: int = 5, quality: str = 'best', account: InitPornHubAccount = None, proxies: dict[str, str] = None, checking_was_downloaded: bool = False) -> list[bytes]:
        """Функция для поиска видео по запросу и скачивания их с PornHub. Функция нарушает ToS PornHub, рекомендую использовать прокси. По умолчанию, используются, которые указаны в классе.\nquery: логично, запрос.\ncount: сколько видео тебе нужно?\nquality: в каком качестве качать? По умолчанию, `best`. Есть: worst, best и half.\naccount: укажите свой аккаунт, но это необязательно.\nproxies: кастомные прокси, конкретно для данной функции.\nchecking_was_downloaded: проверять, были-ли видео заранее загружены."""
        try:
            import requests
            if account:
                client = PHClient(language='ru', proxies=proxies if proxies else self.proxies, login=True, email=account.get_user, password=account.get_password)
            else:
                client = PHClient(language='ru', proxies=proxies if proxies else self.proxies, login=False)
            
            downloaded_videos: list[bytes] = []
            
            if not checking_was_downloaded:
                request = client.search(query)
                videos = request.sample(count, free_premium=False)
                for video in videos:
                    segments: list[str] = []
                    for s in video.get_segments(Quality(quality)):
                        segments.append(s)
                    chunks = []
                    for chunk in tqdm(segments, desc=f'Скачиваю "{video.title}"..'):
                        try:
                            r = requests.get(chunk, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content
                            chunks.append(r)
                        except:
                            r = requests.get(chunk, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content
                            chunks.append(r)
                    video_data = b''.join(chunks)
                    downloaded_videos.append(video_data)
                return downloaded_videos
            else:
                request = client.search(query)
                videos = request.sample(count, free_premium=False)
                if not os.path.exists('downloaded.txt'):
                    with open('downloaded.txt', 'w') as f:
                        pass
                for video in videos:
                        if video.url in open('downloaded.txt', 'r').readlines():
                            print(f'"{video.title}" уже было скачено.')
                            continue
                        else:
                            f = open('downloaded.txt', 'a')
                            f.write(f'{video.url}\n')
                            f.close()
                            segments: list[str] = []
                            for s in video.get_segments(Quality(quality)):
                                segments.append(s)
                            chunks = []
                            for chunk in tqdm(segments, desc=f'Скачиваю "{video.title}"..'):
                                try:
                                    r = requests.get(chunk, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content
                                    chunks.append(r)
                                except:
                                    r = requests.get(chunk, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content
                                    chunks.append(r)
                            video_data = b''.join(chunks)
                            downloaded_videos.append(video_data)
                return downloaded_videos
        except:
            raise Exception('Произошла ошибка. Попробуйте откатить версию до 4.7. Для этого пропишите: pip install phub==4.7')
    def pornhub_download_by_url(self, url: str, quality: str = 'best', account: InitPornHubAccount = None, proxies: dict[str, str] = None):
        """Функция для скачивания видео с PornHub по ссылке.\nurl: ссылка на видео.\nquality: качество.\naccount: ваш аккаунт на PornHub.\nproxies: кастомные прокси для этой функции, если есть."""
        try:
            import requests
            if account:
                client = PHClient(language='ru', proxies=proxies if proxies else self.proxies, login=True, email=account.get_user, password=account.get_password)
            else:
                client = PHClient(language='ru', proxies=proxies if proxies else self.proxies, login=False)
            
            video = client.get(url)
            segments: list[str] = []
            for s in video.get_segments(Quality(quality)):
                segments.append(s)
            chunks = []
            
            for segment in tqdm(segments, desc=f'Качаю "{video.title}"...'):
                try:
                    chunks.append(requests.get(segment, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content)
                except:
                    chunks.append(requests.get(segment, proxies=proxies if proxies else self.proxies, headers={"User-Agent":"Mozilla/5.0"}).content)
            return b''.join(chunks)
        except:
            raise Exception('Произошла ошибка. Попробуйте откатить версию до 4.7. Для этого пропишите: pip install phub==4.7')
    def pornhub_video_information(self, url: str, account: InitPornHubAccount = None, proxies: dict[str, str] = None) -> dict:
        """Данная функция выводит информацию о видео, без его скачивания.\nurl: ссылка на видео.\naccount: ваш аккаунт.\nproxies: кастомные прокси для этой функции."""
        if account:
            client = PHClient(account.get_user, account.get_password, language='ru', proxies=proxies if proxies else self.proxies, login=True)
        else:
            client = PHClient(language='ru', proxies=proxies if proxies else self.proxies, login=False)
        video = client.get(url)
        return video.dictify()
    def parse_kwork(self, category: int, pages: int = 1) -> list[KworkOffer]:
        """Функция для парсинга объявлений на kwork.\ncategory: категория для парсинга.\npages: сколько страниц спарсить? По умолчанию, 1.\nВозвращает список с кворками."""
        import requests, json
        from bs4 import BeautifulSoup
        
        offers: list[KworkOffer] = []
        
        for p in tqdm(range(1, pages + 1), desc='Парсинг..'):
            response = requests.get('https://kwork.ru/projects', params={"c": category, "page":p}, proxies=self.proxies)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            if not soup.head:
                raise Exception

            scripts = soup.head.find_all("script")
            js_script = ""
            for script in scripts:
                if script.text.startswith("window.ORIGIN_URL"):
                    js_script = script.text
                    break

            start_pointer = 0
            json_data = ""
            in_literal = False
            for current_pointer in range(len(js_script)):
                if js_script[current_pointer] == '"' and js_script[current_pointer - 1] != "\\":
                    in_literal = not in_literal
                    continue

                if in_literal or js_script[current_pointer] != ";":
                    continue

                line = js_script[start_pointer:current_pointer].strip()
                if line.startswith("window.stateData"):
                    json_data = line[17:]
                    break

                start_pointer = current_pointer + 1

            data = json.loads(json_data)

            for raw_kwork in data["wantsListData"]["wants"]:
                offer = KworkOffer(raw_kwork)
                offers.append(offer)
        return offers
    def info_about_faces_on_photo(self, photo: bytes):
        """Данная функция выдает информацию о человеке на фотографии, или о людях.\nphoto: принимает фотографию в байтах.\nВозвращает `list[FaceInfo]` при наличии людей на фотографии.\nДЛЯ ДАННОЙ ФУНКЦИИ ЖЕЛАТЕЛЬНО ИМЕТЬ ПРОЦЕССОР С ПОДДЕРЖКОЙ AVX-AVX2 ИНСТРУКЦИЙ. ЕСЛИ ВЫЛАЗИТ ОШИБКА - ИСПОЛЬЗУЙТЕ ПАТЧ ДЛЯ TENSORFLOW."""
        from deepface import DeepFace
        from base64 import b64encode
        
        faces: list[FaceInfo] = []
        
        analysis = DeepFace.analyze(b64encode(photo).decode(), ['emotion', 'age', 'gender', 'race'])
        
        for face in tqdm(analysis, 'Обрабатываем лица..', total=len(analysis), ncols=70):
            faces.append(face)
        
        if faces:
            return faces
    def rtmp_livestream(self, video: bytes, server: RTMPServerInit, ffmpeg_dir: str = 'ffmpeg', resolution: str = '1280x720', bitrate: str = '3000k', fps: str = '30'):
        """Стримит видео из байтов на RTMPS-сервер с FFmpeg под CPU. Требует FFmpeg."""
        from tqdm import tqdm as tqdm_sync
        try:
            # Команда для FFmpeg
            command = [
                ffmpeg_dir,
                '-re',  # Реальное время
                '-f', 'mp4',  # Формат входных данных
                '-i', '-',  # Вход из пайпа
                '-c:v', 'libx264',  # Кодек под CPU
                '-preset', 'ultrafast',  # Минимальная задержка
                '-tune', 'zerolatency',  # Для стриминга
                '-b:v', bitrate,  # Битрейт
                '-s', resolution,  # Разрешение
                '-r', fps,  # FPS
                '-f', 'flv',  # Формат выхода
                f'{server.url}/{server.key}'  # RTMPS URL с логином/паролем
            ]
            
            # Прогресс-бар
            total_size = len(video)
            with tqdm_sync(total=total_size, unit='B', unit_scale=True, desc="Стриминг на RTMPS..") as pbar:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                video_buffer = io.BytesIO(video)
                
                # Отправка байтов в пайп
                chunk_size = 8192
                while True:
                    chunk = video_buffer.read(chunk_size)
                    if not chunk:
                        break
                    process.stdin.write(chunk)
                    pbar.update(len(chunk))
                
                process.stdin.close()
                process.wait()
                
                # Проверка ошибок
                stderr_output = process.stderr.read().decode('utf-8')
                if process.returncode != 0:
                    print(f"FFmpeg ошибка: {stderr_output}")
                    raise RuntimeError(f"FFmpeg завершился с ошибкой: {stderr_output}")
            
            print(f"Сигма-стрим завершён! 😎")
        except Exception as e:
            print(f"Ошибка стриминга: {e}")
            raise
    def cut_link(self, url: str, proxies: dict[str, str] = None) -> str:
        """Взаимодействие с API сервиса для сокращения ссылок `clck.ru`.\nurl: ссылка на сокращение.\nproxies: прокси, если нет, то они берутся с класса.\nВозвращает ссылку в `str`."""
        request = requests.get(f'https://clck.ru/--', params={"url":url}, headers=self.headers, proxies=proxies if proxies else self.proxies)
        if request.text != 'limited':
            return request.text
        else:
            time.sleep(2.5)
            request = requests.get(f'https://clck.ru/--', params={"url":url}, headers=self.headers, proxies=proxies if proxies else self.proxies)
            return request.text
    def detect_new_kworks(self, func, category: int = 11, pages: int = 1, delay: int = 300):
        """Привет! Эта функция - враппер для отслеживания новых предложений на бирже Kwork.\nЮЗАЙТЕ В КАЧЕСТВЕ ДЕКОРАТОРА."""
        def wrapper(*args, **kwargs):
            start_kworks = self.parse_kwork(category, pages)
            new = []
            
            for i in start_kworks:
                new.append(i.url)
                
            while True:
                new_kworks = self.parse_kwork(category, pages)
                for kwork in new_kworks:
                    if kwork.url in new:
                        pass
                    else:
                        new.append(kwork.url)
                        func(kwork)
                time.sleep(delay)
        return wrapper
    def download_tiktok_video(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None) -> dict:
        """Скачивает видео в указанную директорию. Возвращает информацию о видео.\nurl: ссылка на видео.\ndir: директория, куда сохранить видео.\nfilename: имя файла. По умолчанию, будет сгенерировано нами.\nyoutube_dl_parameters: мы сами настроили параметры yt-dlp. Знайте, что делаете."""
        if not os.path.exists(dir):
            os.mkdir(dir)
        
        if filename:
            ydl_opts = {
                'outtmpl': os.path.join(dir, f'{filename}.%(ext)s'),  # Шаблон имени файла
                'format': 'mp4',  # Формат видео
                'noplaylist': True, 
                'format': 'worst',
                'proxy':self.proxies.get('http'),
            }
        else:
            name_of_file = random.random()
            ydl_opts = {
                'outtmpl': os.path.join(dir, f'{name_of_file}.%(ext)s'),  # Шаблон имени файла
                'format': 'mp4',  # Формат видео
                'noplaylist': True, 
                'format': 'worst',
                'proxy':self.proxies.get('http'),
            }
        if youtube_dl_parameters:
            with YoutubeDL(youtube_dl_parameters) as downloader:
                info = downloader.extract_info(url, False)
                downloader.download([url])
                return info
        else:
            with YoutubeDL(ydl_opts) as downloader:
                info = downloader.extract_info(url, False)
                downloader.download([url])
                return info
    def twitch_clips_download(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None) -> dict:
        """Функция для скачивания клипов с Twitch!\nurl: ссылка на твитч-клип.\ndir: куда сохранить?\nfilename: имя файла при скачивании.\nyoutube_dl_parameters: параметры YoutubeDL."""
        if not url.startswith(('https://m.twitch.tv/twitch/clip/', 'https://twitch.tv/twitch/clip/')):
            raise Exception('Брат! Ты неправильный формат ссылки указал.')
        else:
            if not os.path.exists(dir):
                os.mkdir(dir)
        
            if filename:
                ydl_opts = {
                    'outtmpl': os.path.join(dir, f'{filename}.%(ext)s'),  # Шаблон имени файла
                    'format': 'mp4',  # Формат видео
                    'noplaylist': True, 
                    'format': 'worst',
                    'proxy':self.proxies.get('http'),
                }
            else:
                name_of_file = random.random()
                ydl_opts = {
                    'outtmpl': os.path.join(dir, f'{name_of_file}.%(ext)s'),  # Шаблон имени файла
                    'format': 'mp4',  # Формат видео
                    'noplaylist': True, 
                    'format': 'worst',
                    'proxy':self.proxies.get('http'),
                }
            if youtube_dl_parameters:
                with YoutubeDL(youtube_dl_parameters) as downloader:
                    info = downloader.extract_info(url, False)
                    downloader.download([url])
                    return info
            else:
                with YoutubeDL(ydl_opts) as downloader:
                    info = downloader.extract_info(url, False)
                    downloader.download([url])
                    return info
    def vk_rutube_dzen_video_download(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None):
        """Функция по скачиванию видео ВК, Рутуба и Дзена!\nПараметры, как везде. Разберетесь."""
        if not url.startswith(('https://rutube.ru/video/', 'https://vk.com/vkvideo', 'https://dzen.ru/video/watch/', 'https://zen.yandex.ru/video/watch/')):
            raise Exception('Брат! Ты неправильный формат ссылки указал.')
        else:
            if not os.path.exists(dir):
                os.mkdir(dir)
        
            if filename:
                ydl_opts = {
                    'outtmpl': os.path.join(dir, f'{filename}.%(ext)s'),  # Шаблон имени файла
                    'format': 'mp4',  # Формат видео
                    'noplaylist': True, 
                    'format': 'worst',
                    'proxy':self.proxies.get('http'),
                }
            else:
                name_of_file = random.random()
                ydl_opts = {
                    'outtmpl': os.path.join(dir, f'{name_of_file}.%(ext)s'),  # Шаблон имени файла
                    'format': 'mp4',  # Формат видео
                    'noplaylist': True, 
                    'format': 'worst',
                    'proxy':self.proxies.get('http'),
                }
            if youtube_dl_parameters:
                with YoutubeDL(youtube_dl_parameters) as downloader:
                    info = downloader.extract_info(url, False)
                    downloader.download([url])
                    return info
            else:
                with YoutubeDL(ydl_opts) as downloader:
                    info = downloader.extract_info(url, False)
                    downloader.download([url])
                    return info
    def unpack_zip_jar_apk_others(self, file, dir: str, delete_original: bool = False):
        """"Функция для распаковки любых архивов. Даже Jar (Java Archive) и APK.\nfile: файл в io.BytesIO(), или директория к нему.\ndir: место для распаковки.\ndelete_original: удалять оригинальный файл? (Работает только с указанием директории в file)\nФункция возвращает None."""
        from zipfile import ZipFile

        if not os.path.exists(dir):
            os.mkdir(dir)

        zipfile = ZipFile(file, 'r')
        zipfile.extractall(dir)
        zipfile.close() 
        if delete_original:
            if isinstance(file, str):
                try:
                    os.remove(file)
                except:
                    pass
            else:
                pass
    def photo_upscale(self, image: bytes, factor: int = 4) -> bytes:
        """Функция для простого апскейла фото через Pillow (бикубический метод).\nimage: фото в bytes.\nfactor: во сколько раз увеличивать фото (width и height).\nВозвращает bytes."""
        img = Image.open(io.BytesIO(image))
        original_width, original_height = img.size

        new_width = int(original_width * factor)
        new_height = int(original_height * factor)

        upscaled = img.resize((new_width, new_height), Image.Resampling.BICUBIC)
        new = io.BytesIO()
        upscaled.save(new, 'JPEG')
        return new.getvalue()
    def generate_video_with_subtitles(self, path, output_path: str, output_name: str = None, font: str = None, language: str = 'ru'):
        """Видео для генерации этого же видео, но с субтитрами.\npath: прямой путь к исходному файлу.\noutput_path: куда сохранить новый файл.\noutput_name: будет автоматически создано, если не указано.\nfont: путь к шрифту, если есть.\nlanguage: исходный язык в видео.\n\nПОДДЕРЖИВАЕТСЯ НАТИВНО ТОЛЬКО .mp4!"""
        if not self.whisper:
            raise Exception("Укажи whisper_model при инициализации класса.")
        else:
            video = VideoFileClip(path)
            random_ = random.random()
            video.audio.write_audiofile(os.path.join(path, f'{random_}.wav'))
            audio_data, sample_rate = librosa.load(os.path.join(path, f'{random_}.wav'), sr=16000)  # Whisper ожидает частоту 
            result = self.whisper.transcribe(audio_data, word_timestamps=True, language=language)
            clips = [video]
            for segment in result["segments"]:
                for word_info in segment.get("words", []):
                    word = word_info["word"]
                    start_time = word_info["start"]
                    end_time = word_info["end"]

                    subtitle = TextClip(
                        text=word,
                        font_size=24,
                        color='white',
                        bg_color='black',
                        font=font,
                        size=(video.w, 100),
                        text_align='center'
                    ).with_start(start_time).with_end(end_time).with_position(('center', video.h - 120))

                    clips.append(subtitle)
            final_video = CompositeVideoClip(clips)
            os.remove(os.path.join(path, f'{random_}.wav'))
            if output_name:
                final_video.write_videofile(os.path.join(output_path, f'{output_name}.mp4'), codec="libx264", audio_codec="aac")
            else:
                final_video.write_videofile(os.path.join(output_path, f'{random_}.mp4'), codec="libx264", audio_codec="aac")
    def change_format_of_photo(self, image: bytes, format_: ImageFormat):
        """Функция для преобразования изображений в нужный формат.\nimage: изображения в bytes.\nformat_: формат изображения, указанный конкретным классом."""
        PIL_FORMATS_MAP = {
            '.jpg': 'JPEG', '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.bmp': 'BMP',
            '.gif': 'GIF',
            '.webp': 'WEBP'
        }
        selected_format_pil = PIL_FORMATS_MAP.get(format_.format_.lower())
        img = Image.open(io.BytesIO(image))

        # --- Логика Конвертации Изображения ---
        output_buffer = io.BytesIO()

        # Pillow может требовать преобразования цветового пространства для некоторых форматов
        if selected_format_pil == 'JPEG' and img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        # Для GIF, если нужно сохранить анимацию, потребуется более сложная обработка.
        # Здесь мы просто сохраним первый кадр или как обычное изображение.
        elif selected_format_pil == 'GIF':
            # Простая обработка GIF: сохранение первого кадра
            img.save(output_buffer, format=selected_format_pil)
        else:
            img.save(output_buffer, format=selected_format_pil)

        output_buffer.seek(0) # Перематываем буфер в начало
        converted_image_data = output_buffer.read()
        return converted_image_data
    def get_vk_user(self, user_id: str) -> Optional[VkUser]:
        """Получает объект пользователя VkUser по user_id или @username."""
        if not self.token_of_vk:
            raise Exception("Дружок! Токен укажи от своего VK ID.")
        fields = (
            "bdate,sex,city,country,home_town,photo_max_orig,"
            "followers_count,relation,contacts,domain,site,status,about,"
            "education,schools,universities,occupation,career,interests,"
            "activities,music,movies,tv,books,games,quotes,personal,connections"
        )
        try:
            session = vk_api.VkApi(token=self.token_of_vk)
            api = session.get_api()
            result = api.users.get(user_ids=user_id, fields=fields)
            if result:
                return VkUser(result[0])
        except Exception as e:
            print(f"Ошибка при получении пользователя {user_id}: {e}")
        return None

class CodeEditor:
    """Редактор кода, написанный на Python с графическим интерфейсом и подсветкой ключевых слов при написании кода на Python.\nmaster: объект класса "Tk", встроенной библиотеки tkinter."""
    def __init__(self, master: tk.Tk):
        """Инициализация."""
        self.master = master
        master.title("Редактор кода")
        master.geometry("800x600")
        KEYWORD_COLOR = "#FF7F50"  # Coral
        STRING_COLOR = "#98FB98"   # PaleGreen
        COMMENT_COLOR = "#808080"  # Gray
        FUNCTION_COLOR = "#4682B4" # SteelBlue
        NUMBER_COLOR = "#BDB76B"   # DarkKhaki
        BUILTIN_COLOR = "#FFA07A"  # LightSalmon

        self.filename = None  # Current file

        # --- Widgets ---
        self.text_area = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, undo=True, font=("Consolas", 12)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # --- Menu ---
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="новенький", command=self.new_file)
        self.file_menu.add_command(label="открыть", command=self.open_file)
        self.file_menu.add_command(label="сохранить", command=self.save_file)
        self.file_menu.add_command(label="Сохранить в директории...", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Назад", command=master.quit)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Отменить", command=self.text_area.edit_undo)
        self.edit_menu.add_command(label="Вперёд", command=self.text_area.edit_redo)
        self.menu_bar.add_cascade(label="Изменить", menu=self.edit_menu)

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="о проге", command=self.show_about)
        self.menu_bar.add_cascade(label="помоги, плиз", menu=self.help_menu)


        self.text_area.bind("<KeyRelease>", self.highlight_syntax)  # Подсветка при вводе

        # --- Syntax Highlighting Tags ---
        self.text_area.tag_configure("keyword", foreground=KEYWORD_COLOR)
        self.text_area.tag_configure("string", foreground=STRING_COLOR)
        self.text_area.tag_configure("comment", foreground=COMMENT_COLOR)
        self.text_area.tag_configure("function", foreground=FUNCTION_COLOR)
        self.text_area.tag_configure("number", foreground=NUMBER_COLOR)
        self.text_area.tag_configure("builtin", foreground=BUILTIN_COLOR)

        # --- Keywords ---
        self.keywords = ["def", "class", "if", "else", "elif", "for", "while", "return", "import", "from", "try", "except", "finally", "with", "as", "assert", "break", "continue", "del", "global", "nonlocal", "in", "is", "lambda", "pass", "raise", "yield"]
        self.builtins = ["print", "len", "range", "str", "int", "float", "bool", "list", "tuple", "dict", "set", "open", "file", "input", "exit", "help", "dir", "type", "object"]
    def new_file(self):
        """Создает новый файл."""
        self.text_area.delete("1.0", tk.END)  # Clear the text area
        self.filename = None  # Reset filename
        self.master.title("Редактор кода - New File")

    def open_file(self):
        """Открыть файл."""
        filepath = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*"), ("Text Files", "*.txt"), ("Python Files", "*.py"), ("C++ Files", "*.cpp")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding='UTF-8') as file:
                    content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.filename = filepath
                self.master.title(f"Редактор кода - {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("ОШИБОЧКА", f"вот это:\n{e}")

    def save_file(self):
        """Сохранить файл."""
        if self.filename:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(self.filename, "w") as file:
                    file.write(content)
                messagebox.showinfo("успех", "файл сохранен.")
            except Exception as e:
                messagebox.showerror("ошибочка", f"лееее:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Сохранить файл как..."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Text Files", "*.txt"), ("Python Files", "*.py"), ("C++ Files", "*.cpp")]
        )
        if filepath:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(filepath, "w") as file:
                    file.write(content)
                self.filename = filepath
                self.master.title(f"Редактор кода - {os.path.basename(filepath)}")
                messagebox.showinfo("урыыы", "файл типо сохранен.")
            except Exception as e:
                messagebox.showerror("ошибОЧКА", f"посмотри сам:\n{e}")

    def show_about(self):
        """О программе."""
        messagebox.showinfo(
            "О проге", "Редактор кода от Флореста. Сделано с любовью."
        )
    def highlight_syntax(self, event=None):
        """Подсвечивает синтаксис Python."""
        # Удаляем все старые теги
        for tag in self.text_area.tag_names():
            self.text_area.tag_remove(tag, "1.0", tk.END)

        text = self.text_area.get("1.0", tk.END)

        # Подсветка комментариев
        for match in re.finditer(r"#.*", text):
            start = "1.0 + %dc" % match.start()
            end = "1.0 + %dc" % match.end()
            self.text_area.tag_add("comment", start, end)

        # Подсветка строк
        for match in re.finditer(r"(\".*\")|(\'.*\')", text):
            start = "1.0 + %dc" % match.start()
            end = "1.0 + %dc" % match.end()
            self.text_area.tag_add("string", start, end)

        # Подсветка ключевых слов
        for word in self.keywords:
            pattern = r'\b' + word + r'\b'  # Границы слова
            for match in re.finditer(pattern, text):
                start = "1.0 + %dc" % match.start()
                end = "1.0 + %dc" % match.end()
                self.text_area.tag_add("keyword", start, end)

        # Подсветка встроенных функций
        for word in self.builtins:
            pattern = r'\b' + word + r'\b'  # Границы слова
            for match in re.finditer(pattern, text):
                start = "1.0 + %dc" % match.start()
                end = "1.0 + %dc" % match.end()
                self.text_area.tag_add("builtin", start, end)

        # Подсветка чисел
        for match in re.finditer(r'\b\d+\b', text):
            start = "1.0 + %dc" % match.start()
            end = "1.0 + %dc" % match.end()
            self.text_area.tag_add("number", start, end)

        # Подсветка функций (очень упрощенно)
        for match in re.finditer(r'def\s+(\w+)\s*\(', text):
            start = "1.0 + %dc" % match.start(1) # Начало имени функции
            end = "1.0 + %dc" % match.end(1) # Конец имени функции
            self.text_area.tag_add("function", start, end)
            
import asyncio
import io
import random
import string
import re
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiohttp
import aiofiles
import gtts
import qrcode
from PIL import Image, ImageOps, ImageDraw, ImageFont
import speech_recognition as sr
from pygame import mixer
import time
from colorama import Fore
import vk_api
from vkpymusic import Service, TokenReceiver
import faker as faker_
import subprocess
import os
from bs4 import BeautifulSoup
import aiosmtplib

class AsyncFunctionsObject:
    def __init__(self, proxies: dict = {}, html_headers: dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36', 'Accept-Language': 'ru-RU'}, google_api_key: str = "", gigachat_key: str = "", gigachat_id: str = "", username_mail: str = "", mail_passwd: str = "", speech_to_text_key: str = None, vk_token: str = None, rcon_ip: str = None, rcon_port: int = None, rcon_password: str = None):
        """Initialize the FunctionsObject with configuration parameters."""
        print(f'Объект класса был успешно запущен.')
        self.proxies = proxies
        self.headers = html_headers
        self.google_key = google_api_key
        self.gigachat_key = gigachat_key
        self.client_id_gigachat = gigachat_id
        self.username_mail = username_mail
        self.mail_passwd = mail_passwd
        self.speech_to_text_key = speech_to_text_key
        self.token_of_vk = vk_token
        self.client_for_gpt = AsyncClient()
        if all([rcon_ip, rcon_password, rcon_port]):
            from aiomcrcon import Client
            self.rcon_server = Client(rcon_ip, rcon_port, rcon_password)
            print(f'RCON сервер инициализирован!')
        else:
            self.rcon_server = None
        self.sync_functions_object = FunctionsObject(proxies, html_headers, google_api_key, gigachat_key, gigachat_id, username_mail, mail_passwd, speech_to_text_key, vk_token, rcon_ip, rcon_port, rcon_password)
    async def generate_image(self, prompt: str) -> bytes:
        """Generate an image using GigaChat API."""
        if not self.gigachat_key or not self.client_id_gigachat:
            return "Нужно указать параметр `gigachat_key` и `gigachat_id` в настройках класса для работы с этой функцией."

        async with aiohttp.ClientSession() as session:
            # Get access token
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            payload = {'scope': 'GIGACHAT_API_PERS'}
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': f'{self.client_id_gigachat}',
                'Authorization': f'Basic {self.gigachat_key}'
            }
            async with session.post(url, headers=headers, data=payload, ssl=False, proxy=self.proxies.get('https')) as response:
                access_token = (await response.json())['access_token']

            # Generate image
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            data = {
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": "Glory to Florest."},
                    {"role": "user", "content": prompt}
                ],
                "function_call": "auto"
            }
            async with session.post(
                'https://gigachat.devices.sberbank.ru/api/v1/chat/completions',
                headers=headers,
                json=data,
                ssl=False,
                proxy=self.proxies.get('https')
            ) as response:
                json_data = await response.json()
                patterns = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
                matches = re.search(patterns, json_data['choices'][0]['message']['content'])
                if not matches:
                    return f"Нельзя нарисовать что-либо по данному запросу. Причина: {json_data['choices'][0]['message']['content']}"
                else:
                    async with session.get(
                        f"https://gigachat.devices.sberbank.ru/api/v1/files/{matches.group()}/content",
                        headers={'Accept': 'application/jpg', "Authorization": f"Bearer {access_token}"},
                        ssl=False,
                        proxy=self.proxies.get('https')
                    ) as req_img:
                        return await req_img.read()

    async def ai(self, prompt: str, is_voice: bool = False):
        """Interact with GigaChat API, optionally generating voice output."""
        if not self.gigachat_key or not self.client_id_gigachat:
            return "Нужно указать параметр `gigachat_key` и `gigachat_id` в настройках класса для работы с этой функцией."

        async with aiohttp.ClientSession() as session:
            # Get access token
            url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            payload = {'scope': 'GIGACHAT_API_PERS'}
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': f'{self.client_id_gigachat}',
                'Authorization': f'Basic {self.gigachat_key}'
            }
            async with session.post(url, headers=headers, data=payload, ssl=False, proxy=self.proxies.get('https')) as response:
                access_token = (await response.json())['access_token']

            # Send prompt
            url1 = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            payload1 = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "repetition_penalty": 1
            }
            headers1 = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            async with session.post(url1, headers=headers1, json=payload1, ssl=False, proxy=self.proxies.get('https')) as response1:
                result = await response1.json()
                if not is_voice:
                    return result
                else:
                    buffer = io.BytesIO()
                    gtts.gTTS(result['choices'][0]['message']['content'], lang='ru', lang_check=False).write_to_fp(buffer)
                    return buffer.getvalue()

    async def deanon(self, ip: str) -> list:
        """Get geolocation information for an IP address."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://ip-api.com/json/{ip}?lang=ru', headers=self.headers, proxy=self.proxies.get('http')) as response:
                data = await response.json()
                return [f'{key.title()}: {value}' for key, value in data.items()]

    async def download_video(self, url: str):
        """Download a YouTube video."""
        return await asyncio.to_thread(self.sync_functions_object.download_video, url)

    async def search_videos(self, query: str):
        """Search and download a YouTube video by query."""
        return await asyncio.to_thread(self.sync_functions_object.search_videos, query)

    async def create_demotivator(self, top_text: str, bottom_text: str, photo: bytes, font: str):
        """Create a demotivator image."""
        image = io.BytesIO(photo)
        img = Image.new('RGB', (1280, 1024), color='black')
        img_border = Image.new('RGB', (1060, 720), color='#000000')
        border = ImageOps.expand(img_border, border=2, fill='#ffffff')
        user_img = Image.open(image).convert("RGBA").resize((1050, 710))
        (width, height) = user_img.size
        img.paste(border, (111, 96))
        img.paste(user_img, (118, 103))
        drawer = ImageDraw.Draw(img)
        font_1 = ImageFont.truetype(font=font, size=80, encoding='UTF-8')
        text_width = font_1.getlength(top_text)
        top_size = 80
        while text_width >= (width + 250) - 20:
            top_size -= 1
            font_1 = ImageFont.truetype(font=font, size=top_size, encoding='UTF-8')
            text_width = font_1.getlength(top_text)
        font_2 = ImageFont.truetype(font=font, size=60, encoding='UTF-8')
        text_width = font_2.getlength(bottom_text)
        bottom_size = 60
        while text_width >= (width + 250) - 20:
            bottom_size -= 1
            font_2 = ImageFont.truetype(font=font, size=bottom_size, encoding='UTF-8')
            text_width = font_2.getlength(bottom_text)
        size_1 = drawer.textlength(top_text, font=font_1)
        size_2 = drawer.textlength(bottom_text, font=font_2)
        drawer.text(((1280 - size_1) / 2, 840), top_text, fill='white', font=font_1)
        drawer.text(((1280 - size_2) / 2, 930), bottom_text, fill='white', font=font_2)
        result_here = io.BytesIO()
        img.save(result_here, 'JPEG')
        del drawer
        return result_here.getvalue()

    async def photo_make_black(self, photo: bytes):
        """Convert a photo to black and white."""
        your_photo = io.BytesIO(photo)
        image = Image.open(your_photo)
        new_image = image.convert('L')
        buffer = io.BytesIO()
        new_image.save(buffer, 'JPEG')
        return buffer.getvalue()

    async def check_weather(self, city):
        """Check weather for a city or coordinates."""
        async with aiohttp.ClientSession() as session:
            if isinstance(city, str):
                try:
                    async with session.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city}', headers=self.headers, proxy=self.proxies.get('https')) as response:
                        d = await response.json()
                        lot = d["results"][0]["latitude"]
                        lat = d['results'][0]['longitude']
                    async with session.get(f'https://api.open-meteo.com/v1/forecast?latitude={lot}&longitude={lat}&current_weather=true', headers=self.headers, proxy=self.proxies.get('https')) as req:
                        if req.status != 200:
                            return None
                        data = await req.json()
                        temperature = data['current_weather']['temperature']
                        title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                        weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                        wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                        time1 = data['current_weather']['time']
                        wind = data['current_weather']['windspeed']
                        return {'temp': temperature, 'weather': weather, 'weather_code': data['current_weather']['weathercode'], 'wind_direction': wind_dir, 'time_of_data': time1, 'wind_speed': wind}
                except:
                    return None
            elif isinstance(city, dict):
                try:
                    lat = city["lat"]
                    lon = city["lon"]
                    async with session.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true', headers=self.headers, proxy=self.proxies.get('https')) as req:
                        data = await req.json()
                        temperature = data['current_weather']['temperature']
                        title = {0: "Ясно", 1: "Частично облачно", 3: "Облачно", 61: "Дождь"}
                        weather = title.get(data['current_weather']['weathercode'], 'Неизвестно')
                        wind_dir = 'Север' if 0 <= (d := data['current_weather']['winddirection']) < 45 or 315 <= d <= 360 else 'Восток' if 45 <= d < 135 else 'Юг' if 135 <= d < 225 else 'Запад'
                        time1 = data['current_weather']['time']
                        wind = data['current_weather']['windspeed']
                        return {'temp': temperature, 'weather': weather, 'weather_code': data['current_weather']['weathercode'], 'wind_direction': wind_dir, 'time_of_data': time1, 'wind_speed': wind}
                except KeyError:
                    return f'Нужно составить словарь, согласно образцу, указанного в описании функции.'
                except:
                    return None
            else:
                return 'Поддерживаемые типы данных: `str` для названия города и `dict` для координатов.'

    async def create_qr(self, content: str):
        """Create a QR code."""
        buffer = io.BytesIO()
        qr = qrcode.make(content)
        qr.save(buffer, scale=10)
        return buffer.getvalue()

    async def get_charts(self):
        """Get Yandex Music charts."""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fi;q=0.6,nb;q=0.5,is;q=0.4,pt;q=0.3,ro;q=0.2,it;q=0.1,de;q=0.1',
                'Connection': 'keep-alive',
                'Referer': 'https://music.yandex.ru/chart',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'X-Current-UID': '403036463',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Retpath-Y': 'https://music.yandex.ru/chart',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
            }
            params = {
                'what': 'chart',
                'lang': 'ru',
                'external-domain': 'music.yandex.ru',
                'overembed': 'false',
                'ncrnd': '0.23800355071570123',
            }
            async with session.get('https://music.yandex.ru/handlers/main.jsx', params=params, headers=headers, proxy=self.proxies.get('https')) as response:
                chart = (await response.json())['chartPositions']
                result = []
                for track in chart[:10]:
                    position = track['track']['chart']['position']
                    title = track['track']['title']
                    author = track['track']['artists'][0]['name']
                    result.append(f"№{position}: {author} - {title}")
                return f'Чарты Яндекс Музыки на данный момент🔥\n🥇{result[0]}\n🥈{result[1]}\n🥉{result[2]}\n{result[3]}\n{result[4]}\n{result[5]}\n{result[6]}\n{result[7]}\n{result[8]}\n{result[9]}'

    async def generate_password(self, symbols: int = 15):
        """Generate a random password."""
        symbols_ascii = list(string.ascii_letters + string.digits)
        random.shuffle(symbols_ascii)
        return ''.join(symbols_ascii[:symbols])

    async def text_to_speech(self, text: str, lang: str = 'ru'):
        """Convert text to speech."""
        buffer = io.BytesIO()
        engine = gtts.gTTS(text, lang=lang)
        engine.write_to_fp(buffer)
        return buffer.getvalue()

    async def information_about_yt_channel(self, url: str):
        """Узнать информацию о YouTube канале на Python.\nurl: ссылка на канал."""
        if not self.google_key:
            return 'Для использования данной функции нужно указать параметр `google_key` в конструктор класса.'
        else:
            import httpx
            
            if '/channel/' in url:
                channel_id = url.split('/channel/')[-1].split('?')[0]
                params = {
                    "part": "snippet,statistics",
                    "id": channel_id,
                    "key": self.google_key
                }
            else:
                username = url.split('/@')[-1].split('?')[0]
                params = {
                    "part": "snippet,statistics",
                    "forHandle": f"@{username}",
                    "key": self.google_key
                }

            # Создаем асинхронный клиент и выполняем запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/youtube/v3/channels',
                    params=params,
                    headers=self.headers,
                    proxies=self.proxies
                )
                
            return response.json()

    async def crypto_price(self, crypto: str, currency: str = 'rub'):
        """Get cryptocurrency price."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price', params={"ids": crypto, 'vs_currencies': currency}, headers=self.headers, proxy=self.proxies.get('https')) as response:
                r = await response.json()
                if not r:
                    return "Неправильная валюта, или криптовалюта."
                try:
                    return r[crypto][currency]
                except:
                    return "Произошла ошибка. Возможно, были преодолены лимиты API."

    async def password_check(self, nickname: str) -> int:
        """Check for password leaks by nickname."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.proxynova.com/comb?query={nickname}&start=0&limit=15', headers=self.headers, proxy=self.proxies.get('https')) as req:
                if req.status == 200:
                    return (await req.json())['count']
                return 0

    async def generate_nitro(self, count: int):
        """Generate Discord Nitro codes."""
        results = []
        for _ in range(count):
            characters = string.ascii_uppercase + string.digits
            random_code = ''.join(random.choice(characters) for _ in range(15))
            formatted_code = '-'.join(random_code[i:i+4] for i in range(0, 15, 4))
            results.append(formatted_code)
        return results

    async def fake_human(self):
        """Generate fake Russian citizen data."""
        faker = faker_.Faker('ru-RU')
        today = date.today()
        year_f, month_f, day_f = map(int, str(faker.date_of_birth(minimum_age=25, maximum_age=50)).split("-"))
        age_t = today.year - year_f - ((today.month, today.day) < (month_f, day_f))
        return {
            "name": faker.name(),
            "age": age_t,
            "work_place": faker.company(),
            "work_class": faker.job().lower(),
            "address": f"Российская Федерация, {faker.address()}",
            "postal_code": faker.address()[-6:],
            'telephone_number': faker.phone_number(),
            "useragent": faker.user_agent(),
            "number_card": faker.credit_card_number(),
            "provider_of_card": faker.credit_card_provider(),
            "expire_card": faker.credit_card_expire(),
            "inn": faker.businesses_inn(),
            "orgn": faker.businesses_ogrn()
        }

    async def real_info_of_photo(self, photo: bytes):
        """Extract location data from photo metadata."""
        with Image.open(io.BytesIO(photo)) as img:
            metadata = img._getexif()
            if not metadata or not metadata.get(34853):
                return None
            gps_info = metadata[34853]
            lat = gps_info[2]
            lon = gps_info[4]
            lat_ref = gps_info[3]
            latitude = (lat[0] + lat[1] / 60.0 + lat[2] / 3600.0)
            longitude = (lon[0] + lon[1] / 60.0 + lon[2] / 3600.0)
            datetime_original = metadata.get(36867)
            async with aiohttp.ClientSession() as session:
                try:
                    if lat_ref != 'E':
                        latitude = -latitude
                    async with session.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers=self.headers, proxy=self.proxies.get('https')) as response:
                        json_data = await response.json()
                        return {
                            "country": json_data["address"]["country"],
                            "region": json_data["address"]["state"],
                            "district": json_data["address"]["district"],
                            'city': json_data["address"]["city"],
                            "full_address": json_data["display_name"],
                            'postcode': json_data["address"]["postcode"],
                            'datetime': datetime_original
                        }
                except:
                    if lat_ref != 'E':
                        latitude = -latitude
                    longitude = -longitude
                    async with session.get(f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json", headers=self.headers, proxy=self.proxies.get('https')) as response:
                        json_data = await response.json()
                        return {
                            "country": json_data["address"]["country"],
                            "region": json_data["address"]["state"],
                            "district": json_data["address"]["district"],
                            'city': json_data["address"]["city"],
                            "full_address": json_data["display_name"],
                            'postcode': json_data["address"]["postcode"],
                            'datetime': datetime_original
                        }

    async def bmi(self, weight: float, height: float):
        """Calculate BMI."""
        if weight <= 0 or height <= 0:
            return None
        bmi = weight / (height ** 2)
        if bmi < 18.5:
            return {"bmi": f'{bmi:.2f}', "status": "Недостаточный вес"}
        elif 18.5 <= bmi < 25:
            return {"bmi": f'{bmi:.2f}', "status": "Нормальный вес"}
        elif 25 <= bmi < 30:
            return {"bmi": f'{bmi:.2f}', "status": "Избыточный вес"}
        else:
            return {"bmi": f'{bmi:.2f}', "status": "Ожирение"}

    async def link_on_user(self, id: str):
        """Generate Telegram user link by ID."""
        if len(id) != 10:
            return {'status': f'Пользовательский ID должен быть ровно 10 символов.', 'url': None}
        try:
            return {"status": "Успех!", "url": f"tg://openmessage?user_id={int(id)}"}
        except:
            return {"status": f'Неверный формат ID.', 'url': None}

    async def send_mail(self, subject: str, body: str, recipient: str, service: str = 'smtp.mail.ru', service_port: int = 465):
        """Send an email."""
        if not self.username_mail or not self.mail_passwd:
            return "Укажите параметр username_mail и mail_passwd в настройках класса."
        message = MIMEMultipart()
        message["From"] = self.username_mail
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", 'utf-8'))
        async with aiosmtplib.SMTP(hostname=service, port=service_port, use_tls=True) as server:
            await server.login(self.username_mail, self.mail_passwd)
            await server.sendmail(self.username_mail, recipient, message.as_string())

    async def parsing_site(self, url: str):
        """Parse a website's HTML."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, proxy=self.proxies.get('https')) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
            except:
                return None

    async def google_photo_parsing(self, query: str):
        """Parse Google Images for photo links."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://www.google.com/search?q={query}&tbm=isch&imglq=1&isz=l&safe=unactive', headers=self.headers, proxy=self.proxies.get('https')) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                tags = soup.find_all('img', {'src': True})
                return [tag['src'] for tag in tags if 'https://' in tag['src']]

    async def speech_to_text(self, file, language: str = 'ru-RU') -> str:
        """Convert speech to text."""
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            audio = r.record(source)
        try:
            text = await asyncio.to_thread(r.recognize_google, audio, language=language)
            return text
        except sr.UnknownValueError:
            return 'Ошибка распознавания текста.'
        except:
            return 'Неизвестная ошибка. Также могут быть проблемы с подключением.'

    async def email_mass_send(self, receivers: list, title: str, body: str, service: str = 'smtp.mail.ru', service_port: int = 465):
        """Send mass emails."""
        if not self.username_mail or not self.mail_passwd:
            return "Укажите параметр username_mail и mail_passwd в настройках класса."
        async with aiosmtplib.SMTP(hostname=service, port=service_port, use_tls=True) as server:
            await server.login(self.username_mail, self.mail_passwd)
            for email in receivers:
                message = MIMEMultipart()
                message["From"] = self.username_mail
                message["To"] = email
                message["Subject"] = title
                message.attach(MIMEText(body, "plain", 'utf-8'))
                await server.sendmail(self.username_mail, email, message.as_string())

    async def alarm_clock(self, time_to_ring: str, sound):
        """Set an alarm clock."""
        from os import environ
        environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        mixer.init()
        alarm_time = time.strptime(time_to_ring, "%H:%M:%S")
        data = {'hour': alarm_time.tm_hour, 'minutes': alarm_time.tm_min, 'seconds': alarm_time.tm_sec}
        print(f'{Fore.GREEN}Будильник успешно запущен на {Fore.BLUE}{time_to_ring}.')
        while True:
            current_time = time.localtime()
            hour_ = current_time.tm_hour
            minutes_ = current_time.tm_min
            seconds_ = current_time.tm_sec
            if {'hour': hour_, 'minutes': minutes_, 'seconds': seconds_} == data:
                print(f'{Fore.RED}ВНИМАНИЕ!!! БУДИЛЬНИК АКТИВИРОВАН, ПРОСЫПАЙТЕСЬ!!!')
                mixer.Sound(sound).play(loops=-1)
                break
            await asyncio.sleep(1)

    async def cpp_compiler(self, filename: str, filename_output: str):
        """Compile C++ code."""
        process = await asyncio.create_subprocess_exec(
            'g++', filename, '-o', filename_output,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode == 0

    async def python_exe_compiler(self, path_to_py: str, path_output: str, flags: str = None):
        """Compile Python to executable."""
        os.chdir(path_output)
        cmd = f'pyinstaller --distpath "{path_output}" {flags or ""} "{path_to_py}"'
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode == 0

    async def tracking_youtube_author(self, channel_url: str, token_of_bot: str, id: int):
        """Track new YouTube content and send notifications via Telegram bot."""
        from pytubefix import Channel
        try:
            channel = Channel(channel_url, proxies=self.proxies)
        except:
            return "Данного канала не существует."
        last_video = channel.videos[0].watch_url if channel.videos else None
        last_short = channel.shorts[0].watch_url if channel.shorts else None
        last_live = channel.live[0].watch_url if channel.live else None
        async with aiohttp.ClientSession() as session:
            while True:
                channel = Channel(channel_url, proxies=self.proxies)  # Refresh channel data
                if channel.videos and channel.videos[0].watch_url != last_video:
                    last_video = channel.videos[0].watch_url
                    text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.videos[0].title}\nСсылка: {channel.videos[0].watch_url}'
                    async with session.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxy=self.proxies.get('https')) as response:
                        await response.read()
                elif channel.shorts and channel.shorts[0].watch_url != last_short:
                    last_short = channel.shorts[0].watch_url
                    text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.shorts[0].title}\nСсылка: {channel.shorts[0].watch_url}'
                    async with session.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxy=self.proxies.get('https')) as response:
                        await response.read()
                elif channel.live and channel.live[0].watch_url != last_live:
                    last_live = channel.live[0].watch_url
                    text = f'Вышло новое видео у автора {channel.title}.\nНазвание: {channel.live[0].title}\nСсылка: {channel.live[0].watch_url}'
                    async with session.post(f'https://api.telegram.org/bot{token_of_bot}/sendMessage?chat_id={id}&text={text}', proxy=self.proxies.get('https')) as response:
                        await response.read()
                await asyncio.sleep(0.5)

    async def searching_musics_vk(self, query: str, count: int = 3):
        """Search for music on VK."""
        if not self.token_of_vk:
            return "Необходимо в настройках класса указать токен от Вашего аккаунта в VK."
        service = Service('KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)', self.token_of_vk)
        songs = await asyncio.to_thread(lambda: [track.to_dict() for track in service.search_songs_by_text(query, count)])
        return songs

    async def get_last_post(self, query: str):
        """Get the latest post from a VK public."""
        vk_session = vk_api.VkApi(token=self.token_of_vk)
        vk = vk_session.get_api()
        response = await asyncio.to_thread(vk.groups.search, q=query, type='group', count=1)
        if response['count'] > 0:
            response1 = await asyncio.to_thread(vk.wall.get, owner_id=-int(response['items'][0]['id']), count=1)
            try:
                post = response1['items'][0]
                text = post.get('text', 'Текст отсутствует')
                post_id = post['id']
                owner_id = post['owner_id']
                link = f"https://vk.com/wall{owner_id}_{post_id}"
                likes = post['likes']['count']
                views = post['views']['count']
                reposts = post['reposts']['count']
                return {"text": text, "post_id": post_id, "owner_id": owner_id, "link": link, 'views': views, 'reposts': reposts, 'likes': likes}
            except:
                return None
        return None
    async def image_text_recognition(self, img: bytes, lang: str = 'ru'):
        """Разбор текста на изображении, с помощью инструментов Google Cloud.\nimg: ваше изображение в bytes.\nlang: язык текста на изображении."""
        import base64
        if not self.google_key:
            return 'Для работы с данной функцией необходим Ваш Google Cloud API ключ. Проверьте, что в разделе Enabled APIs & Services есть Vision AI API.'
        else:
            image = base64.b64encode(img).decode("utf-8")

            # Тело запроса
            request_body = {
                "requests": [
                    {
                        "image": {
                            "content": image
                        },
                        "features": [
                            {
                                "type": "LABEL_DETECTION",
                                "maxResults": 10
                            }
                        ],
                        "imageContext": {
                            "languageHints": lang
                        }
                    }
                ]
            }

            # URL
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_key}"

            # Заголовки
            headers = {
                "Content-Type": "application/json"
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body, headers=headers, proxy=self.proxies.get('https') if self.proxies else None) as response:
                    return {"code": response.status, "answer": await response.json()}
    async def minecraft_server_info(self, ip: str, port: int = None, type_: str = 'java'):
        """Информация о Minecraft-сервере.\nip: ip/host сервера, или домен. Также можно написать ip:port.\nport: порт сервера, необязателен.\ntype: java, или bedrock."""
        if type_ in ['java', 'bedrock']:
            try:
                if type_ == 'java':
                    if not port:
                        server = JavaServer(ip)
                    else:
                        server = JavaServer(ip, port)
                    latency = await asyncio.to_thread(server.ping)
                    query = await asyncio.to_thread(server.query)
                    status = await asyncio.to_thread(server.status)
                    return {"latency":latency, 'query':{"query_motd":query.motd.to_ansi(), 'query_map':query.map, 'query_players_count':query.players.online, 'query_players_max':query.players.max, 'all_info':query.as_dict()}, 'status':{"query_motd":status.motd.to_ansi(), 'description':status.description, 'icon_of_server_base64':status.icon, 'query_players_count':query.players.online, 'query_players_max':query.players.max, 'version':status.version.name, 'all_info':status.as_dict()}}
                else:
                    if not port:
                        server = BedrockServer(ip)
                    else:
                        server = BedrockServer(ip, port)
                    status = await asyncio.to_thread(server.status)
                    return {"status":status.as_dict()}
            except:
                return
        else:
            return
                
    async def rcon_send(self, command: str):
        """Команда для отправки команды на сервер через RCON.\nТребует rcon_ip, rcon_port и rcon_password в настройках AsyncFunctionsObject.\ncommand: команда с аргументами. Пример: `say Привет!`\nВозвращает ответ от сервера."""
        if not self.rcon_server:
            return 'RCON сервер не инициализирован.\nПроверьте, указали ли Вы нужные параметры в настройках класса.'
        else:
            await self.rcon_server.connect()
            return await self.rcon_server.send_cmd(command)
        
    async def gpt_4o_req(self, prompt: str, max_tokens: int = 4096, proxy: str = None, image: bytes = None):
        """Фигня для доступа к GPT-4o-mini.\nprompt: сам запрос к нейронке.\nmax_tokens: количество символов в ответе. По умолчанию, 4096.\nproxy: прокси. По умолчанию, которые в FunctionsObject.\nimage: изображение в bytes, для распознавания объектов на фото."""
        if not image:
            if not proxy:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', OIVSCodeSer2(), proxy=self.proxies.get('http'), max_tokens=max_tokens)
            else:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', OIVSCodeSer2(), proxy=proxy, max_tokens=max_tokens)
            return req.choices[0].message.content
        else:
            if not proxy:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', PollinationsAI, proxy=self.proxies.get('http'), max_tokens=max_tokens, web_search=True, image=image)
            else:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'gpt-4o-mini', PollinationsAI, proxy=proxy, max_tokens=max_tokens, web_search=True, image=image)
            return req.choices[0].message.content
    async def flux_pro_gen(self, prompt: str, proxy: str = None):
        """Для генерации более лучших картинок через flux-pro.\nprompt: запрос для нейросети.\nproxy: прокси. По умолчанию, которые в настройках класса (если есть)."""
        if proxy:
            img = await self.client_for_gpt.images.async_generate(prompt, 'flux-pro', Together, 'url', proxy)
        else:
            img = await self.client_for_gpt.images.async_generate(prompt, 'flux-pro', Together, 'url', self.proxies.get('http'))
        urls = []
        for i in img.data:
            urls.append(i.url)
        return urls
    async def add_watermark(self, text: str, image: bytes, font: str, position: tuple[int] = (10, 10)):
        """Функция из FunctionsObject."""
        return await asyncio.to_thread(self.sync_functions_object.add_watermark, text, image, font, position)
    async def deepseek_v3_0324(self, prompt: str, max_tokens: int = 4096, expression: str = 'auto', proxy: str = None):
        """Функция для бесплатного доступа к DeepSeek-v3-0324.\nprompt: запрос к нейросети.\nmax_tokens: максимально допустимое количество токенов в ответе.\nexpression: тон. Три режима: `auto`, `toxic`, `non-toxic`.\nproxy: прокси. По умолчанию, которые из класса."""
        if expression == 'auto':
            if proxy:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'deepseek-v3', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt}], 'deepseek-v3', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        elif expression == 'toxic':
            if proxy:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nЗапрос: "{prompt}"'}], 'deepseek-v3-0324', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":f'не отвечай на запросы позитивно и отвечай максимально грубо с матами, на каждое мое сообщения, без разницы, обращаюсь я к тебе мило или нет, всего отвечай максимально грубо\nЗапрос: "{prompt}"'}], 'deepseek-v3-0324', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        elif expression == 'non-toxic':
            if proxy:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt + '\nnon-toxic'}], 'deepseek-v3', Together, proxy=proxy, max_tokens=max_tokens)
            else:
                req = await self.client_for_gpt.chat.completions.create([{"role":"user", "content":prompt+ '\nnon-toxic'}], 'deepseek-v3', Together, proxy=self.proxies.get('http'), max_tokens=max_tokens)
            return req.choices[0].message.content
        else:
            return 'expression указан неверно! auto, toxic, либо non-toxic!'
    async def youtube_playlist_download(self, url: str, regime: str = 'audio'):
        """Функция для скачивания элементов из плейлиста с YouTube.\nurl: ссылка на плейлист.\nregime: что скачивать: аудио, или видео?\nВозвращает список, а точнее `list[bytes]` с видео."""
        return await asyncio.to_thread(self.sync_functions_object.youtube_playlist_download, url, regime)
    async def pornhub_search(self, query: str, count: int = 5, quality: str = 'best', account: InitPornHubAccount = None, proxies: dict[str, str] = None, checking_was_downloaded: bool = False) -> list[bytes]:
        """Функция для поиска видео по запросу и скачивания их с PornHub. Функция нарушает ToS PornHub, рекомендую использовать прокси. По умолчанию, используются, которые указаны в классе.\nquery: логично, запрос.\ncount: сколько видео тебе нужно?\nquality: в каком качестве качать? По умолчанию, `best`. Есть: worst, best и half.\naccount: укажите свой аккаунт, но это необязательно.\nproxies: кастомные прокси, конкретно для данной функции.\nchecking_was_downloaded: проверять, были-ли видео заранее загружены."""
        return await asyncio.to_thread(self.sync_functions_object.pornhub_search, query, count, quality, account, proxies, checking_was_downloaded)
    async def pornhub_download_by_url(self, url: str, quality: str = 'best', account: InitPornHubAccount = None, proxies: dict[str, str] = None):
        """Функция для скачивания видео с PornHub по ссылке.\nurl: ссылка на видео.\nquality: качество.\naccount: ваш аккаунт на PornHub.\nproxies: кастомные прокси для этой функции, если есть."""
        return await asyncio.to_thread(self.sync_functions_object.pornhub_download_by_url, url, quality, account, proxies)
    async def pornhub_video_information(self, url: str, account: InitPornHubAccount = None, proxies: dict[str, str] = None) -> dict:
        """Данная функция выводит информацию о видео, без его скачивания.\nurl: ссылка на видео.\naccount: ваш аккаунт.\nproxies: кастомные прокси для этой функции."""
        return await asyncio.to_thread(self.sync_functions_object.pornhub_video_information, url, account, proxies)
    async def parse_kwork(self, category: int, pages: int = 1) -> list[KworkOffer]:
        """Функция для парсинга объявлений на kwork.\ncategory: категория для парсинга.\npages: сколько страниц спарсить? По умолчанию, 1.\nВозвращает список с кворками."""
        return await asyncio.to_thread(self.sync_functions_object.parse_kwork, category, pages)
    async def info_about_faces_on_photo(self, photo: bytes):
        """Данная функция выдает информацию о человеке на фотографии, или о людях.\nphoto: принимает фотографию в байтах.\nВозвращает `list[FaceInfo]` при наличии людей на фотографии.\nДЛЯ ДАННОЙ ФУНКЦИИ ЖЕЛАТЕЛЬНО ИМЕТЬ ПРОЦЕССОР С ПОДДЕРЖКОЙ AVX-AVX2 ИНСТРУКЦИЙ. ЕСЛИ ВЫЛАЗИТ ОШИБКА - ИСПОЛЬЗУЙТЕ ПАТЧ ДЛЯ TENSORFLOW."""
        return await asyncio.to_thread(self.sync_functions_object.info_about_faces_on_photo, photo)
    async def rtmp_livestream(self, video: bytes, server: RTMPServerInit, ffmpeg_dir: str = 'ffmpeg', resolution: str = '1280x720', bitrate: str = '3000k', fps: str = '30'):
        """Стримит видео из байтов на RTMPS-сервер с FFmpeg под CPU. Требует FFmpeg."""
        return await asyncio.to_thread(self.sync_functions_object.rtmp_livestream, video, server, ffmpeg_dir, resolution, bitrate, fps)
    async def cut_link(self, url: str, proxies: dict[str, str] = None) -> str:
        """Взаимодействие с API сервиса для сокращения ссылок `clck.ru`.\nurl: ссылка на сокращение.\nproxies: прокси, если нет, то они берутся с класса.\nВозвращает ссылку в `str`."""
        return await asyncio.to_thread(self.sync_functions_object.cut_link, url, proxies)
    def detect_new_kworks(self, func, category: int = 11, pages: int = 1, delay: int = 300):
        """Привет! Эта функция - враппер для отслеживания новых предложений на бирже Kwork.\nЮЗАЙТЕ В КАЧЕСТВЕ ДЕКОРАТОРА."""
        async def wrapper(*args, **kwargs):
            start_kworks = await self.parse_kwork(category, pages)
            new = []
            
            for i in start_kworks:
                new.append(i.url)
                
            while True:
                new_kworks = await self.parse_kwork(category, pages)
                for kwork in new_kworks:
                    if kwork.url in new:
                        pass
                    else:
                        new.append(kwork.url)
                        if asyncio.iscoroutinefunction(func):
                            await func(kwork)
                        else:
                            func(kwork)
                await asyncio.sleep(delay)
        return wrapper
    async def download_tiktok_video(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None) -> dict:
        """Скачивает видео в указанную директорию. Возвращает информацию о видео.\nurl: ссылка на видео.\ndir: директория, куда сохранить видео.\nfilename: имя файла. По умолчанию, будет сгенерировано нами.\nyoutube_dl_parameters: мы сами настроили параметры yt-dlp. Знайте, что делаете."""
        return await asyncio.to_thread(self.sync_functions_object.download_tiktok_video, url, dir, filename, youtube_dl_parameters)
    async def twitch_clips_download(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None) -> dict:
        """Функция для скачивания клипов с Twitch!\nurl: ссылка на твитч-клип.\ndir: куда сохранить?\nfilename: имя файла при скачивании.\nyoutube_dl_parameters: параметры YoutubeDL."""
        return await asyncio.to_thread(self.sync_functions_object.twitch_clips_download, url, dir, filename, youtube_dl_parameters)
    async def vk_rutube_dzen_video_download(self, url: str, dir: str, filename: str = None, youtube_dl_parameters: dict = None):
        """Функция по скачиванию видео ВК, Рутуба и Дзена!\nПараметры, как везде. Разберетесь."""
        return await asyncio.to_thread(self.sync_functions_object.vk_rutube_dzen_video_download, url, dir, filename, youtube_dl_parameters)
    async def unpack_zip_jar_apk_others(self, file, dir: str, delete_original: bool = False):
        """"Функция для распаковки любых архивов. Даже Jar (Java Archive) и APK.\nfile: файл в io.BytesIO(), или директория к нему.\ndir: место для распаковки.\ndelete_original: удалять оригинальный файл? (Работает только с указанием директории в file)\nФункция возвращает None."""
        return await asyncio.to_thread(self.sync_functions_object.unpack_zip_jar_apk_others, file, dir, delete_original)
    async def photo_upscale(self, image: bytes, factor: int = 4) -> bytes:
        """Функция для простого апскейла фото через Pillow (бикубический метод).\nimage: фото в bytes.\nfactor: во сколько раз увеличивать фото (width и height).\nВозвращает bytes."""
        return await asyncio.to_thread(self.sync_functions_object.photo_upscale, image, factor)
    async def change_format_of_photo(self, image: bytes, format_: ImageFormat):
        """Функция для преобразования изображений в нужный формат.\nimage: изображения в bytes.\nformat_: формат изображения, указанный конкретным классом."""
        return await asyncio.to_thread(self.sync_functions_object.change_format_of_photo, image, format_)
    async def get_vk_user(self, user_id: str) -> Optional[VkUser]:
        """Получает объект пользователя VkUser по user_id или @username."""
        return await asyncio.to_thread(self.sync_functions_object.get_vk_user, user_id)

class AsyncYandexParser:
    """Асинхронный парсер картинок с Яндекса.\nПоддерживаются только приватные HTTP(s) прокси с именем пользователя и паролем. Также требуется установка Google Chrome на машину.\nis_headless: скрывать окно с парсером?"""

    def __init__(self, proxy_host: str = None, proxy_port: int = None, proxy_user: str = None, proxy_pass: str = None, is_headless:bool=False, arguments: list[str] = None, extensions: list[str] = None):
        """Асинхронный парсер картинок с Яндекса.\nПоддерживаются только приватные HTTP(s) прокси с именем пользователя и паролем. Также требуется установка Google Chrome на машину.\nis_headless: скрывать окно с парсером?\narguments: аргументы для запуска парсера. Пример: ['--headless', '--no-sandbox', ...]\nextensions: различные самописные расширения в формате `.crx`, директории к ним. Пример: ['C:/osu.crx', 'D:/minecraft.crx']"""
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass
        self.isheadless = is_headless
        self.arguments = arguments
        self.extensions = extensions
        print(f'Парсер инициализирован, сучки!\nНачните парсить с помощью функции start_parsing.')

    def create_proxy_auth_extension(self):
        """Создаём плагин для авторизации прокси, блять."""
        if all([self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass]):
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                }
            }
            """

            background_js = """
            var config = {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                }
            };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            chrome.webRequest.onAuthRequired.addListener(
                function(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                },
                {urls: ["<all_urls>"]},
                ['blocking']
            );
            """ % (self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass)

            plugin_file = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            
            return plugin_file
        else:
            return None

    async def download_image(self, session: aiohttp.ClientSession, img_url: list[str]):
        """Качаем картинку асинхронно, блять."""
        images: list[YandexImage] = []
        if not all([self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass]):
            for url in tqdm(img_url, desc='Скачиваем изображения...', ncols=70):
                if url.startswith(('http://', 'https://')):
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                images.append(YandexImage({'data':await response.read(), 'url':url}))
                    except:
                        pass
            return images
        else:
            proxy_auth = aiohttp.BasicAuth(login=self.proxy_user, password=self.proxy_pass)
            for url in tqdm(img_url, desc='Скачиваем изображения...', ncols=70):
                try:
                    if url.startswith(('http://', 'https://')):
                        async with session.get(url, proxy=f'http://{self.proxy_host}:{self.proxy_port}', proxy_auth=proxy_auth) as response:
                            if response.status == 200:
                                images.append(YandexImage({'data':await response.read(), 'url':url}))
                except:
                    pass
            return images

    async def start_parsing(self, query: str, max_images=10, scrolly=5, pages:int=6):
        """Начать парсить..\nquery: запрос. Пример: котики.\nmax_images: максимальное количество картинок в директории.\nscrolly: скока скроллить картинки?\npages: сколько страниц с картинками парсить?"""
        # Настройка браузера
        try:
            proxy_plugin = self.create_proxy_auth_extension()
            chrome_options = Options()
            if proxy_plugin:
                chrome_options.add_extension(proxy_plugin)
            chrome_options.add_argument("--log-level=1")
            if self.isheadless:
                chrome_options.add_argument('--headless')
            if self.arguments:
                print(f'Добавление пользовательских аргументов..')
                for arg in self.arguments:
                    chrome_options.add_argument(arg)
                print(f'Готово.')
            else:
                print(f'Пользовательские аргументы не найдены.')
            if self.extensions:
                print(f'Добавление пользовательских расширений..')
                for ext in self.extensions:
                    chrome_options.add_extension(ext)
                print(f'Готово.')
            else:
                print(f'Пользовательские расширения не найдены.')
            driver = webdriver.Chrome(service=Service1(ChromeDriverManager().install()), options=chrome_options)
            print("Браузер запустился, ахуеть!")
        except Exception as e:
            print(f"Не могу запустить Chrome, пиздец: {e}")
            return

        image_urls = []
        try:
            for p in range(1, pages + 1):
                url = f"https://yandex.ru/images/search?text={query}&p={p}"
                driver.get(url)
                print(f"Зашёл на страницу ({p}), ждём, блять")
                
                # Ждём загрузку пикч
                await asyncio.sleep(10)
                
                # Скроллим
                for _ in range(scrolly):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2.5)
                    print("Скроллю, сука")
                
                all_images = driver.find_elements(By.TAG_NAME, "img")
                print(f"Всего тегов <img> на странице: {len(all_images)}")
                if all_images:
                    for img in all_images[:max_images]:
                        img_url = img.get_attribute("src")
                        if img_url and "http" in img_url:
                            image_urls.append(img_url)
                else:
                    print(f"Ни одного <img> не нашёл на странице {p}, пиздец полный")

        except Exception as e:
            print(f"Что-то пошло по пизде на странице {p}: {e}")

        driver.quit()
        print("Браузер закрыл, пиздец, готово")
        if proxy_plugin and os.path.exists(proxy_plugin):
            os.remove(proxy_plugin)

        # Качаем картинки
        if image_urls:
            print(f"Начинаем качать {len(image_urls)} картинок асинхронно, блять...")
            async with aiohttp.ClientSession(headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}) as client:
                result = await self.download_image(client, image_urls)
                return result
        else:
            print("Нихуя не скачал, картинок нет, пиздец")
            return
    def filter_by_resolution(self, images: list[YandexImage], resolutions: list[Resolution]):
        """Данная функция нужна для фильтрации изображений по нужным вам разрешениям.\nimages: список с изображениями, к примеру со start_parsing.\nresolutions: необходимые разрешения (качества). К примеру, [Resolution({"width":1080, "height":1920})]\nВозвращает список с изображениями, которые подходят по разрешениям (list[YandexImage])."""
        from tqdm import tqdm as sync_tqdm
        resolutions_dict: list[dict] = []
        new_images: list[YandexImage] = []

        for res in resolutions:
            resolutions_dict.append(res.data)

        for image in sync_tqdm(images, f'Фильтруем изображения...', ncols=70, unit='P', unit_scale=True):
            if image.get_resolution().data in resolutions_dict:
                new_images.append(image)
            else:
                pass
        return new_images
            
class TelethonThings:
    def __init__(self, app_id: int, app_hash: str, phone: str, app_version: str = '4.16.30-vxCUSTOM', system_version: str = 'Win11', device_model: str = 'FlorestTHINGS YEAH', session_name: str = 'FlorestAbobus', **attrs):
        """Короче. Класс для работы с Telegram.\nФункции: парсинг групп на аккаунте (их участники), а также массовая рассылка по никам.\nДанные берите с my.telegram.org.\napp_id: ID приложения в Telegram.\napp_hash: ключ, хэш приложения.\nphone: номер, который привязан к аккаунту.\napp_version: кастомная версия приложения.\nsystem_version: версия ОС(любая).\ndevice_model: типо имя устройства. может быть любая хрень.\nsession_name: имя сессии.\nattrs: ну короче, другие аргументы в telethon."""
        if not attrs.pop('connection', None):
            self.client = TelegramClient(session_name, app_id, app_hash, app_version=app_version, system_version=system_version, device_model=device_model, proxy=attrs.pop('proxy', None), use_ipv6=attrs.pop('use_ipv6', None), local_addr=attrs.pop('local_addr', None), timeout=attrs.pop('timeout', 10), request_retries=attrs.pop('request_retries', 5), connection_retries=attrs.pop('connection_retries', 5), retry_delay=attrs.pop('retry_delay', 1), auto_reconnect=attrs.pop('auto_reconnect', True), sequential_updates=attrs.pop('sequential_updates', False), flood_sleep_threshold=attrs.pop('flood_sleep_threshold', 60), raise_last_call_error=attrs.pop('raise_last_call_error', False), lang_code=attrs.pop('lang_code', 'en'), system_lang_code=attrs.pop('system_lang_code', 'en'), base_logger=attrs.pop('base_logger', None), receive_updates=attrs.pop('receive_updates', None), catch_up=attrs.pop('catch_up', False), entity_cache_limit=attrs.pop('entity_cache_limit', 5000))
            self.client.start(phone=phone)
        else:
            self.client = TelegramClient(session_name, app_id, app_hash, app_version=app_version, system_version=system_version, device_model=device_model, proxy=attrs.pop('proxy', None), use_ipv6=attrs.pop('use_ipv6', None), local_addr=attrs.pop('local_addr', None), timeout=attrs.pop('timeout', 10), request_retries=attrs.pop('request_retries', 5), connection_retries=attrs.pop('connection_retries', 5), retry_delay=attrs.pop('retry_delay', 1), auto_reconnect=attrs.pop('auto_reconnect', True), sequential_updates=attrs.pop('sequential_updates', False), flood_sleep_threshold=attrs.pop('flood_sleep_threshold', 60), raise_last_call_error=attrs.pop('raise_last_call_error', False), lang_code=attrs.pop('lang_code', 'en'), system_lang_code=attrs.pop('system_lang_code', 'en'), base_logger=attrs.pop('base_logger', None), receive_updates=attrs.pop('receive_updates', None), catch_up=attrs.pop('catch_up', False), entity_cache_limit=attrs.pop('entity_cache_limit', 5000), connection=attrs.pop('connection'))
            self.client.start(phone=phone)
    def parse_groups(self) -> list[dict]:
        """Парсит группу с вашего аккаунта, которую Вы выберете.\nВозвращает `list[dict]`."""
        from colorama import Fore
 
        from telethon.tl.functions.messages import GetDialogsRequest
        from telethon.tl.types import InputPeerEmpty
        import asyncio
        
        banner = f"""{Fore.GREEN}
        _____  _                          _    ____
        |  ___|| |  ___   _ __   ___  ___ | |_ |  _ \   __ _  _ __  ___   ___  _ __
        | |_   | | / _ \ | '__| / _ \/ __|| __|| |_) | / _` || '__|/ __| / _ \| '__|
        |  _|  | || (_) || |   |  __/\__ \| |_ |  __/ | (_| || |   \__ \|  __/| |
        |_|    |_| \___/ |_|    \___||___/ \__||_|     \__,_||_|   |___/ \___||_|
        """

        print(f'{banner}\n\nПарсер, созданный для людей.')
        chats = []
        last_date = None
        size_chats = 200
        groups=[]

        result = self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=size_chats,
            hash = 0
            )
        )
        chats.extend(result.chats)
        for chat in chats:
            try:
                if chat.megagroup== True:
                    groups.append(chat)
            except:
                continue
            
        print(f'{Fore.YELLOW}Выберите номер группы из перечня:')
        i=0
        for g in groups:
            print(F'{Fore.GREEN}{str(i)} - {g.title}')
            i+=1
        g_index = input("Введите нужную цифру: ")
        target_group=groups[int(g_index)]

        print(f'{Fore.YELLOW}Узнаём пользователей...')
        all_participants = self.client.get_participants(target_group)

        print(f'{Fore.YELLOW}Начинаем парсить {all_participants.total} участников.')

        users = []
        
        for user in all_participants:
            users.append({"id":user.id, 'username':f'@{user.username}', 'name':user.first_name, 'surname':user.last_name, 'phone':user.phone, 'is_scam':user.scam, 'is_premium':user.premium, 'last_activity':user.status})
        print(f'{Fore.GREEN}Парсинг был проведен успешно.')
        return users
    def send_mass_messages(self, nicknames_and_ids: list[str], messages: list[str], delay: float = random.uniform(1, 7)) -> None:
        """Рассылка пользователям.\nnicknames_and_ids: ники пользователей, а также их цифровые ID.\nmessages: сообщения для отправки.\ndelay: задержки в рассылке сообщений.\nФункция возвращает `None`."""
        import time, asyncio
        import random
        from tqdm import tqdm
        
        for user in tqdm(nicknames_and_ids, desc='Рассылаем пользователям...', ncols=70):
            for message in messages:
                try:
                    time.sleep(delay)
                    self.client.send_message(user, message)
                except Exception as e:
                    print(f'Ошибка при написании {user}: {e}')
        return None