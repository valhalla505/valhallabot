import telebot
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from datetime import datetime, timedelta
import threading
import json
import os

class ValhallaBot:
    def __init__(self, bot_token, admin_id):
        self.bot = telebot.TeleBot(bot_token)
        self.admin_id = admin_id
        self.user_data = {}
        self.allowed_users = [str(admin_id)]
        self.subscription_data = {}

        self.keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        self._setup_keyboard()

        self._register_handlers()

    def _setup_keyboard(self):
        btn_add_recipient = telebot.types.InlineKeyboardButton(' اضف ايميل الدعم', callback_data='add_recipient')
        btn_add_sender = telebot.types.InlineKeyboardButton('اضف ايميل شد', callback_data='add_sender')
        btn_set_subject = telebot.types.InlineKeyboardButton('تعيين الموضوع', callback_data='set_subject')
        btn_set_message = telebot.types.InlineKeyboardButton('تعيين الكليشة', callback_data='set_message')
        btn_set_interval = telebot.types.InlineKeyboardButton('تعيين السليب', callback_data='set_interval')
        btn_set_message_count = telebot.types.InlineKeyboardButton('تعيين عدد الرسائل', callback_data='set_message_count')
        btn_start_sending = telebot.types.InlineKeyboardButton(' بدء الارسال', callback_data='start_sending')
        btn_show_accounts = telebot.types.InlineKeyboardButton(' ايميلاتي', callback_data='show_accounts')
        btn_show_all_info = telebot.types.InlineKeyboardButton(' عرض المعلومات', callback_data='show_all_info')
        btn_clear_all_info = telebot.types.InlineKeyboardButton(' مسح كل المعلومات', callback_data='clear_all_info')
        btn_delete_email = telebot.types.InlineKeyboardButton(' حذف ايميل محدد', callback_data='delete_email')
        btn_stop_sending = telebot.types.InlineKeyboardButton(' إيقاف الإرسال', callback_data='stop_sending')

        self.keyboard.add(btn_start_sending, btn_show_accounts)
        self.keyboard.add(btn_add_recipient, btn_add_sender)
        self.keyboard.add(btn_set_subject, btn_set_message)
        self.keyboard.add(btn_set_interval, btn_set_message_count)
        self.keyboard.add(btn_show_all_info, btn_clear_all_info)

        self.admin_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_add_subscriber = telebot.types.InlineKeyboardButton(' اضف مشترك', callback_data='add_subscriber')
        btn_show_subscribers = telebot.types.InlineKeyboardButton('عرض المشتركين', callback_data='show_subscribers')
        btn_remove_subscriber = telebot.types.InlineKeyboardButton('حذف مشترك', callback_data='remove_subscriber')
        self.admin_keyboard.add(btn_add_subscriber, btn_show_subscribers, btn_remove_subscriber)

        self.duration_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_one_day = telebot.types.InlineKeyboardButton(' يوم', callback_data='duration_1_day')
        btn_one_week = telebot.types.InlineKeyboardButton('اسبوع', callback_data='duration_1_week')
        btn_one_month = telebot.types.InlineKeyboardButton(' شهر', callback_data='duration_1_month')
        btn_one_year = telebot.types.InlineKeyboardButton(' سنه', callback_data='duration_1_year')
        self.duration_keyboard.add(btn_one_day, btn_one_week, btn_one_month, btn_one_year)

    def _register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            user_id = str(message.from_user.id)
            self._add_user_to_data(user_id)
            self.bot.reply_to(message, 'اهلا بك في بوت الرفع الخارجي (صلخ بل نعال) ', reply_markup=self.keyboard)

        @self.bot.message_handler(commands=['stop'])
        def stop(message):
            user_id = str(message.from_user.id)
            user_info = self.user_data.get(user_id)
            if user_info:
                user_info['stop_sending'] = True
                self.bot.reply_to(message, 'تم إيقاف عملية الإرسال بنجاح!')
            else:
                self.bot.reply_to(message, 'لم تقم ببدء عملية الإرسال بعد.')

        @self.bot.message_handler(commands=['admin'])
        def show_admin_commands(message):
            if message.from_user.id == self.admin_id:
                self.bot.send_message(message.chat.id, 'اختر الأمر الذي ترغب في تنفيذه:', reply_markup=self.admin_keyboard)
            else:
                self.bot.reply_to(message, 'أنت لست مطورًا مصرحًا')

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            user_id = str(call.from_user.id)
            self._add_user_to_data(user_id)
            user_info = self.user_data[user_id]

            if call.data == 'add_recipient':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""
                قم بأرسال ايميلات الشركة بهذه الطريقة:
email@tele.com email2@tele.com""")
                self.bot.register_next_step_handler(call.message, self._add_recipient, user_id)
            elif call.data == 'add_sender':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="""
                قم بارسال ايميلات الشد بهاذه الطريقة:
email1:pass1
email2:pass2""")
                self.bot.register_next_step_handler(call.message, self._add_sender, user_id)
            elif call.data == 'set_subject':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال الموضوع:')
                self.bot.register_next_step_handler(call.message, self._set_subject, user_id)
            elif call.data == 'set_message':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال الكليشة:')
                self.bot.register_next_step_handler(call.message, self._set_message, user_id)
            elif call.data == 'set_interval':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال السليب:')
                self.bot.register_next_step_handler(call.message, self._set_interval, user_id)
            elif call.data == 'set_message_count':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال عدد الرسائل:')
                self.bot.register_next_step_handler(call.message, self._set_message_count, user_id)
            elif call.data == 'start_sending':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='جارٍ بدء إرسال الرسائل...')
                self._start_sending(user_id)
            elif call.data == 'show_accounts':
                self._show_accounts(call.message, user_id)
            elif call.data == 'show_all_info':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ايميلات الدعم: {}\n\nالموضوع: {}\n\nالكليشة: {}\n\nالسليب: {} ثانية\n\nعدد الرسائل: {}'.format(', '.join(user_info['recipients']), user_info['email_subject'], user_info['email_message'], user_info['interval_seconds'], user_info['message_count']))
            elif call.data == 'clear_all_info':
                self._clear_all_info(call.message, user_id)
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='تم مسح جميع المعلومات بنجاح!')
            elif call.data == 'delete_email':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال رقم البريد الإلكتروني الذي ترغب في حذفه.')
                self.bot.register_next_step_handler(call.message, self._delete_email, user_id)
            elif call.data.startswith('delete_'):
                self._handle_delete_email_callback(call)
            elif call.data == 'stop_sending':
                self._stop_sending(call.message)
            elif call.data == 'add_subscriber':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال ID الشخص الذي تريد اضافته لقائمة المشتركين')
                self.bot.register_next_step_handler(call.message, self._add_subscriber)
            elif call.data == 'show_subscribers':
                self._show_subscribers(call.message)
            elif call.data == 'remove_subscriber':
                self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='الرجاء إرسال ID الشخص الذي تريد حذفه من قائمة المشتركين')
                self.bot.register_next_step_handler(call.message, self._remove_subscriber)
            elif call.data.startswith('duration_'):
                self._handle_subscription_duration(call, user_id, call.data)

    def _load_user_data(self, user_id):
        file_path = f'{user_id}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return {
            'email_senders': [],
            'email_passwords': [],
            'recipients': [],
            'email_subject': '',
            'email_message': '',
            'interval_seconds': 0,
            'message_count': 0
        }

    def _save_user_data(self, user_id, data):
        file_path = f'{user_id}.json'
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _add_user_to_data(self, user_id):
        self.user_data[user_id] = self._load_user_data(user_id)

    def _add_recipient(self, message, user_id):
        recipients = message.text.split()
        if recipients:
            user_info = self._load_user_data(user_id)
            user_info['recipients'].clear()
            user_info['recipients'].extend(recipients)
            self._save_user_data(user_id, user_info)
            self.bot.reply_to(message, 'تمت إضافة الحسابات المستلمة بنجاح!')
        else:
            self.bot.reply_to(message, 'خطأ في إضافة الحسابات المستلمة. الرجاء المحاولة مرة أخرى.')

    def _add_sender(self, message, user_id):
        email_password_pairs = message.text.split('\n')
        success_count = 0
        failure_count = 0
        user_info = self._load_user_data(user_id)

        for pair in email_password_pairs:
            sender_email_password = pair.split(':')
            if len(sender_email_password) == 2:
                sender_email = sender_email_password[0].strip()
                sender_password = sender_email_password[1].strip()
                if sender_email and sender_password:
                    user_info['email_senders'].append(sender_email)
                    user_info['email_passwords'].append(sender_password)
                    success_count += 1
                else:
                    failure_count += 1
            else:
                failure_count += 1

        self._save_user_data(user_id, user_info)
        
        if success_count > 0:
            self.bot.reply_to(message, f'تمت إضافة {success_count} حساب مرسل بنجاح!')
        if failure_count > 0:
            self.bot.reply_to(message, f'حدث خطأ في إضافة {failure_count} حساب مرسل. الرجاء التحقق من الصيغة الصحيحة (Email:pass).')

    def _set_subject(self, message, user_id):
        user_info = self._load_user_data(user_id)
        user_info['email_subject'] = message.text
        self._save_user_data(user_id, user_info)
        self.bot.reply_to(message, 'تم تعيين الموضوع بنجاح!')

    def _set_message(self, message, user_id):
        user_info = self._load_user_data(user_id)
        user_info['email_message'] = message.text
        self._save_user_data(user_id, user_info)
        self.bot.reply_to(message, 'تم تعيين الكليشة بنجاح!')

    def _set_interval(self, message, user_id):
        try:
            interval_seconds = int(message.text)
            user_info = self._load_user_data(user_id)
            user_info['interval_seconds'] = interval_seconds
            self._save_user_data(user_id, user_info)
            self.bot.reply_to(message, 'تم تعيين السليب بنجاح!')
        except ValueError:
            self.bot.reply_to(message, 'الرجاء إدخال رقم صحيح للسليب.')

    def _set_message_count(self, message, user_id):
        try:
            message_count = int(message.text)
            user_info = self._load_user_data(user_id)
            user_info['message_count'] = message_count
            self._save_user_data(user_id, user_info)
            self.bot.reply_to(message, 'تم تعيين عدد الرسائل بنجاح!')
        except ValueError:
            self.bot.reply_to(message, 'الرجاء إدخال رقم صحيح لعدد الرسائل.')

    def _delete_email(self, message, user_id):
        try:
            index = int(message.text) - 1
            user_info = self._load_user_data(user_id)
            if index >= 0 and index < len(user_info['email_senders']):
                del user_info['email_senders'][index]
                del user_info['email_passwords'][index]
                self._save_user_data(user_id, user_info)
                self.bot.reply_to(message, 'تم حذف البريد الإلكتروني بنجاح!')
            else:
                self.bot.reply_to(message, 'خطأ في حذف البريد الإلكتروني. الرجاء المحاولة مرة أخرى.')
        except ValueError:
            self.bot.reply_to(message, 'خطأ في التحويل إلى رقم. يرجى إدخال رقم صحيح لحذف البريد الإلكتروني.')

    def _send_email(self, sender_email, sender_password, recipient, subject, message):
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg['X-Device'] = 'iPhone 16'
        msg.attach(MIMEText(message, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            return False

    def _send_emails(self, user_id, user_info):
        success_count = 0
        error_count = 0
        prev_message_id = None
        blocked_senders = set()

        initial_message = ("بدأ عملية الارسال، سوف يتم الارسال بشكل عمودي ..\n"
                           "تم ارسال: 0\n"
                           "فشل اثناء: 0\n"
                           "سوف تكتمل العملية قريبا!\n"
                           "ارسل /stop للايقاف")
        
        try:
            sent_message = self.bot.send_message(user_id, initial_message)
            prev_message_id = sent_message.message_id

            for i in range(user_info['message_count']):
                for sender, password in zip(user_info['email_senders'], user_info['email_passwords']):
                    if sender in blocked_senders:
                        continue

                    try:
                        recipient_email = random.choice(user_info['recipients'])

                        if user_info.get('stop_sending'):
                            del user_info['stop_sending']
                            self.bot.send_message(user_id, 'تم إيقاف عملية الإرسال.')
                            return

                        if self._send_email(sender, password, recipient_email, user_info['email_subject'], user_info['email_message']):
                            success_count += 1
                        else:
                            error_count += 1
                            blocked_senders.add(sender)
                            self.bot.send_message(user_id, f'الإيميل {sender} محظور، تم التوقف عن استخدامه.')

                    except Exception as e:
                        error_count += 1
                        blocked_senders.add(sender)
                        self.bot.send_message(user_id, f'الإيميل {sender} تم التوقف عن استخدامه')

                    time.sleep(user_info['interval_seconds'])

                    status_message = (f"تم ارسال: {success_count}\n"
                                      f"فشل اثناء: {error_count}\n"
                                      "سوف تكتمل العملية قريبا!\n"
                                      "ارسل /stop للايقاف")
                    self.bot.edit_message_text(chat_id=user_id, message_id=prev_message_id, text=status_message)

            final_message = (f"تم الانتهاء.\n"
                             f"تم ارسال: {success_count}\n"
                             f"فشل اثناء: {error_count}\n")
            self.bot.edit_message_text(chat_id=user_id, message_id=prev_message_id, text=final_message)
        
        except Exception as e:
            pass

    def _start_sending(self, user_id):
        user_info = self.user_data[user_id]
        if len(user_info['recipients']) == 0:
            self.bot.send_message(user_id, 'لا يوجد حسابات مستلمة. الرجاء إضافة حساب مستلم أولاً.')
            return

        if len(user_info['email_senders']) == 0:
            self.bot.send_message(user_id, 'لا يوجد حسابات مرسلة. الرجاء إضافة حساب مرسل أولاً.')
            return

        if user_info['email_subject'] == '':
            self.bot.send_message(user_id, 'لم يتم تعيين الموضوع. الرجاء تعيين الموضوع أولاً.')
            return

        if user_info['email_message'] == '':
            self.bot.send_message(user_id, 'لم يتم تعيين الرسالة. الرجاء تعيين الرسالة أولاً.')
            return

        if user_info['message_count'] == 0:
            self.bot.send_message(user_id, 'لم يتم تعيين عدد الرسائل. الرجاء تعيين عدد الرسائل أولاً.')
            return

        self.bot.send_message(user_id, 'جارٍ بدء إرسال الرسائل...')
        
        sending_thread = threading.Thread(target=self._send_emails, args=(user_id, user_info))
        sending_thread.start()

    def _show_accounts(self, message, user_id):
        user_info = self._load_user_data(user_id)
        if len(user_info['email_senders']) == 0:
            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='لم يتم إضافة أي حسابات مرسلة حتى الآن.')
        else:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            for i, sender in enumerate(user_info['email_senders']):
                btn_delete_email = telebot.types.InlineKeyboardButton(f'حذف {sender}', callback_data=f'delete_{i}')
                keyboard.add(btn_delete_email)

            self.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='إيميلات المرسلين:', reply_markup=keyboard)

    def _handle_delete_email_callback(self, call):
        user_id = str(call.from_user.id)
        self._add_user_to_data(user_id)
        index = int(call.data.split('_')[1])
        user_info = self._load_user_data(user_id)

        if index >= 0 and index < len(user_info['email_senders']):
            del user_info['email_senders'][index]
            del user_info['email_passwords'][index]
            self._save_user_data(user_id, user_info)
            self.bot.answer_callback_query(call.id, text='تم حذف البريد الإلكتروني بنجاح!')
        else:
            self.bot.answer_callback_query(call.id, text='خطأ في حذف البريد الإلكتروني. الرجاء المحاولة مرة أخرى.')

        self._show_accounts(call.message, user_id)

    def _show_all_info(self, message, user_id):
        user_info = self._load_user_data(user_id)
        info_message = f"ايميلات الدعم: {', '.join(user_info['recipients'])}\n\n"
        info_message += f"الموضوع: {user_info['email_subject']}\n\n"
        info_message += f"الكليشة: {user_info['email_message']}\n\n"
        info_message += f"السليب: {user_info['interval_seconds']} ثانية\n\n"
        info_message += f"عدد الرسائل: {user_info['message_count']}\n"
        self.bot.reply_to(message, info_message)

    def _clear_all_info(self, message, user_id):
        user_info = {
            'email_senders': [],
            'email_passwords': [],
            'recipients': [],
            'email_subject': '',
            'email_message': '',
            'interval_seconds': 0,
            'message_count': 0
        }
        self._save_user_data(user_id, user_info)
        self.bot.reply_to(message, 'تم مسح جميع المعلومات بنجاح!')

    def _add_subscriber(self, message):
        new_user_id = message.text
        self.bot.reply_to(message, 'اختار مدة الاشتراك', reply_markup=self.duration_keyboard)
        self.subscription_data['temp_user_id'] = new_user_id

    def _handle_subscription_duration(self, call, admin_id, duration):
        temp_user_id = self.subscription_data.get('temp_user_id')
        if not temp_user_id:
            self.bot.send_message(admin_id, 'لم يتم العثور على المستخدم. الرجاء المحاولة مرة أخرى.')
            return

        duration_map = {
            'duration_1_day': timedelta(days=1),
            'duration_1_week': timedelta(weeks=1),
            'duration_1_month': timedelta(days=30),
            'duration_1_year': timedelta(days=365)
        }
        duration_timedelta = duration_map.get(duration)
        if not duration_timedelta:
            self.bot.send_message(admin_id, 'مدة اشتراك غير صالحة. الرجاء المحاولة مرة أخرى.')
            return

        expiration_date = datetime.now() + duration_timedelta
        self.allowed_users.append(temp_user_id)
        self.subscription_data[temp_user_id] = expiration_date
        self.bot.send_message(admin_id, f'تم إضافة المستخدم {temp_user_id} بنجاح لمدة {duration_timedelta.days} يوم.')

        Thread(target=self._remove_user_after_duration, args=(temp_user_id, duration_timedelta)).start()

    def _remove_user_after_duration(self, user_id, duration):
        time.sleep(duration.total_seconds())
        if user_id in self.allowed_users:
            self.allowed_users.remove(user_id)
            del self.subscription_data[user_id]
            self.bot.send_message(self.admin_id, f'تمت إزالة المستخدم {user_id} بعد انتهاء مدة الاشتراك.')

    def _show_subscribers(self, message):
        if not self.subscription_data:
            self.bot.reply_to(message, 'لا يوجد مشتركون حاليًا.')
            return

        subscribers_info = []
        for user_id, expiration_date in self.subscription_data.items():
            subscribers_info.append(f'ID: {user_id}, مدة الاشتراك: {expiration_date}')

        self.bot.reply_to(message, '\n'.join(subscribers_info))

    def _remove_subscriber(self, message):
        user_id = message.text
        if user_id in self.allowed_users:
            self.allowed_users.remove(user_id)
            del self.subscription_data[user_id]
            self.bot.reply_to(message, f'تم حذف المستخدم {user_id} بنجاح.')
        else:
            self.bot.reply_to(message, 'المستخدم غير موجود في قائمة المشتركين.')

    def run(self):
        self.bot.infinity_polling()