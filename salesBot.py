
#staging-api-key = 


import sqlite3 , emoji ,time , telegram , logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler , CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup , Bot , Update

MAIN_MENU, CATEGORY_MENU, ADMIN_MENU = range(3)



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

con = sqlite3.connect("botdb.db")
cur = con.cursor()
cur.execute("SELECT api_key FROM bot_api_token where id =1")
result = cur.fetchone()
API_TOKEN = f'{result[0]}' 
con.close()

bot = telegram.Bot(token=API_TOKEN)




user_action_counts = {}
user_action_timestamps = {}




def button(update, context):
    query = update.callback_query
    query.answer()
    user_id = get_user_id(update)

    if user_id in user_action_timestamps:
        current_time = time.time()
        last_time = user_action_timestamps[user_id]
        time_elapsed = current_time - last_time
        interval_duration = 1
        if time_elapsed < interval_duration:
            freeze_time(update ,user_id,context)
            return
    user_action_timestamps[user_id] = time.time()


    if query.data == "admin_panel":
        admin_panel_buttons(query)
    elif query.data == "categories":
        categories(query)
    elif query.data == "admin_categories":
        admin_categories(query)
    elif query.data == "show_all_categories":
        show_all_categories(query)
    elif query.data == "add_category":
        add_category(query,update)
    elif query.data == "submit_new_category":
        submit_new_category(update)
    elif query.data.startswith('turn_category_'):
        parts = query.data.split('_')
        category_id = parts[2] 
        status = parts[3] 
        category_turn_status(query, category_id, status)
    elif query.data == "sub_categories":
        subcategories_buttons(query)
    elif query.data == "main_menu":
        start(update, context)
    elif query.data == "new_post":
        new_post(query)
    elif query.data == "admins_list":
        admins_list(query)
    elif query.data == "add_new_admin":
        add_new_admin(query , update)
    elif query.data == "add_new_admin_userid":
        add_new_admin_userid(query , update)



        


def add_new_admin(query, update):
    user_id = get_user_id(update)
    update_user_state(user_id, 'add_new_admin_username', 'None')
    buttons = [
        [InlineKeyboardButton("منصرف شدم", callback_data="admin_list")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='لطفا اسم ادمین جدید رو  وارد کنید ', reply_markup=reply_markup)


def add_new_admin_userid(query ,update):
    user_id = get_user_id(update)
    state , admin_username = get_state_and_text(user_id)
    con =  sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO admins_id  username =  {admin_username}")
    con.commit()
    con.close()
    update_user_state(user_id, 'add_new_admin_userid', 'None')
    buttons = [
        [InlineKeyboardButton("منصرف شدم", callback_data="admins_list")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='اطلاعات ادمین جدید با موفقیت ثبت شد', reply_markup=reply_markup)
    add_new_admin_userid_to_db(query , update)

def add_new_admin_userid_to_db(query , update):
    user_id = get_user_id(update)
    state , admin_userid = get_state_and_text(user_id)
    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute(f"UPDATE admins_id SET user_id = {admin_userid} WHERE username IS NULL")
    con.commit()
    con.close()
    update_user_state(user_id, 'None', 'None')
    admins_list(query)

def cancel_add_new_admin(query):
    user_id = get_user_id(update)
    update_user_state(user_id, 'None', 'None')
    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute("DELETE FROM admins_id WHERE username IS NULL OR user_id IS NULL")
    con.commit()
    con.close()
    admins_list(query)















def admins_list(query):

    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute("SELECT username , user_id FROM admins_id ")
    records = cur.fetchall()
    con.close() 
    buttons = []

    buttons.append([
            InlineKeyboardButton("Admin Name", callback_data="no_action"),
            InlineKeyboardButton("User ID", callback_data="no_action")
        ])
        
    for username, user_id in records:
        row = [
            InlineKeyboardButton(f"{username}", callback_data="no_action"),
            InlineKeyboardButton(f"{user_id}", callback_data="no_action")
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("اضافه کردن ادمین جدید", callback_data="add_new_admin")])
    buttons.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="لیست ادمین ها:", reply_markup=reply_markup)



















def  show_all_subcategory_parent(query):
    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute("SELECT category_id , name FROM categories")
    records = cur.fetchall()
    con.close() 
    buttons = []
    for category_id ,name in records:
        row = [
            InlineKeyboardButton(f"{category_id} -  {name}", callback_data=f"add_sub"),
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("بازگشت به پنل ادمین", callback_data="admin_categories")])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="ابتدا دسته بندی اصلی رو انتخاب کن", reply_markup=reply_markup)


def subcategories_buttons(query):
    buttons = [
        [InlineKeyboardButton("نمایش همه دسته بندی های جانبی", callback_data="show_all_categories")],
        [InlineKeyboardButton(" اضافه کردن دسته بندی جانبی", callback_data="add_category")],
        [InlineKeyboardButton("بازگشت به پنل ادمین", callback_data="admin_panel")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='لطفا انتخاب کنید', reply_markup=reply_markup)

def admin_panel_buttons(query):
    buttons = [
            [InlineKeyboardButton("پست جدید", callback_data="new_post"),
            InlineKeyboardButton("ویرایش و حذف", callback_data="edit_post_or_delete")],
            [InlineKeyboardButton(" دسته بندی ها ", callback_data="admin_categories"),
            InlineKeyboardButton(" دسته بندی های جانبی", callback_data="sub_categories")],
            [InlineKeyboardButton("لیست ادمین ها", callback_data="admins_list")],
            [InlineKeyboardButton(" پیام همگانی ", callback_data="all_user_message")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="main_menu")],
        ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='پنل ادمین', reply_markup=reply_markup)


def categories(query):

    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute("SELECT category_id , name FROM categories WHERE status = 'on'")
    records = cur.fetchall()
    con.close() 
    buttons = []

    for category_id ,name in records:
        row = [
            InlineKeyboardButton(f"{name}", callback_data=f"{category_id}_{name}"),
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="لیست دسته بندی محصولات:", reply_markup=reply_markup)


def admin_categories(query):
    buttons = [
        [InlineKeyboardButton("نمایش همه دسته بندی ها", callback_data="show_all_categories")],
        [InlineKeyboardButton("اضافه کردن دسته بندی", callback_data="add_category")],
        [InlineKeyboardButton("بازگشت به پنل ادمین", callback_data="admin_panel")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='لطفا انتخاب کنید', reply_markup=reply_markup)

def new_post(query):
    buttons = [
            [InlineKeyboardButton("ساخت پست جدید", callback_data="creat_post"),
            InlineKeyboardButton("ویرایش پست ها", callback_data="edit_existing_post")],
            [InlineKeyboardButton("بازگشت به منوی اصلی", callback_data="main_menu")],
        ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='پست جدید', reply_markup=reply_markup)


def show_all_categories(query):
    con = sqlite3.connect("botdb.db")
    cur = con.cursor()
    cur.execute("SELECT category_id , name, status FROM categories")
    records = cur.fetchall()
    con.close() 
    buttons = []
    for category_id ,name, status in records:
        if status == 'on':
            status = f"ON {emoji.emojize(':check_mark_button:')}"
            turn_status = "off"
        elif status == 'off':
            status = f"OFF {emoji.emojize(':cross_mark:')}"
            turn_status = "on"
        row = [
            InlineKeyboardButton(f"{category_id} -  {name}", callback_data="None"),
            InlineKeyboardButton(f"وضعیت : {status}", callback_data=f"turn_category_{category_id}_{turn_status}")
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("بازگشت به پنل ادمین", callback_data="admin_categories")])
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="برای تغییر وضعیت روی دکمه ON/OFF وضعیت کلیک کنید", reply_markup=reply_markup)


def add_category(query , update):
    user_id = get_user_id(update)
    update_user_state(user_id, 'add_new_category', 'None')
    buttons = [
        [InlineKeyboardButton("تایید", callback_data="submit_new_category")],
        [InlineKeyboardButton("بازگشت به پنل دسته بندی ها", callback_data="admin_categories")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text='لطفا اسم دسته بندی رو  وارد کن و بعدش تایید رو بزن', reply_markup=reply_markup)


def submit_new_category(update):
    user_id = get_user_id(update)
    state , category_name = get_state_and_text(user_id)
    conn = sqlite3.connect("botdb.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name, status) VALUES (?, 'off')", (category_name,))
    conn.commit()
    conn.close()
    bot.send_message(chat_id=user_id, text=f"دسته بندی '{category_name}' اضافه شد")


def category_turn_status(query, category_id, status):
    conn = sqlite3.connect('botdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE category_id = ?", (category_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE categories SET status = ? WHERE category_id = ?", (status, category_id))
        conn.commit()
    conn.close()
    show_all_categories(query)


def update_user_state(user_id, state, text):
    conn = sqlite3.connect('botdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_state WHERE user_id = ?", (user_id,))
    existing_row = cursor.fetchone()
    if existing_row:
        cursor.execute("UPDATE user_state SET state = ?, user_input = ? WHERE user_id = ?",(state, text, user_id))
    else:
        cursor.execute("INSERT INTO user_state (user_id, state, user_input) VALUES (?, ?, ?)",(user_id, state, text))
    conn.commit()
    conn.close()


def get_state_and_text(user_id):
    conn = sqlite3.connect('botdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT state, user_input FROM user_state WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row[1]:
        state, text = row[0] , row[1]
        return state, text
    elif row[0]:
        state = row[0]
    else:
        return None, None


def freeze_time(update, user_id, context):
    freeze_time = 5
    message_ids = []
    
    while freeze_time > 0:
        message_id=bot.send_message(chat_id=user_id, text=f"لطفا {freeze_time} ثانیه صبر کنید ").message_id
        message_ids.append(message_id)
        time.sleep(1)
        freeze_time -= 1
        
    for i in message_ids:
        context.bot.deleteMessage(message_id=i, chat_id=update.callback_query.message.chat.id)

def get_user_id(update):
    user_id = None
    if update.message:
        user_id = update.message.chat.id
    elif update.callback_query:
        user_id=update.callback_query.message.chat.id
    else:
        update.effective_user.id
    return user_id

def is_user_admin(user_id):
    conn = sqlite3.connect('botdb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins_id WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def start(update: Update, context: CallbackContext):
    query = None
    if update.callback_query:
        query = update.callback_query
    user_id = update.effective_user.id
    buttons = [
        [InlineKeyboardButton("دسته بندی ها", callback_data="categories")],
    ]
    if is_user_admin(user_id):
        buttons.append([InlineKeyboardButton("پنل ادمین", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(buttons)
    if query:
        query.edit_message_text(text='لطفا انتخاب کنید', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=user_id, text='لطفا انتخاب کنید', reply_markup=reply_markup)
    logger.info(f"User {user_id} started the bot.")






def handle_text(update, context):
    query = update.callback_query
    message_text = update.message.text
    print("hoooooooooooooooooooooooooooooooooooooooooooooooooo               ", message_text)
    user_id = get_user_id(update)
    state , text = get_state_and_text(user_id)
    if state == 'add_new_category':
        update_user_state(user_id, 'add_new_category', message_text)
    elif state == 'add_new_admin_username':
        update_user_state(user_id, 'add_new_admin_username', message_text) 
        add_new_admin_userid(query ,update)

    elif state == 'add_new_admin_userid':
        update_user_state(user_id, 'add_new_admin_userid', message_text)





def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_text))


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
