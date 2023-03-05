import settings
import telebot
import random
#import functions as func
from telebot import types


# Main menu
main_menu = types.InlineKeyboardMarkup(row_width=3)
main_menu.add(
    types.InlineKeyboardButton(text='🚬 Каталог', callback_data='catalog'),
    types.InlineKeyboardButton(text='👤 Профиль', callback_data='profile'),
    types.InlineKeyboardButton(text='ℹ️ Информация', callback_data='info'),
    types.InlineKeyboardButton(text='🛒 Мои покупки', callback_data='purchases'),
    types.InlineKeyboardButton(text='💲Пополнить баланс ', callback_data='popolnenie'),
)
main_menu.add(
    types.InlineKeyboardButton(text='🙋🏻‍♂️ Реферальная система', callback_data='referral_web'),
    types.InlineKeyboardButton(text='💸 Работа', callback_data='rabota')
)

# Admin menu
admin_menu = types.InlineKeyboardMarkup(row_width=2)
admin_menu.add(types.InlineKeyboardButton(text='Управление городами', callback_data='catalog_control'))
admin_menu.add(types.InlineKeyboardButton(text='Управление товаром', callback_data='section_control'))
admin_menu.add(types.InlineKeyboardButton(text='Изменить баланс', callback_data='give_balance'))
admin_menu.add(types.InlineKeyboardButton(text='Рассылка', callback_data='admin_sending_messages'))
admin_menu.add(types.InlineKeyboardButton(text='Топ рефералов ', callback_data='admin_top_ref'))
admin_menu.add(
    types.InlineKeyboardButton(text='Информация', callback_data='admin_info'),
    types.InlineKeyboardButton(text='Выйти', callback_data='exit_admin_menu')
)

# Admin control
nazad = types.InlineKeyboardMarkup(row_width=1)
nazad.add(
    types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu')
)

# Admin control
admin_menu_control_catalog = types.InlineKeyboardMarkup(row_width=1)
admin_menu_control_catalog.add(
    types.InlineKeyboardButton(text='Добавить город', callback_data='add_section_to_catalog'),
    types.InlineKeyboardButton(text='Удалить город', callback_data='del_section_to_catalog'),
    types.InlineKeyboardButton(text='Назад', callback_data='back_to_admin_menu')
)

popolnenie = types.InlineKeyboardMarkup(row_width=1)
popolnenie.add(
    types.InlineKeyboardButton(text='Bitcoin', callback_data='bitcoin'),
    types.InlineKeyboardButton(text='Qiwi', callback_data='replenish_balance'),
    types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu')
)

# Admin control section
admin_menu_control_section = types.InlineKeyboardMarkup(row_width=1)
admin_menu_control_section.add(
    types.InlineKeyboardButton(text='Добавить товар в город', callback_data='add_product_to_section'),
    types.InlineKeyboardButton(text='Удалить товар из города', callback_data='del_product_to_section'),
    types.InlineKeyboardButton(text='Загрузить товар', callback_data='download_product'),
    types.InlineKeyboardButton(text='Назад', callback_data='back_to_admin_menu')
)

# Back to admin menu
back_to_admin_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_admin_menu.add(
    types.InlineKeyboardButton(text='Вернуться в админ меню', callback_data='back_to_admin_menu')
)

btn_purchase = types.InlineKeyboardMarkup(row_width=2)
btn_purchase.add(
    types.InlineKeyboardButton(text='Купить', callback_data='buy'),
    types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_menu')
)

btn_ok = types.InlineKeyboardMarkup(row_width=3)
btn_ok.add(
    types.InlineKeyboardButton(text='Понял', callback_data='btn_ok')
)

to_close = types.InlineKeyboardMarkup(row_width=3)
to_close.add(
    types.InlineKeyboardButton(text='Назад', callback_data='exit_to_menu')
)
goroda = telebot.types.ReplyKeyboardMarkup(True, True)
goroda.row('Москва')
goroda.row('Санкт-Петербург')
goroda.row('Нижний Новгород')
goroda.row('Самара')
goroda.row('Челябинск')
goroda.row('Краснодар')
goroda.row('Ярославль')
goroda.row('Екатеринбуг')
goroda.row('Новосибирск')

interesno = telebot.types.ReplyKeyboardMarkup(True, True)
interesno.row('Заинтересовало!')
interesno.row('Вернуться в главное меню')


def replenish_balance(code):
    replenish_balance = types.InlineKeyboardMarkup(row_width=3)
    replenish_balance.add(
        types.InlineKeyboardButton(text='Оплатить', url=f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={settings.QIWI_NUMBER}&amountInteger=100&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&blocked[0]=account'),
        types.InlineKeyboardButton(text='🔄 Проверить', callback_data='check_payment'),
        types.InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_payment')
    )
    return replenish_balance