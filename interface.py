# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

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
        input_mode = "waiting for greeting"
        self.params = None
        waiting_for_greeting = True
        no_city = False
        no_bdate = False
        no_sex = False

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                print(self.params)
                if no_city:
                    self.params['city'] = event.text
                    self.message_send(event.user_id, f'Итак, ваш город: {self.params["city"]}')
                    no_city = False
                elif no_bdate:
                    self.params['bdate'] = event.text
                    self.message_send(event.user_id, f'Итак, дата вашего рождения: {self.params["bdate"]}')
                    no_bdate = False
                elif no_sex:
                    if event.text.strip()[0].lower() in 'mм':
                        self.params['sex'] = 2
                        self.message_send(event.user_id, 'Итак, Вы мужчина.')
                        no_sex = False
                    elif event.text.strip()[0].lower() in 'fж':
                        self.params['sex'] = 1
                        self.message_send(event.user_id, 'Итак, Вы женщина.')
                        no_sex = False
                    else:
                        self.message_send(event.user_id, f'Попробуйте ещё раз.')
                
            
                elif command == 'привет' or command == 'здравствуйте':
                    if self.params is None:
                        self.params = self.api.get_profile_info(event.user_id)
                        '''Следующие три строки нужны только для тестирования.
                        Для нормального использования программы
                        их нужно удалить или закомментировать.'''
                        self.params['city'] = ''
                        self.params['bdate'] = None
                        self.params['sex'] = 0
                    self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]}')
                    
                    
                    if self.params['city'] == '':
                        self.message_send(event.user_id, f'В каком городе Вы находитесь?')
                        no_city = True
                    elif self.params['bdate'] == None:
                        self.message_send(event.user_id, f'Пожалуйста, введите дату вашего рождения в формате ДД.ММ.ГГГГ:')
                        no_bdate = True
                    elif self.params['sex'] == 0:
                        self.message_send(event.user_id, 'Укажите ваш пол: м, m - мужской, f, ж - женский')
                        no_sex = True
                    else:
                        waiting_for_greeting = False
                        self.message_send(event.user_id, 'Готово. Теперь Вы можете использовать команду "Поиск"')
                    print(self.params)

                elif command == 'поиск':
                    if not waiting_for_greeting:
                        count = 50
                        profile = self.search(self.params, count)
                        if profile is None:
                            self.message_send(event.user_id, 'Вы уже просмотрели все подходящие анкеты.')
                        else:
                            photos_user = self.api.get_photos(profile['id'])      
                            
                            attachment = ""
                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.message_send(event.user_id,
                                                f'Встречайте: {profile["name"]}: vk.com/id{profile["id"]}',
                                                attachment=attachment
                                                ) 
                            #добавляем профиль в список просмотренных
                            ds.add_profile(user=self.params['id'], profile=profile['id'])
                        
                    else:
                        self.message_send(event.user_id, 'Сначала нужно поздороваться!')

                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

            
