#-------------------------------------------------------------------------------
# coding: utf-8
# Wedpro bot
#-------------------------------------------------------------------------------

import argparse
import json
import random
import time
import logging
from io import open
from configobj import ConfigObj

from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains


class Automatization:
    def __init__(self,arg_param):
        # get user's email and password from json
        try:
            self.lg = logging.getLogger('wedpro')
            self.arg_param = arg_param

            self.category = 'popular'
            self.url_discussed = 'https://wedpro.com.ua/ru/photos/discussed/'
            self.url_popular = 'https://wedpro.com.ua/ru/photos/popular/'

            # загружаем конфиг
            try:
                self.data = ConfigObj('config/config.ini')
            except:
                self.lg.exception('ConfigObj')


            # загружаем комментарии
            self.comments = self.load("config/comments_wedpro.txt")

            # определяем случайное количество постов для обработки
            self.photos_processing_count = random.randint(int(self.data.get('count_show_photos_min')),
                                                         int(self.data.get('count_show_photos_max')))

            #загружаем список уже обработанных фото
            self.prosessing_photo_url = self.load('config/processing_photo.txt')
            # загружаем список уже обработанных профилей
            self.prosessing_profile_url = self.load('config/processing_profile.txt')

            chrome_options = Options()
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument('--lang=en-US')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-setuid-sandbox')
            if self.data.get('proxy') != 'None':
                chrome_options.add_argument('--proxy-server={}'.format(self.data.get('proxy')))

            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            self.driver.maximize_window()
        except:
            self.lg.exception('init')

    def load(self,path):
        try:
            with open(path,encoding='utf-8')  as f:
                com = f.readlines()
                comments = [x.strip() for x in com]
            f.close()
            return comments
        except:
            self.lg.exception('load_comments')
            return None

    def save(self,path,data):
        try:
            with open(path,'w',encoding='utf-8') as f:
                try:
                    for com in data:
                        f.writelines(com +'\n')
                except:
                    self.lg.exception('save 1')
                    pass
            f.close()
        except:
            self.lg.exception('save')

    def save_comments(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                try:
                    for com in data:
                        f.writelines(com + '\n')
                except:
                    self.lg.exception('save_comments 1')
                    pass
            f.close()
        except:
            self.lg.exception('save_comments')

    def get_comments(self):
        try:
            # отпраялем комментарий и удаляем его из списка
            try:
                return self.comments.pop()
            except:
                return None
        except:
            self.lg.exception('get_comments')

    def login(self):
        try:
            driver = self.driver
            data = self.data

            q_login_url = "https://kh.wedpro.com.ua/"
            driver.get(q_login_url)
            #'.//a[@class="menu_login"]'
            WebDriverWait(driver, 15).until(
                lambda driver: driver.find_element_by_xpath('.//a[@class="menu_login"]')).click()
            # './/i[@class="soc-gp"]'
            WebDriverWait(driver, 15).until(
                lambda driver: driver.find_element_by_xpath('.//i[@class="soc-gp"]')).click()

            user_email = data.get('login')
            user_password = data.get('pass')
            self.lg.info("Logining use {}".format( user_email ))

            WebDriverWait(driver, 10).until(
                EC.number_of_windows_to_be(2)
            )
            time.sleep(random.randint(1, 5))
            main_w = driver.window_handles[0]
            child = driver.window_handles[1]
            driver.switch_to.window(child)

            time.sleep(random.randint(1, 5))

            login = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element_by_id('identifierId'))
            login.send_keys(user_email)

            time.sleep(random.randint(1, 5))
            WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element_by_id('identifierNext')).click()

            time.sleep(random.randint(3, 5))
            passw = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element_by_xpath('.//input[@type="password"]'))
            #passw.click()

            driver.execute_script("arguments[0].click();", passw)
            time.sleep(random.randint(1, 5))
            passw.send_keys(user_password)

            WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element_by_id('passwordNext')).click()

            driver.switch_to.window(main_w)

            time.sleep(random.randint(3, 5))
            # проверям зашли или нет
            try:
                menu_login = WebDriverWait(driver, 5).until(
                    lambda driver: driver.find_element_by_xpath('.//a[@class="menu_toggler"]'))

                self.lg.info('Login successful')
                return True
            except:
                return False


        except:
            self.lg.exception('login')
            return False

    def show_arrow(self,driver):
        # наводи мышку на фото и прокручивам в поле видимости
        try:
            actions = ActionChains(driver)
            photos = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element_by_xpath('.//img[@class="mediaGallery_photo"]'))
            driver.execute_script("arguments[0].scrollIntoView(true);", photos)
            actions.move_to_element(photos).perform()
        except:
            self.lg.exception('swhow_arrow')

    def photo_not_processed(self,url):
        try:
            # проверям обработанное ли фото ранне
            if url in self.prosessing_photo_url:
                self.lg.info('Photo {} alredy processing'.format(url))
                return False
            else:
                # может добавлять в список тут?
                return True
        except:
            self.lg.exception('photo_is_processed')

    def profile_not_processed(self,url):
        try:
            # проверям обработанн ли профиль пользователя
            if url in self.prosessing_profile_url:
                self.lg.info('Profile {} alredy processing'.format(url))
                return False
            else:
                # может добавлять в список тут?
                self.prosessing_profile_url.append(url)
                self.save('config/processing_profile.txt',self.prosessing_profile_url)
                return True
        except:
            self.lg.exception('photo_is_processed')

    def processing_photo_in_category(self,category):
        try:
            # следующая страница .//a[@class="paginator_arrow-next"]
            # номер последней страницы .//a[@class="paginator_last"]

            # фото на старнице .//li[@class="album_grid shown"]
            # листаем дальше .//div[@class="mediaGallery_arrow-next"]
            # ссылка на профайл фотографа .//a[@class="avatar_profile"]


            driver = self.driver
            data = self.data

            if category == 'popular':
                driver.get(self.url_popular)
            else:
                driver.get(self.url_discussed)


            ph = WebDriverWait(driver, 15).until(
                lambda driver: driver.find_elements_by_xpath('.//li[@class="album_grid shown"]'))
            ph[0].click()
            time.sleep(2)
            # листаем показать есть фото или пока не достигним лимита
            # с учетом тех которые обработаные раньше?
            self.lg.info('For processing {} photos'.format(self.photos_processing_count))
            count_processed_photos = 0
            while True:
                try:

                    # получаем урл фото
                    url = driver.current_url


                    # тут проверяем есть ли єто фото в обрабтанных
                    if self.photo_not_processed(url):
                        landc = False
                        self.lg.info('Processing  photo {} ...'.format(url))
                        #тут  лайк #тут коммент
                        if self.set_like(driver):
                            landc = True
                            if self.set_comment(driver):
                                landc = True
                        else:
                            if self.set_comment(driver):
                                # если что то есть то сохраняем в обработанные
                                landc = True

                        if landc:
                            self.prosessing_photo_url.append(url)
                            self.save('config/processing_photo.txt', self.prosessing_photo_url)
                        # если обработали то защитываем
                        count_processed_photos = count_processed_photos + 1


                    # тут проверям ссылку на профайл, если не обработанная то обрабатываем
                    profile = arr_next = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//a[@class="avatar_profile"]'))
                    url_profile = profile.get_attribute('href')

                    if self.profile_not_processed(url_profile):
                        # добавляем в избранное
                        self.add_to_fav(driver)
                        # обрабатываем профайл
                        self.processing_profile(driver,url)

                    # тут провереям сколько обработали
                    if count_processed_photos > self.photos_processing_count:
                        break

                    time.sleep(1)
                    # наводим мышку на фото
                    self.show_arrow(driver)
                    time.sleep(1)
                    # листаем следующее фото
                    arr_next = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//div[@class="mediaGallery_arrow-next"]'))
                    arr_next.click()
                    # тут пауза между листаниями фото
                    time.sleep(random.randint(int(self.data.get('pause_show_photos_min')),
                                              int(self.data.get('pause_show_photos_max'))))

                except:
                    self.lg.exception('processing_photo_in_category main loop')

            self.lg.info('Processing {} posts in category {} completed successfully'.format(count_processed_photos,
                                                                                            category))
            return True
        except:
            self.lg.exception('processing_photo_in_category')

    """
    def processing_category(self,category):
        try:
            driver = self.driver
            data = self.data

            if category == 'popular':
                driver.get(self.url_popular)
            else:
                driver.get(self.url_discussed)

            # следующая страница .//a[@class="paginator_arrow-next"]
            # номер последней страницы .//a[@class="paginator_last"]

            # фото на старнице .//li[@class="album_grid shown"]
            # листаем дальше .//div[@class="mediaGallery_arrow-next"]
            # ссылка на профайл фотографа

            # листаем показать еще пока не пропадет кнопка
            while True:
                try:
                    b_more = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//div[@class="svadbaList_more"]'))
                    driver.execute_script("arguments[0].scrollIntoView(true);", b_more)
                    b_more.click()

                    time.sleep(3)
                except:
                    break

            # ищем фото, пока не листая
            posts = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_elements_by_xpath('.//div[@class="svadba"]/div/a[@class="svadba_link"]'))

            count_posts = len(posts)
            self.lg.info('Found {} posts in category {}'.format(count_posts, self.category))
            self.lg.info('For processing {} posts'.format(self.posts_processing_count))

            count_processed_posts = 0
            for i in xrange(count_posts-1):
                # проверяме обрабатывали ли мы уже такой пост
                post_url_r = posts[i].get_attribute('href')
                # обоабатываем урл осавляя только альбом без ссылки на фото
                #post_url = post_url[:len(post_url) - 1]
                #post_url_r = post_url[:post_url.rfind('/') + 1]

                if post_url_r in self.prosessing_post_url:
                    self.lg.info('Post {} alredy processing'.format(post_url_r))
                    continue
                else:
                    self.processing_post(posts[i])
                    count_processed_posts += 1
                    #сохраняем в список уже обработанных
                    self.prosessing_post_url.append(post_url_r)

                # проверяем может уже хватит
                if count_processed_posts > self.posts_processing_count:
                    break

            self.lg.info('Processing {} posts in category {} completed successfully'.format(count_processed_posts,
                                                                                            category))
            return True
        except:
            self.lg.exception('processing_category')
    """
    def processing_profile(self,driver,url):
        try:
            # тут обрабатываем аккаунт фотографа
            driver.execute_script("window.open('{}', 'new_window')".format(url))
            # ждем покаоткроется новая вкладка
            WebDriverWait(driver, 10).until( EC.number_of_windows_to_be(2))
            main_w = driver.window_handles[0]
            child = driver.window_handles[1]

            # переходим в новую вкладку
            driver.switch_to.window(child)
            # что то делвем
            self.lg.info('Processing profile {} ...'.format(driver.current_url))
            time.sleep(random.randint(int(self.data.get('pause_show_profile_min')),
                                      int(self.data.get('pause_show_profile_max'))))
            # просматриваем контакты
            if self.data.get('contacts') == 'on':
                self.show_contacts(driver)
            elif self.data.get('contacts') == 'rand':
                if random.randint(1, 2) == 1:  # рандомно смотрим или нет
                    self.show_contacts(driver)

            # закрываем вкладку
            driver.close()
            #переходим обратно
            driver.switch_to.window(main_w)
            return True
        except:
            self.lg.exception('processing_profile')

    def show_photos(self, driver):
        try:
            #.//li[@class="album_grid shown"]
            photos = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_elements_by_xpath('.//li[@class="album_grid shown"]'))
            photos[0].click()


            # Вычисляем количество фото которое будем просматривать
            max_count = random.randint(int(self.data.get('count_show_photos_min')),int(self.data.get('count_show_photos_max')))
            self.lg.info('Show {} photos ...'.format(max_count))

            # листаем фото пока есть или пока количество не превысит расчеткного
            c = 0
            while True:
                actions = ActionChains(driver)
                photos = WebDriverWait(driver, 5).until(
                    lambda driver: driver.find_element_by_xpath('.//div[@class="fotorama__stage"]'))
                driver.execute_script("arguments[0].scrollIntoView(true);", photos)
                actions.move_to_element(photos).perform()
                arr_next = WebDriverWait(driver, 5).until(
                    lambda driver: driver.find_element_by_xpath('.//div[@class="fotorama__arr fotorama__arr--next"]'))

                if c > max_count:
                    break
                try:
                    arr_next.click()
                    c += 1
                except:
                    #self.lg.exception('arr_next.click()')
                    break
                ## тут лайкаем если надо
                #self.set_like(driver)
                # тут добавляем комментарии
                #self.set_comment(driver)
                # тут пауза между листаниями фото
                time.sleep(random.randint(int(self.data.get('pause_show_photos_min')),int(self.data.get('pause_show_photos_max'))))
        except:
            self.lg.exception('show_photos')


    def show_contacts(self,driver, countswindows = 3):
        try:
            # просматриваем контакты .//button[@class="button-small"]
            driver.find_element_by_xpath('.//button[@class="button-small"]').click()
            self.lg.info('Show contacts')
            time.sleep(random.randint(int(self.data.get('pause_show_contact_min')),
                                      int(self.data.get('pause_show_contact_max'))))

            # тут просматриваем внешние ссылки
            self.show_any_urls(driver,'.//a[@class="ppContacts_link-site"]',countswindows) # сайт
            time.sleep(2)
            self.show_any_urls(driver,'.//a[@class="ppContacts_link-fb"]',countswindows)  # фейсбук
            time.sleep(2)


            # кликаем на кнопку "все прошло хорошо"
            if self.data.get('authorization') == 'off':
                # нажимаем кнопку все хорошо './/div[@class="ppContacts_feedbacks"]/a'
                feedbaks = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_elements_by_xpath('.//div[@class="ppContacts_feedbacks"]/a'))
                id = feedbaks[0].get_attribute('feedback-id')
                if id == '1':
                    feedbaks[0].click()
                    self.lg.info(u'Click to "Все прошло хорошо"')
            time.sleep(1)
            # закрыть './/div[@class="lightbox_close"]'
            driver.find_element_by_xpath('.//div[@class="lightbox_close"]').click()
        except:
            self.lg.exception('show_contacts')

    def show_any_urls(self,driver,xpah,countswindows = 3):
        try:
            # .//a[@class="ppContacts_link-site"]
            # .//a[@class="ppContacts_link-fb"]
            if self.data.get('show_any_urls') == 'on':
                try:
                    urls = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath(xpah))
                    urls.click()
                    # ждем откритие окна
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(countswindows))
                    main_w = driver.window_handles[countswindows - 2]
                    child = driver.window_handles[countswindows -1]
                    # переключаемся в него
                    driver.switch_to.window(child)
                    # пауза
                    time.sleep(random.randint(int(self.data.get('pause_show_any_urls_min')),
                                              int(self.data.get('pause_show_any_urls_max'))))
                    # закрываем и перключаемся назад
                    driver.close()
                    # переходим обратно
                    driver.switch_to.window(main_w)
                except:
                    self.lg.info('No urls')
        except:
            self.lg.exception('show_any_urls')

    def add_to_fav(self,driver):
        try:
            # .//a[@class="fav"]' - кнопка избраное на панели контактов
            # орабатывать нужно перед обраоткой профиля фотографа
            if self.data.get('add_fav') == 'on':
                try:
                    button_fav = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//a[@class="fav"]'))
                    button_fav.click()
                    self.lg.info('Add to favorites')
                    return True
                except:
                    pass
            elif self.data.get('add_fav') == 'rand':
                if random.randint(1,2) == 1: # рандомно добавляем  или нет
                    try:
                        button_fav = WebDriverWait(driver, 5).until(
                            lambda driver: driver.find_element_by_xpath('.//a[@class="fav"]'))
                        button_fav.click()
                        self.lg.info('Add ro favorites')
                        return True
                    except:
                        pass
                else:
                    self.lg.info('Don"t Add ro favorites')
            else:
                return False
        except:
            self.lg.exception('add_to_fav')

    def set_like(self,driver):
        try:
            # лайк в галерее .//div[@class="mediaGallery_like"]
            # .//div[@class="fotorama_like"]
            if self.data.get('like') == 'on':
                try:
                    button_like = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//div[@class="mediaGallery_like"]'))
                    button_like.click()
                    self.lg.info('Like')
                    return True
                except:
                    pass
            elif self.data.get('like') == 'rand':
                if random.randint(1,2) == 1: # рандомно лайкаєм или нет
                    try:
                        button_like = WebDriverWait(driver, 5).until(
                            lambda driver: driver.find_element_by_xpath('.//div[@class="mediaGallery_like"]'))
                        button_like.click()
                        self.lg.info('Like')
                        return True
                    except:
                        pass
                else:
                    self.lg.info('Don"t Like')
            else:
                return False
        except:
            self.lg.exception('set_like')

    def set_comment(self,driver):
        try:
            if self.data.get('comments') == 'on':
                # проверяме есть ли комменты в файле
                comment = self.get_comments()
                if comment:
                    textcomment = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_element_by_xpath('.//textarea[@class="comment_field"]'))
                    driver.execute_script("arguments[0].scrollIntoView(true);", textcomment)
                    textcomment.click()
                    textcomment.send_keys(comment)
                    time.sleep(2)
                    b = WebDriverWait(driver, 5).until(
                        lambda driver: driver.find_elements_by_xpath('.//button[@class="button-small"]'))
                    b[1].click()
                    self.lg.info(u'Post comment: {}'.format(comment))
                    return True
                else:
                    self.lg.info('Comments ended.')

            elif self.data.get('comments') == 'rand':
                if random.randint(1, 2) == 1:  # рандомно комментируем или нет
                    comment = self.get_comments()
                    if comment:
                        textcomment = WebDriverWait(driver, 5).until(
                            lambda driver: driver.find_element_by_xpath('.//textarea[@class="comment_field"]'))
                        driver.execute_script("arguments[0].scrollIntoView(true);", textcomment)
                        textcomment.click()
                        textcomment.send_keys(comment)
                        time.sleep(2)
                        b = WebDriverWait(driver, 5).until(
                            lambda driver: driver.find_elements_by_xpath('.//button[@class="button-small"]'))
                        b[1].click()
                        self.lg.info(u'Post comment: {}'.format(comment))
                        return True
                    else:
                        self.lg.info('Comments ended.')
            else:
                return False
        except:
            self.lg.exception('set_comment')

    def run(self):
        try:
            self.lg.info('!------------------------------------------!')
            self.lg.info('! Wedpro bot v. 1.03                       !')
            self.lg.info('! 11.09.2018                               !')
            self.lg.info('!------------------------------------------!')
            if self.data.get('proxy') != 'None':
                self.lg.info('Use proxy: {}'.format(self.data.get('proxy')))

            if self.data.get('authorization') == 'on':
                self.lg.info('Authorized mode')

                if not self.login():
                    logger.info('Login error')
                    return

                self.lg.info('Start processing category popular')
                self.processing_photo_in_category('popular')

                self.lg.info('Start processing category discussed')
                self.processing_photo_in_category('discussed')
            else:
                self.lg.info('Non authorized mode')
                try:
                    self.lg.info('Processain profile {}'.format(self.data.get('profile_url')))
                    # заходим в выбраный профайл
                    self.driver.get(self.data.get('profile_url'))
                    # листаем фото
                    self.show_photos(self.driver)
                    # смотрим контакты
                    self.show_contacts(self.driver,countswindows = 2)

                    pass
                except:
                    self.lg.exception('Non authorized mode')

            self.save_comments("config/comments_wedpro.txt", self.comments)
        except:
            self.save_comments("config/comments_wedpro.txt", self.comments)
            self.lg.exception('run')
            return False





def createParser():
    parser = argparse.ArgumentParser()
    #parser.add_argument('user')
    return parser

if __name__ == "__main__":
    DEBUG = False

    parser = createParser()
    arg_param = parser.parse_args()
    logger = logging.getLogger('wedpro')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log/wedpro_log.txt')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    if DEBUG:
        formatter = logging.Formatter('[LINE:%(lineno)d]#%(asctime)s: %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s: %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)


    wedbot = Automatization(arg_param)
    wedbot.run()
