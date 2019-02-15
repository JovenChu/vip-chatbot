# 任务型对话系统


## 1. Rasa Review

*   **使用Rasa框架进行二次开发,完成任务型的对话系统搭建。**

* （1）进入[rasa官网](https://rasa.com/)了解rasa的详情；

* （2）了解rasa基础模型文件：[Rasa-nlu](https://github.com/RasaHQ/rasa_nlu) 和 [Rasa-core](https://github.com/RasaHQ/rasa_core)

* （3）Rasa的安装：在Linux或Mac OS中安装较为方便，而Windows安装需要进行编译，较为繁杂。
  
  ```
  pip install rasa_core==0.9.8
  pip install -U scikit-learn sklearn-crfsuite
  pip install git+https://github.com/mit-nlp/MITIE.git
  pip install jieba
  ```
* （4）Rasa的对话流程pipeline：
  
  ```yaml
  language: "zh"

  pipeline:
    - name: "nlp_mitie"  # 命名实体识别，词向量训练
      model: "data/total_word_feature_extractor.dat"  # 加载通过mitie预训练的词向量模型
    - name: "tokenizer_jieba"  # 结巴分词
      dictionary_path: "nlu_data/jieba_dictionary.txt"  # jieba自定义词典
    - name: "ner_mitie"  # 实体识别
    - name: "ner_synonyms"  # 同义词替换
    - name: "intent_entity_featurizer_regex"  # 额外的正则特征
    - name: "intent_featurizer_mitie"  # 意图特征提取（通过词向量，把每个词的词向量相加后取平均，作为句子特征的表示，作为sk-learn的输入）
    - name: "intent_classifier_sklearn"  # 意图识别分类器
  ```


## 2. 项目搭建

* 2.1 项目目录
  
  ```
  vip-chatbot
    |——consolution
        |——answer  # 问答库相关映射文件
        |    |——qa.json  # 正常问答时，action到答案的映射文件
        |    |——qa_by_entity.json  # 单轮Fallback时，实体与相关问题和答案的映射文件
        |    |——qa_by_intent.json  # 单轮Fallback时，意图与相关问题和答案的映射文件
        |——core_data  
        |    |——domain.yml  # 定义意图，实体，槽，action，模板
        |    |——story.md  # 意图与action的故事脚本
        |——models  # 训练后保存的模型
        |    |——nlu  # 训练好的rasa-nlu意图分类模型
        |    |——dialogue  # 训练好的rasa-core模型
        |——nlu_data
             |——chatito  # 定义句子模板，用于生成rasa-nlu格式的训练数据
             |——train_data  # 生成后的rasa-nlu意图分类器训练数据
                |——rasa_dataset_training.json  # chatito生成的json格式的样本，定义了同义词
                |——regex.json  # 定义的正则，用于额外的正则特征提取
        static  # 网页版的咨询机器人
        bot.py  # rasa-nlu和rasa-core训练与rasa对话系统运行接口
        myregex_entity_extrator.py  # 自定义的实体提取类
        pipeline_config.yml  # rasa-nlu的流水线定义文件
        webchat.py  # 网页版机器人启动的python脚本
        vip_action.py  # 执行所有的action，找到最佳答案

  ```

* 2.2 Rasa-nlu训练数据准备
  
  > * （1）**确定意图：**如办卡方式（banka_fangshi）、查询业务（chaxun_work）、使用范围（use_fanwei）
  
  > * （2）**准备训练数据规则：**参考`vip-vhatbot/consolution/nlu_data/chatito`中的格式书写规则文件。该文件由意图句式和同义词词表组成，排列组合从而批量生成rasa格式的训练样本数据。
  
  > * （3）**安装nodejs：**进入[Node.js官网](https://nodejs.org/en/)，下载并一路安装，重启终端即可使用npx命令。
  
  > * （4）**生成训练数据：**在终端cd到`vip-vhatbot/consolution/nlu_data`目录后，执行`npx chatito chatito --format=rasa`命令，即可在`./nlu_data`中得到rasa的训练数据rasa_dataset_training.json。将该文件放入`vip-vhatbot/consolution/nlu_data/train_data`中。
  
  > * （5）**创建额外正则特征：**参考`vip-vhatbot/consolution/nlu_data/train_data/regex.json`中的格式书写正则特征文件，可以使用这些正则特征来增强特征的表示，以用于意图分类。
  
  > * （6）至此完成训练数据的准备，即可开始训练。

* 2.3 Rasa-core训练数据准备
  
  > * **domain.yml：**需要定义槽、意图、实体、action和固定的模版返回（用于问候语或多轮）
    
    ```yaml
      slots:
        槽名1：
          - type: text
        槽名2：
          - type: text
      intents:
        - 意图名1
        - 意图名2
      entities:
        - 实体名1
        - 实体名2
      templates:
        utter_greet:
          - "Hello"
          - "Hi"
        utter_goodbye:
          - "再见，为您服务很开心^_^"
          - "Bye，下次再见"
      actions:
        - action名1
        - action名2
      ```
  
  > * **story.md：**用意图和action构建了会话的训练数据。
    
    ```markdown
      ## story greet 故事name，训练用不到，官方文档提示在debug的时候会显示story的名字
      * greet
        - utter_greet

      ## story goodbye
      * goodbye
        - utter_goodbye

      ## story greet goodbye
      * greet
        - utter_greet
      * goodbye
        - utter_goodbye

      ## story inform num
      * inform_num{"num":"1"}  包含的实体
        - Numaction
     ```
  > * **vip_action.py：**创建预测后的行动到寻找答案的策略文件
  
  > * **myregex_entity_extrator.py：**槽实体的正则特征
  
  > * 至此完成训练数据的准备，即可开始训练。

* 2.4 问答库文件准备：
  
  > * **qa.json：**将意图与其答案对应起来。 
    ```json
      # 1. action与答案直接对应（以办理方式为例）
      "Bankafangshi":"提供个人身份证原件和电话号码等信息，即可在官网办理会员卡。"
      # 2. action的不同实体与答案一一对应（以查询业务为例）
      "Chaxunwork":{
        "订单":"在XX卡小程序上点击办卡进度即可查看订单。",
        "余额":"在微信公众号，选“其他-个人中心-我的会员卡”-绑定你的会员卡后首页点击会员卡—“账单查询”按钮，进入账单查询界面即可查询余额。
      }
    ```
  > * **qa_by_entity.json、qa_by_intent.json：**当意图置信度低于阈值时，触发fallback问答，将准备好的问题回复给用户，由用户选择并给予答复，是弥补意图不全或分类不足的方法之一。优先考虑实体相关，其次是意图相关。（这两个文件需要在设计完意图和实体后做）
