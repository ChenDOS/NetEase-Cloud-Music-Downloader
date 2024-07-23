import requests
from PyQt6 import QtWidgets, QtCore, uic
import sys
from ast import literal_eval
from threading import Thread
import os

now_version = 2
thread_data_pool = {"state":True, "state_str":"状态: 正在验证目录"}

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



class Window_Update_show(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("update_show_window.ui", self)
        self.timer = QtCore.QTimer()
        self.timer.start(80)
        self.timer.timeout.connect(self.control)

    def control(self):
        text_1 = \
        """更新内容:
1. 基本音乐下载功能
2. 导出音乐到指定目录
        """
        text_1S = \
        """更新内容:
1. 1.0版本 Windows 7、Windows 8、Windows 8.1 64位移植版
2. 1.0版本 Windows 7、Windows 8、Windows 8.1、Windows 10 32位移植版
        """
        text_2 = \
        """更新内容:
1. 窗口右下角、标题栏显示当前版本号，添加"更新了什么"按钮
2. 为主要按钮添加图标
3. 添加"输出路径"一栏，无需点击"开始下载"后选择路径
4. 下载过程添加进度条，下载完成后自动打开文件位置
5. 修复了网络不畅时点击下载出现未响应及弹窗显示"下载成功"的问题
        """
        if self.comboBox.currentText() == "1.0":
            self.textEdit.setText(text_1)
        elif self.comboBox.currentText() == "1.0Super":
            self.textEdit.setText(text_1S)
        elif self.comboBox.currentText() == "2.0":
            self.textEdit.setText(text_2)

class Downloads_Window(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("downloads_window.ui", self)
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
        self.pushButton_4.clicked.connect(self.choose_dir)
        self.pushButton_5.clicked.connect(self.show_update)
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
        if self.lineEdit.text() != "":
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)
        if self.listWidget.currentRow() == -1:
            self.pushButton_2.setEnabled(False)
        else:
            self.pushButton_2.setEnabled(True)
        if (self.listWidget.count() != 0) and (self.lineEdit_2.text() != ""):
            self.pushButton_3.setEnabled(True)
        else:
            self.pushButton_3.setEnabled(False)

    def remove_item(self):
        selected_row = self.listWidget.currentRow()
        item = self.listWidget.takeItem(selected_row)
        del item

    def start_download(self):
        global thread_data_pool
        count = self.listWidget.count()
        dir_path = self.lineEdit_2.text()
        if os.path.exists(dir_path) == False:
            QtWidgets.QMessageBox.critical(self, "错误", "您选择的目录不存在!")
        else:
            window_downloads.show()
            window_downloads.label_3.setText("状态: 正在下载")
            thread_data_pool["count"] = count
            thread_data_pool["dir_path"] = dir_path
            thread_data_pool["listWidget"] = self.listWidget
            thread_data_pool["self"] = self
            self.thread_1 = Worker()
            self.thread_1.progressBarValue.connect(self.update_bar)
            self.thread_1.start()


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

    def choose_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self,"选择保存音乐的目录", "")
        self.lineEdit_2.setText(dir_path)

    def show_update(self):
        window_show_update.show()

    def update_bar(self, i):
        global thread_data_pool
        if i == 101:
            if thread_data_pool["state"] == True:
                QtWidgets.QMessageBox.information(self, "消息", "音乐下载成功!")
            else:
                QtWidgets.QMessageBox.critical(self, "错误", "一个或多个文件下载失败!")
            window_downloads.progressBar.setValue(0)
            window_downloads.label_2.setText(f"已完成 0%")
            window_downloads.hide()
            thread_data_pool["dir_path"] = thread_data_pool["dir_path"].replace("/","\\")
            thread_data_pool["dir_path"] = '"'+thread_data_pool["dir_path"]+'"'
            os.popen("explorer "+thread_data_pool["dir_path"])
            thread_data_pool = {"state": True, "state_str": "状态: 正在验证目录"}
        else:
        # int((i + 1) / count * 100)
            window_downloads.progressBar.setValue(i)
            window_downloads.label_2.setText(f"已完成 {i}%")


class Worker(QtCore.QThread):
    progressBarValue = QtCore.pyqtSignal(int)

    def __init__(self):
        super(Worker, self).__init__()

    def run(self):
        global thread_data_pool
        count = thread_data_pool["count"]
        state = thread_data_pool["state"]
        for i in range(count):
            ret = downloads_music(thread_data_pool["listWidget"].item(i).text(), thread_data_pool["dir_path"] + f"/music{i + 1}.mp3")
            if ret == False:
                state = False
            self.progressBarValue.emit(int((i + 1) / count * 100))
        thread_data_pool["state"] = state
        self.progressBarValue.emit(101)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window_show_update = Window_Update_show()
    window_downloads = Downloads_Window()
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
