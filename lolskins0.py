# -*- coding: utf-8 -*-
# BY: OUYANG T.

"""
This script aims to download LOL hero skins from https://lol.qq.com/data/info-heros.shtml.
"""


import re
import os
import json
import requests


class LoLSkins(object):
    def __init__(self, dirs, flush=True):
        self.n_heroes = 0
        self.n_skins = 0
        self.n_notfound = 0
        self.notfound_urls = []
        self.dirs = dirs

        # javascript url
        self.heroes_url = r'https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js'
        self.hero_url = r'https://game.gtimg.cn/images/lol/act/img/js/hero/{:s}.js'


        if not os.path.isdir(dirs['js']):
            os.makedirs(dirs['js'])


    def _download(self, url, filename=''):
        if filename == '':
            filename = url.split('/')[-1]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
        elif r.status_code == 404:
            self.n_notfound += 1
            self.notfound_urls.append(url)
        else:
            # r.raise_for_status()
            pass


    def parse_heroes(self):
        js_filename = os.path.join(self.dirs['js'], self.heroes_url.split('/')[-1])
        self._download(self.heroes_url, js_filename)

        with open(js_filename, 'r') as f:
            heroes_data = json.load(f)
            version = heroes_data['version']
            filetime = heroes_data['fileTime']
            heroes_list = heroes_data['hero']
        

        print("Version {:s}".format(version))
        print("{:d} heroes detected".format(len(heroes_list)))
        print("Filetime {:s}".format(filetime))

        for i, h in enumerate(heroes_list):
            self.n_heroes += 1
            self.download_hero(i, h)

        print("\n{:d} skins for {:d} heroes downloaded.".format(self.n_skins, self.n_heroes))

        # if self.n_notfound:
        #     print("{:d} files not found.".format(self.n_notfound))
        #     print(self.notfound_urls)


    def download_hero(self, i, hero):
        js_filename = os.path.join(self.dirs['js'], '{:s}_{:s}.js'.format(hero['heroId'], hero['alias']))
        self._download(self.hero_url.format(hero['heroId']), js_filename)

        with open(js_filename, 'r') as f:
            hero_data = json.load(f)
            version = hero_data['version']
            filetime = hero_data['fileTime']
            info = hero_data['hero']
            skins = hero_data['skins']

            hero_id = info['heroId']
            name = info['name']
            alias = info['alias']
            title = info['title']

        print("[{:d}] hero_id: {:s}, name: {:s}, title: {:s}, alias: {:s}".format(i+1, hero_id, name, title, alias))

        # make dirs
        dirs = {}
        for d in self.dirs['hero']:
            dirs[d] = self.dirs['hero'][d].format(name+' '+title)
            if not os.path.isdir(dirs[d]):
                os.makedirs(dirs[d])

        n_skins = 0
        for j in range(len(skins)):
            if skins[j]['chromas'] == '1':
                continue
            n_skins += 1
            skin_id = skins[j]['skinId']
            skin_name = skins[j]['name']
            print("    skin_id: {:s}, skin_name: {:s}".format(skin_id, skin_name))

            # for filename rules on e.g., Windows
            skin_name = re.sub(r'[\\/:*?"<>|]+', '', skin_name)

            self._download(skins[j]['mainImg'], os.path.join(dirs['main'], skin_name+'.'+skins[j]['mainImg'].split('.')[-1]))
            self._download(skins[j]['loadingImg'], os.path.join(dirs['loading'], skin_name+'.'+skins[j]['loadingImg'].split('.')[-1]))
        
        self.n_skins += n_skins
        print("    {:d} skins downloaded".format(n_skins))

        self._download(info['selectAudio'], os.path.join(dirs['audio'], 'pick_'+info['selectAudio'].split('/')[-1]))
        self._download(info['banAudio'], os.path.join(dirs['audio'], 'ban_'+info['selectAudio'].split('/')[-1]))
        print("    pick/ban audio downloaded")



if __name__ == '__main__':

    dirs = {
        'js': 'lolhero/js',
        'hero': {
            'audio': 'lolhero/hero/{:s}/audio',
            'main': 'lolhero/hero/{:s}/main',
            'loading': 'lolhero/hero/{:s}/loading',
            # 'icon': 'lolhero/hero/{:s}/icon',
            # 'video': 'lolhero/hero/{:s}/video',
            # 'source': 'lolhero/hero/{:s}/source'
        }
    }


    parser = LoLSkins(dirs)
    parser.parse_heroes()
    