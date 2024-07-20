import requests
from PyQt6 import QtWidgets, QtCore, uic
import sys
from ast import literal_eval
from threading import Thread
import os

now_version = 1

def downloads_music(url_or_id:str, path) -> bool:
    try:
        Headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        }
        try:
            id = int(url_or_id)
        except ValueError:
            id = url_or_id.split("id=")[1]
            url = f"http://music.163.com/song/media/outer/url?id={id}.mp3"
        else:
            url = f"http://music.163.com/song/media/outer/url?id={id}.mp3"
        ret = requests.get(url, headers=Headers)
        music_data = ret.content
        with open(path,"wb") as f:
            f.write(music_data)
    except Exception:
        return False
    else:
        return True

class Window(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("window.ui", self)
        self.timer = QtCore.QTimer()
        self.flag = (False, None)
        self.timer.start(80)
        self.timer.timeout.connect(self.control_disabled)
        self.pushButton.clicked.connect(self.add_item)
        self.pushButton_2.clicked.connect(self.remove_item)
        self.pushButton_3.clicked.connect(self.start_download)
        self.t = Thread(target=self.update)
        self.t.start()
        self.t.join()




    def add_item(self):
        try:
            text = self.lineEdit.text()
            list_item = QtWidgets.QListWidgetItem(text)
            self.listWidget.addItem(list_item)
        except Exception as e:
            print(e)

    def control_disabled(self):
        if self.listWidget.currentRow() == -1:
            self.pushButton_2.setEnabled(False)
        else:
            self.pushButton_2.setEnabled(True)

    def remove_item(self):
        selected_row = self.listWidget.currentRow()
        item = self.listWidget.takeItem(selected_row)
        del item

    def start_download(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self,"选择保存音乐的目录", "")
        if dir_path == "":
            QtWidgets.QMessageBox.information(self, "消息", "音乐下载失败(未选择下载目录)")
        else:
            count = self.listWidget.count()
            for i in range(count):
                downloads_music(self.listWidget.item(i).text(), dir_path+f"/music{i+1}.mp3")
            QtWidgets.QMessageBox.information(self, "消息", "音乐下载成功!")

    def update(self):
        try:
            update_url = "https://chendos.github.io/api"
            Headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
            }
            ret = requests.get(update_url, headers=Headers)
            with open("update.txt", "wb") as f:
                f.write(ret.content)
            with open("update.txt", "r") as f:
                data = literal_eval(f.read())
                versions = data["versions"]
                if list(versions.keys())[-1] > now_version:
                    self.flag = (True, versions[list(versions.keys())[-1]])
                else:
                    self.flag = (False, None)
        except:
            self.flag = (False, None)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    if window.flag[0] == True:
        reply = QtWidgets.QMessageBox.question(window, "消息", "检测到新版本，是否更新?")
        if reply == 16384:
            os.system("start " + window.flag[1])
        else:
            window.show()
            app.exec()

    else:
        window.show()
        app.exec()
