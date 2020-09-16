#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 20:17:24 2020

Copyright 2020 David S. Ochs. All Rights Reserved

"""
import numpy as np
import csv
from guizero import App, Box, Text, TextBox, PushButton
import os
import smtplib, ssl
# import pathlib

class item:
    def __init__(self, item_no, label):
        self.item_no = item_no
        self.quant = 0
        self.disp_text = label

    def add_to_screen(self, box, row, col):
        self.text = Text(box, grid=[col+0, row], text=self.disp_text,
                    align="right", size=text_size)
        self.text.bg = 'white'
        self.plus = PushButton(box, grid=[col+3, row], text="+",
                               command=self.add_1, align="left", width=pm_width,
                               padx=0, pady=6)
        self.plus.bg = 'white'
        self.val = TextBox(box, grid=[col+2, row], text=str(self.quant), width=2,
                           align="left")
        self.val.bg = 'white'
        self.minus = PushButton(box, grid=[col+1, row], text="-",
                                command=self.sub_1, align="left", width=pm_width,
                                padx=0, pady=6)
        self.minus.bg = 'white'
    def add_1(self):
        self.quant += 1
        self.val.value = str(self.quant)
        update_list()

    def sub_1(self):
        if self.quant - 1 >= 0:
            self.quant -= 1
        else:
            self.quant = 0
        self.val.value = self.quant
        update_list()

def update_list():
    disp_list = list_display.value.splitlines()
    disp_list = [x.replace('\t', '') for x in disp_list]
    disp_list = [x.replace('\t', '') for x in list_display.value.splitlines()]
    custom_items = np.setdiff1d(disp_list, g_items)
    if custom_items[0] == '':
        custom_items = np.delete(custom_items, 0)

    # find items that have (#); they h will be flagged as custom by the first check
    dc = []  # double check list
    for i in custom_items:
        if i[-2].isnumeric():
            x = [j for j in range(len(i)) if i.startswith('(', j)]
            if x:
                dc.append(i[:(x[-1]-1)])
                if i[:(x[-1]-1)] in g_items:
                    custom_items = custom_items[custom_items != i]

    tmp_list = []
    d_str = ""
    for i in g_items:
        if item_d[i].quant > 0:
            if item_d[i].quant > 1:
                tmp_list.append(str(i + ' (' + str(item_d[i].quant) + ')'))
                d_str += str(i + ' (' + str(item_d[i].quant) + ')\n')
            else:
                tmp_list.append(i)
                d_str += str(i + "\n")
    for i in custom_items:
        d_str += str(i + "\n")
    list_display.value = d_str


def save_list():
    global save_name_old
    update_list()
    save_name = app.select_file(title = "Select File", save = True, filetypes=[["CSV files", ".csv"]])
    if save_name:
        try:
            tmp = save_name.split('.')
            if tmp[-1] != 'csv':
                filename = tmp[0] + '.csv'
            else:
                filename = save_name
        except:
            filename = save_name + '.csv'
            pass
        # if os.path.exists(filename):
        #     tmp_path = pathlib.Path(filename)
        #     choice = app.yesno("File Exists",
        #                        "Do you want to overwrite " + tmp_path.name + " ?")
        else:
            choice = True
        if choice:
            str_list = []
            tmp = ''
            for i in range(0, len(list_display.value)):
                if list_display.value[i] != '\n':
                    tmp += list_display.value[i]
                else:
                    if tmp:
                        str_list.append(tmp)
                    tmp = ''
            with open(filename, mode='w') as write_file:
                file_writer = csv.writer(write_file, delimiter=',')
                for i in str_list:
                    file_writer.writerow([i])
        save_name_old = save_name

def load_list():
    global save_name_old
    load_file = app.select_file(title="Select Saved List", folder=".",
                                filetypes=[["CSV files", ".csv"]])
    if load_file != '':
        clear_list()
        loaded_d = dict()
        with open(load_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                tmp = row[0]
                if tmp[-1] == ')' and (tmp[-2].isnumeric()):
                    tmp_num = int(tmp[-2])
                    if tmp[-4] == ' ': # handle space or not in custom item
                        loaded_d.update({tmp[0:-4]: tmp_num})
                    else:
                        loaded_d.update({tmp[0:-3]: tmp_num})
                else:
                    loaded_d.update({tmp: 1})
        c_str = ''
        for k, v in loaded_d.items():
            if k in item_d:
                item_d[k].quant = v
            else:
                if v > 1:
                    c_str += str(k) + " (" + str(v) + ")" + "\n"
                else:
                    c_str += str(k + "\n")
        list_display.value = c_str
        update_list()
        save_name_old = load_file

def clear_list():
    for n in item_d.values():
        n.quant = 0
        n.val.value = "0"
    list_display.value = ''
    update_list()

def ask_clear_list():
    if app.yesno("Clear", "Do you want to clear the list?"):
        clear_list()

def load_store(store):
    global num_pages, page_no
    ret_val = dict()
    if store == 'ask':
        load_file = app.select_file(title="Select Store", folder=".",
                                    filetypes=[["CSV files", ".csv"]])
    elif store[-4:]:
        load_file = store
    else:
        app.error('Incorrect File', 'Incorrect file type selected')

    if 'load_file' in locals():
        items = []
        with open(load_file, encoding='utf-8-sig') as csv_file:  # handle csv's saved by excel
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                items.append(row[0])

        items = [x.replace('\t', '') for x in items]
        # TODO: handle cases where I load a store with fewer items that were previously loaded
        r = 0
        c = 0
        c_cnt = 0
        sorted_items = sorted(items)
        ino = 1
        added = 0
        for i in sorted_items:
            ret_val.update({i: item(ino, i)})
            ino += 1
            ret_val[i].add_to_screen(content_boxes[page_no], r, c)
            r += 1
            c_cnt += 1
            if np.mod(c_cnt, column_limit) == 0:
                c += 4
                c_cnt = 0
                r = 0
            added += 1
            if added >= page_limit:
                content_boxes[page_no].visible = False
                r = 0
                c = 0
                c_cnt = 0
                added = 0
                content_boxes.append(Box(app, align="top", layout="grid",
                                         width="fill", border=False))
                page_no += 1
                content_boxes[page_no].tk.configure(background='white')
    return items, ret_val

def page_change(dir):
    global page_no
    if dir > 0 and page_no < len(content_boxes):
        content_boxes[page_no].visible = False
        page_no += 1
        content_boxes[page_no].visible = True
    elif dir < 0 and page_no >= 1:  # backwards
        content_boxes[page_no].visible = False
        page_no -= 1
        content_boxes[page_no].visible = True

def load_store_clear():
    global g_items, item_d
    item_d.clear()
    g_items = []
    g_items, item_d = load_store('ask')
    clear_list()

def closing_action():
    if app.yesno("Close", "Do you want to save the list before closing?"):
        save_list()
    app.destroy()

def email_list():
    receiver_email = app.question("Enter Email", "Enter Email Address")
    if receiver_email:
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        subject = "Subject: Your Sorted Shopping List\n"
        message = subject + list_display.value
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


page_limit = 40
column_limit = 20
last_item = 0
text_size = 16
save_name_old = ''
pm_width = 1
app = App(title="Grocery List Sorter", height=1200, width=920,
          bgcolor='white')

buttons_box = Box(app, width="fill", align="bottom", border=True)
PushButton(buttons_box, text="Load Store", command=load_store_clear, align="left")
PushButton(buttons_box, text="Save List", command=save_list, align="left")
PushButton(buttons_box, text="Load List", command=load_list, align="left")
PushButton(buttons_box, text="Clear List", command=ask_clear_list, align="left")
PushButton(buttons_box, text="Next Page", command=page_change, args = [1], align="right")
PushButton(buttons_box, text="Previous Page", command=page_change, args = [-1], align="right")

list_box = Box(app, height="fill", align="right", border=True)
list_display = TextBox(list_box, multiline=True, scrollbar=True, height="fill",
                       width=30, align="left", text="")
list_display.text_size = text_size

content_boxes = []
content_boxes.append(Box(app, align="top", layout="grid", width="fill", border=False))
content_boxes[0].tk.configure(background='white')
page_no = 0

default_store = 'stores/Lawrence_Aldi.csv'
g_items, item_d = load_store(default_store)
while page_no > 0:
    page_change(-1)
app.when_closed = closing_action

# Set up email service
if os.path.exists('credentials.txt'):
    with open('credentials.txt', 'r') as f:
        sender_email = f.readline()
        password = f.readline()
    sender_email = sender_email[:-1]
    password = password[:-1]

    # Add a send email button
    PushButton(buttons_box, text="Email List", command=email_list, align="left")
app.display()
