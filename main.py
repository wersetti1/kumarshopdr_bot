#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import menu
import settings
import functions as func
import telebot
import requests
from telebot import types
import time
import datetime
import random
pip install --upgrade wheel

catalog_dict = {}
product_dict = {}
download_dict = {}
balance_dict = {}
admin_sending_messages_dict = {}

def start_bot():
    bot = telebot.TeleBot(settings.bot_token)

    # Command start
    @bot.message_handler(commands=['start'])
    def handler_start(message):

        chat_id = message.chat.id
        a = func.first_join(user_id=chat_id, name=message.from_user.username, code=message.text[6:])

        bot.send_message(chat_id,
                      '{}, добро пожаловать в магазин {} \n'
                      " \n" 
                      "В данном магазине вы можете получить в короткие сроки необходимый вам товар. \n" 
                      " \n" 
                      "Выдача адресов происходит круглосуточно через бота!\n" 
                      " \n" 
                      "Внимательней проверяйте адрес Telegram, остерегайтесь фейков.\n" 
                      " \n" 
                      "Если вашего города нет в каталоге,напишите оператору \n"
                      "возможна единоразовая поставка товара в необходимый город \n".format(message.from_user.first_name,settings.bot_login),reply_markup=menu.main_menu)
                      
    # Command admin
    @bot.message_handler(commands=['admin'])
    def handler_admin(message):
        chat_id = message.chat.id
        if chat_id == settings.admin_id_1 or chat_id == settings.admin_id_2:
            bot.send_message(chat_id, 'Вы перешли в меню админа', reply_markup=menu.admin_menu)

    # Обработка данных
    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # Main menu
        if call.data == 'catalog':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Выберите необходимый город из списка:',
                reply_markup=func.menu_catalog()
            )

        if call.data == 'exit_from_catalog':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вышли из меню покупки товара',
                reply_markup=menu.main_menu
            )


        if call.data in func.list_sections():
            name = call.data
            product = func.Product(chat_id)
            product_dict[call.message.chat.id] = product
            product.section = name

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'❕ Выберите нужный товар',
                reply_markup=func.menu_section(call.data)
            )

        if call.data in func.list_product():
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{call.data}"')
            row = cursor.fetchall()
            if len(row) > 0:
                product = func.Product(chat_id)
                product_dict[chat_id] = product
                product = product_dict[chat_id]

                info = func.menu_product(call.data, product)
                product.product = info[1].product
                product.section = info[1].section
                product.amount_MAX = info[1].amount_MAX
                product.price = info[1].price

                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=info[0],
                    reply_markup=menu.btn_purchase
                )

            if len(row) == 0:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text='Товар закончился, сообщите об этом оператору',
                    reply_markup=menu.main_menu
                )

        if call.data == 'buy':
            try:
                product = product_dict[chat_id]
                msg = bot.send_message(chat_id=chat_id,
                                       text=f'❕ Введите кол-во товара\n❕ От 1 - {product.amount_MAX}')
                bot.register_next_step_handler(msg, buy)
            except:
                pass
                
        if call.data == 'info':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=settings.info,
                reply_markup=menu.main_menu
            )

        if call.data == 'purchases':
            msg = func.basket(chat_id)
            if len(msg) > 0:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=msg,
                                      reply_markup=menu.main_menu)
            if len(msg) == 0:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text='Покупок не найдено..',
                                      reply_markup=menu.main_menu)


        if call.data == 'exit_to_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вернулись в главное меню',
                reply_markup=menu.main_menu
            )

        if call.data == 'btn_ok':
            bot.delete_message(chat_id, message_id)

        if call.data == 'profile':
            info = func.profile(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=settings.profile.format(
                                      id=info[0],
                                      login=f'@{info[1]}',
                                      data=info[2][:19],
                                      balance=info[5]
                                  ),
                                  reply_markup=menu.main_menu)

        # Admin menu
        if call.data == 'admin_info':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=func.admin_info(),
                reply_markup=menu.admin_menu
            )

        if call.data == 'add_section_to_catalog':
            if chat_id == settings.admin_id_1 or settings.admin_id_2:
                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите название города:')
                bot.register_next_step_handler(msg, create_section)

        if call.data == 'del_section_to_catalog':
            if chat_id == settings.admin_id_1 or settings.admin_id_2:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()
                cursor.close()
                conn.close()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(
                    chat_id=chat_id,
                    text='Введите порядковый номер города одним числом\n\n'
                         f'{text}'
                )
                bot.register_next_step_handler(msg, del_section)

        if call.data == 'add_product_to_section':
            if chat_id == settings.admin_id_1 or settings.admin_id_2:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите название города, в который хотите добавить товар\n\n'
                                            f'{text}')
                bot.register_next_step_handler(msg, create_product)

        if call.data == 'del_product_to_section':
            if chat_id == settings.admin_id_1 or settings.admin_id_2:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите порядковый номер города одним числом\n\n'
                                            f'{text}')
                bot.register_next_step_handler(msg, del_product)

        if call.data == 'download_product':
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите город\n\n'
                                        f'{text}')
            bot.register_next_step_handler(msg, download_product)

        if call.data == 'exit_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы покинули меню админа',
                reply_markup=menu.main_menu
            )

        if call.data == 'back_to_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в меню админа',
                reply_markup=menu.admin_menu
            )

        if call.data == 'catalog_control':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в управление каталогом',
                reply_markup=menu.admin_menu_control_catalog
            )

        if call.data == 'section_control':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в управление городами',
                reply_markup=menu.admin_menu_control_section
            )

        if call.data == 'replenish_balance':
            info = func.replenish_balance(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=info[0],
                                  reply_markup=menu.replenish_balance(info[1]))

        if call.data == 'popolnenie':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='Выберите способ пополнения:',
                                  reply_markup=menu.popolnenie)
        if call.data == 'bitcoin':
            btc = settings.btc
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=f'Для пополнения баланса с Bitcoin, необходимо перевести сумму на зарезервированный для вас Bitcoin адрес: \n\n {btc} \n  '
                                       f'\n На данный момент, оплата криптовалютой проходит в ручном режиме,приносим извинения за задержку',
                                  reply_markup=menu.nazad)

        if call.data == 'cancel_payment':
            func.cancel_payment(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='❕ Добро пожаловать!',
                                  reply_markup=menu.main_menu)

        if call.data == 'check_payment':
            check = func.check_payment(chat_id)
            if check[0] == 1:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=f'✅ Вы успешно пополнили баланс!'
                                           f'\nСумма - {check[1]} руб',
                                      reply_markup=menu.main_menu)

                bot.send_message(chat_id=settings.admin_id_1,
                                 text='💰 Пополнение баланса\n'
                                      f'🔥 От - {chat_id}\n'
                                      f'🔥 Сумма - {check[1]} руб')

                try:
                    bot.send_message(chat_id=f'-100{settings.CHANNEL_ID}',
                                     text='💰 Пополнение баланса\n'
                                          f'🔥 От - {chat_id}\n'
                                          f'🔥 Сумма - {check[1]} руб')
                except: pass

            if check[0] == 0:
                bot.send_message(chat_id=chat_id,
                                 text='❌ Оплата не найдена',
                                 reply_markup=menu.to_close)

        if call.data == 'to_close':
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)

        if call.data == 'give_balance':
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите ID человека, которому будет изменён баланс')

            bot.register_next_step_handler(msg, give_balance)

        if call.data == 'admin_sending_messages':
            msg = bot.send_message(chat_id,
                                   text='Введите текст рассылки')
            bot.register_next_step_handler(msg, admin_sending_messages)

        if call.data == 'referral_web':
            ref_code = func.check_ref_code(chat_id)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'👥 Реферальная система\n\n'
                     f'Ваша реферальная ссылка:\n'
                     f'https://teleg.run/{settings.bot_login}?start={ref_code}\n\n'
                     f'За всё время вы заработали - {func.check_all_profit_user(chat_id)} ₽\n\n'
                     f'<i>Если человек, приглашенный по вашей реферальной ссылке, пополнит баланс, то вы получите {settings.ref_percent}% от суммы его депозита</i>',
                reply_markup=menu.main_menu,
                parse_mode='html'
                )
        
        if call.data == 'admin_top_ref':
            bot.send_message(
                chat_id=chat_id,
                text=func.admin_top_ref(),
                parse_mode='html'
            )
        if call.data == 'rabota':
            msg = bot.send_message(chat_id=chat_id,
                                   text='Выберите необходимый город из списка:',
                                   reply_markup=menu.goroda)

            bot.register_next_step_handler(msg, rabota)

    def rabota(message):
        try:
            rabota = message.text

            msg = bot.send_message(chat_id=message.chat.id,
                               text=f'Вы выбрали город {rabota}. \n'
                                    f'Нам требуются как опытные сотрудники, так и люди без опыта работы.\n\n'
                                    'Почему именно мы? Чем мы лучше других организаций? Что же мы предлагаем? Давайте по порядку:\n\n'
                                    '- Мы платим за загруженные адреса, Вам не нужно ожидать продажи клада\n'
                                    '- ЗП приходит на Ваш личный BTC кошелек\n'
                                    '- Премии, бонусы и конкурсы среди курьеров организуются ежемесячно\n'
                                    '- В конце каждого года разыгрываем крупные денежные призы от миллиона рублей\n'
                                    '- Обладаем огромной библиотекой обучающих материалов\n'
                                    '- Обучение проводится сотрудниками со стажем работы более пяти лет\n'
                                    '- Обучаем не только курьерскому мастерству, но так же и растеневодству и грибоводству\n'
                                    '- Присутствует чат для курьеров, в котором Вы сможете обмениваться опытом с другими сотрудниками и просто беседовать на свободные темы\n'
                                    '- Есть возможность командировок для желающих зарабатывать более миллиона рублей в месяц\n'
                                    '- Возможность карьерного роста вплоть до куратора для добросовестных и исполнительных сотрудников\n'
                                    '- Дополнительные навыки не будут оставлены без внимания, химики, гроверы, аналитики - для Вас точно найдется место в нашей компании!\n \n'
                                    'Какие требования для трудоустройства в нашу команду?\n\n'
                                    '- Иметь телефон на базе Android 6.1 или выше\n'
                                    '- Работать со всеми видами товара\n'
                                    '- Быть на связи утром и вечером\n'
                                    '- Обладать залогом от 3000 рублей\n'
                                    'Лучший момент для устройства в наш коллектив - был десять лет назад, следующий подходящий для этого момент - сегодня.'
                                    'Если вас заинтересовали данные условия для работы, то нажмите соответствующую кнопку ниже:',
                                   reply_markup=menu.interesno)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def give_balance(message):
        try:
            balance = func.GiveBalance(message.text)
            balance_dict[message.chat.id] = balance

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите сумму на которую изменится баланс (к балансу не добавится эта сумма, а баланс изменится на неё)')

            bot.register_next_step_handler(msg, give_balance_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def give_balance_2(message):
        try:
            balance = balance_dict[message.chat.id]
            balance.balance = message.text
            code = random.randint(111, 999)
            balance.code = code
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'ID - {balance.login}\n'
                                        f'Баланс изменится на - {balance.balance}\n'
                                        f'Для подтверждения введите {code}')

            bot.register_next_step_handler(msg, give_balance_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def give_balance_3(message):
        try:
            balance = balance_dict[message.chat.id]
            if int(message.text) == balance.code:
                func.give_balance(balance)
                bot.send_message(chat_id=message.chat.id,
                                 text='✅ Баланс успешно изменён')
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def create_section(message):
        try:
            name = message.text
            catalog = func.Catalog(name)
            catalog_dict[message.chat.id] = catalog

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=name + '\n Создать? \n'
                                        'Напишите "да" или "нет"')
            bot.register_next_step_handler(msg, create_section_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def buy(message):
        try:
            product = product_dict[message.chat.id]
            if int(message.text) in range(1, int(product.amount_MAX)+1):
                product.amount = int(message.text)

                code = random.randint(111, 999)
                product.code = code

                msg = bot.send_message(chat_id=message.chat.id,
                    text=f'❕ Вы выбрали - {product.product}\n'
                       f'❕ Кол-во - {product.amount}\n'
                       f'❕ Цена - {float(product.price) * int(product.amount)} руб\n'
                       f'Для подтверждения покупки отправьте {code}')
                bot.register_next_step_handler(msg, buy_2)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='❌ Неверное количествово',
                                 reply_markup=menu.main_menu)
        except:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def buy_2(message):
        try:
            product = product_dict[message.chat.id]
            if int(message.text) == product.code:
                check = func.check_balance(product.user_id, (float(product.price)*int(product.amount)))

                conn = sqlite3.connect('base_ts.sqlite')
                cursor = conn.cursor()
                worker_id = cursor.execute(f'SELECT ref_code FROM users WHERE user_id = "{message.chat.id}"').fetchall()[0][0]
                login_worker = cursor.execute(f'SELECT name FROM users WHERE user_id = "{worker_id}"').fetchall()[0][0]
                conn.commit()

                if check == 1:

                    list = func.buy(product)
                    bot.send_message(chat_id=message.chat.id,
                                     text=f'✅ Вы успешно купили товар\n\n{list}',
                                     reply_markup=menu.main_menu)

                    bot.send_message(chat_id=settings.admin_id_1,
                                     text=f'🔥 Успешная оплата 🔥\n\n'
                                          f'🙋🏻‍♂️ Воркер - @{login_worker}\n'
                                          f'💴 Сумма покупки - {float(product.price) * int(product.amount)}\n'
                                          f'💴 Доля воркера - {(((float(product.price) * int(product.amount))* int(settings.worker_procent)) / 100)}\n'
                                          f'🧑‍🦽 Купил - @{message.chat.username}\n'
                                          f'❕ Дата покупки - {datetime.datetime.now()}\n'
                                          f'❕ Купленный товар ⬇️\n\n{list}')

                    try:
                        bot.send_message(chat_id=f'-100{settings.CHANNEL_ID}',
                                         text=f'🔥 Успешная оплата 🔥\n\n'
                                              f'🙋🏻‍♂️ Воркер - @{login_worker}\n'
                                              f'💴 Сумма покупки - {float(product.price) * int(product.amount)}\n'
                                              f'💴 Доля воркера - {(((float(product.price) * int(product.amount))* int(settings.worker_procent)) / 100)}\n'
                                              f'🧑‍🦽 Купил - @{message.chat.username}\n'
                                              f'❕ Дата покупки - {datetime.datetime.now()}\n'
                                              f'❕ Купленный товар ⬇️\n\n{list}')

                    except: pass

                if check == 0:
                    bot.send_message(chat_id=message.chat.id,
                                     text='❌ На балансе недостаточно средств',
                                     reply_markup=menu.to_close)

            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='❌ Покупка отменена',
                                 reply_markup=menu.main_menu)
        except:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def create_section_2(message):
        try:
            if message.text.lower() == 'да':
                catalog = catalog_dict[message.chat.id]
                func.add_section_to_catalog(catalog.name)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Город: {catalog.name}\n'
                         f'✅Успешно добавлен в каталог',
                    reply_markup=menu.admin_menu
                )
            if message.text.lower() == 'нет':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            print(e)

    def del_section(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            nm = row[int(message.text)][0]
            num_catalog = func.Catalog(name)
            catalog_dict[message.chat.id] = num_catalog

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'Выбран {nm}\n'
                                        f'Удалить этот город?\n'
                                        'Напишите "да" или "нет"')

            bot.register_next_step_handler(msg, del_section_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def del_section_2(message):
        try:
            if message.text.lower() == 'да':
                catalog = catalog_dict[message.chat.id]
                func.del_section_to_catalog(catalog.name)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Город: {catalog.name}\n'
                         f'✅Успешно удален из каталога',
                    reply_markup=menu.admin_menu
                )
            if message.text.lower() == 'нет':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def create_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            num_catalog = func.Product(name)
            product_dict[message.chat.id] = num_catalog

            addproduct = product_dict[message.chat.id]
            addproduct.section = name

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{name}\nВведите название товара')

            bot.register_next_step_handler(msg, create_product_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def create_product_2(message):
        try:
            product_name = message.text
            product = product_dict[message.chat.id]
            product.product = product_name

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите цену на товар')
            bot.register_next_step_handler(msg, create_product_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def create_product_3(message):
        try:
            price = message.text
            product = product_dict[message.chat.id]
            product.price = price

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите описание товара')

            bot.register_next_step_handler(msg, create_product_4)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def create_product_4(message):
        try:
            product = product_dict[message.chat.id]
            product.info = message.text

            product_name = f'{product.product} | {product.price} руб'
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{product_name}\n\n'
                                        'Создать? \n'
                                        'Напишите "да" или "нет"')
            bot.register_next_step_handler(msg, create_product_5)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def create_product_5(message):
        try:
            if message.text.lower() == 'да':
                product = product_dict[message.chat.id]
                product_name = f'{product.product} | {product.price} руб'

                func.add_product_to_section(product_name, product.price, product.section, product.info)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Товар: {product_name}\n'
                         f'✅Успешно добавлен в город',
                    reply_markup=menu.admin_menu
                )
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def del_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            product = func.AddProduct(name)
            product_dict[message.chat.id] = product

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{name}"')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Выберите номер товара который хотите удалить\n\n'
                                        f'{text}')
            bot.register_next_step_handler(msg, del_product_2)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def del_product_2(message):
        try:
            product = product_dict[message.chat.id]

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM '{product.section}'")
            row = cursor.fetchall()

            name_product = row[int(message.text)][0]
            product.product = name_product

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='❕Удалить ⬇️\n'
                                        f'❕{product.product}\n\n'
                                        '❕из города ⬇️\n'
                                        f'❕{product.section}  ? \n'
                                        'Напишите "да" или "нет"')
            bot.register_next_step_handler(msg, del_product_3)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def del_product_3(message):
        try:
            if message.text.lower() == 'да':
                product = product_dict[message.chat.id]

                func.del_product_to_section(product.product, product.section)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Товар: {product.product}\n'
                         f'✅Успешно удален из города',
                    reply_markup=menu.admin_menu
                )
            if message.text.lower() == 'нет':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану')

    def download_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()

            name_section = row[int(message.text)][1]
            download = func.DownloadProduct(name_section)
            download_dict[message.chat.id] = download

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{name_section}"')
            row = cursor.fetchall()

            cursor.close()
            conn.close()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Выберите номер товара\n\n'
                                        f'{text}')
            reply_markup = menu.main_menu

            bot.register_next_step_handler(msg, download_product_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')



    def download_product_2(message):
        try:
            product = download_dict[message.chat.id]

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{product.name_section}"')
            row = cursor.fetchall()

            product.name_product = row[int(message.text)][2]


            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Вы хотите добавить товар в ⬇️\n\n'
                                        f'ID - {product.name_product} \n'
                                        'Напишите "да" или "нет"')

            bot.register_next_step_handler(msg, download_product_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def download_product_3(message):
        try:
            if message.text.lower() == 'да':
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='❕Отправьте txt файл с товаром\n\n'
                                            '❗️ 1 строчка = 1 товару!!!\n\n'
                                            '❗️ ПРИМЕР ФАЙЛА:\n'
                                            'main@mail.ru:password\n'
                                            'QWERT-QWERY-QWERY\n'
                                            'какая-то_ссылка.ru')

                bot.register_next_step_handler(msg, download_product_4)

            if message.text.lower() == 'нет':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    def admin_sending_messages(message):
        dict = func.Admin_sending_messages(message.chat.id)
        admin_sending_messages_dict[message.chat.id] = dict

        dict = admin_sending_messages_dict[message.chat.id]
        dict.text = message.text

        msg = bot.send_message(message.chat.id,
                               text='Отправьте "ПОДТВЕРДИТЬ" для подтверждения')
        bot.register_next_step_handler(msg, admin_sending_messages_2)

    def admin_sending_messages_2(message):
        conn = sqlite3.connect('base_ts.sqlite')
        cursor = conn.cursor()
        dict = admin_sending_messages_dict[message.chat.id]
        if message.text == 'ПОДТВЕРДИТЬ':
            cursor.execute(f'SELECT * FROM users')
            row = cursor.fetchall()

            for i in range(len(row)):
                try:
                    time.sleep(1)
                    bot.send_message(row[i][0], dict.text)

                except:
                    pass
        else:
            bot.send_message(message.chat.id, text='Рассылка отменена')

    @bot.message_handler(content_types=['document'])
    def download_product_4(message):
        try:
            chat_id = message.chat.id
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            download = download_dict[message.chat.id]

            with open(message.document.file_name, 'wb') as doc:
                doc.write(downloaded_file)

            func.download_product(message.document.file_name, download.name_product)

            bot.send_message(chat_id=chat_id,
                             text='❕ Товар загружен 👍')
        except Exception as e:
            pass
            bot.send_message(chat_id=message.chat.id,
                             text='Упс, что-то пошло не по плану')

    @bot.message_handler(content_types=["text"])
    def next_menu(message):
        chat_id = message.chat.id
        message_id = message.message_id
        if message.text == "Вернуться в главное меню":
            bot.send_message(chat_id=message.chat.id,
                             text='Возвращаемся в главное меню..',
                             reply_markup=menu.main_menu)
        if message.text == 'Заинтересовало!':
            info = func.replenish_balance(chat_id)
            bot.send_message(chat_id=message.chat.id,
                             text='Мы рады,что вас заинтересовала данная вакансия. \n\n '
                                  'Перед началом работы, необходимо оплатить залог в размере 3000 рублей. \n\n '
                                  'После проверки оплаты, бот пришлет вам юзернейм оператора, которому необходимо будет написать!')

            bot.send_message(chat_id=chat_id,
                             text=info[0],
                             reply_markup=menu.replenish_balance(info[1]))


    bot.polling(none_stop=True)


start_bot()
