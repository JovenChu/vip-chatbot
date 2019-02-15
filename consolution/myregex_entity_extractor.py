#!/usr/bin/env python
#-*- coding:utf-8 -*- 
# Author: Joven Chu
# Email: jovenchu@gmail.com
# Time: 2019-02-15 11:30:22
# Project: vip
# About: 槽实体的正则特征

import re
import time
from rasa_nlu.extractors import EntityExtractor
class MyRegeexEntityExtractor(EntityExtractor):
    name = "ner_regex"
    provides = ["entities"]
    requires = ["tokens"]
    language_list = ["zh"]

    def __init__(self, component_config=None):
        super(MyRegeexEntityExtractor, self).__init__(component_config)
        self.banka_item_pattern = re.compile("(个人|用户|客户|单位|公司|企业|线上)")
        self.chaxun_item_pattern = re.compile("(订单|余额|明细|账单|账单明细|消费记录)")     
        self.num_pattern = re.compile("(?<=#)\d+")

    def extract_entities(self, text):
        banka_item_ent = re.search(self.banka_item_pattern, text)
        chaxun_item_ent = re.search(self.chaxun_item_pattern, text)
        num_ent = re.search(self.num_pattern, text)

        ents = []
        if banka_item_ent is not None:
            ents.append({
                "entity": "banka_item",
                "value": text[banka_item_ent.start():banka_item_ent.end()],
                "start": banka_item_ent.start(),
                "end": banka_item_ent.end(),
                "extractor": self.name,
                "confidence": None
            })
        if chaxun_item_ent is not None:
            ents.append({
                "entity": "chaxun_item",
                "value": text[chaxun_item_ent.start():chaxun_item_ent.end()],
                "start": chaxun_item_ent.start(),
                "end": chaxun_item_ent.end(),
                "extractor": self.name,
                "confidence": None
            })
        if num_ent is not None:
            ents.append({
                "entity": "num",
                "value": text[num_ent.start():num_ent.end()],
                "start": num_ent.start(),
                "end": num_ent.end(),
                "extractor": self.name,
                "confidence": None
            })
        print("my regex entity:", ents)
        return ents

    def process(self, message, **kwargs):
        """
        用正则匹配实体，并与现有实体去重
        :param message: 
        :param kwargs: 
        :return: 
        """
        from copy import deepcopy

        # old_ents = message.get("entities", [])
        # print("mitie entity:", old_ents)
        # 计算命名实体识别耗时
        time_ner1 = time.time()
        new_ents = self.extract_entities(message.text)
        time_ner2 =time.time()
        result_ents = deepcopy(new_ents)

        cross_flag = False
        for old_ent in old_ents:
            for new_ent in new_ents:
                if new_ent["start"] >= old_ent["start"] and new_ent["end"] <= old_ent["end"]:
                    cross_flag = True
                if old_ent["start"] >= new_ent["start"] and old_ent["end"] <= new_ent["end"]:
                    cross_flag = True
            if not cross_flag:
                result_ents.append(old_ent)
            cross_flag = False
        print("all entity:", result_ents)
        message.set("entities", new_ents, add_to_output=True)

    def train(self, training_data, cfg, **kwargs):
        print("************************************it's work***************************************s")