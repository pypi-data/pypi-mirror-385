import asyncio
import io
import logging
import time
import uuid
from collections import deque
from tkinter import NO
from typing import Optional

import click
import colorlog
import numpy as np
import sounddevice as sd
from PIL import ImageGrab

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.config import (
    INPUT_AUDIO_CHANNELS,
    INPUT_AUDIO_FRAME_DURATION,
    INPUT_AUDIO_SAMPLE_RATE,
)

# 定义自定义日志级别
INFO1 = 21
INFO2 = 22
INFO3 = 23

# 添加自定义日志级别到logging模块
logging.addLevelName(INFO1, "INFO1")
logging.addLevelName(INFO2, "INFO2")
logging.addLevelName(INFO3, "INFO3")


# 为logger添加自定义方法
def info1(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO1):
        self._log(INFO1, message, args, **kwargs)


def info2(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO2):
        self._log(INFO2, message, args, **kwargs)


def info3(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO3):
        self._log(INFO3, message, args, **kwargs)


# 将自定义方法添加到Logger类
logging.Logger.info1 = info1
logging.Logger.info2 = info2
logging.Logger.info3 = info3

# 配置彩色logging
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)-5s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "white",
            "INFO": "white",
            "INFO1": "green",
            "INFO2": "cyan",
            "INFO3": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = logging.getLogger("xiaozhi_sdk")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 全局状态
input_audio_buffer: deque[bytes] = deque()
device_stauts = "listen"  # "speak" or "listen"

is_end = False
human_speak_time = None


def get_image_byte(data):
    logger.info("请截图需要识别的内容:")
    time.sleep(1)
    for _ in range(20):
        im = ImageGrab.grabclipboard()
        if not im:
            time.sleep(0.3)
            continue
        if im.mode == "RGBA":
            im = im.convert("RGB")

        byte_io = io.BytesIO()
        im.save(byte_io, format="JPEG", quality=30)
        # im.save("./test.jpg", format='JPEG', quality=30)

        img_bytes = byte_io.getvalue()
        logger.info("截图成功")

        # if platform.system() == "Darwin":
        #     subprocess.run("pbcopy", input=b"")

        return img_bytes, False

    logger.error("截图失败, 请在10秒内完成截图")
    return "截图失败", True


async def handle_message(message):
    global device_stauts
    global human_speak_time

    """处理接收到的消息"""
    global is_end
    if message["type"] == "tts" and message["state"] == "start":  # start
        pass

    elif message["type"] == "stt":  # 人类语音
        human_speak_time = time.time()
        logger.info1("human: %s", message["text"])

    elif message["type"] == "tts" and message["state"] == "sentence_start":  # AI语音
        device_stauts = "speak"  # 防止打断
        logger.info2("AI: %s", message["text"])

    elif message["type"] == "tts" and message["state"] == "stop":
        device_stauts = "listen"
        # logger.info2("播放结束")
        logger.info("聆听中...")
    elif message["type"] == "llm":  # 表情
        logger.info3("emotion: %s", message["text"])
    else:  # 其他消息
        pass
        # logger.info("other: %s", message)

    if message["type"] == "websocket" and message["state"] == "close":
        is_end = True


async def play_assistant_audio(audio_queue: deque[bytes], enable_audio, audio_samplerate):
    """播放音频流"""
    global device_stauts
    global human_speak_time

    stream = None
    if enable_audio:
        stream = sd.OutputStream(samplerate=audio_samplerate, channels=INPUT_AUDIO_CHANNELS, dtype=np.int16)
        stream.start()

    last_audio_time = None

    while True:
        if is_end:
            return

        if device_stauts == "listen":
            last_audio_time = None

        if not audio_queue:
            # 空音频 超过 2s ，将device_stauts 设置为listen，代表聆听中
            if device_stauts == "speak" and last_audio_time and time.time() - last_audio_time > 2:
                device_stauts = "listen"

            await asyncio.sleep(0.01)
            continue

        last_audio_time = time.time()

        if human_speak_time:
            logger.debug("首个音频包响应时间：%s 秒", time.time() - human_speak_time)
            human_speak_time = None

        pcm_data = audio_queue.popleft()
        if stream:
            stream.write(pcm_data)


class XiaoZhiClient:
    """小智客户端类"""

    def __init__(
        self,
        url: Optional[str] = None,
        ota_url: Optional[str] = None,
        wake_word: str = "",
    ):
        self.xiaozhi: Optional[XiaoZhiWebsocket] = None
        self.url = url
        self.ota_url = ota_url
        self.mac_address = ""
        self.wake_word = wake_word

    async def start(self, mac_address: str, serial_number: str, license_key: str, enable_audio, audio_samplerate):
        """启动客户端连接"""
        self.mac_address = mac_address
        self.xiaozhi = XiaoZhiWebsocket(
            handle_message,
            url=self.url,
            ota_url=self.ota_url,
            wake_word=self.wake_word,
            audio_sample_rate=audio_samplerate,
        )
        from xiaozhi_sdk.utils.mcp_tool import take_photo

        take_photo["tool_func"] = get_image_byte

        await self.xiaozhi.set_mcp_tool([take_photo])
        await self.xiaozhi.init_connection(
            self.mac_address, aec=False, serial_number=serial_number, license_key=license_key
        )

        asyncio.create_task(play_assistant_audio(self.xiaozhi.output_audio_queue, enable_audio, audio_samplerate))

    def audio_callback(self, indata, frames, time, status):
        """音频输入回调函数"""
        pcm_data = (indata.flatten() * 32767).astype(np.int16).tobytes()
        input_audio_buffer.append(pcm_data)

    async def process_audio_input(self):
        """处理音频输入"""
        while True:

            if is_end:
                return

            if not input_audio_buffer:
                await asyncio.sleep(0.01)
                continue

            pcm_data = input_audio_buffer.popleft()
            if device_stauts == "listen":

                await self.xiaozhi.send_audio(pcm_data)
            else:
                input_audio_buffer.clear()


async def run_client(
    mac_address: str,
    url: str,
    ota_url: str,
    serial_number: str,
    license_key: str,
    enable_audio: bool,
    wake_word: str,
):
    """运行客户端的异步函数"""
    logger.debug("Recording... Press Ctrl+C to stop.")
    client = XiaoZhiClient(url, ota_url, wake_word)
    await client.start(mac_address, serial_number, license_key, enable_audio, INPUT_AUDIO_SAMPLE_RATE)
    blocksize = INPUT_AUDIO_SAMPLE_RATE * INPUT_AUDIO_FRAME_DURATION // 1000
    with sd.InputStream(
        callback=client.audio_callback,
        channels=INPUT_AUDIO_CHANNELS,
        samplerate=INPUT_AUDIO_SAMPLE_RATE,
        blocksize=blocksize,
    ):
        logger.info("聆听中...")
        await client.process_audio_input()


def get_mac_address():
    mac = uuid.getnode()
    mac_addr = ":".join(["%02x" % ((mac >> ele) & 0xFF) for ele in range(40, -8, -8)])
    return mac_addr


@click.command()
@click.argument("mac_address", required=False)
@click.option("--url", help="服务端websocket地址")
@click.option("--ota_url", help="OTA地址")
@click.option("--serial_number", default="", help="设备的序列号")
@click.option("--license_key", default="", help="设备的授权密钥")
@click.option("--enable_audio", default=True, help="是否开启音频播放")
@click.option("--wake_word", default="", help="唤醒词")
def main(
    mac_address: str,
    url: str,
    ota_url: str,
    serial_number: str,
    license_key: str,
    enable_audio: bool,
    wake_word: str,
):
    """小智SDK客户端

    MAC_ADDRESS: 设备的MAC地址 (格式: XX:XX:XX:XX:XX:XX)
    """
    mac_address = mac_address or get_mac_address()
    asyncio.run(run_client(mac_address, url, ota_url, serial_number, license_key, enable_audio, wake_word))
