from datetime import datetime
import time

import vk_api

from config import access_token



class VkTools():
    def __init__(self, access_token):
       self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town' 
                            }
                            )
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'],
                     'city': info['home_town']
                     }
        return user_info
    
    def search_users(self, params, count, offset):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        age = params['age']
        age_from = age - 5
        age_to = age + 5

        step = 500
        delay = 1
        steps = count // step

        users_list = []

        for i in range(steps + 1):
            print("Step", i + 1)
            users = self.api.method('users.search',
                                    {'count': step,
                                    'offset': offset,
                                    'age_from': age_from,
                                    'age_to': age_to,
                                    'sex': sex,
                                    'home_town': city,
                                    'status': 6,
                                    'is_closed': False
                                    }
                                )
            if len(users['items']) == 0:
                   break

            try:
                users_list += users['items']
            except KeyError:
                break
            else:
                offset += len(users['items'])
                print(len(users['items']))
            time.sleep(delay)
        print('After all steps', len(users_list))

        res = []
        for user in users_list:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError:
            return []
        
        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res

# просто тестовый код
if __name__ == '__main__':
    bot = VkTools(access_token)
    params = bot.get_profile_info(789657038)
    user_year = int(params['bdate'].split('.')[2])
    current_year = datetime.now().year
    params['age'] = current_year - user_year
    print(params)
    users = bot.search_users(params, count=3300, offset=0)
    print(bot.get_photos(users[2]['id']))

