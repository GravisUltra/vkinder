from datetime import datetime 

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

        thousands = count // 1000
        remainder = count % 1000

        users_list = []

        for i in range(1, thousands):
            users = self.api.method('users.search',
                                    {'count': 1000,
                                    'offset': offset,
                                    'age_from': age_from,
                                    'age_to': age_to,
                                    'sex': sex,
                                    'home_town': city,
                                    'status': 6,
                                    'is_closed': False
                                    }
                                )

            try:
                users_list += users['items']
            except KeyError:
                break
            else:
                offset += i * 1000


        if remainder != 0:
            users = self.api.method('users.search',
                                    {'count': remainder,
                                    'offset': offset,
                                    'age_from': age_from,
                                    'age_to': age_to,
                                    'sex': sex,
                                    'home_town': city,
                                    'status': 6,
                                    'is_closed': False
                                    }
                                )
            offset += remainder
            try:
                users_list += users['items']
            except KeyError:
                pass
        
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
    params['age'] = 30
    users = bot.search_users(params, count=10, offset=0)
    print(bot.get_photos(users[2]['id']))

