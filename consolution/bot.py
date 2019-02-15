# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.featurizers import  \
    MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy

from klein import Klein
from rasa_nlu.config import RasaNLUModelConfig

logger = logging.getLogger(__name__)

from rasa_core.channels.channel import InputChannel, OutputChannel
from rasa_core.channels.channel import UserMessage

class MyOutputChannel(OutputChannel):
    def __init__(self):
        self.output = '没有查找到相关信息'
    def send_text_message(self, recipient_id, message):
        self.output = message

class MyInputChannel(InputChannel):
    def __init__(self):
        self.outPutChannel = MyOutputChannel()
        self.num_messages = 0# 消息条数计数
        self.INTENT_MESSAGE_PREFIX = '/'
        self.handler = None

    def start_async_listening(self, message_queue):
        self.handler = message_queue
    def start_sync_listening(self, message_handler):
        self.handler = message_handler

    def compute(self, input, request_id,  max_message_limit=None):
        if max_message_limit is None or num_messages < max_message_limit:
            if input == self.INTENT_MESSAGE_PREFIX + 'stop':
                return
            self.handler(UserMessage(input, self.outPutChannel, request_id))
            self.num_messages += 1
            return self.outPutChannel.output




def train_nlu():
    from rasa_nlu.training_data.loading import load_data # 新api,会将目录下的所有文件合并
    from rasa_nlu.config import RasaNLUModelConfig#新 API
    from rasa_nlu.model import Trainer
    from rasa_nlu.config import load

    # 生成46634意图样本，22003实体样本
    training_data = load_data("nlu_data/train_data")
    trainer = Trainer(load("pipeline_config.yaml"))# load的返回值就是一个RasaNLUModelConfig对象，而且其初始化需要传入的不是文件名，而是读取的配置文件内容，一个字典
    trainer.train(training_data)
    model_directory = trainer.persist("models/", project_name="nlu",fixed_nmodel_name="model_ner_reg_all")
    # model_directory = trainer.persist("models/", project_name="ivr", fixed_model_name="demo")

    return model_directory



def train_dialogue(domain_file="core_data/domain.yml",
                   model_path="models/dialogue/core",
                   training_data_file="core_data/story.md",
                   max_history=3):
    from rasa_core.policies.fallback import FallbackPolicy
    # agent = Agent(domain_file,
    #               policies=[MemoizationPolicy(max_history=2), MobilePolicy()])
    agent = Agent(domain_file, policies=[
        KerasPolicy(MaxHistoryTrackerFeaturizer(BinarySingleStateFeaturizer(),max_history=max_history)),
        FallbackPolicy(fallback_action_name='action_default_fallback',
                       core_threshold=0.3,
                       nlu_threshold=0.3)])
    #如果给的是data的地址，会自动调用load_data
    agent.train(
        training_data_file,
        epochs=200,
        batch_size=16,
        augmentation_factor=50,
        validation_split=0.2
    )

    agent.persist(model_path)
    return agent

# def my_run_ivrbot_online(input_channel=ConsoleInputChannel(),
#                       domain_file="mobile_domain.yml",
#                       training_data_file="data/mobile_story.md"):
#     agent = Agent(domain_file,
#                   policies=[MemoizationPolicy(), KerasPolicy()],
#                   interpreter=RasaNLUInterpreter("models/nlu/model_20180918-222229"))#之前这个interperter在本函数的参数初始化的，读取函数定义的说话就会执行，然后报文件不存在的错
#
#     agent.train_online(training_data_file,
#                        input_channel=input_channel,
#                        batch_size=16,
#                        epochs=200,
#                        max_training_samples=300)
#
#     return agent


def run(serve_forever=True):
    agent = Agent.load("models/dialogue/core", interpreter=RasaNLUInterpreter("models/nlu/model_ner_reg"))

    inputChannel = MyInputChannel()
    if serve_forever:
        agent.handle_channel(ConsoleInputChannel())
        # agent.handle_channel(inputChannel)
        # for i in range(10):
        #     answer = inputChannel.compute('那些银行可以办理储值卡')
        #     print(answer)


class YueBot():
    def __init__(self):
        self.agent = Agent.load("models/dialogue/core", interpreter=RasaNLUInterpreter("models/nlu/model_ner_reg"))
        self.inputChannel = MyInputChannel()
        self.agent.handle_channel(self.inputChannel)

    def bot(self, text, request_id='default'):
        try:
            return self.inputChannel.compute(text,request_id)
        except Exception:
            return "目前系统还没有收录相关信息"

if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    # parser = argparse.ArgumentParser(
    #     description="starts the bot")
    #
    # parser.add_argument(
    #     "task",
    #     choices=["train-nlu", "train-dialogue", "run", "online_train"],
    #     help="what the bot should do - e.g. run or train?")
    # task = parser.parse_args().task

    # decide what to do based on first parameter of the script
    # task = "train-dialogue"
    task = "train-nlu"
    # task = "run"
    if task == "train-nlu":
        train_nlu()
    elif task == "test-nlu":
        model_dir = "models/nlu/model_20180918-125225"
        store = ItemStore(model_dir)
        store.app.run('127.0.0.1', 1235)
    elif task == "train-dialogue":
        train_dialogue()
    elif task == "run":
        run()
    elif task == "online_train":
        my_run_ivrbot_online()
    else:
        warnings.warn("Need to pass either 'train-nlu', 'train-dialogue' or "
                      "'run' to use the script.")
        exit(1)