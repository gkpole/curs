#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import telebot
import config
def search(str2, h):
    vault = ar_vault[h]
    index = str2.find(vault)
    if str2[index - 1].isdigit():
        last = index
        first = 0
        m = 1
        j = True
        while j:
            if str2[index - m].isdigit():
                m = m + 1
                j = True
            else:
                j = False
                first = index - m + 1
    print(str2[last:])
    return int(str2[first:last])

def change_vaults(money, h):
    #ar_vault = ["грн", "руб", "гривен", "р.", "дол", "бакс"]
    s=""
    if h == 1 or h == 3 or h==7:
        #print(type(money))
        ua = round(money * 0.39, 2)
        en = round(money * 0.015, 2)
        s = str(money) + " RUB:" + "\n" + "\n" + "-" + str(ua) + " UAH" + "\n" + "-" + str(en) + " USD"
    elif h == 0 or h == 2:
        #print("ua")
        ru = round(money * 2.57, 2)
        en = round(money * 0.038, 2)
        s = str(money) + " UAH:" + "\n" + "\n" + "-" + str(ua) + " RUB" + "\n" + "-" + str(en) + " USD"
    elif h == 4 or h == 5 or h==6:
        #print("en")
        ru = round(money * 68.32, 2)
        ua = round(money * 26.58, 2)
        s = str(money) + " USD:" + "\n" + "\n" + "-" + str(ua) + " RUB" + "\n" + "-" + str(en) + " UAH"
    return s

def delete_space(message):
    s = message.text
    s = s.replace(' ', '')
    return s    

def check_for_numbers(r):
    k = False
    for i in r:
        if i.isdigit():
            k = True
            break
    return k

def check_vault(str1):
    global ar_vault
    ar_vault = ["грн", "руб", "гривен", "р.", "дол", "бакс","$","₽"] #made global to avoid futher confusion
    r = [] #contain all currencies that were found in message
    for cur in range(len(ar_vault)):
        if str1.find(ar_vault[cur]) != -1:
            r.append(cur)
    return r