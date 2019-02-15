#!/usr/bin/env python
#-*- coding:utf-8 -*- 
# Author: Joven Chu
# Email: jovenchu@gmail.com
# Time: 2019-02-15 11:30:56
# Project: vip
# About: 创建预测后的行动到寻找答案的策略文件

import json
from rasa_core.actions import Action
from rasa_core.events import Restarted



with open('answer/qa.json', 'r', encoding='utf-8') as fw:
    result =json.load(fw)
with open('answer/qa_by_entity.json', 'r', encoding='utf-8') as fw:
    qa_list_by_entity: object =json.load(fw)
with open('answer/qa_by_intent.json', 'r', encoding='utf-8') as fw:
    qa_list_by_intent =json.load(fw)


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
        of the dialogue"""

    def name(self):
        return 'action_default_fallback'

    def run(self, dispatcher, tracker, domain):
        # from rasa_core.events import UserUtteranceReverted
        print("fallback")
        print(tracker.latest_message.intent["name"], tracker.latest_message.intent["confidence"])
        # dispatcher.utter_template("utter_default", tracker, silent_fail=True)#新API，第二个参数是一个tracker
        # dispatcher.utter_template("utter_default", filled_slots=tracker.current_slot_values(), silent_fail=True)#老API，第二个参数是槽值
        bankaitem_entity = tracker.get_slot("banka_item")
        chaxunitem_entity = tracker.get_slot("chaxun_item")

        if not hasattr(tracker, "fail_count"):
            tracker.fail_count = 1
        else:
            tracker.fail_count += 1
        if  bankaitem_entity is None and \
            chaxunitem_entity is None:
            most_likely_intent = tracker.latest_message.intent["name"]
            if most_likely_intent == "greet":
                dispatcher.utter_template("utter_greet")
            elif most_likely_intent == "goodbye":
                dispatcher.utter_template("utter_goodbye")
            elif most_likely_intent == "thanks":
                dispatcher.utter_template("utter_thanks")
            elif most_likely_intent == "confirm":
                dispatcher.utter_template("utter_confirm")
            else:
                try:
                    tracker.answer_list = qa_list_by_intent[most_likely_intent]["answers"]
                    dispatcher.utter_message(qa_list_by_intent[most_likely_intent]["questions"])
                    return [Restarted()]
                except Exception:
                    print('exception')
                    dispatcher.utter_template("utter_no_info", filled_slots=tracker.current_slot_values(),
                                              silent_fail=True)
        else:
            if bankaitem_entity is not None:
                try:
                    tracker.answer_list = qa_list_by_entity[bankaitem_entity]["answers"]
                    dispatcher.utter_message(qa_list_by_entity[bankaitem_entity]["questions"])
                    return [Restarted()]
                except Exception:
                    print('exception')
                    dispatcher.utter_template("utter_no_info", filled_slots=tracker.current_slot_values(),
                                              silent_fail=True)

            elif chaxunitem_entity is not None:
                try:
                    tracker.answer_list = qa_list_by_entity[chaxunitem_entity]["answers"]
                    dispatcher.utter_message(qa_list_by_entity[chaxunitem_entity]["questions"])
                    return [Restarted()]
                except Exception:
                    print('exception')
                    dispatcher.utter_template("utter_no_info", filled_slots=tracker.current_slot_values(),
                                              silent_fail=True)

      

class Numaction(Action):
    def name(self):
        return "Numaction"

    def run(self, dispatcher, tracker, domain):
        try:
            num = int(tracker.get_slot('num'))
        except Exception:
            dispatcher.utter_template("utter_wrong_num", filled_slots=tracker.current_slot_values(), silent_fail=True)
            return []
        print("Numaction", num)
        # print(tracker.answer_list)
        if not isinstance(num, int):
            dispatcher.utter_template("utter_wrong_num",filled_slots=tracker.current_slot_values(), silent_fail=True)
            return [Restarted()]
        if hasattr(tracker, "answer_list"):
            a_len = len(tracker.answer_list)
            for i in range(a_len):
                dispatcher.utter_message(str(i) + '：' + tracker.answer_list[i])
            if num > 0 and num <= len(tracker.answer_list):
                dispatcher.utter_message(tracker.answer_list[num - 1])
                return [Restarted()]
            else:
                dispatcher.utter_message("数字超出范围！")
                dispatcher.utter_template("utter_wrong_num", filled_slots=tracker.current_slot_values(),
                                          silent_fail=True)
                return [Restarted()]
        else:
            dispatcher.utter_message("不存在该列表！")
            dispatcher.utter_template("utter_wrong_num", filled_slots=tracker.current_slot_values(), silent_fail=True)
            return [Restarted()]



class Bankafangshi(Action):
    def name(self):
        return "Bankafangshi"

    def run(self, dispatcher, tracker, domain):
        if hasattr(tracker, "fail_count"):
            tracker.fail_count = 0
        item = tracker.get_slot('banka_item')
        print("Bankafangshi", item)
        # 判断实体是否为空
        if item is None:
            dispatcher.utter_message(result["Bankafangshi"]["None"])
            return [Restarted()]
        else:
            try:
                # 初始化标志位
                key_note = 0
                for i in result["Bankafangshi"]:
                    if item == i:
                        key_note = 1
                if key_note == 1:
                    dispatcher.utter_message(result["Bankafangshi"][item])
                    return [Restarted()]
                else:
                    dispatcher.utter_message(result["Bankafangshi"]["None"])
                    return [Restarted()]
            except Exception:
                dispatcher.utter_template("utter_no_info", filled_slots=tracker.current_slot_values(), silent_fail=True)


class Chaxunwork(Action):
    def name(self):
        return "Chaxunwork"

    def run(self, dispatcher, tracker, domain):
        if hasattr(tracker, "fail_count"):
            tracker.fail_count = 0
        item = tracker.get_slot('chaxun_item')
        print("Chaxunwork", item)
        # 判断实体是否为空
        if item is None:
            dispatcher.utter_message(result["Chaxunwork"]["None"])
            return [Restarted()]
        else:
            try:
                # 初始化标志位
                key_note = 0
                for i in result["Chaxunwork"]:
                    if item == i:
                        key_note = 1
                if key_note == 1:
                    dispatcher.utter_message(result["Chaxunwork"][item])
                    return [Restarted()]
                else:
                    dispatcher.utter_message(result["Chaxunwork"]["None"])
                    return [Restarted()]
            except Exception:
                dispatcher.utter_template("utter_no_info", filled_slots=tracker.current_slot_values(), silent_fail=True)


class Usefanwei(Action):
    def name(self):
        return "Usefanwei"

    def run(self, dispatcher, tracker, domain):
        if hasattr(tracker,"fail_count"):
            tracker.fail_count = 0
        print("Usefanwei")
        dispatcher.utter_message(result["Usefanwei"])
        return [Restarted()]





