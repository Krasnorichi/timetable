import psycopg2
import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QMessageBox)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Shedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_shedule_tab()
        self._create_teacher_tab()
        self._create_subject_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database='Telegram-bot',
                                     user='postgres',
                                     password='Alex5623Sh',
                                     host='localhost',
                                     port='5432')

        self.cursor = self.conn.cursor()

    def _create_shedule_tab(self):
        self.shedule_tab = QWidget()
        self.tabs.addTab(self.shedule_tab, "Shedule")

        self.monday_gbox = QGroupBox("Monday")
        self.tuesday_gbox = QGroupBox('Tuesday')
        self.wednesday_gbox = QGroupBox('Wednesday')
        self.thursday_gbox = QGroupBox('Thursday')
        self.friday_gbox = QGroupBox('Friday')
        self.saturday_gbox = QGroupBox('Saturday')

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()
        self.shbox3 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox3)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.monday_gbox)
        self.shbox1.addWidget(self.tuesday_gbox)
        self.shbox1.addWidget(self.wednesday_gbox)
        self.shbox3.addWidget(self.thursday_gbox)
        self.shbox3.addWidget(self.friday_gbox)
        self.shbox3.addWidget(self.saturday_gbox)

        self._create_monday_table()
        self._create_tuesday_table()
        self._create_wednesday_table()
        self._create_thursday_table()
        self._create_friday_table()
        self._create_saturday_table()

        self.update_shedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_shedule)

        self.shedule_tab.setLayout(self.svbox)

    def _create_teacher_tab(self):
        self.teacher_tab = QWidget()
        self.tabs.addTab(self.teacher_tab, "Teachers")
        self.teacher_gbox = QGroupBox('Teachers')
        self.t_svbox = QVBoxLayout()
        self.t_shbox1 = QHBoxLayout()
        self.t_shbox2 = QHBoxLayout()
        self.t_svbox.addLayout(self.t_shbox1)
        self.t_svbox.addLayout(self.t_shbox2)
        self.t_shbox1.addWidget(self.teacher_gbox)
        self._create_teacher_table()
        self.update_teacher_button = QPushButton('Update')
        self.t_shbox2.addWidget(self.update_teacher_button)
        self.update_teacher_button.clicked.connect(self._update_shedule)
        self.teacher_tab.setLayout(self.t_svbox)

    def _create_teacher_table(self):
        self.teacher_table = QTableWidget()
        self.teacher_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teacher_table.setColumnCount(4)
        self.teacher_table.setHorizontalHeaderLabels(["Teacher", "Subject", "", ''])

        self._update_teacher_table()

        self.t_mvbox = QVBoxLayout()
        self.t_mvbox.addWidget(self.teacher_table)
        self.teacher_gbox.setLayout(self.t_mvbox)

    def _update_teacher_table(self):
        self.cursor.execute("SELECT * FROM public.teacher order by full_name asc")
        records = list(self.cursor.fetchall())

        self.teacher_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.teacher_table.setItem(i, 0, QTableWidgetItem(str(r[1])))
            self.teacher_table.setItem(i, 1, QTableWidgetItem(str(r[2])))
            self.teacher_table.setCellWidget(i, 2, joinButton)
            self.teacher_table.setCellWidget(i, 3, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_teacher(num, records))
            joinButton.clicked.connect(lambda ch, num=i: self._change_teacher(num, records))

        addButton = QPushButton('Add')
        self.teacher_table.setCellWidget(self.teacher_table.rowCount() - 1, 2, addButton)
        addButton.clicked.connect(lambda: self._add_teacher(self.teacher_table.rowCount() - 1))

        self.teacher_table.resizeRowsToContents()

    def _delete_row_from_teacher(self, rowNum, arr):
        maxx = self.teacher_table.rowCount() - 2
        self.cursor.execute('DELETE FROM teacher WHERE full_name=%s and subject=%s', (arr[rowNum][1], arr[rowNum][2]))
        self.conn.commit()

        self.teacher_table.setItem(maxx, 0, QTableWidgetItem(str('')))
        self.teacher_table.setItem(maxx, 1, QTableWidgetItem(str('')))
        self.teacher_table.setItem(maxx, 3, QTableWidgetItem(str('')))
        self._update_shedule()

    def _change_teacher(self, rowNum, arr):
        row = list()
        for i in range(self.teacher_table.columnCount()):
            try:
                row.append(self.teacher_table.item(rowNum, i).text())
            except:
                row.append(None)

        try:
            self.cursor.execute("UPDATE teacher SET full_name=%s, subject=%s WHERE full_name=%s and subject=%s",
                                (row[0], row[1], arr[rowNum][1], arr[rowNum][2]))

        except:
            QMessageBox.about(self, "Error", "Enter all fields")
        self.conn.commit()
        self._update_shedule()

    def _add_teacher(self, rowNum):
        row = list()
        for i in range(self.teacher_table.columnCount()):
            try:
                row.append(self.teacher_table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute('INSERT INTO teacher(full_name, subject) VALUES (%s, %s)', (row[0], row[1]))

        except:
            QMessageBox.about(self, 'Error', 'Enter all fields or there is no such subject')
        self.conn.commit()
        self._update_shedule()

    def _create_monday_table(self):
        self.monday_table = QTableWidget()
        self.monday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.monday_table.setColumnCount(5)
        self.monday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_monday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.monday_table)
        self.monday_gbox.setLayout(self.mvbox)

    def _update_monday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='monday' order by time asc")
        records = list(self.cursor.fetchall())

        self.monday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.monday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.monday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.monday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.monday_table.setCellWidget(i, 3, joinButton)
            self.monday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'monday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.monday_table, records, 'monday'))

        addButton = QPushButton('Add')
        self.monday_table.setCellWidget(self.monday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.monday_table.rowCount() - 1, self.monday_table, 'monday'))

        self.monday_table.resizeRowsToContents()

    def _change_day_from_table(self, rowNum, table, arr, day):
        row = list()
        for i in range(table.columnCount()):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)

        try:
            self.cursor.execute(
                "UPDATE timetable SET subject=%s, time=%s, cabinet=%s WHERE subject=%s and time=%s and cabinet=%s and day=%s",
                (row[0], row[1], row[2], arr[rowNum][2], arr[rowNum][3], arr[rowNum][4], day))

        except:
            QMessageBox.about(self, "Error", "Enter all fields")
        self.conn.commit()
        self._update_shedule()

    def _delete_row_from_table(self, rowNum, arr, day):
        maxx = self.monday_table.rowCount() - 2
        self.cursor.execute('DELETE FROM timetable WHERE subject=%s and time=%s and cabinet=%s and day=%s',
                            (arr[rowNum][2], arr[rowNum][3], arr[rowNum][4], day))
        self.conn.commit()

        self.monday_table.setItem(maxx, 0, QTableWidgetItem(str('')))
        self.monday_table.setItem(maxx, 1, QTableWidgetItem(str('')))
        self.monday_table.setItem(maxx, 2, QTableWidgetItem(str('')))
        self.monday_table.setItem(maxx, 4, QTableWidgetItem(str('')))
        self._update_shedule()

    def _add_row_into_table(self, rowNum, table, day):
        row = list()
        for i in range(table.columnCount()):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute('INSERT INTO timetable(day, subject, time, cabinet) VALUES (%s, %s, %s, %s)',
                                (day, row[0], row[1], row[2]))

        except:
            QMessageBox.about(self, 'Error', 'Enter all fields or there is no such subject')
        self.conn.commit()
        self._update_shedule()

    def _create_tuesday_table(self):
        self.tuesday_table = QTableWidget()
        self.tuesday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.tuesday_table.setColumnCount(5)
        self.tuesday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_tuesday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.tuesday_table)
        self.tuesday_gbox.setLayout(self.mvbox)

    def _update_tuesday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='tuesday' order by time asc")
        records = list(self.cursor.fetchall())

        self.tuesday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.tuesday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.tuesday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.tuesday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.tuesday_table.setCellWidget(i, 3, joinButton)
            self.tuesday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'tuesday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.tuesday_table, records, 'tuesday'))

        addButton = QPushButton('Add')
        self.tuesday_table.setCellWidget(self.tuesday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.tuesday_table.rowCount() - 1, self.tuesday_table, 'tuesday'))

        self.tuesday_table.resizeRowsToContents()

    def _create_wednesday_table(self):
        self.wednesday_table = QTableWidget()
        self.wednesday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.wednesday_table.setColumnCount(5)
        self.wednesday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_wednesday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.wednesday_table)
        self.wednesday_gbox.setLayout(self.mvbox)

    def _update_wednesday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='wednesday' order by time asc")
        records = list(self.cursor.fetchall())

        self.wednesday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.wednesday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.wednesday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.wednesday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.wednesday_table.setCellWidget(i, 3, joinButton)
            self.wednesday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'wednesday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.wednesday_table, records, 'wednesday'))

        addButton = QPushButton('Add')
        self.wednesday_table.setCellWidget(self.wednesday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.wednesday_table.rowCount() - 1, self.wednesday_table, 'wednesday'))

        self.wednesday_table.resizeRowsToContents()

    def _create_thursday_table(self):
        self.thursday_table = QTableWidget()
        self.thursday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.thursday_table.setColumnCount(5)
        self.thursday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_thursday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.thursday_table)
        self.thursday_gbox.setLayout(self.mvbox)

    def _update_thursday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='thursday' order by time asc")
        records = list(self.cursor.fetchall())

        self.thursday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.thursday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.thursday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.thursday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.thursday_table.setCellWidget(i, 3, joinButton)
            self.thursday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'thursday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.thursday_table, records, 'thursday'))

        addButton = QPushButton('Add')
        self.thursday_table.setCellWidget(self.thursday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.thursday_table.rowCount() - 1, self.thursday_table, 'thursday'))

        self.thursday_table.resizeRowsToContents()

    def _create_friday_table(self):
        self.friday_table = QTableWidget()
        self.friday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.friday_table.setColumnCount(5)
        self.friday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_friday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.friday_table)
        self.friday_gbox.setLayout(self.mvbox)

    def _update_friday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='friday' order by time asc")
        records = list(self.cursor.fetchall())

        self.friday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.friday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.friday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.friday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.friday_table.setCellWidget(i, 3, joinButton)
            self.friday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'friday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.friday_table, records, 'friday'))

        addButton = QPushButton('Add')
        self.friday_table.setCellWidget(self.friday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.friday_table.rowCount() - 1, self.friday_table, 'friday'))

        self.friday_table.resizeRowsToContents()

    def _create_saturday_table(self):
        self.saturday_table = QTableWidget()
        self.saturday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.saturday_table.setColumnCount(5)
        self.saturday_table.setHorizontalHeaderLabels(["Subject", "Time", "Cabinet", "", ''])

        self._update_saturday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.saturday_table)
        self.saturday_gbox.setLayout(self.mvbox)

    def _update_saturday_table(self):
        self.cursor.execute("SELECT * FROM public.timetable WHERE day='saturday' order by time asc")
        records = list(self.cursor.fetchall())

        self.saturday_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.saturday_table.setItem(i, 0, QTableWidgetItem(str(r[2])))
            self.saturday_table.setItem(i, 1, QTableWidgetItem(str(r[3])))
            self.saturday_table.setItem(i, 2, QTableWidgetItem(str(r[4])))
            self.saturday_table.setCellWidget(i, 3, joinButton)
            self.saturday_table.setCellWidget(i, 4, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_row_from_table(num, records, 'saturday'))

            joinButton.clicked.connect(
                lambda ch, num=i: self._change_day_from_table(num, self.saturday_table, records, 'saturday'))

        addButton = QPushButton('Add')
        self.saturday_table.setCellWidget(self.saturday_table.rowCount() - 1, 3, addButton)
        addButton.clicked.connect(
            lambda: self._add_row_into_table(self.saturday_table.rowCount() - 1, self.saturday_table, 'saturday'))

        self.saturday_table.resizeRowsToContents()

    def _create_subject_tab(self):
        self.subject_tab = QWidget()
        self.tabs.addTab(self.subject_tab, "Subject")

        self.subject_gbox = QGroupBox("Subjects")
        self.s_svbox = QVBoxLayout()
        self.s_shbox1 = QHBoxLayout()
        self.s_shbox2 = QHBoxLayout()

        self.s_svbox.addLayout(self.s_shbox1)
        self.s_svbox.addLayout(self.s_shbox2)

        self.s_shbox1.addWidget(self.subject_gbox)

        self._create_subject_table()

        self.update_subject_button = QPushButton("Update")
        self.s_shbox2.addWidget(self.update_subject_button)
        self.update_subject_button.clicked.connect(self._update_shedule)

        self.subject_tab.setLayout(self.s_svbox)

    def _create_subject_table(self):
        self.subject_table = QTableWidget()
        self.subject_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.subject_table.setColumnCount(3)
        self.subject_table.setHorizontalHeaderLabels(["Subject", "", ''])

        self._update_subject_table()

        self.s_mvbox = QVBoxLayout()
        self.s_mvbox.addWidget(self.subject_table)
        self.subject_gbox.setLayout(self.s_mvbox)

    def _update_subject_table(self):
        self.cursor.execute("SELECT * FROM public.subject order by name asc")
        records = list(self.cursor.fetchall())

        self.subject_table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            deleteButton = QPushButton('Delete')

            self.subject_table.setItem(i, 0, QTableWidgetItem(str(r[1])))
            self.subject_table.setCellWidget(i, 1, joinButton)
            self.subject_table.setCellWidget(i, 2, deleteButton)

            deleteButton.clicked.connect(lambda ch, num=i: self._delete_subject(num, records))
            joinButton.clicked.connect(lambda ch, num=i: self._change_subject(num, records))

        addButton = QPushButton('Add')
        self.subject_table.setCellWidget(self.subject_table.rowCount() - 1, 1, addButton)
        addButton.clicked.connect(lambda: self._add_subject(self.subject_table.rowCount() - 1))

        self.subject_table.resizeRowsToContents()

    def _delete_subject(self, rowNum, arr):
        maxx = self.subject_table.rowCount() - 2
        self.cursor.execute("DELETE FROM subject WHERE name='%s'" % str(arr[rowNum][1]))
        self.conn.commit()

        self.subject_table.setItem(maxx, 0, QTableWidgetItem(str('')))
        self.subject_table.setItem(maxx, 2, QTableWidgetItem(str('')))
        self._update_shedule()

    def _change_subject(self, rowNum, arr):
        row = list()
        for i in range(self.subject_table.columnCount()):
            try:
                row.append(self.subject_table.item(rowNum, i).text())
            except:
                row.append(None)

        try:
            self.cursor.execute("UPDATE subject SET name=%s WHERE name=%s ", (row[0], arr[rowNum][1]))

        except:
            QMessageBox.about(self, "Error", "Enter all fields or such subject already exists")
        self.conn.commit()
        self._update_shedule()

    def _add_subject(self, rowNum):
        row = list()
        for i in range(self.subject_table.columnCount()):
            try:
                row.append(self.subject_table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("INSERT INTO subject(name) VALUES ('%s')" % row[0])
            # self.conn.commit()
        except:
            QMessageBox.about(self, 'Error', 'Enter all fields or such subject already exists')
        self.conn.commit()
        self._update_shedule()

    def _update_shedule(self):
        self._update_monday_table()
        self._update_tuesday_table()
        self._update_wednesday_table()
        self._update_thursday_table()
        self._update_friday_table()
        self._update_saturday_table()
        self._update_teacher_table()
        self._update_subject_table()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())

