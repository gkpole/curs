
# Public libraries
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread
import sys
from datetime import datetime
import time
import os

# Own libraries
import DBH
from NewPrint import Print, EnableLogging, DisableLogging, PrintMainInfo
from SkipUpdates import EnableUpdates, DisableUpdates, IsUpdate
from GetExchangeRates import SheduleUpdate, SheduleCryptoUpdate 
from BlackList import IsUserInBlackList, LoadBlackList, RemoveFromBlackList, AddToBlackList
import Processing
from Processing import AnswerText, LoadCurrencies, LoadCrypto, LoadDictionaries, LoadFlags, SearchValuesAndCurrencies, SpecialSplit, TextToDigit, RemoveLinksAndWords
import TextHelper as CustomMarkup
from TextHelper import LoadTexts, GetText
import ListsCache
import StopDDoS

# Main variables
bot = Bot(token=botToken)
dp = Dispatcher(bot)
IsStartedCount = False

botToken = "5963665229:AAGAwdVf61gOMipqHvGH_1Ia03KAUH5sWzQ"
botUsername = "Conventortgbot"

numberizerUA = numberize.Numberizer(lang='uk')
numberizerRU = numberize.Numberizer(lang='ru')
numberizerEN = numberize.Numberizer(lang='en')

# Public commands
@dp.message_handler(commands=['about'])  # analog about and source
async def AboutMes(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    IsChatExist(chatID, chatType)
    await message.reply(GetText(chatID, "about", chatType), reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['help'])
async def HelpMes(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    IsChatExist(chatID, chatType)
    await message.reply(GetText(chatID, "help", message.chat.type), reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

def CanUserEditSettings(chatID: str, chatType: str, memberStatus: str, userID: str, userName: str, AllMembersAreAdministrators: bool = False) -> bool:
    сanUserEditSettings = False
    AllChatSettings = DBH.GetAllSettings(chatID, chatType)
    if DBH.IsAdmin(userID):
        сanUserEditSettings = True
    elif chatType == "private":
        сanUserEditSettings = True
    else:
        whoCanEditSettings = AllChatSettings['editSettings']
        if whoCanEditSettings == "everybody":
            сanUserEditSettings = True
        elif chatType == "group":
            if AllMembersAreAdministrators == True and whoCanEditSettings == 'admins':
                сanUserEditSettings = True
            elif AllMembersAreAdministrators == True and whoCanEditSettings == 'creator':
                if memberStatus == 'creator' or userName == "GroupAnonymousBot":
                    сanUserEditSettings = True
            elif AllMembersAreAdministrators == False:
                if whoCanEditSettings == 'admins' and (memberStatus == "administrator" or memberStatus == "creator" or userName == "GroupAnonymousBot") or whoCanEditSettings == 'creator' and (memberStatus == "creator" or userName == "GroupAnonymousBot"):
                    сanUserEditSettings = True
        elif chatType == "supergroup":
            if whoCanEditSettings == 'admins' and (memberStatus == "administrator" or memberStatus == "creator" or userName == "GroupAnonymousBot") or whoCanEditSettings == 'creator' and (memberStatus == "creator" or userName == "GroupAnonymousBot"):
                сanUserEditSettings = True
    return сanUserEditSettings

@dp.message_handler(commands=['settings'])
async def SettingsMes(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
    userName = message.from_user.username
    if IsUserInBlackList(fromUserId, chatID):
        return
    IsChatExist(chatID, chatType)
    
    member = await message.chat.get_member(fromUserId)
    if CanUserEditSettings(chatID, chatType, member.status, message.from_user.id, userName, message.chat.all_members_are_administrators):
        await message.reply(GetText(chatID, "main_settings_menu", chatType), reply_markup = CustomMarkup.SettingsMarkup(chatID, chatType))
    else:
        await message.reply(GetText(chatID, "error_main_settings_menu", chatType), reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['donate'])
async def DonateMes(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
    if IsUserInBlackList(fromUserId, chatID):
        return
    IsChatExist(chatID, message.chat.type)
    await message.reply(GetText(chatID, "donate", chatType), reply_markup = CustomMarkup.DonateMarkup(chatID, chatType))

@dp.message_handler(commands=['wrong'])
async def WrongMes(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
    
    if IsUserInBlackList(fromUserId, chatID):
        return
    IsChatExist(chatID, chatType)
    try:
        MessageText = message.reply_to_message.text
    except:
        Print("Wrong mes error", "E")
        if message.photo or message.video is not None or message.document is not None:
            MessageText = message.reply_to_message.caption
    DBH.AddReport(chatID, fromUserId, MessageText)

# Admin`s commands
@dp.message_handler(commands=['echo'])
async def EchoVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        MessageToUsers = (message.text).replace("/echo ", "")
        adminList = DBH.GetAdmins()
        for i in adminList:
            await bot.send_message(i, "Начата рассылка сообщения всем пользователям. Текст сообщения:\n\n" + MessageToUsers, reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
        listGC = DBH.GetGroupChatIDs()
        for i in listGC:
            try:
                await bot.send_message(i, MessageToUsers, reply_markup = CustomMarkup.DonateMarkup(i, "group"))
            except:
                Print("Chat " + str(i) + " is not available.", "W")
            time.sleep(0.035)
        listPC = DBH.GetPrivateChatIDs()
        for i in listPC:
            try:
                await bot.send_message(i, MessageToUsers, reply_markup = CustomMarkup.DonateMarkup(i, "private"))
            except:
                Print("Chat " + str(i) + " is not available.", "W")
            time.sleep(0.035)
        for i in adminList:
            await bot.send_message(i, "Рассылка закончена.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))

@dp.message_handler(commands=['write'])
async def EchoVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        MessageToUsers = (message.text).replace("/write ", "")
        index = MessageToUsers.find(" ")
        toChatID = MessageToUsers[0:index]
        print(toChatID)
        MessageToUsers = MessageToUsers.replace(str(chatID) + " ", "")
        try:
            await bot.send_message(toChatID, MessageToUsers)
            await bot.send_message(fromUserId, "Сообщение отправлено.")
        except:
            await bot.send_message(fromUserId, "Не удалось отправить сообщение.")
       

@dp.message_handler(commands=['count'])  # Analog of "count".
async def CountVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    global IsStartedCount
    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        if not IsStartedCount:
            isShortVariant = False
            Variant = (message.text).replace("/count", "").replace(" ", "")
            if Variant == "short":
                isShortVariant = True
            adminList = DBH.GetAdmins()
            for i in adminList:
                if not isShortVariant:
                    await bot.send_message(i, "Начат подсчёт количества участников всех чатов.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
                else:
                    await bot.send_message(i, "Начат подсчёт количества участников групповых чатов.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
            IsStartedCount = True
            CountUsers = 0
            listGC = DBH.GetGroupChatIDs()
            for i in listGC:
                try:
                    CountUsers += await bot.get_chat_members_count(i)
                except:
                    Print("Chat " + str(i) + " not found.", "W")
                time.sleep(0.035)
                IsStartedCount = False
            if not isShortVariant:
                IsStartedCount = True
                listPC = DBH.GetPrivateChatIDs()
                for i in listPC:
                    try:
                        CountUsers += await bot.get_chat_members_count(i) - 1
                    except:
                        Print("Chat " + str(i) + " not found.", "W")
                    time.sleep(0.035)
                IsStartedCount = False
            for i in adminList:
                if not isShortVariant:
                    await bot.send_message(i, "Количество участников всех чатов: " + str(CountUsers), reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
                else:
                    await bot.send_message(i, "Количество участников групповых чатов: " + str(CountUsers), reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
        else:
            await message.reply("Подсчёт уже начат.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['newadmin']) 
async def AddAdminVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        newAdminID = message.text
        newAdminID = newAdminID.replace("/newadmin ", "")
        if newAdminID.isdigit():
            if not DBH.IsAdmin(newAdminID):
                DBH.AddAdmin(int(newAdminID))
                ListOfAdmins = DBH.GetAdmins()
                if newAdminID in ListOfAdmins:
                    await message.reply("Новый администратор успешно добавлен.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
                else:
                    await message.reply("Не удалось добавить нового администратора.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
            else:
                await message.reply("Данный ID уже есть в списке администраторов.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
        else:
            await message.reply("В ID должны быть только цифры и возможно минус.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['stats'])
async def StatsVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
    
    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        chatStats = DBH.GetChatsAmount()
        answerMes = "ЛС: " + str(chatStats['private']) + "\nГруппы: " + str(chatStats['groups'])
        await message.reply(answerMes, reply_markup=CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['fullstats'])
async def FullStatsVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        chatStats = DBH.GetTimeStats()
        StatsByOneDay = DBH.GetStatsInPeriod(1)
        answerMes = "За всё время:\nЛС: " + str(chatStats['private']) + "\nГруппы: " + str(chatStats['groups']) + "\n\nЗа сутки:\nЛС: " + str(StatsByOneDay['activePrivate']) + "\nГруппы: " + str(StatsByOneDay['activeGroups']) + "\n\nЗа неделю:\nЛС: " + str(chatStats['activePrivateWeek']) + "\nГруппы: " + str(chatStats['activeGroupsWeek']) + "\n\nЗа 30 дней:\nЛС: " + str(chatStats['activePrivateMonth']) + "\nГруппы: " + str(chatStats['activeGroupsMonth'])
        await message.reply(answerMes, reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['backup']) # analog "backup", "logs" and "reports".
async def BackupVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
    
    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        nameOfBackup = DBH.CreateAllBackups()
        fileSize = os.path.getsize(nameOfBackup)
        if fileSize <= 5242880:
            try:
                backupFile = open(nameOfBackup, 'rb')
                await bot.send_document(chatID, backupFile)
            except:
                await message.reply("Не удалось отправить файл.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
        else:
            await message.reply("Файл слишком велик. Его вес " + str(fileSize) + " Байт.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['unban'])
async def UnbanVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        unbanID = message.text
        unbanID = unbanID.replace("/unban ", "")
        if unbanID.isdigit():
            if DBH.IsBlacklisted(int(unbanID)):
                RemoveFromBlackList(int(unbanID))
                if not DBH.IsBlacklisted(int(unbanID)):
                    await message.reply("Пользователь успешно разблокирован.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
                else:
                    await message.reply("Не удалось разблокировать пользователя.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
            else:
                await message.reply("Данный пользователь не находится в ЧС. Разблокировка не возможна.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
        else:
            await message.reply("В ID должны быть только цифры и минус.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

@dp.message_handler(commands=['ban'])
async def UnbanVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type

    if IsUserInBlackList(fromUserId, chatID):
        return
    if DBH.IsAdmin(fromUserId):
        banID = message.text
        banID = banID.replace("/ban ", "")
        if banID.isdigit() or (banID[1:].isdigit() and banID[0] == '-'):
            if not DBH.IsBlacklisted(int(banID)):
                AddToBlackList(int(banID), chatID, chatID)
                if DBH.IsBlacklisted(int(banID)):
                    await message.reply("Пользователь/чат успешно заблокирован.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
                else:
                    await message.reply("Не удалось заблокировать пользователя/чат.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
            else:
                await message.reply("Данный пользователь/чат находится в ЧС. Блокировка не возможна.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
        else:
            await message.reply("В ID должны быть только цифры и минус.", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))

# Technical commands
@dp.message_handler(commands=['start'])
async def StartVoid(message: types.Message):
    chatID = message.chat.id
    chatType = message.chat.type
    fromUserId = message.from_user.id
    if IsUserInBlackList(fromUserId, chatID):
        return

    IsChatExist(chatID, chatType)
    if chatType == "private":
        await message.reply(GetText(chatID, "main_settings_menu", chatType), reply_markup = CustomMarkup.SettingsMarkup(chatID, chatType))

@dp.message_handler(content_types=ContentType.ANY)
async def MainVoid(message: types.Message):
    fromUserId = message.from_user.id
    chatID = message.chat.id
    chatType = message.chat.type
 
    def w2n(MesString: str, lang: str):
        if lang == "ua":
            return numberizerUA.replace_numerals(MesString)
        elif lang == "ru":
            return numberizerRU.replace_numerals(MesString)
        else:
            return numberizerEN.replace_numerals(MesString)

    try:
        if message.forward_from.username == botUsername:
            return
    except:
        pass

    # Checking if a user is on the blacklist
    if IsUserInBlackList(fromUserId, chatID):
        return

    # Get message text
    MessageText = message.text
    if message.photo or message.video is not None or message.document is not None:
        MessageText = message.caption
    if MessageText is None or MessageText == "":
        return

    # Logging basic information to terminal
    PrintMainInfo(message, MessageText)

    # Checking the chat in the database
    IsChatExist(chatID, chatType)

    # word to num
    OriginalMessageText = MessageText
    MessageText = MessageText.lower()
    MessageText = RemoveLinksAndWords(MessageText)
    MessageText = w2n(MessageText, 'ru')
    MessageText = w2n(MessageText, 'uk')
    MessageText = w2n(MessageText, 'en')
    Print(MessageText, "L")

    # Check digit
    if not any(map(str.isdigit, MessageText)):
        return

    # Preparing a message for searching currencies
    try:
        TextArray = SpecialSplit(MessageText)
    except:
        Print("Error split.", "E")
        return
    Print(str(TextArray), "L")

    # '5kk USD' to '5000000 USD'
    TextArray = TextToDigit(TextArray)
    Print(str(TextArray), "L")
    
    # Searching Currencies
    NumArray = SearchValuesAndCurrencies(TextArray)
    Print(str(NumArray), "L")

    # If there are no currencies, then work is interrupted
    if NumArray == [[],[],[],[]]:
        return
        
    if StopDDoS.updateData(fromUserId, chatID, len(NumArray[1]) + len(NumArray[3]), message.chat.title):
        await message.reply(GetText(chatID, 'added_to_bl', chatType))
        ListAdmins = DBH.GetAdmins()
        for i in ListAdmins:
            await bot.send_message(i, "Пользователь " + str(fromUserId) + " заблокирован. Его возможное имя пользователя: @" + str(message.from_user.username), reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
        return
    
    result = AnswerText(NumArray, chatID, chatType)
    try:
        await message.reply(result, parse_mode = "HTML", reply_markup = CustomMarkup.DeleteMarkup(chatID, chatType))
    except:
        Print("Cannot send message", "E")
        Print("Username: " + str(message.from_user.username) + " | User ID: " + str(message.from_user.id) + " | First name: " + str(message.from_user.first_name) + " | Last name: " + str(message.from_user.last_name), "E")
        Print("Chat ID: " + str(message.chat.id) + " | Chat name: " + str(message.chat.title) + " | Chat username: "+str(message.chat.username) + " | Chat type: "+str(message.chat.type), "E")
        Print("Message: " + str(OriginalMessageText), "E")
    DBH.UpdateChatUsage(chatID)
    # for i in NumArray[1]:
    #     DBH.ProcessedCurrency(chatID, fromUserId, ListsCache.GetListOfCur()[i], OriginalMessageText)
    # for i in NumArray[3]:
    #     DBH.ProcessedCurrency(chatID, fromUserId, ListsCache.GetListOfCrypto()[i], OriginalMessageText)

@dp.callback_query_handler(lambda call: True)
async def CallbackAnswer(call: types.CallbackQuery):
    fromUserId = call.from_user.id
    chatID = call.message.chat.id
    chatType = call.message.chat.type
    callData = call.data
    allAdmins = call.message.chat.all_members_are_administrators
    userName = call.from_user.username

    if IsUserInBlackList(call.message.from_user.id, chatID):
        return
    if callData == "delete":
        CanUserDeleteMes = False
        if chatType == "private":
            CanUserDeleteMes = True
        else:
            whoCanDeleteMes = DBH.GetSetting(chatID, "deleteRules", chatType)
            if whoCanDeleteMes == "everybody":
                CanUserDeleteMes = True
            elif chatType == "group":
                member = await call.message.chat.get_member(fromUserId)
                if allAdmins == True and whoCanDeleteMes == 'admins':
                    CanUserDeleteMes = True
                elif allAdmins == True and whoCanDeleteMes == 'creator':
                    if member.status == 'creator':
                        CanUserDeleteMes = True
                elif allAdmins == False:
                    if whoCanDeleteMes == 'admins' and (member.status == "administrator" or member.status == "creator") or whoCanDeleteMes == 'creator' and member.status == "creator":
                        CanUserDeleteMes = True
            elif chatType == "supergroup":
                member = await call.message.chat.get_member(fromUserId)
                if whoCanDeleteMes == 'admins' and (member.status == "administrator" or member.status == "creator") or whoCanDeleteMes == 'creator' and member.status == "creator":
                    CanUserDeleteMes = True
        if CanUserDeleteMes:
            try:
                await bot.edit_message_text(call.message.text + "\n\n@" + str(call.from_user.username) + " (id: " + str(fromUserId) + ")" + " delete it.", chatID, call.message.message_id)
                await call.message.delete()
            except:
                Print("Cannot delete message.", "E")
    elif str(callData).find("delbut_") == 0:
        member = await call.message.chat.get_member(fromUserId)
        if not CanUserEditSettings(chatID, chatType, member.status, call.from_user.id, userName, allAdmins):
            return
        Index = str(callData).find("_") + 1
        Value = str(callData)[Index:len(str(callData))]
        if Value == "menu":
            pass
        elif Value == "button":
            IsFlag = DBH.GetSetting(chatID, 'deleteButton', chatType)
            DBH.SetSetting(chatID, 'deleteButton', int(not IsFlag), chatType)
        else:
            DBH.SetSetting(chatID, 'deleteRules', Value, chatType)
        await bot.edit_message_text(GetText(chatID, 'delete_button_menu', chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.DeleteButtonMenuMarkup(chatID, chatType))
    
    elif str(callData).find("lang_") == 0:
        member = await call.message.chat.get_member(fromUserId)
        if not CanUserEditSettings(chatID, chatType, member.status, call.from_user.id, userName, allAdmins):
            return
        Index = str(callData).find("_") + 1
        Value = str(callData)[Index:len(str(callData))]
        if Value == "menu":
            pass
        else:
            DBH.SetSetting(chatID, 'lang', Value, chatType)
        await bot.edit_message_text(GetText(chatID, 'lang_menu', chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.LanguageMenuMarkup(chatID, chatType))
    
    elif str(callData).find("flags_") == 0:
        member = await call.message.chat.get_member(fromUserId)
        if not CanUserEditSettings(chatID, chatType, member.status, call.from_user.id, userName, allAdmins):
            return
        Index = str(callData).find("_") + 1
        Value = str(callData)[Index:len(str(callData))]
        if Value == "menu":
            pass
        elif Value == "button":
            IsFlag = DBH.GetSetting(chatID, 'flags', chatType)
            DBH.SetSetting(chatID, 'flags', int(not IsFlag), chatType)
        await bot.edit_message_text(GetText(chatID, 'flags_menu', chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.FlagsMarkup(chatID, chatType))

    elif str(callData).find("edit_") == 0:
        member = await call.message.chat.get_member(fromUserId)
        memberStatus = member.status
        if not CanUserEditSettings(chatID, chatType, memberStatus, call.from_user.id, userName, allAdmins):
            return
        Index = str(callData).find("_") + 1
        Value = str(callData)[Index:len(str(callData))]
        if Value == "menu":
            pass
        else:
            if memberStatus == "member":
                pass
            elif memberStatus == "administrator" and (Value == "admins" or Value == "everybody"):
                DBH.SetSetting(chatID, 'editSettings', Value, chatType)
            elif memberStatus == "creator":
                DBH.SetSetting(chatID, 'editSettings', Value, chatType)
        await bot.edit_message_text(GetText(chatID, 'edit_menu', chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.EditMenuMarkup(chatID, chatType))
    
    elif str(callData).find("cur_") == 0:
        member = await call.message.chat.get_member(fromUserId)
        memberStatus = member.status
        if not CanUserEditSettings(chatID, chatType, memberStatus, call.from_user.id, userName, allAdmins):
            return
        Index = str(callData).find("_") + 1
        Value = str(callData)[Index:len(str(callData))]

        if Value == "menu":
            await bot.edit_message_text(GetText(chatID, "currencies_mainmenu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CurrenciesMainMenuMarkup(chatID, chatType))
        elif Value == "cryptomenu":
            await bot.edit_message_text(GetText(chatID, "crypto_mainmenu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CryptoMenuMarkup(chatID, chatType))
        elif Value == "curmenu":
            await bot.edit_message_text(GetText(chatID, "currencies_menu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CurrenciesMenuMarkup(chatID, chatType))
        elif len(Value) == 1 or len(Value) == 2:
            await bot.edit_message_text(GetText(chatID, "letter_menu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CurrenciesSetupMarkup(chatID, chatType, Value))
        elif len(Value) == 3 or len(Value) == 4:
            DBH.ReverseCurrencySetting(chatID, Value)
            if Value in ListsCache.GetListOfCrypto():
                await bot.edit_message_text(GetText(chatID, "crypto_mainmenu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CryptoMenuMarkup(chatID, chatType))
            else:
                dictForMU = {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'df', 'E': 'df', 'F': 'df', 'G': 'gh', 'H': 'gh', 'I': 'ij', 'J': 'ij', 'K': 'kl', 'L': 'kl', 'M': 'm', 'N': 'nq', 'O': 'nq', 'P': 'nq', 'Q': 'nq', 'R': 'rs', 'S': 'rs', 'T': 'tu', 'U': 'tu', 'V': 'vz', 'W': 'vz', 'X': 'vz', 'Y': 'vz', 'Z': 'vz'}
                await bot.edit_message_text(GetText(chatID, "letter_menu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.CurrenciesSetupMarkup(chatID, chatType, dictForMU[Value[0]]))

    elif callData == "settings":
        await bot.edit_message_text(GetText(chatID, "main_settings_menu", chatType), chatID, call.message.message_id, reply_markup = CustomMarkup.SettingsMarkup(chatID, chatType))


def CheckArgument(key: str, value: str) -> bool:
    isAllOkArg = True
    if key == "--logs" or key == "-l":
        if value == "on":
            EnableLogging()
        elif value == "off":
            DisableLogging()
        else:
            isAllOkArg = False
    elif key == "--admin" or key == "-a":
        if value.isdigit():
            if not DBH.IsAdmin(value):
                DBH.AddAdmin(value)
        else:
            isAllOkArg = False
    elif key == "--updates" or key == "-u":
        if value == "on":
            EnableUpdates()
        elif value == "off":
            DisableUpdates()
        else:
            isAllOkArg = False
    else:
        print("Error. Unknow argument '{}'".format(key))
    return isAllOkArg

def IsChatExist(chatID: str, chatType: str):
    if DBH.ChatExists(chatID):
        pass
    else:
        DBH.AddID(chatID, chatType)
        DBH.AddIDStats(chatID, chatType)

def LoadDataForBot():
    DBH.DBIntegrityCheck()
    LoadBlackList()
    LoadCurrencies()
    LoadCrypto()
    LoadFlags()
    LoadDictionaries()
    LoadTexts()

def RegularBackup():
    while True:
        nameOfArch = DBH.CreateAllBackups()
        time.sleep(86400)

def RegularStats():
    while True:
        Stats = DBH.GetSetTimeStats()
        time.sleep(86400)

if __name__ == '__main__':
    LoadDataForBot()

    if len(sys.argv) == 3:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            Print("Error arg.", "E")
            sys.exit()
    elif len(sys.argv) == 5 and sys.argv[1] != sys.argv[3]:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            Print("Error arg.", "E")
            sys.exit()
        elif not CheckArgument(sys.argv[3], sys.argv[4]):
            Print("Error arg.", "E")
            sys.exit()
    elif len(sys.argv) == 7 and sys.argv[1] != sys.argv[3] and sys.argv[1] != sys.argv[2] and sys.argv[2] != sys.argv[3]:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            Print("Error arg.", "E")
            sys.exit()
        elif not CheckArgument(sys.argv[3], sys.argv[4]):
            Print("Error arg.", "E")
            sys.exit()
        elif not CheckArgument(sys.argv[5], sys.argv[6]):
            Print("Error arg.", "E")
            sys.exit()
    elif len(sys.argv) == 5 and not sys.argv[1] != sys.argv[3] or len(sys.argv) == 7 and not (sys.argv[1] != sys.argv[3] and sys.argv[1] != sys.argv[2] and sys.argv[2] != sys.argv[3]):
        Print("Error. Duplicate argument.", "E")
        sys.exit()

    ThreadUpdateExchangeRates = Thread(target = SheduleUpdate)
    ThreadUpdateExchangeRates.start()
    ThreadUpdateCryptoRates = Thread(target = SheduleCryptoUpdate)
    ThreadUpdateCryptoRates.start()
    ThreadRegularBackup = Thread(target = RegularBackup)
    ThreadRegularBackup.start()
    ThreadRegularStats = Thread(target = RegularStats)
    ThreadRegularStats.start()
    executor.start_polling(dp, skip_updates = IsUpdate())
