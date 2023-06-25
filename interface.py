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
        profiles = self.api.search_users(params=params, count=count, offset=offset)
        if len(profiles) > 0:
            profile = profiles.pop()
            while ds.profile_is_viewed_by(profile['id'], self.params['id']):
                if len(profiles) > 0:
                    profile = profiles.pop()
                else:
                    offset += count
                    profiles = profiles = self.api.search_users(params=params, count=count, offset=offset)
                    if len(profiles) > 0:
                        profile = profiles.pop()
                    else:
                        # self.message_send(event.user_id, 'Вы уже просмотрели все подходящие анкеты.')
                        profile = None
                        break
        return profile

        
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет' or command == 'здравствуйте':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]}')

                elif command == 'поиск':
                    count = 50
                    profile = self.search(self.params, count)
                    if profile is None:
                        self.message_send(event.user_id, 'Вы уже просмотрели все подходящие анкеты.')
                    else:
                        photos_user = self.api.get_photos(profile['id'])
                        #добавляем провфиль в список просмотренных
                        ds.add_profile(user=self.params['id'], profile=profile['id'])          
                        
                        attachment = ''
                        for num, photo in enumerate(photos_user):
                            attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                            if num == 2:
                                break
                        self.message_send(event.user_id,
                                            f'Встречайте: {profile["name"]}',
                                            attachment=attachment
                                            ) 

            
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')



if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()

            

