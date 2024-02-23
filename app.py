# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=150高清
# qn=250超清
# qn=400蓝光
# qn=10000原画
import os

import requests
import gradio as gr
import openai
import read_frame


class BiliBili:
    def __init__(self, rid):
        """
        有些地址无法在PotPlayer播放，建议换个播放器试试
        Args:
            rid:
        """
        rid = rid
        self.header = {
            'User-Agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1',
        }
        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init'
        param = {
            'id': rid
        }
        with requests.Session() as self.s:
            res = self.s.get(r_url, headers=self.header, params=param).json()
        if res['msg'] == '直播间不存在':
            raise Exception(f'bilibili {rid} {res["msg"]}')
        live_status = res['data']['live_status']
        if live_status != 1:
            raise Exception(f'bilibili {rid} 未开播')
        self.real_room_id = res['data']['room_id']

    def get_real_url(self, current_qn: int = 10000) -> dict:
        url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
        param = {
            'room_id': self.real_room_id,
            'protocol': '0,1',
            'format': '0,1,2',
            'codec': '0,1',
            'qn': current_qn,
            'platform': 'h5',
            'ptype': 8,
        }
        res = self.s.get(url, headers=self.header, params=param).json()
        stream_info = res['data']['playurl_info']['playurl']['stream']
        qn_max = 0

        for data in stream_info:
            accept_qn = data['format'][0]['codec'][0]['accept_qn']
            for qn in accept_qn:
                qn_max = qn if qn > qn_max else qn_max
        if qn_max != current_qn:
            param['qn'] = qn_max
            res = self.s.get(url, headers=self.header, params=param).json()
            stream_info = res['data']['playurl_info']['playurl']['stream']

        stream_urls = {}
        # flv流无法播放，暂修改成获取hls格式的流，
        for data in stream_info:
            format_name = data['format'][0]['format_name']
            if format_name == 'ts':
                base_url = data['format'][-1]['codec'][0]['base_url']
                url_info = data['format'][-1]['codec'][0]['url_info']
                for i, info in enumerate(url_info):
                    host = info['host']
                    extra = info['extra']
                    stream_urls[f'线路{i + 1}'] = f'{host}{base_url}{extra}'
                break
        return stream_urls


def get_real_url(rid):
    try:
        bilibili = BiliBili(rid)
        return bilibili.get_real_url()
    except Exception as e:
        print('Exception：', e)
        return False

def setzhibojianhao(直播间id,channel):
    os.environ["BILI_ROOM_ID"]=直播间id
    return get_flv_url(channel)

def get_flv_url(channel):
    tmp= get_real_url(os.environ["BILI_ROOM_ID"])
    if channel not in tmp.keys():
        return "无效线路，请检查你的直播间号和线路是否正确"
    else:
        os.environ["BILI_VIDEO_CHANNEL"]= tmp[channel]
        return os.environ["BILI_ROOM_ID"]

def set_openai_api(api_key,proxy):
    os.environ["OPENAI_API_KEY"]=api_key
    openai.base_url=proxy
    return "Success!"


def analyze_live_broadcast(prompt):
    client = openai.OpenAI()
    ret=read_frame.readframe()
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "下面是bilibili直播的几帧画面，请依据此帮我向用户回答问题"+prompt+":",
                # 自行修改prompt
                *map(lambda x: {"image": x, "resize": 768}, ret[0::60])
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "prompt": PROMPT_MESSAGES,
    }
    response= client.completions.create(**params)
    return response.choices[0]


if __name__ == '__main__':
    with gr.Blocks() as demo:
        with gr.Tab("工具页"):
            with gr.Row():
                addr = gr.Textbox(value="当前未加载直播间",interactive=False)
            with gr.Row():
                comment = gr.Textbox(label="GPT将根据提问后15秒的直播内容做出回答")
                btn = gr.Button(value="提问")
            with gr.Row():
                opt = gr.Textbox()
                btn.click(fn=analyze_live_broadcast,inputs=comment,outputs=opt)
        with gr.Tab("设置"):
            with gr.Row():
                rid = gr.Textbox(placeholder="直播间id在网页live.bilibili.com/后?前",label="直播间id")
            with gr.Row():
                dropbox = gr.Dropdown(choices=["线路1","线路2","线路3","线路4"],label="线路")
                button_update = gr.Button(value="确认")
                button_update.click(fn=setzhibojianhao, inputs=[rid,dropbox], outputs=addr)
            with gr.Row():
                api_key = gr.Textbox(label="Your Openai Api_Key",value="sk-iAEdBE0RN2pxr7wtHfkhu8jz1bDVNQKD5OjH6XJb6A8cR7vb")
                proxy = gr.Textbox(label="Using Proxy(前加上http;//或者https://,有些可能要加/v1)", value="api.openai-proxy.org/v1")
            with gr.Row():
                button_set = gr.Button(value="Set API")
                text=gr.Text(label="status",value="Not Set")
                button_set.click(fn=set_openai_api,inputs=[api_key,proxy],outputs=text)


    demo.launch()
