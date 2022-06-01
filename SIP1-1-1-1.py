#!/usr/bin/python3
# -- coding: utf-8 --
# @Author : Long.Hou
# @Email : Long2.Hou@luxshare-ict.com
# @File : SIP1-1-1-1.py
# @Project : H28_SIP1_1_1_!
# @Time : 2022/5/30 10:04
# -------------------------------
import os.path
from threading import Thread
from logHelper import *
import serial
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import json, csv, time, socket
from PIL import Image, ImageTk


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_test_plan_csv(filename):
    with open(filename, 'r') as f:
        datas = []
        reader = csv.reader(f)
        reader = list(reader)
        header = reader[0]
        for row in reader[1:]:
            data = {}
            for i in range(len(header)):
                data[header[i]] = row[i]
            datas.append(data)
        return datas


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.site_num = None
        self.master = master
        try:
            self.test_items = read_test_plan_csv(data['test_plan_file'])
        except FileNotFoundError:
            # 消息提升框
            messagebox.showerror(title='Error', message='Test plan file not found!\nPlease check the file path!')
            exit()
        try:
            self.term = serial.Serial(data['serial_port'], 115200, timeout=0.5)
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((data['server_ip'], data['server_port']))
        except Exception as e:
            # 消息提升框
            messagebox.showerror(title='Error',
                                 message='Serial port error!\nPlease check the serial port! Error: %s' % e)
            exit()
        self.setup_init()
        self.config(bg='gray')
        self.pack()
        self.create_widgets()
        self.serial_socket_init()


    # 绘图函数
    def create_widgets(self):
        self.top_widget_init()
        self.bottom_widget_init()
        self.main_widget_init()
        self.menu_bar_init()

    def top_widget_init(self):
        f1 = tk.Frame(self, relief='solid', height=170, width=1360, bg='Gainsboro')
        f1.pack(side='top', fill=tk.X)
        # 显示测试良率信息
        for i in range(2):
            f1_1 = tk.Frame(f1, relief='solid', height=130, width=250, borderwidth=0.5)
            tk.Label(f1_1, textvariable=self.slot_args_list[i]['str_var'][0]).place(x=10, y=10)
            tk.Label(f1_1, textvariable=self.slot_args_list[i]['str_var'][1]).place(x=10, y=50)
            tk.Label(f1_1, textvariable=self.slot_args_list[i]['str_var'][2]).place(x=10, y=90)
            # 设置label的字体为黑色加粗17号
            tk.Label(f1_1, text="工位{}".format(i + 1), font=('Arial', 17, 'bold')).place(x=150, y=20)
            # 设置按钮为透明
            tk.Button(f1_1, text='Clear Count', height=2, bg='Gainsboro',
                      command=lambda i=i: self.clear_count(i)).place(x=140, y=70)
            f1_1.place(x=150 + i * 280, y=80, anchor='center')
        # 显示测试时间label
        tk.Label(f1, textvariable=self.ct_string_var, bg='Gainsboro', font=('Arial', 27, 'bold')).place(x=630, y=30)
        tk.Label(f1, textvariable=self.pdca_string_var, bg='Gainsboro', font=('Arial', 27, 'bold')).place(x=800, y=30)
        # 显示SN label
        tk.Label(f1, text='Serial Number', bg='Gainsboro').place(x=630, y=86)
        # 显示SN entry
        tk.Entry(f1, width=30, textvariable=self.sn_string_var, font=('Arial', 15, 'bold')).place(x=630, y=110)
        # 显示测试名称 label
        tk.Label(f1, text=data['station_name'], font=('Arial', 19, 'bold')).place(x=1000, y=10)
        self.img_open1 = Image.open("luxshare2.png")
        size = 290, 150
        self.img_open1.thumbnail(size)
        self.img_png1 = ImageTk.PhotoImage(self.img_open1)
        tk.Label(f1, image=self.img_png1).place(x=1000, y=45)

    def main_widget_init(self):
        f1 = tk.Frame(self, relief='solid', height=800, width=1360, borderwidth=0.5)
        f1.pack(side='bottom')
        headers = ['NO', 'TestItem', 'Upper', 'Lower']
        for i in range(14):
            headers.append("Slot{}".format(i + 1))
        self.test_table = ttk.Treeview(f1, show="headings", height=22, columns=headers, )
        for header in headers:
            if header == "NO":
                self.test_table.column(header, width=25, anchor='center')
                self.test_table.heading(header, text=header)
            elif header == 'TestItem':
                self.test_table.column(header, width=120, anchor='center')
                self.test_table.heading(header, text=header)
            else:
                self.test_table.column(header, width=76, anchor='center')
                self.test_table.heading(header, text=header)
        self.test_table.pack(fill=tk.BOTH)
        i = 0
        for item in self.test_items:
            if item["Enable"]:
                self.test_table.insert('', index=i, values=(item["NO"], item["TestItem"], item["Upper"], item["Lower"]))
                i += 1
        # 遍历表格的item,加背景色
        for i, item in enumerate(self.test_table.get_children()):
            if i % 2 == 0:
                self.test_table.item(item, tags='even')
                self.test_table.tag_configure('even', background="#f0f0f0")
            else:
                self.test_table.item(item, tags="odd")
                self.test_table.tag_configure('odd', background='white')

    def bottom_widget_init(self):
        f1 = tk.Frame(self, relief='solid', height=30, width=1360, bg='Gainsboro')
        f1.pack(side='top', fill=tk.X)
        # 显示测试结果label
        for i in range(14):
            b = tk.Label(f1, text="Ready", width=7, bg='Cyan')
            b.place(x=305 + i * 76, y=0)
            self.result_label_list.append(b)

    # 菜单栏
    def menu_bar_init(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Setting", command=self.open_password)
        filemenu.add_command(label="About", command=self.open_show_information)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="Menu", menu=filemenu)
        self.master.config(menu=menubar)

    # 设置窗口
    def setting_widget(self):
        pdca_window = tk.Toplevel(self)
        pdca_window.title(" Setting")
        pdca_window.geometry('1000x600+180+40')
        pdca_window.resizable(False, False)
        pdca_window.wm_attributes('-topmost', 1)
        pdca_window.wait_window()

    # 接口函数
    def setup_init(self):
        self.log = LogHelper('admin', logging.DEBUG)
        self.site_num = 0
        self.result_label_list = []
        self.slot_args_list = []
        self.ct_num = 0
        self.ct_string_var = tk.StringVar(self)
        self.ct_string_var.set('CT: {}'.format(self.ct_num))
        self.pdca_string_var = tk.StringVar(self)
        self.pdca_string_var.set('PDCA' if data['PDCA_mode'] else 'NOPDCA')
        self.sn_string_var = tk.StringVar(self)
        self.sn_string_var.set('')
        for i in range(2):
            pass_num = data['pass_number_site{}'.format(i + 1)]
            fail_num = data['fail_number_site{}'.format(i + 1)]
            pass_str = tk.StringVar()
            pass_str.set('PASS Qty: {}'.format(pass_num))
            fail_str = tk.StringVar()
            fail_str.set('FAIL Qty: {}'.format(fail_num))
            yield_num = tk.StringVar()
            try:
                yield_num.set('Yield: {:.2f}%'.format(pass_num / (pass_num + fail_num) * 100))
            except ZeroDivisionError:
                yield_num.set('Yield: 100%')
            self.slot_args_list.append({"str_var": [pass_str, fail_str, yield_num], "num_var": [pass_num, fail_num]})

    def add_pass_num(self, site_num):
        self.slot_args_list[site_num]['num_var'][0] += 1
        self.slot_args_list[site_num]['str_var'][0].set(
            'PASS Qty: {}'.format((self.slot_args_list[site_num]['num_var'][0])))
        self.slot_args_list[site_num]['str_var'][2].set(
            'Yield: {:.2f}%'.format(self.slot_args_list[site_num]['num_var'][0] /
                                    (self.slot_args_list[site_num]['num_var'][1] +
                                     self.slot_args_list[site_num]['num_var'][
                                         0]) * 100))

    def add_fail_num(self, site_num):
        self.slot_args_list[site_num]['num_var'][1] += 1
        self.slot_args_list[site_num]['str_var'][1].set(
            'FAIL Qty: {}'.format(self.slot_args_list[site_num]['num_var'][1]))
        self.slot_args_list[site_num]['str_var'][2].set(
            'Yield: {:.2f}%'.format(self.slot_args_list[site_num]['num_var'][0] /
                                    (self.slot_args_list[site_num]['num_var'][1] +
                                     self.slot_args_list[site_num]['num_var'][
                                         0]) * 100))

    def clear_count(self, site_num):
        self.slot_args_list[site_num]['num_var'][0] = 0
        self.slot_args_list[site_num]['num_var'][1] = 0
        self.slot_args_list[site_num]['str_var'][0].set('PASS Qty: 0')
        self.slot_args_list[site_num]['str_var'][1].set('FAIL Qty: 0')
        self.slot_args_list[site_num]['str_var'][2].set('Yield: 100%')

    def set_test_result_to_label(self, slot_index, result):
        if result == 'PASS':
            self.result_label_list[slot_index].config(bg='green')
        else:
            self.result_label_list[slot_index].config(bg='red')
        self.result_label_list[slot_index].config(text=result)

    def set_result_label_testing(self, slot_index):
        self.result_label_list[slot_index].config(text='Testing')
        self.result_label_list[slot_index].config(bg='yellow')

    def open_password(self):
        self.pass_word = tk.StringVar()
        self.f = tk.Toplevel(self)
        self.f.title('Password')
        self.f.geometry("{}x{}+{}+{}".format(250, 90, 680, 320))
        self.f.resizable(False, False)
        tk.Label(self.f, font=('Arial', 9)).pack()
        tk.Entry(self.f, textvariable=self.pass_word, show='*').pack()
        tk.Label(self.f, font=('Arial', 6)).pack()
        tk.Button(self.f, text='确认', font=('Arial', 13), height=1, width=5,
                  command=self.judge_password).pack()

    def open_show_information(self):
        # 显示作者消息
        f = tk.Toplevel(self)
        f.title('Information')
        f.geometry("{}x{}+{}+{}".format(250, 240, 680, 320))
        f.resizable(width=0, height=0)
        tk.Label(f, font=('Arial', 13)).pack(anchor=tk.CENTER)
        tk.Label(f, font=('Arial', 13), text='H28 SIP 测试工装1').pack(anchor=tk.CENTER)
        tk.Label(f, font=('Arial', 13), text='作者：侯龙').pack(anchor=tk.CENTER)
        tk.Label(f, font=('Arial', 13), height=2, text='邮箱：long2.hou@luxshare-ict.com').pack(anchor=tk.CENTER)
        self.img_open = Image.open("information.png")
        size = 290, 150
        self.img_open.thumbnail(size)
        self.img_png = ImageTk.PhotoImage(self.img_open)
        tk.Label(f, image=self.img_png).pack(anchor=tk.CENTER)

    def judge_password(self, ):
        if self.pass_word.get() == "admin":
            # 退出密码输入窗口
            self.f.destroy()
            self.setting_widget()

        else:
            # 密码错误提示，消息提示
            messagebox.showerror('Error', '密码错误！')

    def serial_socket_init(self):
        if self.term.is_open:
            self.term.write('PC_READY\n'.encode('utf-8'))
            time.sleep(0.5)
            if 'PASS' not in self.term.readall().decode('utf-8'):
                messagebox.showerror('Error', '串口通信失败！')
                self.term.close()
                exit()
        self.client.send('PC_READY\n'.encode('utf-8'))
        if 'PASS' not in self.client.recv(1024).decode('utf-8'):
            messagebox.showerror('Error', '网口通信失败！')
            self.term.close()
            self.client.close()
            exit()
        messagebox.showinfo('Info', '设备初始化成功！')

    def socket_thread(self):
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if data == 'START1 PASS':
                    if self.sn_string_var.get() == '':
                        continue
                    log_path = '{}/{}'.format(data['LogPath'], time.strftime('%Y-%m-%d', time.localtime()))
                    if not os.path.exists(log_path):
                        os.makedirs(log_path)
                    self.log.create_new_log('{}/{}-{}-1#.log'.format(log_path, self.sn_string_var.get(),
                                                                     time.strftime('%H-%M-%S',
                                                                                   time.localtime(time.time()))))
                    self.site_num = 0
                    time.sleep(0.5)
                    self.client.send('GET_RESULT'.encode('utf-8'))
                    self.log.send_log('GET_RESULT')
                    start_time = time.time()
                    text = ''
                    while True:
                        line = self.client.recv(1024).decode('utf-8')
                        self.log.receive_log(line)
                        text += line
                        if 'DATA_FINISH' in line:
                            break
                        text += line
                        if time.time() - start_time > 20:
                            break
                    self.client.send('CYLINDER UP\n'.encode('utf-8'))
                    self.log.send_log('CYLINDER UP')
                    time.sleep(0.5)
                    data = self.client.recv(1024).decode('utf-8')
                    self.log.receive_log(data)
                    if 'PASS' in data:
                        self.dispose_data(text,0)
                elif data == 'START2 PASS':
                    if self.sn_string_var.get() == '':
                        continue
                    log_path = '{}/{}'.format(data['log_path'], time.strftime('%Y-%m-%d', time.localtime()))
                    if not os.path.exists(log_path):
                        os.makedirs(log_path)
                    self.log.create_new_log('{}/{}-{}-1#.log'.format(log_path, self.sn_string_var.get(),
                                                                     time.strftime('%H-%M-%S',
                                                                                   time.localtime(time.time()))))
                    self.site_num = 1
            except Exception as e:
                print(e)

    def serial_thread(self):
        while True:
            try:
                if self.site_num == 1:
                    time.sleep(1)
                    self.term.write('GET_RESULT\n'.encode('utf-8'))
                    self.log.send_log('GET_RESULT')
                    txt = ''
                    start_time = time.time()
                    while True:
                        line = self.term.readline().decode('utf-8')
                        self.log.receive_log(line)
                        txt += line
                        if 'DATA_FINISH' in line:
                            break
                        if time.time() - start_time > 20:
                            break
                    self.term.write('CYLINDER UP\n'.encode('utf-8'))
                    self.log.send_log('CYLINDER UP')
                    time.sleep(0.5)
                    data = self.term.readall().decode('utf-8')
                    self.log.receive_log(data)
                    if 'PASS' in data:
                        self.dispose_data(txt, 1)
            except Exception as e:
                print(e)

    def dispose_data(self, d,site):
        i1 = 0
        for item in self.test_items:
            temp = hex(i1 + 1).upper()
            if len(temp) < 4:
                index = 'I00{}'.format(temp[-1:])
            else:
                index = 'I0{}'.format(temp[-2:])
            if item['Enable']:
                self.log.item_start(item['TestItem'])
                if item["Mode"] == 'Compare':
                    for x in range(14):
                        try:
                            a = str(x + 1) if x > 8 else '0' + str(x + 1)
                            flag = '{}{}='.format(item['StartFlag'], a)
                            start_index = d.find(flag) + len(flag)
                            end_index = str(d[start_index:]).find(item['EndFlag']) + start_index
                            if start_index == -1 or end_index == -1:
                                self.test_table.selection_set(index)
                                self.test_table.set(item=index, column=4 + x, value='-FAIL-')
                                self.log.set_item_result('start_index:{},end_index:{}'.format(start_index,end_index),
                                                         'PASS', x + 1, item['Lower'], item['Upper'])
                                self.add_fail_num(site)
                                continue
                            value = d[start_index:end_index]
                            if float(item['Lower']) <= float(value) <= float(item['Upper']):
                                self.test_table.selection_set(index)
                                self.add_pass_num(site)
                                self.test_table.set(item=index, column=4 + x, value=value)
                                self.log.set_item_result(value, 'PASS', x + 1, item['Lower'], item['Upper'])
                            else:
                                self.test_table.selection_set(index)
                                self.add_fail_num(site)
                                self.test_table.set(item=index, column=4 + x, value='-FAIL-')
                                self.log.set_item_result(value, 'FAIL', x + 1, item['Lower'], item['Upper'])
                        except Exception as e:
                            self.add_fail_num(site)
                            self.log.set_item_result(str(e), 'FAIL', x + 1, item['Lower'], item['Upper'])
                            self.test_table.selection_set(index)
                            self.test_table.set(item=index, column=4 + x, value='-FAIL-')
                            continue
                elif item['Mode'] == 'Skip':
                    for i in range(14):
                        self.test_table.selection_set(index)
                        self.test_table.set(item=index, column=4 + i, value='PASS')
                        self.log.set_item_result('PASS', 'PASS', i + 1,item['Lower'], item['Upper'])

                i1 += 1
                self.log.item_end(item['TestItem'])
                time.sleep(0.3)


if __name__ == '__main__':
    data = read_json("config.json")
    root = tk.Tk()
    root.title('SIP1-1-1-1')
    root.geometry("{}x{}".format(1366, 768 - 120))
    root.resizable(False, False)
    # 设置背景为灰色
    # root.config(bg='gray')
    app = Application(master=root)
    app.mainloop()
