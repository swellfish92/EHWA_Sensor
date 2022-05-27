

import asyncio
import json
# from Environment.Environment import Environment
# from object.User_Setting_Interface import User_Setting_Interface
# from object.Smart_Window import Smart_Window
from datetime import datetime, date
import math
import paho.mqtt.client as mqtt_client
import json
import requests
import xmltodict



# 알고리즘 모델

class Model:
    def __init__(self, roomtype='normal', EWSET=2000, INTSET=10, LEVSET=5, EOSET=30000, SPLUGSET=15):
        """
        에너지 절약 모드
        """
        # 실내 창측 조도 기준(E_w,set) ~ 2000lx ~ 사용자가 변경 가능하도록
        self.__E_w_set = EWSET
        # 거주자 선호 실내 창측 조도 기준(E_w,set,f) ~ 도출해야할 목표 값.
        self.__E_w_set_f = self.__E_w_set
        # 제어 시간 간격(INT,set) ~ 10 min ~ 고려할 필요 없음 10분으로 고정
        self.__INT_set = INTSET

        """
        홈시어터 쾌적 시청 모드
        """
        # 현휘 제어용 변색 단계 기준(LEV,set) ~ 자동 계산되어 도출, 사용자가 변경 가능하도록
        self.__LEV_set = LEVSET
        # 거주자 선호 현휘 제어용 변색 단계 기준(LEV,set,f) ~ 자동 계산되어 도출
        self.__LEV_set_f = self.__LEV_set

        # 현휘 제어용 실외조도 기준(E_o,set) ~ 단위 : lx ~ 사용자가 변경 가능하도록
        self.__E_o_set = EOSET
        # 거주자 선호 현휘 제어용 실외 조도 기준(E_o,set,f) ~ 단위 : lx ~ 자동 계산 되어 도출
        self.__E_o_set_f = self.__E_o_set

        self.__S_plug_set=SPLUGSET

        # vt_arr값을 입력함
        self.__vt_arr_set = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        # 방 타입을 입력함 (에너지절약모드의 타입을 설정)
        self.__roomtype_set = roomtype



    """
    getter
    """

    @property
    def E_w_set(self):
        return self.__E_w_set

    @property
    def E_w_set_f(self):
        return self.__E_w_set_f

    @property
    def INT_set(self):
        return self.__INT_set

    @property
    def LEV_set(self):
        return self.__LEV_set

    @property
    def LEV_set_f(self):
        return self.__LEV_set_f

    @property
    def E_o_set(self):
        return self.__E_o_set

    @property
    def E_o_set_f(self):
        return self.__E_o_set_f

    @property
    def S_plug_set(self):
        return self.__S_plug_set

    @property
    def vt_arr_set(self):
        return self.__vt_arr_set

    @property
    def summer_time_start_set(self):
        return self.__summer_time_start_set

    @property
    def summer_time_end_set(self):
        return self.__summer_time_end_set

    @property
    def T_i_set(self):
        return self.__T_i_set

    @property
    def roomtype_set(self):
        return self.__roomtype_set

    """
    setter
    @name.setter
    """

    @E_w_set.setter
    def E_w_set(self, data):
        self.__E_w_set = data

    @E_w_set_f.setter
    def E_w_set_f(self, data):
        self.__E_w_set_f = data

    @INT_set.setter
    def INT_set(self, data):
        self.__INT_set = data

    @LEV_set.setter
    def LEV_set(self, data):
        self.__LEV_set = data

    @LEV_set_f.setter
    def LEV_set_f(self, data):
        self.__LEV_set_f = data

    @E_o_set.setter
    def E_o_set(self, data):
        self.__E_o_set = data

    @E_o_set_f.setter
    def E_o_set_f(self, data):
        self.__E_o_set_f = data

    @S_plug_set.setter
    def S_plug_set(self,data):
        self.__S_plug_set=data

    @vt_arr_set.setter
    def vt_arr_set(self,data):
        self.__vt_arr_set=data

    @vt_arr_set.setter
    def summer_time_start_set(self,data):
        self.__summer_time_start_set=data

    @vt_arr_set.setter
    def summer_time_end_set(self,data):
        self.__summer_time_end_set=data

    @T_i_set.setter
    def T_i_set(self,data):
        self.__T_i_set=data

    @roomtype_set.setter
    def roomtype_set(self,data):
        self.__roomtype_set=data

    # 홈시어터 쾌적 시청 모드 알고리즘
    def home_theatre_alg(self,E_o,datetime_time,datetime_time_sunrise,datetime_time_sunset,S_plug):
        if (datetime_time_sunrise < datetime_time) and (datetime_time < datetime_time_sunset):
            if S_plug>self.S_plug_set():
                if E_o>self.E_o_set():
                    vt_value = 10
                else:
                    vt_value = 1
            else:
                vt_value = 1
        else:
            vt_value = 1
        return vt_value

    # 에너지 절약모드 알고리즘
    # 2022.05.09 가시성을 위해 날자조건 (6/1~9/30구간 사이)을 여기로 옮김. 조건문이 두 번 들어가서 비효율적이 되더라도, 가시성이 나을 것 같아 보임.
    def energy_saving_alg(self,E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,hometheatre_mode):
        def calc_vt(self, vt_val):
            vt_arr = self.vt_arr_set()
            # 10개 구간으로 분할
            for iter in range(len(vt_arr)):
                if vt_val < vt_arr[iter]:
                    return iter + 1
            return 10

        if int(datetime_date.strftime("%m%d")) >= self.set_summer_time_start() and int(datetime_date.strftime("%m%d")) <= self.set_summer_time_end():
            if (datetime_time_sunrise < datetime_time) and (datetime_time < datetime_time_sunset):
                if Mo == 1:

                    # 2022.05.09
                    # 왜 거주자 희망 E_w(산출해야 하는 목표값)을 쓰는 것인지..? 로직만 보면 E_w_set을 쓰는 것이 타당해 보임...
                    calculated_penetration = math.round(self.E_w_set/E_o, 2)
                    vt_value = calc_vt(calculated_penetration)
                else:
                    vt_value = 1
            else:
                vt_value = 1
        else:
            if hometheatre_mode == True:
                return self.home_theatre_alg(E_o,datetime_time,datetime_time_sunrise,datetime_time_sunset,S_plug)
            else:
                if (datetime_time_sunrise < datetime_time) and (datetime_time < datetime_time_sunset):
                    vt_value = 1
                else:
                    vt_value = 10

        return vt_value

    def energy_saving_alg_bedroom(self,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,T_i):
        self.T_i_set(26)
        if int(datetime_date.strftime("%m%d")) >= self.set_summer_time_start() and int(datetime_date.strftime("%m%d")) <= self.set_summer_time_end():
            if (datetime_time_sunrise < datetime_time) and (datetime_time < datetime_time_sunset):
                vt_value = 1
            else:
                vt_value = 10
        else:
            if (datetime_time_sunrise < datetime_time) and (datetime_time < datetime_time_sunset):
                vt_value = 1
            else:
                if Mo == 1:
                    vt_value = 1
                else:
                    if T_i >= self.T_i_set():
                        vt_value = 10
                    else:
                        vt_value = 1


    # 모드 선택 알고리즘,
    # 지정한 시간 마다 동작하거나 LEV_set_user가 LEV_c와 달라졌을 때 run.
    def predict(self,E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i):
        if off_control == True:
            pass
        elif energy_saving_mode == True:
            if self.roomtype_set() == 'bedroom':
                return self.energy_saving_alg_bedroom(datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,T_i)
            else:
                return self.energy_saving_alg(E_o, datetime_date, datetime_time, datetime_time_sunrise, datetime_time_sunset, Mo, S_plug, hometheatre_mode)
        elif hometheatre_mode == True:
            return self.home_theatre_alg(E_o,datetime_time,datetime_time_sunrise,datetime_time_sunset,S_plug)
        elif manual_mode == True:
            return self.LEV_set()
        else:
            raise IOError

    # 거주자가 직접 변색 단계를 바꾸었을 때 함수.
    # def Change_LEV_c_user(self):
    #     if self.User_Setting_Interface.LEV_c_user != self.Smart_Window.LEV_c:
    #         if self.User_Setting_Interface.LEV_c_user == 1:
    #             self.E_w_set_f = self.Environment.E_o * self.Smart_Window.VT_1
    #         elif self.User_Setting_Interface.LEV_c_user == 2:
    #             self.E_w_set_f = self.Environment.E_o * self.Smart_Window.VT_2
    #         elif self.User_Setting_Interface.LEV_c_user == 3:
    #             self.E_w_set_f = self.Environment.E_o * self.Smart_Window.VT_3
    #         elif self.User_Setting_Interface.LEV_c_user == 4:
    #             self.E_w_set_f = self.Environment.E_o * self.Smart_Window.VT_4
    #         elif self.User_Setting_Interface.LEV_c_user == 5:
    #             self.E_w_set_f = self.Environment.E_o * self.Smart_Window.VT_5
    #         self.Smart_Window.LEV_c = self.User_Setting_Interface.LEV_c_user
    #         self.mode_selection()


#     def parse_message(self,message):
#         """
#         별도의 서버에서 보내지는 메시지는 다음의 형태로 이루어져야합니다.
#            message : encoded json serialized dictionary
#            {
#                "Environment":{
#                    "E_o": float,
#                    "locale" : string,
#                    "date" : "string" ~ datetime.date.isoformat()의 반환 값 string
#                    "time" : "string" ~ datetime.time.isoformat()의 반환 값 string
#                    "r_time" : "string" ~ datetime.time.isoformat()의 반환 값 string
#                    "s_time" : "string" ~ datetime.time.isoformat()의 반환 값 string
#                    "Mo" : int
#                    "S_plug" : int
#                    "T_i" : int
#                }
#                "User_Setting_Interface":{
#                    "LEV_c_user" : int,
#                    "INT_user" : int
#                }
#                "Smart_Window":{
#                    "VT_1" : float,
#                    "VT_2" : float,
#                    "VT_3" : float,
#                    "VT_4" : float,
#                    "VT_5" : float,
#                    "LEV_c" : int
#                }
#
#            }
#         """
#         # decode 후 json 라이브러리를 이용하여 load
#         json_obj = json.loads(message.decode())
#         env_dict=json_obj["Environment"]
#         user_setting_interface_dict=json_obj["User_Setting_Interface"]
#         smart_window_dict=json_obj["Smart_Window"]
#         e_o=env_dict["E_o"]
#         locale=env_dict["locale"]
#         d=datetime.date.fromisoformat(env_dict["date"])
#         t=datetime.time.fromisoformat(env_dict["time"])
#         r_time=datetime.time.fromisoformat(env_dict["r_time"])
#         s_time=datetime.time.fromisoformat(env_dict["s_time"])
#         mo=env_dict["Mo"]
#         s_plug=env_dict["S_plug"]
#         T_i=env_dict["T_i"]
#         lev_c_user=user_setting_interface_dict["LEV_c_user"]
#         int_user=user_setting_interface_dict["INT_user"]
#         vt_1=smart_window_dict["VT_1"]
#         vt_2=smart_window_dict["VT_2"]
#         vt_3=smart_window_dict["VT_3"]
#         vt_4=smart_window_dict["VT_4"]
#         vt_5=smart_window_dict["VT_5"]
#         lev_c=smart_window_dict["LEV_c"]
#
#         new_env_obj=Environment(e_o,locale,d,t,r_time,s_time,mo,s_plug,T_i)
#         new_user_setting_interface_obj=User_Setting_Interface(lev_c_user,int_user)
#         new_smart_window_obj=Smart_Window(vt_1,vt_2,vt_3,vt_4,vt_5,lev_c)
#
#         return new_env_obj,new_user_setting_interface_obj,new_smart_window_obj
#
#
#
#
#     async def client_run(self,host, port):
#         # 서버와의 연결을 생성합니다.
#         reader: asyncio.StreamReader
#         writer: asyncio.StreamWriter
#         reader, writer = await asyncio.open_connection(host, port)
#         # show connection info
#         print("[C] connected")
#         # 루프를 돌면서 입력받은 내용을 서버로 보내고,
#         # 응답을 받으면 출력합니다.
#         while True:
#             # 서버로부터 데이터 수신을 기다립니다. 사용자가 지정한 INTERVAL(min)*60=초를 기다리고 안된다면 타임아웃 에러를 일으킵니다.
#             try:
#                 data = await asyncio.wait_for(reader.read(1024),timeout=User_Setting_Interface.INT_user*60)
#
#             except asyncio.TimeoutError: # 타임아웃이 일어나면 mode_selection 알고리즘을 실행.
#                 print("Timeout")
#                 if self.Environment == None :
#                     print("No Environment")
#                 elif isinstance(self.Environment,Environment):
#                     self.mode_selection()
#             else: # 타임아웃이 일어나지 않고 서버로부터 새로운 데이터를 받았다면
#                 new_env_obj,new_user_setting_interface_obj,new_smart_window_obj=self.parse_message(data)
#                 if self.Environment==None:
#                     self.Environment=new_env_obj
#                 else :
#                     self.Environment=new_env_obj
#                 if self.User_Setting_Interface.LEV_c_user!=new_user_setting_interface_obj.LEV_c_user or self.User_Setting_Interface.INT_user != new_user_setting_interface_obj.INT_user:
#                     self.User_Setting_Interface=new_user_setting_interface_obj
#                     self.Change_LEV_c_user()
#                 else:
#                     self.mode_selection()
#
#         # 연결을 종료합니다.
#         print("[C] closing connection...")
#
#         await writer.wait_closed()
#
#

# =====================================================================================================================
# 여기부터는 모델과 관련없는 구동에 필요한 기타 함수임
def get_suntime(location, date):
    key = 'owsao31Eak4pE2i8SQkuu6bVXieWxILomFCxifqPQAW4wgbkVJ%2F9X0hIzljulAYMV6KcUZPLla2xAUusk4B1wg%3D%3D'
    call_string = 'http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService/getAreaRiseSetInfo?location='+ location +'&locdate=' + str(date) + '&ServiceKey=' + key
    result = requests.get(call_string)
    jsonresult = json.loads(json.dumps(xmltodict.parse(result.text)))
    print(jsonresult)
    sunrise = jsonresult['response']['body']['items']['item']['sunrise']
    sunset = jsonresult['response']['body']['items']['item']['sunset']
    return sunrise, sunset

print(get_suntime('서울', 20220527))
raise IOError

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos, model_living, model_1, model_2, model_3, area='서울', filedir='./log.csv'):
    print("subscribed: " + str(mid) + " // " + str(granted_qos))
    # 받은 메시지를 변수값으로 분해
    r_time, s_time, datetime_year, datetime_month, datetime_date, E_o, Mo, S_plug, T_i = resolve_message(mid)
    # 로그용 현재 시간을 구함
    current_time = datetime.datetime.now()
    # 받은 값들을 CSV로 저장
    write_csv = (filedir, [current_time, r_time, s_time, datetime_date, datetime_time, E_o, Mo, S_plug, T_i])
    # 일출/일몰시각을 기상청 API로 받아옴 (귀찮으니 매번 받아옴)
    datetime_time_sunrise, datetime_time_sunset = get_suntime(area, str(datetime_year)+str(datetime_month).zfill(2)+str(datetime_date).zfill(2))
    # 받아온 값으로 실별 모델예측을 수행
    living_var = model_living.predict(E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i)
    model_1_var = model_1.predict(E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i)
    model_2_var = model_2.predict(E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i)
    model_3_var = model_3.predict(E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i)
    # json으로 포장
    #json_wrap = (living_var, model_1_var, model_2_var, model_3_var)
    client.publish(topic_name, json.dumps({"living": living_var, 'room1': model_1_var, 'room2': model_2_var, 'room3': model_3_var}), 1)

def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))


if __name__ == '__main__':

    broker_addr = 'localhost'
    broker_port = 1111
    topic = 'test_topic'
    qos = 1

    # https://www.data.go.kr/data/15012688/openapi.do
    # 일자구간 값도 직접 할당 가능하도록


    print('Generating Models...')

    #모델 객체 생성
    room_model_living = Model()
    room_model_1 = Model()
    room_model_2 = Model(roomtype = 'bedroom')
    room_model_3 = Model(roomtype = 'bedroom')

    print('Generating finished successfully')
    print('MQTT Connecting...')

    # 클라이언트 초기값 설정 (일단 단일로 돌아가도록)
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe(model_living=room_model_living, model_1 = room_model_1, model_2 = room_model_2, model_3 = room_model_3)
    client.on_message = on_message

    # 설정된 주소로 연결 시도
    client.connect(broker_addr, broker_port)
    client.subscribe(topic, qos)

    print('MQTT connection finished successfully')

    client.loop_forever()

    # 모델 예측 수행.
    # Level=room_model_1.predict(E_o,datetime_date,datetime_time,datetime_time_sunrise,datetime_time_sunset,Mo,S_plug,T_i)

