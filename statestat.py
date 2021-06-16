import codecs
import configparser
import os
import re
import sys
import threading
import time
import socket
import psutil
import datetime
import psycopg2
from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QApplication, QSystemTrayIcon, QAction, qApp, QMenu
from plyer import notification
from psycopg2 import OperationalError
red_color = "style='color:#FF0000'"
green_color = "style='color:#006262'"
states = []
config = configparser.ConfigParser()  # создаём объекта парсера
# Settings
def configuration():
    # Settings -> [db_conf]
    try:
        getconf = config.read("settings.ini")
        try:
            from_setup_user = config["db_conf"]["user"]
            from_setup_password = config["db_conf"]["password"]
            from_setup_host = config["db_conf"]["host"]
            from_setup_port = config["db_conf"]["port"]
        except:
            states.append(f"<p {red_color}>Не верные параметры конфигурации <u>settings.ini</u> в блоке <u>[db_conf]</u></p>")

            # Settings -> [socket_conf]

        try:
            from_setup_socket_sw = config["socket_conf"]["sw"]
            from_setup_socket_host = config["socket_conf"]["host"]
            from_setup_socket_port = config["socket_conf"]["port"]
        except:
            states.append(f"<p {red_color}>Не верные параметры конфигурации <u>settings.ini</u> в блоке <u>[socket_conf]</u></p>")
        try:

            # Settings -> [tab_conf]

            from_setup_tab_conf_sw = config["tab_conf"]["sw"]
            from_setup_tab_conf_dbname = config["tab_conf"]["dbname"]
            from_setup_tab_conf_tabname = config["tab_conf"]["tabname"]
            from_setup_tab_conf_tabname_viol = config["tab_conf"]["viol"]
            if from_setup_tab_conf_tabname_viol != 0:
                from_setup_tab_conf_tabname_viol = from_setup_tab_conf_tabname_viol.replace(' ', '')
        except:
            states.append(f"<p {red_color}>Не верные параметры конфигурации <u>settings.ini</u> в блоке <u>[tab_conf]</u></p>")

        return getconf, from_setup_user, from_setup_password, from_setup_host, from_setup_port, from_setup_socket_sw, from_setup_socket_host, from_setup_socket_port, from_setup_tab_conf_sw, from_setup_tab_conf_dbname, from_setup_tab_conf_tabname, from_setup_tab_conf_tabname_viol
    except:
        getconf = False
        return getconf

try:
    getconf, from_setup_user, from_setup_password, from_setup_host, from_setup_port, from_setup_socket_sw, from_setup_socket_host, from_setup_socket_port, from_setup_tab_conf_sw, from_setup_tab_conf_dbname, from_setup_tab_conf_tabname, from_setup_tab_conf_tabname_viol = configuration()
except:
    getconf = configuration()

conf_path = os.path.join(os.environ["USERPROFILE"], "AppData/Local/Recognition Technologies/AvtoUragan ver 3.7/Config")
if (os.path.exists(conf_path)):
    config.read(f"{conf_path}/UrsStatusPlugin.ini")
    from_setup_path = config["/PluginData"]["Output"]
    if (os.path.exists(f"{from_setup_path}/UrsStatusPlugin.dat")):
        from_setup_path_file = os.path.normpath(f"{from_setup_path}/UrsStatusPlugin.dat")
        from_setup_path_file = from_setup_path_file.replace('\\', '/')
        print(from_setup_path_file)
        from_setup_path_sw = "1"
    else:
        from_setup_path_sw = "0"
else:
    from_setup_path_sw = "0"


now = datetime.datetime.now()
current_time = now.strftime("%H:%M:%S")

def create_notif(message, app_name, app_icon, timeout):
    notification.notify(
        message=message,
        app_name=app_name,
        app_icon=app_icon,
        timeout=timeout
    )


class OutputLogger(QObject):
    emit_write = Signal(str, int)

    class Severity:
        DEBUG = 0
        ERROR = 1

    def __init__(self, io_stream, severity):
        super().__init__()

        self.io_stream = io_stream
        self.severity = severity

    def write(self, text):
        self.io_stream.write(text)
        self.emit_write.emit(text, self.severity)

    def flush(self):
        self.io_stream.flush()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)
        self.setCentralWidget(self.text_edit)
        self.setWindowTitle("TR-Soft StateStat")
        self.resize(300, 150)
        self.setStyleSheet('background: #edf9fe;')
        self.setWindowIcon(QIcon("image.ico"))
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("image.ico"))
        show_action = QAction("Показать", self)
        quit_action = QAction("Закрыть", self)
        # mouseDoubleClickEvent.connect(self.show)
        show_action.triggered.connect(self.show)
        # hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        self.disambiguateTimer = QTimer(self)
        self.disambiguateTimer.setSingleShot(True)

        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("TR-Soft StateStat")
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        create_notif("Приложение свернуто в трей и работает в фоновом режиме.", "TR-Soft StateStat", "trns.ico", 3)


    def hideEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.show()

    def showEvent(self, event):
        self.show()

    def append_log(self, text, severity):
        text = str(text)
        text = "<b>{}</b>".format(text)
        self.text_edit.append(text)

    def onTrayIconActivated(self, reason):
        # print("onTrayIconActivated:") , reason
        if reason == QSystemTrayIcon.Trigger:
            self.disambiguateTimer.start(qApp.doubleClickInterval())
        elif reason == QSystemTrayIcon.DoubleClick:
            self.disambiguateTimer.stop()
            self.show()

   # def disambiguateTimerTimeout(self):
        # print("Tray icon single clicked")

# DB Funcs

create_database_query = "CREATE DATABASE statestat"

create_status_table = """
CREATE TABLE IF NOT EXISTS StatusPluginTable (
  StatusPluginValue VARCHAR
)
"""

create_stat_table = """
CREATE TABLE IF NOT EXISTS statistic (  
  trstime VARCHAR, 
  counts VARCHAR,
  type VARCHAR
)
"""

def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        # print("Соединение с PostgreSQL установлено")
    except:
        pass
        #print(f"Не удалось установить соединение с PostgreSQL!{e}")
    return connection

def create_database(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except Exception:
        pass



def execute_query(connection, query):
    if re.search(r'\bStatusPluginTable\b', query):
        tabname = "статусов"
    elif re.search(r'\bstatistic\b', query):
        tabname = "статистики"
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print(f"Таблица  {tabname} готова к работе")
    except:
        states.append(f"Ошибка при создании таблицы {tabname}")

def pg_check():
    global getconf
    if getconf:
        sock_pg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_pg.settimeout(5)
        pg_check_result = sock_pg.connect_ex((from_setup_host, int(from_setup_port)))
        if pg_check_result == 0:
            # states.append("<p style='color:#006262'>Служба PostgreSQL работает</p>")
            # print("<p>Подключение к базам данных</p>")
            connection = create_connection(
                "postgres", from_setup_user, from_setup_password, from_setup_host, from_setup_port
            )
            if connection:
                states.append(f"<p {green_color}>Соединение с PostgreSQL установлено</p>")
                create_database(connection, create_database_query)
                connection = create_connection(
                    "statestat", from_setup_user, from_setup_password, from_setup_host, from_setup_port
                )
                execute_query(connection, create_status_table)
                execute_query(connection, create_stat_table)
            else:
                connection = False
                states.append(f"<p {red_color}>Не удалось установить соединение с PostgreSQL! </p>"
                      "<p>Настройте параметры подключения к базе данных в  "
                      "<u>settings.ini</u> раздел: <u>[db_conf]</u></p>")
        else:
            connection = False
            states.append(f"<p {red_color}>Сервис PostgreSQL не доступен!"
                  "Настройте параметры подключения к базе данных в  "
                  "<u>settings.ini</u> раздел: <u>[db_conf]</u></p>")
    else:
        connection = False
    return connection
connection = pg_check()

# DB


# Parse func

def pg_set_db_check():
    global getconf
    if getconf:
        connection_journals = create_connection(
            from_setup_tab_conf_dbname, from_setup_user, from_setup_password, from_setup_host, from_setup_port
        )
        if connection_journals:
            states.append(f"<p {green_color}>Подключено к {from_setup_tab_conf_dbname}</p>")
        else:
            states.append(f"<p {red_color}>Не удалось подключиться к {from_setup_tab_conf_dbname}</p>")
    else:
        connection_journals = False
    return connection_journals
connection_journals = pg_set_db_check()

def statsallcount():
    if connection_journals:
        states.append(f"<p {green_color}>Подсчет всех ТС запущен</p>")
        while True:
            carscount = []
            now_cic = datetime.datetime.now()
            current_time_in_cic = now_cic.strftime("%H:%M:%S")
            cursor = connection_journals.cursor()
            cursor_st = connection.cursor()
            setup_tab_query = f'SELECT * FROM "{from_setup_tab_conf_tabname}"'
            try:
                cursor.execute(setup_tab_query)
                tmstamps = cursor.fetchall()
                for row in tmstamps:
                    try:
                        cursor_st.execute(f"SELECT * FROM statistic WHERE trstime = '{row[0]}'")
                        if cursor_st.rowcount > 0:
                            #print("уже есть")
                            pass
                        else:
                            subtab = f"{from_setup_tab_conf_tabname}{row[0]}"
                            cursor.execute(f'SELECT trplate, trviol FROM "{subtab}"')
                            # print(subtab)
                            trstime = row[0]
                            counted = cursor.rowcount
                            #print(f"allcount{counted}")
                            query = f"INSERT INTO statistic (trstime, counts, type) VALUES ('{trstime}','{counted}','all')"
                            cursor_st.execute(query)
                    except Exception:
                        pass
                delta = datetime.timedelta(hours=1)
                current_time_hour = (now_cic+delta).strftime("%H:%M:%S")
                carscount.append(f"<p>Подсчет всех ТС успешно выполнен_{current_time_in_cic}</p>")
                carscount.append(f"<p>Следующий подсчет всех ТС в_{current_time_hour}</p>")
                carscount_out = "</br>".join(carscount)
                print(carscount_out)
                time.sleep(3600)
            except:
                break

def statsviolcount():
    if connection_journals:
        if from_setup_tab_conf_sw == "1":
            if from_setup_tab_conf_tabname_viol != "0":
                states.append(f"<p {green_color}>Подсчет нарушений {from_setup_tab_conf_tabname_viol} запущен</p>")
                cursor = connection_journals.cursor()
                cursor_st = connection.cursor()
                # Check for changing conf
                cursor_st.execute(f"SELECT DISTINCT type FROM statistic WHERE  type = '{from_setup_tab_conf_tabname_viol}' LIMIT 1")
                if cursor_st.rowcount == 0:
                    cursor_st.execute(f"DELETE FROM statistic WHERE  type != '{from_setup_tab_conf_tabname_viol}' AND type != 'all'")
                if ',' in from_setup_tab_conf_tabname_viol:
                    viols = from_setup_tab_conf_tabname_viol.split(',')
                else:
                    viols = [from_setup_tab_conf_tabname_viol]
                while True:
                    carscount_viol = []
                    now_cic = datetime.datetime.now()
                    current_time_in_cic = now_cic.strftime("%H:%M:%S")
                    setup_tab_query = f'SELECT * FROM "{from_setup_tab_conf_tabname}"'
                    try:
                        cursor.execute(setup_tab_query)
                        tmstamps = cursor.fetchall()
                        for row in tmstamps:
                            # print(row[0])
                            try:
                                cursor_st.execute(f"SELECT * FROM statistic WHERE trstime = '{row[0]}' AND type = '{from_setup_tab_conf_tabname_viol}'")
                                if cursor_st.rowcount > 0:
                                    # print("уже есть")
                                    pass
                                else:
                                    subtab = f"{from_setup_tab_conf_tabname}{row[0]}"
                                    outlist = []
                                    for viol in viols:
                                        cursor.execute(f'SELECT trplate, trviol FROM "{subtab}" WHERE trviol = {viol}')
                                        # print(subtab)
                                        trstime = row[0]
                                        counted = cursor.rowcount
                                        outlist.append(f"{viol}={counted}")
                                    outlist = "|".join(outlist)
                                    # print(outlist)
                                    query = f"INSERT INTO statistic (trstime, counts, type) VALUES ('{trstime}','{outlist}','{from_setup_tab_conf_tabname_viol}')"
                                    cursor_st.execute(query)

                            except Exception:
                                pass
                    except:
                        states.append(f"<p {red_color}>Таблица {from_setup_tab_conf_tabname} не сущетсвует в БД {from_setup_tab_conf_dbname}</p>")
                        break
                    delta = datetime.timedelta(hours=1)
                    current_time_hour = (now_cic + delta).strftime("%H:%M:%S")
                    carscount_viol.append(f"<p>Подсчет нарушений успешно выполнен_{current_time_in_cic}</p>")
                    carscount_viol.append(f"<p>Следующий подсчет нарушений в_{current_time_hour}</p>")
                    carscount_viol_out = "</br>".join(carscount_viol)
                    print(carscount_viol_out)
                    time.sleep(3600)


def dothis():
    status = []
    try:
        if (os.path.exists(from_setup_path_file)):
            f = codecs.open(f"{from_setup_path_file}", "r", "cp1251")
            lines = f.readlines()
            todb = ("|".join(lines))
            f.close()
            cursor = connection.cursor()
            query = "SELECT * from StatusPluginTable"
            cursor.execute(query)
            records = cursor.rowcount
            insdb = re.sub("^\s+|\n|\r|\s+$", '', todb)
            # print(insdb)
            if records > 0:
                qtodo = f"UPDATE StatusPluginTable SET StatusPluginValue = '{insdb}'"
            else:
                qtodo = f"INSERT INTO StatusPluginTable (StatusPluginValue) VALUES ('{insdb}')"
            cursor.execute(qtodo)
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            status.append(f"<p {green_color}>Сатусы обновлены_{current_time}</p>")
        else:
            states.append(f"<p {red_color}><u>{from_setup_path}</u> Папки н"
                          f"е существует. Настройте параметр <u>[path_conf]</u> в файле <u>settings.ini</u></p> ")
            time.sleep(20)
            dothis()
    except:
        print(f"<p {red_color}>Ошибка. Повторный опрос через 20 секунд</p>")
        time.sleep(20)
        dothis()

    status_out = "</br>".join(status)
    print(status_out)
# Parse

OUTPUT_LOGGER_STDOUT = OutputLogger(sys.stdout, OutputLogger.Severity.DEBUG)
OUTPUT_LOGGER_STDERR = OutputLogger(sys.stderr, OutputLogger.Severity.ERROR)

sys.stdout = OUTPUT_LOGGER_STDOUT
sys.stderr = OUTPUT_LOGGER_STDERR

# Слушаем входящие подключения




def server_sock():
    if configuration:
        if from_setup_socket_sw == "1":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (from_setup_socket_host, int(from_setup_socket_port))
            states.append(f'<p {green_color}>Запущен TCP сокет {from_setup_socket_host} : {int(from_setup_socket_port)}</p>')
            sock.bind(server_address)
            sock.listen(1)
            while True:
                # ждем соединения
                # print('Ожидание соединения...')
                connection, client_address = sock.accept()
                try:
                    # print('Подключено к:', client_address)
                    # Принимаем данные порциями и ретранслируем их
                    while True:
                        data = connection.recv(16)
                        if data:
                            # print(f'Получено: {data.decode()}')
                            # print('Обработка данных...')
                            data = data.upper()
                            # print('Отправка обратно клиенту.')
                            connection.sendall(data)
                        else:
                            break

                finally:
                    # Очищаем соединение
                    print('Закрываем соединение')
                    connection.close()
# Socket

def watch_file_update():
    if from_setup_path_sw == "1":
        states.append(f"<p {green_color}>Отслеживание UrsStatusPlugin.dat включено</p>")
        if (os.path.exists(from_setup_path)):
            timestamp = os.stat(from_setup_path).st_mtime
            while True:
                if timestamp != os.stat(from_setup_path).st_mtime:
                    timestamp = os.stat(from_setup_path).st_mtime
                    dothis()
                else:
                    time.sleep(5)
        else:
            dothis()
    else:
        states.append(f"<p {green_color}>Отслеживание UrsStatusPlugin.dat выключено</p>")

# Listen
#states = '|'.join(states)

if __name__ == '__main__':
    get_processes_by_name = lambda t: filter(lambda p: p.name() == t,psutil.process_iter())
    getc = len(list(get_processes_by_name("StateStat.exe")))
    if getc > 1:
        create_notif("Приложение уже запущено", "TR-Soft StateStat", "trns.ico", 3)
        raise SystemExit
    app = QApplication([])
    app.setWindowIcon(QIcon('image.ico'))
    mw = MainWindow()
    mw.show()
    if getconf:
        threading.Thread(target=server_sock, daemon=True).start()
        threading.Thread(target=pg_check, args=(), daemon=True).start()
        threading.Thread(target=pg_set_db_check, args=(), daemon=True).start()
        threading.Thread(target=statsallcount, args=(), daemon=True).start()
        threading.Thread(target=statsviolcount, args=(), daemon=True).start()
        threading.Thread(target=watch_file_update, args=(), daemon=True).start()
        states_out = "</br>".join(states)
        print(states_out)
    else:
        print(f"<p {red_color}>Отсутствует файл конфигурации <u>settings.ini</u></p>")
    app.exec()
