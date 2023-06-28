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

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if input_mode == "city":
                    self.params['city'] = event.text
                    self.message_send(event.user_id, f'Итак, ваш город: {self.params["city"]}')
                    input_mode = 'ready'
                if input_mode == "city":
                    self.params['year'] = event.text
                    input_mode = "ready"
                if input_mode == "sex":
                    if event.text.strip()[0].lower() in 'mм':
                        self.params['sex'] = 2
                    elif event.text.strip()[0].lower() in 'fж':
                        self.params['sex'] = 1
                    else:
                        self.message_send(event.user_id, f'Попробуйте ещё раз.')
                

                elif command == 'привет' or command == 'здравствуйте':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]}')
                    print(self.params)
                    if self.params['city'] == '':
                        self.message_send(event.user_id, f'В каком городе Вы находитесь?')
                        input_mode = "city"
                    elif self.params['bdate'] == None:
                        self.message_send(event.user_id, f'Пожалуйста, введите дату вашего рождения в формате ДД.ММ.ГГГГ:')
                        input_mode = "bdate"
                    elif self.params['sex'] == 0:
                        self.message_send(event.user_id, 'Укажите ваш пол: м, m - мужской, f, ж - женский')
                        input_mode = "sex"
                    else:
                        input_mode = "ready"



                elif command == 'поиск':
                    if input_mode == "ready":
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

            
