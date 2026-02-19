import sqlite3
import logging
import requests
import time
import random
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

TOKEN = "8345973355:AAHx8SaENqxPggAowdM8bi94GdL8lgknuJg"
SET_CHANNEL = 1

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ПОЛНЫЙ СПИСОК 51 МАРКА (ИЗОЛИРОВАННО ДЛЯ КАЖДОГО)
CAR_DATA = {
    'abarth': ['500', '595', '695', '124-spider'], 'acura': ['mdx', 'rdx', 'tlx', 'tsx', 'ilx', 'zdx'],
    'alfa-romeo': ['giulia', 'stelvio', 'giulietta', '159', '156', 'mito', '147', 'brera', 'gt'],
    'aston-martin': ['db9', 'db11', 'dbs', 'vantage', 'rapide', 'dbx'],
    'audi': ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'q2', 'q3', 'q5', 'q7', 'q8', 'tt', '80', '100'],
    'bentley': ['continental', 'bentayga', 'flying-spur', 'mulsanne'],
    'bmw': ['1-seria', '2-seria', '3-seria', '4-seria', '5-seria', '6-seria', '7-seria', '8-seria', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'z4', 'm3', 'm5'],
    'bugatti': ['veyron', 'chiron'], 'buick': ['encore', 'enclave', 'regal', 'lacrosse'],
    'byd': ['han', 'tang', 'atto-3', 'dolphin'], 'cadillac': ['escalade', 'cts', 'srx', 'xt5', 'xt6', 'ct6', 'ats'],
    'chery': ['tiggo-4', 'tiggo-7', 'tiggo-8', 'qq', 'amulet'],
    'chevrolet': ['aveo', 'cruze', 'captiva', 'spark', 'orlando', 'camaro', 'corvette', 'lacetti', 'epica', 'trax'],
    'chrysler': ['voyager', '300c', 'pt-cruiser', 'pacifica', 'sebring'],
    'citroen': ['c1', 'c2', 'c3', 'c4', 'c5', 'berlingo', 'jumper', 'c4-picasso', 'cactus', 'jumpy'],
    'cupra': ['formentor', 'leon', 'ateca', 'born'], 'dacia': ['duster', 'sandero', 'logan', 'lodgy', 'dokker', 'jogger'],
    'daewoo': ['lanos', 'matiz', 'nubira', 'leganza', 'tico', 'nexia'], 'daihatsu': ['terios', 'sirion', 'cuore', 'materia'],
    'dodge': ['ram', 'challenger', 'charger', 'durango', 'journey', 'avenger', 'caliber', 'nitro'],
    'ds': ['ds3', 'ds4', 'ds5', 'ds7'], 'ferrari': ['458', '488', 'f430', 'california', 'roma'],
    'fiat': ['500', 'tipo', 'panda', 'ducato', 'punto', 'bravo', 'doblo', 'stilo', '126p', '125p', 'seicento'],
    'ford': ['focus', 'mondeo', 'fiesta', 'kuga', 's-max', 'c-max', 'galaxy', 'mustang', 'transit', 'ranger', 'puma', 'explorer', 'edge', 'sierra', 'scorpio'],
    'geely': ['emgrand', 'monjaro', 'tugella', 'coolray', 'atlas'], 'genesis': ['g70', 'g80', 'g90', 'gv70', 'gv80'],
    'gmc': ['sierra', 'yukon', 'terrain', 'acadia'], 'great-wall': ['hover', 'steed', 'wingle', 'poer'],
    'haval': ['h6', 'jolion', 'h9', 'f7'], 'honda': ['civic', 'accord', 'cr-v', 'hr-v', 'jazz', 'prelude', 'insight', 'legend'],
    'hummer': ['h2', 'h3'], 'hyundai': ['i10', 'i20', 'i30', 'i40', 'tucson', 'santa-fe', 'kona', 'elantra', 'getz', 'ix35', 'h-1'],
    'infiniti': ['qx70', 'fx', 'g37', 'q50', 'q30', 'qx30', 'qx80'], 'isuzu': ['d-max', 'trooper', 'rodeo'],
    'iveco': ['daily', 'eurocargo', 'stralis'], 'jaguar': ['xf', 'xj', 'f-pace', 'xe', 'e-pace', 'f-type', 's-type', 'x-type'],
    'jeep': ['grand-cherokee', 'wrangler', 'compass', 'renegade', 'cherokee', 'patriot'],
    'kia': ['sportage', 'ceed', 'rio', 'sorento', 'stinger', 'picanto', 'niro', 'venga', 'carens', 'proceed', 'stonic'],
    'lamborghini': ['gallardo', 'huracan', 'aventador', 'urus', 'murcielago'],
    'lancia': ['delta', 'ypsilon', 'musa', 'kappa', 'phedra', 'lybra'],
    'land-rover': ['range-rover', 'discovery', 'freelander', 'defender', 'evoque', 'velar'],
    'lexus': ['rx', 'nx', 'is', 'gs', 'ls', 'ux', 'es', 'lx'],
    'lifan': ['x60', 'solano', 'smily'], 'lincoln': ['navigator', 'aviator', 'continental', 'mkz'],
    'lotus': ['elise', 'exige', 'emira'], 'maserati': ['ghibli', 'levante', 'quattroporte', 'granturismo', 'grecale'],
    'mazda': ['2', '3', '5', '6', 'cx-3', 'cx-30', 'cx-5', 'cx-7', 'cx-9', 'mx-5', '323', '626'],
    'mclaren': ['570s', '720s', 'gt'],
    'mercedes-benz': ['a-klasa', 'b-klasa', 'c-klasa', 'e-klasa', 's-klasa', 'cla', 'cls', 'gla', 'glb', 'glc', 'gle', 'gls', 'g-klasa', 'vito', 'sprinter'],
    'mg': ['mg4', 'zs', 'hs', 'mg5'], 'mini': ['cooper', 'countryman', 'clubman', 'one'],
    'mitsubishi': ['lancer', 'outlander', 'asx', 'pajero', 'l200', 'galant', 'space-star', 'colt'],
    'man': ['tga', 'tgx', 'tgl', 'tge'],
    'nissan': ['qashqai', 'juke', 'x-trail', 'micra', 'leaf', 'patrol', 'navara', 'note', 'primera', 'almera'],
    'opel': ['astra', 'insignia', 'corsa', 'mokka', 'zafira', 'vectra', 'meriva', 'omega', 'frontera', 'vivaro'],
    'pagani': ['zonda', 'huayra'], 'peugeot': ['108', '206', '207', '208', '307', '308', '407', '508', '2008', '3008', '5008', 'partner', 'boxer'],
    'pontiac': ['gto', 'firebird', 'vibe'], 'porsche': ['911', 'cayenne', 'panamera', 'macan', 'boxster', 'taycan'],
    'ram': ['1500', '2500', '3500'], 'renault': ['megane', 'clio', 'scenic', 'captur', 'kadjar', 'talisman', 'laguna', 'espace', 'master', 'trafic'],
    'rolls-royce': ['ghost', 'phantom', 'cullinan'], 'rover': ['75', '45', '25'],
    'saab': ['9-3', '9-5', '900', '9000'], 'seat': ['leon', 'ibiza', 'ateca', 'alhambra', 'altea', 'tarraco', 'arona', 'toledo'],
    'skoda': ['octavia', 'fabia', 'superb', 'kodiaq', 'karoq', 'kamiq', 'rapid', 'scala', 'yeti'],
    'smart': ['fortwo', 'forfour'], 'ssangyong': ['korando', 'musso', 'rexton', 'tivoli'],
    'subaru': ['forester', 'outback', 'impreza', 'legacy', 'xv', 'brz'],
    'suzuki': ['vitara', 'swift', 'grand-vitara', 'jimny', 'sx4', 's-cross', 'ignis', 'baleno'],
    'tatra': ['603', '613', '815', 'phoenix'], 'tesla': ['model-3', 'model-s', 'model-x', 'model-y'],
    'toyota': ['corolla', 'yaris', 'rav4', 'avensis', 'auris', 'aygo', 'c-hr', 'camry', 'land-cruiser', 'hilux'],
    'volkswagen': ['golf', 'passat', 'tiguan', 'touran', 'polo', 'arteon', 'touareg', 'sharan', 'caddy', 't4', 't5', 't6'],
    'volvo': ['v40', 'v50', 'v60', 'v90', 's40', 's60', 's80', 's90', 'xc40', 'xc60', 'xc70', 'xc90'],
    'zotye': ['t600', 'z500']
}

VOIVODESHIPS = {
    'all': 'Вся Польша', 'dolnoslaskie': 'Нижняя Силезия', 'kujawsko-pomorskie': 'Куяво-Поморское',
    'lubelskie': 'Люблинское', 'lubuskie': 'Любушское', 'lodzkie': 'Лодзинское',
    'malopolskie': 'Малопольское', 'mazowieckie': 'Мазовецкое', 'opolskie': 'Опольское',
    'podkarpackie': 'Подкарпатское', 'podlaskie': 'Подляское', 'pomorskie': 'Поморское',
    'slaskie': 'Силезское', 'swietokrzyskie': 'Свентокшиское', 'warminsko-mazurskie': 'Варминьско-Мазурское',
    'wielkopolskie': 'Великопольское', 'zachodniopomorskie': 'Западно-Поморское'
}

def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (user_id INTEGER PRIMARY KEY, brand TEXT DEFAULT "all", 
                     model TEXT DEFAULT "all", max_price INTEGER DEFAULT 1000000, 
                     min_year INTEGER DEFAULT 1970, region TEXT DEFAULT "all", 
                     channel_id TEXT DEFAULT "")''')
    # Изоляция seen_cars по user_id
    conn.execute('CREATE TABLE IF NOT EXISTS seen_cars (user_id INTEGER, link TEXT, PRIMARY KEY (user_id, link))')
    conn.commit()
    conn.close()

def main_menu(user_id):
    conn = sqlite3.connect('users.db')
    u = conn.execute('SELECT brand, model, max_price, min_year, region, channel_id FROM users WHERE user_id=?', (user_id,)).fetchone()
    conn.close()
    if not u: u = ('all', 'all', 1000000, 1970, 'all', '')
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🏎 МАРКА: {u[0].upper()}", callback_data='menu_brand')],
        [InlineKeyboardButton(f"🚙 МОДЕЛЬ: {u[1].upper()}", callback_data='menu_model')],
        [InlineKeyboardButton(f"💰 ЦЕНА ДО: {u[2]} PLN", callback_data='menu_price')],
        [InlineKeyboardButton(f"📅 ОТ ГОДА: {u[3]}", callback_data='menu_year')],
        [InlineKeyboardButton(f"📍 РЕГИОН: {VOIVODESHIPS.get(u[4], u[4]).upper()}", callback_data='menu_region')],
        [InlineKeyboardButton(f"📢 КАНАЛ: {u[5] if u[5] else 'УКАЗАТЬ'}", callback_data='ask_channel')],
        [InlineKeyboardButton("🚀 ПРИМЕНИТЬ И ЗАПУСТИТЬ", callback_data='action_start')]
    ])

def scan_task(context: CallbackContext):
    conn = sqlite3.connect('users.db')
    users = conn.execute('SELECT user_id, brand, model, max_price, min_year, region, channel_id FROM users WHERE channel_id != ""').fetchall()
    for uid, brand, model, price, year, region, channel_id in users:
        reg_p = f"{region}/" if region != 'all' else ""
        b_p = f"{brand}/" if brand != 'all' else ""
        m_p = f"{model}/" if model != 'all' else ""
        url = f"https://www.olx.pl/d/motoryzacja/samochody/{reg_p}{b_p}{m_p}?search%5Bfilter_float_price%3Ato%5D={price}&search%5Bfilter_float_year%3Afrom%5D={year}&search%5Border%5D=created_at%3Adesc"
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for card in soup.find_all('div', {'data-cy': 'l-card'}):
                link_tag = card.find('a', href=True)
                if link_tag:
                    link = ("https://www.olx.pl" + link_tag['href'] if not link_tag['href'].startswith('http') else link_tag['href']).split('?')[0]
                    if not conn.execute('SELECT 1 FROM seen_cars WHERE user_id=? AND link=?', (uid, link)).fetchone():
                        conn.execute('INSERT INTO seen_cars (user_id, link) VALUES (?, ?)', (uid, link))
                        conn.commit()
                        msg = f"🌟 **НОВОЕ ОБЪЯВЛЕНИЕ**\n\n⚙️ {brand.upper()} {model.upper()}\n📍 Регион: {VOIVODESHIPS.get(region)}\n💰 До {price} PLN | 📅 От {year}\n\n🔗 [ОТКРЫТЬ НА OLX]({link})"
                        context.bot.send_message(chat_id=channel_id, text=msg, parse_mode='Markdown')
            time.sleep(random.uniform(0.5, 1))
        except: pass
    conn.close()

def start(update, context):
    init_db()
    uid = update.effective_user.id
    conn = sqlite3.connect('users.db')
    conn.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (uid,))
    conn.commit()
    conn.close()
    update.message.reply_text("🚛 Выберите параметры поиска (каждый клиент настраивает бота под себя):", reply_markup=main_menu(uid))

def callback_proc(update, context):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    conn = sqlite3.connect('users.db')
    if data == 'menu_brand':
        btns = [InlineKeyboardButton(b.upper(), callback_data=f'set_brand_{b}') for b in sorted(CAR_DATA.keys())]
        query.edit_message_text("Выберите марку:", reply_markup=InlineKeyboardMarkup([btns[i:i+3] for i in range(0, len(btns), 3)]))
    elif data.startswith('set_brand_'):
        val = data.replace('set_brand_', '')
        conn.execute('UPDATE users SET brand=?, model="all" WHERE user_id=?', (val, uid))
        conn.commit()
        query.edit_message_text("✅ Марка выбрана", reply_markup=main_menu(uid))
    elif data == 'menu_model':
        res = conn.execute('SELECT brand FROM users WHERE user_id=?', (uid,)).fetchone()
        brand = res[0] if res else 'all'
        models = CAR_DATA.get(brand, ['all'])
        btns = [InlineKeyboardButton(m.upper(), callback_data=f'set_model_{m}') for m in sorted(models)]
        query.edit_message_text("Выберите модель:", reply_markup=InlineKeyboardMarkup([btns[i:i+3] for i in range(0, len(btns), 3)]))
    elif data.startswith('set_model_'):
        val = data.replace('set_model_', '')
        conn.execute('UPDATE users SET model=? WHERE user_id=?', (val, uid))
        conn.commit()
        query.edit_message_text("✅ Модель выбрана", reply_markup=main_menu(uid))
    elif data == 'menu_price':
        prices = [10000, 30000, 50000, 100000, 500000]
        btns = [InlineKeyboardButton(f"{p} PLN", callback_data=f'set_price_{p}') for p in prices]
        query.edit_message_text("Цена до:", reply_markup=InlineKeyboardMarkup([btns[i:i+2] for i in range(0, len(btns), 2)]))
    elif data.startswith('set_price_'):
        val = int(data.replace('set_price_', ''))
        conn.execute('UPDATE users SET max_price=? WHERE user_id=?', (val, uid))
        conn.commit()
        query.edit_message_text("✅ Цена сохранена", reply_markup=main_menu(uid))
    elif data == 'menu_year':
        years = list(range(1990, 2026, 5))
        btns = [InlineKeyboardButton(f"ОТ {y} г.", callback_data=f'set_year_{y}') for y in years]
        query.edit_message_text("Год от:", reply_markup=InlineKeyboardMarkup([btns[i:i+4] for i in range(0, len(btns), 4)]))
    elif data.startswith('set_year_'):
        val = int(data.replace('set_year_', ''))
        conn.execute('UPDATE users SET min_year=? WHERE user_id=?', (val, uid))
        conn.commit()
        query.edit_message_text("✅ Год сохранен", reply_markup=main_menu(uid))
    elif data == 'menu_region':
        btns = [InlineKeyboardButton(name, callback_data=f'set_reg_{key}') for key, name in VOIVODESHIPS.items()]
        query.edit_message_text("Выберите воеводство:", reply_markup=InlineKeyboardMarkup([btns[i:i+2] for i in range(0, len(btns), 2)]))
    elif data.startswith('set_reg_'):
        val = data.replace('set_reg_', '')
        conn.execute('UPDATE users SET region=? WHERE user_id=?', (val, uid))
        conn.commit()
        query.edit_message_text("✅ Регион сохранен", reply_markup=main_menu(uid))
    elif data == 'ask_channel':
        query.edit_message_text("Пришлите @username канала:")
        conn.close()
        return SET_CHANNEL
    elif data == 'action_start':
        u = conn.execute('SELECT channel_id FROM users WHERE user_id=?', (uid,)).fetchone()[0]
        try:
            context.bot.send_message(chat_id=u, text="🚀 Поиск запущен по вашим фильтрам!")
            query.answer("Запущено!", show_alert=True)
        except:
            query.answer("❌ Ошибка! Проверьте права бота в канале.", show_alert=True)
    conn.close()
    query.answer()

def save_channel(update, context):
    uid = update.effective_user.id
    raw = update.message.text.strip()
    cid = '@' + raw.split('/')[-1] if 't.me/' in raw else (raw if raw.startswith(('@','-100')) else '@'+raw)
    conn = sqlite3.connect('users.db')
    conn.execute('UPDATE users SET channel_id=? WHERE user_id=?', (cid, uid))
    conn.commit()
    conn.close()
    update.message.reply_text(f"✅ Канал {cid} привязан!", reply_markup=main_menu(uid))
    return ConversationHandler.END

if __name__ == '__main__':
    init_db()
    updater = Updater(TOKEN)
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_proc)],
        states={SET_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, save_channel)]},
        fallbacks=[CommandHandler('start', start)],
        per_message=False
    )
    updater.job_queue.run_repeating(scan_task, interval=120, first=10)
    updater.dispatcher.add_handler(conv)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_proc))
    updater.start_polling()
    updater.idle()
