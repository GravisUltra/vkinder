# импорты
from typing import Any
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime 
from config import community_token, access_token
from core import VkTools
import data_store as ds

class BotInterface():


    def __init__(self,community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.params = None
        self.profiles = []


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
        

    def get_command(self):
        sulongpoll = VkLongPoll(self.interface)
        for subevent in sulongpoll.listen():
            if subevent.type == VkEventType.MESSAGE_NEW and subevent.to_me:
                return {'user_id': subevent.user_id,
                        'command': subevent.text.lower()}
                

    def ask_city(self):
        sublongpoll = VkLongPoll(self.interface)
        for subevent in sublongpoll.listen():
            if subevent.type == VkEventType.MESSAGE_NEW and subevent.to_me:
                return subevent.text
            

    def input_text(self):
        sublongpoll = VkLongPoll(self.interface)
        for subevent in sublongpoll.listen():
            if subevent.type == VkEventType.MESSAGE_NEW and subevent.to_me:
                return {'user_id': subevent.user_id,
                        'text': subevent.text}
    
    def ask_age(self):
        age = 0
        while age == 0:
            data = self.input_text()
            user_id = data['user_id']
            text = data['text']
            try:
                age = int(text)
                if not 17 <  age < 101:
                    self.message_send(user_id, f'Некорректно указан возраст. Попробуйте ещё раз.')
                    age = 0
            except:
                self.message_send(user_id, f'Некорректно указан возраст. Попробуйте ещё раз.')
                age = 0
        return age

         
    def ask_sex(self):
        sublongpoll = VkLongPoll(self.interface)
        for subevent in sublongpoll.listen():
            if subevent.type == VkEventType.MESSAGE_NEW and subevent.to_me:
                if subevent.text.strip()[0].lower() in 'mм':
                    self.params['sex'] = 2
                    self.message_send(subevent.user_id, 'Итак, Вы мужчина.')
                    return 2
                elif subevent.text.strip()[0].lower() in 'fж':
                    self.params['sex'] = 1
                    self.message_send(subevent.user_id, 'Итак, Вы женщина.')
                    return 1
                else:
                    self.message_send(subevent.user_id, f'Попробуйте ещё раз.')


    def check_and_fill_params(self, params):
        user_id = params['id']
        if params['bdate'] != None:
            user_year = int(params['bdate'].split('.')[2])
            current_year = datetime.now().year
            params['age'] = current_year - user_year
        else:
            params['age'] = None
        
        if params['city'] == '':
            self.message_send(user_id, f'В каком городе Вы живёте?')
            params['city'] = self.ask_city()
            self.message_send(user_id, f'Итак, ваш город: {params["city"]}')
            
        if self.params['age'] == None:
            self.message_send(user_id, f'Пожалуйста, введите ваш возраст (от 18 до 100 лет).')
            params['age'] = self.ask_age()
            self.message_send(user_id, f'Итак, ваш возраст: {params["age"]}')

        if self.params['sex'] == 0:
            self.message_send(user_id, f'Укажите ваш пол: м, m - мужской; f, ж - женский')
            params['sex'] = self.ask_sex()
            
        return params
    
        
    def search(self, params, count):
        offset = 0
        if len(self.profiles) == 0:
            self.profiles = self.api.search_users(params=params, count=count, offset=offset)
        
        if len(self.profiles) > 0:
            profile = self.profiles.pop()
            while ds.profile_is_viewed_by(profile['id'], self.params['id']):
                if len(self.profiles) > 0:
                    profile = self.profiles.pop()
                else:
                    offset += count
                    self.profiles = self.api.search_users(params=params, count=count, offset=offset)
                    if len(self.profiles) > 0:
                        profile = self.profiles.pop()
                    else:
                        profile = None
                        break
        return profile


    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        self.params = None
        waiting_for_greeting = True

        while True:
                command_pack = self.get_command()
                user_id = command_pack['user_id']
                command = command_pack['command']
            
                if command == 'привет' or command == 'здравствуйте':
                    if self.params is None:
                        self.params = self.api.get_profile_info(user_id)
                        '''Следующие три строки нужны только для тестирования.
                        Для нормального использования программы
                        их нужно удалить или закомментировать.'''
                        # self.params['city'] = ''
                        # self.params['bdate'] = None
                        # self.params['sex'] = 0
                    self.message_send(user_id, f'Здравствуйте, {self.params["name"]}')
                    # print("До проверрки:", self.params)
                    self.params = self.check_and_fill_params(self.params)
                    waiting_for_greeting = False
                    self.message_send(user_id, 'Готово. Теперь Вы можете использовать команду "Поиск"')
                    # print("После проверки:", self.params)

                elif command == 'поиск':
                    if not waiting_for_greeting:
                        self.message_send(user_id, 'Ищу...')
                        profile = self.search(self.params, count)
                        if profile is None:
                            self.message_send(user_id, 'Вы уже просмотрели все подходящие анкеты.')
                        else:
                            photos_user = self.api.get_photos(profile['id'])      
                            
                            attachment = ""
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.message_send(user_id,
                                                f'Встречайте: {profile["name"]}\n vk.com/id{profile["id"]}',
                                                attachment=attachment
                                                ) 
                            #добавляем профиль в список просмотренных
                            ds.add_profile(user=self.params['id'], profile=profile['id'])
                        
                    else:
                        self.message_send(user_id, 'Сначала нужно поздороваться!')

                elif command == 'пока':
                    self.message_send(user_id, 'Пока!')
                else:
                    self.message_send(user_id, f'Команда "{command}" не опознана.')


# демонстрация обхода ограничения на количесвтво профилей, выдаваемых методом "search" VK API 
count = 1501

if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

