from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QPushButton, QTextBrowser, QGroupBox, QMessageBox
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from itertools import permutations
from yandex_music import Client
from datetime import datetime
from PyQt6.QtGui import QIcon
from enum import Enum
import configparser
import pypresence
import requests
import asyncio
import psutil
import time
import sys
import os
from PyQt6 import QtTest


# Enum для статуса воспроизведения мультимедийного контента.
class PlaybackStatus(Enum):
    Unknown = 0
    Closed = 1
    Opened = 2
    Paused = 3
    Playing = 4
    Stopped = 5


class WinYandexMusicRPC(QMainWindow):
    def __init__(self):
        #for RCP
        self.exe_names = ["Discord.exe", "DiscordCanary.exe", "DiscordPTB.exe"]
        self.client = None
        self.currentTrack = None
        self.rpc = None
        self.running = False
        self.paused = False
        self.paused_time = 0
        self.name_prev = ""
        

        #for GUI
        super().__init__()
        self.logs = []
        self.config = configparser.ConfigParser()
        self.layout:QVBoxLayout = QVBoxLayout()
        self.widget:QWidget = QWidget()
        self.button:QPushButton = QPushButton()

        self.create_widgets()
        self.setWindowTitle("WinYandexMusicRPC")
        self.initialize_config()
        self.get_last_version()

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def initialize_config(self):
        if not os.path.exists("config.ini"):
            self.error("config.ini", "Не найден файл config.ini. Пожалуйста, скачайте его вместе с программой!")
        self.config.read("config.ini")
        self.config = self.config["INFO"]

    def error(self, title, msg):
        if not os.path.exists("config.ini"):
            button = QMessageBox.critical(
                self,
                title,
                msg,
                buttons=QMessageBox.StandardButton.Close
            )
            if button:
                exit()

    def create_widgets(self): 
        logs = QGroupBox("Logs")
        logsLayout = QVBoxLayout()
        self.text = QTextBrowser()
        self.text.setMinimumSize(500,200)
        logsLayout.addWidget(self.text)
        logs.setLayout(logsLayout)
        self.layout.addWidget(logs)
        
        self.button.setText("Start")
        self.button.clicked.connect(self.buttonClick)
        self.button.setCheckable(True)
        self.layout.addWidget(self.button)
    
    def addLineToLogs(self, line):
        now = datetime.now()
        ctime = "[{}:{}:{}] ".format(now.hour, now.minute, now.second)
        self.logs.insert(0, ctime + line)
        self.text.setText("\n".join(self.logs))

    def get_last_version(self):
        try:
            response = requests.get(self.config["repo"] + "/releases/latest")
            response.raise_for_status()
            latest_version = response.url.split("/")[-1]
            if self.config["version"] != latest_version:
                self.addLineToLogs(f"A new version has been released on GitHub! You are using - {self.config["version"]}. A new version - {latest_version}")
            else:
                self.addLineToLogs("You are using the latest version of the script")
        except requests.exceptions.RequestException as e:
            self.addLineToLogs("Error getting latest version:", e)

    def buttonClick(self, checked):
        if checked:
            self.addLineToLogs("Starting...")
            self.button.setText("Stop")
            self.start_rpc()
            return
        if not checked:
            self.addLineToLogs("Stoped!")
            self.running = False
            self.button.setText("Start")
            return
        
    def start_rpc(self):
        if not any(name in (p.name() for p in psutil.process_iter()) for name in self.exe_names):
            self.error("Discord not found","Discord is not launched!")

        self.rpc = pypresence.Presence(self.config["client_id"])
        self.rpc.connect()
        self.client = Client().init()
        self.running = True

        while self.running:
            currentTime = time.time()

            if not any(name in (p.name() for p in psutil.process_iter()) for name in self.exe_names):
                self.error("Discord not found","Discord was closed!")

            ongoing_track = self.getTrack()

            if self.currentTrack != ongoing_track : # проверяем что песня не играла до этого, т.к она просто может быть снята с паузы.
                if ongoing_track["success"]: 
                    if self.currentTrack is not None and "label" in self.currentTrack and self.currentTrack["label"] is not None:
                        if ongoing_track["label"] != self.currentTrack["label"]: 
                            self.addLineToLogs(f"Changed track to \"{ongoing_track["label"]}\"")
                    else:
                        self.addLineToLogs(f"Changed track to \"{ongoing_track["label"]}\"")
                    self.paused_time = 0
                    trackTime = currentTime
                    remainingTime = ongoing_track["durationSec"] - 2 - (currentTime - trackTime)
                    self.rpc.update(
                        details=ongoing_track["title"],
                        state=ongoing_track["artist"],
                        end=currentTime + remainingTime,
                        large_image=ongoing_track["og-image"],
                        large_text=ongoing_track["album"],
                        buttons=[{"label": "Listen on Yandex.Music", "url": ongoing_track["link"]}] #Для текста кнопки есть ограничение в 32 байта. Кириллица считается за 2 байта.
                                                                                            #Если превысить лимит то Discord RPC не будет виден другим пользователям.
                    )

                else:
                    self.rpc.clear()
                    self.addLineToLogs(f"Clear RPC")

                self.currentTrack = ongoing_track

            else: #Песня не новая, проверяем статус паузы
                if ongoing_track["success"] and ongoing_track["playback"] != PlaybackStatus.Playing.name and not self.paused:
                    self.paused = True
                    self.addLineToLogs(f"Track {ongoing_track["label"]} on pause")

                    if ongoing_track["success"]:
                        trackTime = currentTime
                        remainingTime = ongoing_track["durationSec"] - 2 - (currentTime - trackTime)
                        self.rpc.update(
                            details=ongoing_track["title"],
                            state=ongoing_track["artist"],
                            large_image=ongoing_track["og-image"],
                            large_text=ongoing_track["album"],
                            buttons=[{"label": "Listen on Yandex.Music", "url": ongoing_track["link"]}], #Для текста кнопки есть ограничение в 32 байта. Кириллица считается за 2 байта.
                                                                                                    #Если превысить лимит то Discord RPC не будет виден другим пользователям.
                            small_image="https://raw.githubusercontent.com/AtikD/WinYandexMusicRPC/main/assets/pause.png",
                            small_text="На паузе"
                        )

                elif ongoing_track["success"] and ongoing_track["playback"] == PlaybackStatus.Playing.name and self.paused:
                    self.addLineToLogs(f"Track {ongoing_track["label"]} off pause.")
                    self.paused = False

                elif ongoing_track["success"] and ongoing_track["playback"] != PlaybackStatus.Playing.name and self.paused and trackTime != 0:
                    self.paused_time = currentTime - trackTime
                    if self.paused_time > 5 * 60:  # если пауза больше 5 минут
                        trackTime = 0
                        self.rpc.clear()
                        self.addLineToLogs(f"Clear RPC due to paused for more than 5 minutes")
                else:
                    self.paused_time = 0  # если трек продолжает играть, сбрасываем paused_time
            QtTest.QTest.qWait(3000)

            
    def getTrack(self) -> dict:
        try:
            current_media_info = asyncio.run(get_media_info())
            name_current = current_media_info["artist"] + " - " + current_media_info["title"]
            if str(name_current) != self.name_prev:
                self.addLineToLogs(f"Now listening to \"{name_current}\"")
            else: #Если песня уже играет, то не нужно ее искать повторно. Просто вернем её с актуальным статусом паузы.
                currentTrack_copy = self.currentTrack.copy()
                currentTrack_copy["playback"] = current_media_info["playback_status"]
                return currentTrack_copy

            self.name_prev = str(name_current)
            search = self.client.search(name_current, True, "all", 0, False)

            if search.tracks == None:
                self.addLineToLogs(f"Can't find the song: {name_current}")
                return {"success": False}
            
            finalTrack = None
            debugStr = []
            for index, trackFromSearch in enumerate(search.tracks.results[:5], start=1): #Из поиска проверяем первые 5 результатов
                if trackFromSearch.type not in ["music", "track", "podcast_episode"]:
                    debugStr.append(f"The result #{index} has the wrong type.")
                
                # Авторы могут отличатся положением, поэтому делаем все возможные варианты их порядка.
                artists = trackFromSearch.artists_name()
                all_variants = list(permutations(artists))
                all_variants = [list(variant) for variant in all_variants]
                findTrackNames = []
                for variant in all_variants:
                    findTrackNames.append(", ".join([str(elem) for elem in variant]) + " - " + trackFromSearch.title)
                # Также может отличаться регистр, так что приведём всё в один регистр.    
                boolNameCorrect = any(name_current.lower() == element.lower() for element in findTrackNames)

                if self.config["strong_find"] and not boolNameCorrect: #если strong_find и название трека не совпадает, продолжаем поиск
                    findTrackName = ", ".join([str(elem) for elem in trackFromSearch.artists_name()]) + " - " + trackFromSearch.title
                    debugStr.append(f"The result #{index} has the wrong title. Now play: {name_current}. But we find: {findTrackName}")
                    continue
                else: #иначе трек найден
                    finalTrack = trackFromSearch
                    break

            if finalTrack == None:
                for i in debugStr:
                    self.addLineToLogs(i)
                self.addLineToLogs(f"Can't find the song (strong_find): {name_current}")
                return {"success": False}

            track = finalTrack
            trackId = track.trackId.split(":")

            if track:
                return {
                    "success": True,
                    "title": TrimString(track.title, 40),
                    "artist": TrimString(f"{", ".join(track.artists_name())}",40),
                    "album": TrimString(track.albums[0].title,25),
                    "label": TrimString(f"{", ".join(track.artists_name())} - {track.title}",50),
                    "duration": "Duration: None",
                    "link": f"https://music.yandex.ru/album/{trackId[1]}/track/{trackId[0]}/",
                    "durationSec": track.duration_ms // 1000,
                    "playback": current_media_info["playback_status"],
                    "og-image": "https://" + track.og_image[:-2] + "400x400"
                }

        except Exception as exception:
            self.addLineToLogs(f"Something happened: {exception}")
            return {"success": False}

# Асинхронная функция для получения информации о мультимедийном контенте через Windows SDK.
async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != "_"}
        info_dict["genres"] = list(info_dict["genres"])
        playback_status = PlaybackStatus(current_session.get_playback_info().playback_status)
        info_dict["playback_status"] = playback_status.name
        return info_dict
    return "The music is not playing right now :("

def TrimString(string, maxChars):
    if len(string) > maxChars:
        return string[:maxChars] + "..."
    else:
        return string


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico")) # from https://yandex.ru/support/music/performers-and-copyright-holders/icon.html
    window = WinYandexMusicRPC()
    window.show()
    app.exec()