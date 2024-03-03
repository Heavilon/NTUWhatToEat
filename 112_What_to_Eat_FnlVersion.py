import tkinter as tk
import tkinter.ttk as tt
import tkinter.messagebox
import pymysql  # pip install pymysql (macOS: pip3 install pymysql)
import requests  # pip install requests (macOS: pip3 install requests)
import json
import emoji  # pip install emoji (macOS: pip3 install emoji)
from PIL import ImageTk, Image  # pip install pillow (macOS: pip3 install pillow)

# MySQL記得改成自己得密碼和db名稱
db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "QntwsB08701215",
    "db": "ntu_what_to_eat",
    "charset": "utf8"
    }

class GooglePlaces(object):
    def __init__(self, apiKey):
        super(GooglePlaces, self).__init__()
        self.apiKey = apiKey

    # 先執行place_search取得place_id，才能執行place_details
    def place_search(self, name, inputtype):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        place = []
        params = {
            'input': name,
            'inputtype': inputtype,
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params = params)
        result = json.loads(res.content)  # 成為dictionary
        return result

    def get_place_details(self, place_id, fields, language):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'placeid': place_id,
            'language': language,
            'fields': ",".join(fields),
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params = params)
        place_details =  json.loads(res.content)
        return place_details

window1 = tk.Tk()
window1.title("112 What to Eat?")
window1.geometry('455x315')

window1_canvas = tk.Canvas(window1, width=455, height=315, bd=0, highlightthickness=0)

# 圖片檔案記得改成自己的路徑
imgpath = '/Users/Aaron/Documents/112_background.png'
img = Image.open(imgpath)
photo = ImageTk.PhotoImage(img)

window1_canvas.create_image(227, 157, image=photo)
window1_canvas.pack()

region_option = ["公館", "118巷&科技大樓", "溫州街", "台科大"]
region = tk.StringVar(window1)
region.set("請選擇地區")

opt_region = tk.OptionMenu(window1, region, *region_option)
opt_region.config(width=90)
opt_region.pack()
window1_canvas.create_window(227, 140, width=130, height=20, window=opt_region)

ctg_option = ["中式", "日式", "韓式", "西式", "泰式", "素食", "健身餐"] 
ctg = tk.StringVar(window1)
ctg.set("請選擇類型")

opt_ctg = tk.OptionMenu(window1, ctg, *ctg_option)
opt_ctg.config(width=90)
opt_ctg.pack()
window1_canvas.create_window(227, 170, width=130, height=20, window=opt_ctg)

global region_selected
region_selected = ""
global ctg_selected
ctg_selected = ""
def btn1_command():
    region_selected = region.get()
    ctg_selected = ctg.get()
    if region_selected == "請選擇地區" or ctg_selected == "請選擇類型":
        tkinter.messagebox.showinfo(title='!', message="請確認地區與類型都已選擇")
    else:
        restaurant_info = ""
        restaurant_dict = {}
        try:
            conn = pymysql.connect(**db_settings)
            # 建立Cursor物件
            with conn.cursor() as cursor:
                # 查詢資料SQL語法
                command = "\
                SELECT r_name, r_address, r_tel \
                FROM restaurant \
                JOIN region ON restaurant.region_id = region.region_id \
                JOIN class ON restaurant.class_id = class.class_id \
                WHERE region_name LIKE '%s' AND class_name = '%s'" % (region_selected, ctg_selected)
                # 執行指令
                cursor.execute(command)
                # 取得所有資料
                result = cursor.fetchall()
                r_option = []
                for i in range(len(result)):
                    restaurant_name = result[i][0]
                    restaurant_loc = result[i][1]
                    restaurant_tel = result[i][2]

                    if __name__ == '__main__':
                        api = GooglePlaces("AIzaSyCMsYTNLTxXwCfQuFo1-8cr0ug1cg7j_VI")  # Google API架設key
                        place = api.place_search(restaurant_name, "textquery")
                        place_id = place['candidates'][0]['place_id']
                        fields = ['name', 'business_status', 'opening_hours',
                                  'price_level', 'rating', 'review']

                        details = api.get_place_details(place_id, fields, "zh-TW")

                        try:
                            name = details['result']['name']
                        except KeyError:
                            name = "ERROR"

                        try:
                            rating = details['result']['rating']
                        except KeyError:
                            rating = "無資訊"

                        try:
                            business_status = details['result']['business_status']
                            if business_status == "CLOSED_TEMPORARILY":
                                business_status = "暫時停業"
                            elif business_status == "CLOSED_PERMANENTLY":
                                business_status = "永久停業"
                            else:
                                business_status = details['result']['opening_hours']['open_now']
                                if business_status is True:
                                    business_status = "現在營業中"
                                elif business_status is False:
                                    business_status = "現在休息中"
                        except KeyError:
                            business_status = "無資訊"

                        try:
                            reviews = details['result']['reviews']
                        except KeyError:
                            reviews = []

                        restaurant_info += restaurant_name + \
                                           "\n餐廳地址: " + \
                                           restaurant_loc + \
                                           "\n餐廳電話: " + \
                                           restaurant_tel + \
                                           "\n營業狀態: " + \
                                           business_status + \
                                           "\n店家星星: " + \
                                           str(rating) + "星\n"
                        if i != len(result) - 1:
                            restaurant_info += "\n"

                        if len(result) != 0:
                            r_option.append(result[i][0])

                if len(result) == 0:
                    tkinter.messagebox.showinfo(title='!', \
                                                message="QQ" + \
                                                region_selected + "沒有" + \
                                                ctg_selected + "的餐廳ಥ_ಥ")
                else:
                    window2 = tk.Toplevel(window1)
                    window2_title = region_selected + "的" + ctg_selected + "餐廳"
                    window2.title(window2_title)
                    tk.Label(window2, \
                              text = restaurant_info, \
                              wraplength = 460, \
                              justify = 'left').pack()

                    if len(result) != 0:
                        budget_list = ["50元", "100元", "150元", "200元", "200元以上"]
                        char_budget = tk.StringVar(window2)
                        char_budget.set("請選擇預算")

                        opt_budget = tk.OptionMenu(window2, char_budget, *budget_list)
                        opt_budget.config(width=25)
                        opt_budget.pack(side="top")

                        r_offer = tk.StringVar(window2)
                        if len(result) == 1:
                            r_offer.set(result[0][0])
                        else:
                            r_offer.set("請選擇餐廳")

                        opt_r = tk.OptionMenu(window2, r_offer, *r_option)
                        opt_r.config(width=25)
                        opt_r.pack(side="top")

                        def btn2_command():
                            restaurant_selected = r_offer.get()
                            budget = char_budget.get()
                            if budget == "請選擇預算" and restaurant_selected != "請選擇餐廳":
                                tkinter.messagebox.showinfo(title='!', message='尚未選擇預算\n將為您顯示完整菜單')
                                budget_sql = ""
                            elif budget == "50元":
                                budget_sql = "AND dish_price <= 50"
                            elif budget == "100元":
                                budget_sql = "AND dish_price <= 100"
                            elif budget == "150元":
                                budget_sql = "AND dish_price <= 150"
                            elif budget == "200元":
                                budget_sql = "AND dish_price <= 200"
                            elif budget == "200元以上":
                                budget_sql = ""

                            if restaurant_selected == "請選擇餐廳":
                                tkinter.messagebox.showinfo(title='!', message='尚未選擇餐廳')
                            else:
                                comment_info = ""
                                if __name__ == '__main__':
                                    api = GooglePlaces("AIzaSyCMsYTNLTxXwCfQuFo1-8cr0ug1cg7j_VI")  # Google API架設key
                                    place = api.place_search(restaurant_selected, "textquery")
                                    place_id = place['candidates'][0]['place_id']
                                    fields = ['name', 'business_status', 'opening_hours',
                                              'price_level', 'rating', 'review']

                                    details = api.get_place_details(place_id, fields, "zh-TW")

                                    try:
                                        name = details['result']['name']
                                    except KeyError:
                                        name = "ERROR"

                                    try:
                                        rating = details['result']['rating']
                                    except KeyError:
                                        rating = "無資訊"

                                    try:
                                        reviews = details['result']['reviews']
                                    except KeyError:
                                        reviews = []

                                    comment_info += restaurant_selected + "\n在Google Maps上的最新評論:\n"

                                    for review in reviews:
                                        rating = review['rating']
                                        text = review['text']

                                        def is_emoji(word):
                                            return word in emoji.UNICODE_EMOJI

                                        comment_info += str(rating) + "星, "

                                        tempVar = 0
                                        for i in range(50):
                                            if i == len(text) - 1:
                                                if is_emoji(text[i]) is False:  # 移除表情符號
                                                    comment_info += text[i]
                                                tempVar = 1
                                                break
                                            if text[i] != "\n":  # 移除空格與換行
                                                if is_emoji(text[i]) is False:  # 移除表情符號
                                                    comment_info += text[i]
                                        if tempVar == 0:  # 若該則評論超過50字元，後加「......」
                                            comment_info += "......"
                                        comment_info += "\n"

                                dish_info = "菜單\n"
                                try:
                                    conn = pymysql.connect(**db_settings)
                                    # 建立Cursor物件
                                    with conn.cursor() as cursor:
                                        # 查詢資料SQL語法
                                        command = "\
                                        SELECT dish_name, dish_price \
                                        FROM dish \
                                        JOIN restaurant ON dish.r_id = restaurant.r_id \
                                        WHERE r_name = '%s' %s" % (restaurant_selected, budget_sql)
                                        # 執行指令
                                        cursor.execute(command)
                                        # 取得所有資料
                                        result = cursor.fetchall()
                                        if len(result) != 0:
                                            for i in range(len(result)):
                                                dish_info += "$" + str(result[i][1]).ljust(5) + result[i][0] + "\n"
                                        elif restaurant_selected == "料理王健康素食自助餐" or \
                                             restaurant_selected == "如來素食樂園" or \
                                             restaurant_selected == "全國食養健康素食自助餐" or \
                                             restaurant_selected == "品客自助餐":
                                            dish_info += "本餐廳為自助餐，價格依現場為準。"
                                        else:
                                            dish_info += "..ToT.." + restaurant_selected + \
                                                         "沒有" + budget + "以下的餐點\n"

                                except Exception as ex:
                                    print(ex)

                                comment_menu = comment_info + "\n" + dish_info

                                window3 = tk.Toplevel(window2)
                                window3.title(restaurant_selected + "的評論與菜單")
                                tk.Label(window3, \
                                         text = comment_menu, \
                                         wraplength = 400, \
                                         justify = 'left', \
                                         font = "Courier").pack()

                        btn2 = tk.Button(window2, width=10, text='確定', command=btn2_command)
                        btn2.pack()

        except Exception as ex:
            print(ex)

btn1 = tk.Button(window1, text='確定', width=10, command=btn1_command)
btn1.pack()
window1_canvas.create_window(227, 200, width=40, height=20, window=btn1)

window1.mainloop()
