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
  
  > * （1）确定意图：如办卡方式（banka_fangshi）、查询业务（chaxun_work）、使用范围（use_fanwei）
  > * （2）准备训练数据规则：参考`vip-vhatbot/consolution/nlu_data/chatito`中的格式书写规则文件。该文件由意图句式和同义词词表组成，排列组合从而批量生成rasa格式的训练样本数据。
  > * （3）安装nodejs：进入[Node.js官网](https://nodejs.org/en/)，下载并一路安装，重启终端即可使用npx命令。
  > * （4）生成训练数据：在终端cd到`vip-vhatbot/consolution/nlu_data`目录后，执行`npx chatito chatito --format=rasa`命令，即可在`./nlu_data`中得到rasa的训练数据rasa_dataset_training.json。将该文件放入`vip-vhatbot/consolution/nlu_data/train_data`中。
  > * （5）创建额外正则特征：参考`vip-vhatbot/consolution/nlu_data/train_data/regex.json`中的格式书写正则特征文件，可以使用这些正则特征来增强特征的表示，以用于意图分类。
  > * （6）至此完成训练数据的准备，即可开始训练。

* 2.3 Rasa-core训练数据准备
  
  > * domain.yml：需要定义槽、意图、实体、action和固定的模版返回（用于问候语或多轮）
  >  
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
  > * story.md：用意图和action构建了会话的训练数据。
  >  
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
  > * vip_action.py：创建预测后的行动到寻找答案的策略文件
  > * myregex_entity_extrator.py：槽实体的正则特征
  > * 至此完成训练数据的准备，即可开始训练。

* 2.4 问答库文件准备：
  
  > * qa.json：将意图与其答案对应起来。 
    ```json
      # 1. action与答案直接对应（以办理方式为例）
      "Bankafangshi":"提供个人身份证原件和电话号码等信息，即可在官网办理会员卡。"
      # 2. action的不同实体与答案一一对应（以查询业务为例）
      "Chaxunwork":{
        "订单":"在XX卡小程序上点击办卡进度即可查看订单。",
        "余额":"在微信公众号，选“其他-个人中心-我的会员卡”-绑定你的会员卡后首页点击会员卡—“账单查询”按钮，进入账单查询界面即可查询余额。
      }
    ```
  > * qa_by_entity.json、qa_by_intent.json：当意图置信度低于阈值时，触发fallback问答，将准备好的问题回复给用户，由用户选择并给予答复，是弥补意图不全或分类不足的方法之一。优先考虑实体相关，其次是意图相关。（这两个文件需要在设计完意图和实体后做）

## 3.模型训练
* Rasa-nlu训练意图分类模型：

  ```python
    def train_nlu():
        from rasa_nlu.training_data.loading import load_data # 新api,会将目录下的所有文件合并
        from rasa_nlu.config import RasaNLUModelConfig #新 API
        from rasa_nlu.model import Trainer
        from rasa_nlu.config import load

        training_data = load_data("nlu_data/train_data")
        trainer = Trainer(load("pipeline_config.yaml")) # load的返回值就是一个RasaNLUModelConfig对象，而且其初始化需要传入的不是文件名，而是读取的配置文件内容，一个字典
        trainer.train(training_data)
        model_directory = trainer.persist("models/", project_name="nlu",fixed_nmodel_name="model_ner_reg_all") # 意图分类模型保存路径

        return model_directory

  ```
* Rasa-core训练action预测分类模型：
  ```python
    def train_dialogue(domain_file="core_data/domain.yml",
                 model_path="models/core/dialogue",
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

    ```
* Demo运行：
    ```
    $ python webchat.py
    ```

## 4.意图分类训练过程详解

- 4.1 训练总控及数据处理：`rasa_nlu/model.py`

```python
    def train(self, data, **kwargs):
        # type: (TrainingData) -> Interpreter
        """Trains the underlying pipeline using the provided training data."""
        # 获取训练数据
        self.training_data = data
        # kwargs就是当你传入key=value时存储的字典
        context = kwargs  # type: Dict[Text, Any]
        #遍历检查组件是否缺失
        for component in self.pipeline:
            updates = component.provide_context()
            if updates:
                context.update(updates)

        # Before the training starts: check that all arguments are provided
        if not self.skip_validation:
            components.validate_arguments(self.pipeline, context)

        # data gets modified internally during the training - hence the copy
        working_data = copy.deepcopy(data)
        # 开始每个组件的训练
        for i, component in enumerate(self.pipeline):
            logger.info("Starting to train component {}"
                        "".format(component.name))
            component.prepare_partial_processing(self.pipeline[:i], context)
            updates = component.train(working_data, self.config,
                                      **context)
            logger.info("Finished training component.")
            if updates:
                context.update(updates)

        return Interpreter(self.pipeline, context)

    # 加载mitie用于训练所有词向量的特征，还有维基百科中文的词向量文件：nlu_data/total_word_feature_extractor.dat
    def provide_context(self):
        type: () -> Dict[Text, Any]
        return {"mitie_feature_extractor": self.extractor,
                "mitie_file": self.component_config.get("model")
```

- 4.2 自定义训练的流程组件

```yaml
language: "zh"

pipeline:
- name: "nlp_mitie" # 初始化MITIE
  model: "nlu_data/yue_total_word_feature_extractor.dat"
- name: "tokenizer_jieba"
  dictionary_path: "nlu_data/jieba_dictionary.txt"
- name: "ner_mitie"
- name: "myregex_entity_extractor.MyRegeexEntityExtractor"
- name: "ner_synonyms"
- name: "intent_entity_featurizer_regex"
- name: "intent_featurizer_mitie"
- name: "intent_classifier_sklearn"

```

- 4.3 ner命名实体识别训练组件，得到最优的惩罚系数C：`rasa_nlu/extractors/mitie_entity_extractor.py`

```python
  def train(self, training_data, config, **kwargs):
        # type: (TrainingData, RasaNLUModelConfig) -> None
        import mitie
        # 加载预训练好的维基百科词向量文件
        model_file = kwargs.get("mitie_file")
        if not model_file:
            raise Exception("Can not run MITIE entity extractor without a "
                            "language model. Make sure this component is "
                            "preceeded by the 'nlp_mitie' component.")
        # 初始化词向量的训练器
        trainer = mitie.ner_trainer(model_file)
        # 线程数为1
        trainer.num_threads = kwargs.get("num_threads", 1)
        found_one_entity = False

        # filter out pre-trained entity examples
        # 遍历加载训练数据中实体实例
        filtered_entity_examples = self.filter_trainable_entities(
                training_data.training_examples)

        for example in filtered_entity_examples:
            sample = self._prepare_mitie_sample(example)

            found_one_entity = sample.num_entities > 0 or found_one_entity
            trainer.add(sample)

        # Mitie will fail to train if there is not a single entity tagged
        if found_one_entity:
            self.ner = trainer.train()

    # 准备实体训练所需要的数据，并返回分词在文本中的位置信息
    def filter_trainable_entities(self, entity_examples):
        # type: (List[Message]) -> List[Message]
        """Filters out untrainable entity annotations.

        Creates a copy of entity_examples in which entities that have
        `extractor` set to something other than self.name (e.g. 'ner_crf')
        are removed."""
        # 储存所有的训练数据的实体内容信息（实体，意图）及其位置信息（始止）
        filtered = []
        # 遍历json文件中的每个训练数据
        for message in entity_examples:
            entities = []
            # 获取每条训练数据中的所有实体信息
            for ent in message.get("entities", []):
                extractor = ent.get("extractor")
                if not extractor or extractor == self.name:
                    entities.append(ent)
            # 更新实体信息
            data = message.data.copy()
            data['entities'] = entities
            # 如语料‘我要上海明天的天气’中的实体（地点，日期）信息：{'intent': 'weather_address_date-time', 'entities': [{'start': 2, 'end': 4, 'value': '上海', 'entity': 'address'}, {'start': 4, 'end': 6, 'value': '明天', 'entity': 'date-time'}]
            filtered.append(
                Message(text=message.text,
                        data=data,
                        output_properties=message.output_properties,
                        time=message.time))

        return filtered

    def _prepare_mitie_sample(self, training_example):
        import mitie
        # 获取训练数据：‘我要上海明天的天气’
        text = training_example.text
        # 分词后的list：['我要','上海','明天','的','天气']
        tokens = training_example.get("tokens")
        sample = mitie.ner_training_instance([t.text for t in tokens])
        # 遍历语料中的实体，地点和时间：{'start': 2, 'end': 4, 'value': '上海', 'entity': 'address'}, {'start': 4, 'end': 6, 'value': '明天', 'entity': 'date-time'}]
        for ent in training_example.get("entities", []):
            try:
                # if the token is not aligned an exception will be raised
                start, end = MitieEntityExtractor.find_entity(
                        ent, text, tokens)
            except ValueError as e:
                logger.warning("Example skipped: {}".format(str(e)))
                continue
            try:
                # mitie will raise an exception on malicious
                # input - e.g. on overlapping entities
                sample.add_entity(list(range(start, end)), ent["entity"])
            except Exception as e:
                logger.warning("Failed to add entity example "
                               "'{}' of sentence '{}'. Reason: "
                               "{}".format(str(e), str(text), e))
                continue
        return sample

    def train(self):
        if self.size == 0:
            raise Exception("You can't call train() on an empty trainer.")
        # Make the type be a c_void_p so the named_entity_extractor constructor will know what to do.
        # 获取最优C参数的训练
        obj = ctypes.c_void_p(_f.mitie_train_named_entity_extractor(self.__obj))
        if obj is None:
            raise Exception("Unable to create named_entity_extractor.  Probably ran out of RAM")
        return named_entity_extractor(obj)

```

- 4.4 同义词替换训练组件：`rasa_nlu/extractors/entity_synonyms.py`

```python
    def train(self, training_data, config, **kwargs):
        # type: (TrainingData) -> None
        # 获取json数据中的同义词信息，加入到self的synonyms参数当中来
        for key, value in list(training_data.entity_synonyms.items()):
            self.add_entities_if_synonyms(key, value)
        # 将实体词加入到self的entity参数当中来
        for example in training_data.entity_examples:
            for entity in example.get("entities", []):
                entity_val = example.text[entity["start"]:entity["end"]]
                self.add_entities_if_synonyms(entity_val,
                                              str(entity.get("value")))
```

- 4.5 自定义正则特征加强组件：`rasa_nlu/featurizers/regex_featurizer.py`

```python
    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, RasaNLUModelConfig, **Any) -> None

        # 加载自定义的正则特征：regex.json
        for example in training_data.regex_features:
            self.known_patterns.append(example)

        for example in training_data.training_examples:
            updated = self._text_features_with_regex(example)
            example.set("text_features", updated)
```

- 4.6 实体特征向量化组件：`rasa_nlu/featurizers/mitie_featurizer.py`

```python
    def train(self, training_data, config, **kwargs):
        # type: (TrainingData, RasaNLUModelConfig, **Any) -> None

        mitie_feature_extractor = self._mitie_feature_extractor(**kwargs)
        for example in training_data.intent_examples:
            # 构建向量化特征
            features = self.features_for_tokens(example.get("tokens"),
                                                mitie_feature_extractor)
            example.set("text_features",
                        self._combine_with_existing_text_features(
                                example, features))

```

- 4.7 意图识别分类器训练组件：在`rasa_nlu/classifiers/sklearn_intent_classifier.py`

```python
    def train(self, training_data, cfg, **kwargs):
        # type: (TrainingData, RasaNLUModelConfig, **Any) -> None
        """Train the intent classifier on a data set."""
        # 定义线程数，可否增加，会对训练有什么影响？
        num_threads = kwargs.get("num_threads", 1)
        # 获取训练数据中的意图标签
        labels = [e.get("intent")
                  for e in training_data.intent_examples]
        # 意图标签需要至少两类，否则发出警告
        if len(set(labels)) < 2:
            logger.warn("Can not train an intent classifier. "
                        "Need at least 2 different classes. "
                        "Skipping training of intent classifier.")
        else:
            # 将字符串标签用num来表示
            y = self.transform_labels_str2num(labels)

            # 获取one-hot编码的训练数据
            X = np.stack([example.get("text_features")
                          for example in training_data.intent_examples])
            # 创建训练器
            self.clf = self._create_classifier(num_threads, y)
            # 开始训练
            self.clf.fit(X, y)

    def _create_classifier(self, num_threads, y):
        from sklearn.model_selection import GridSearchCV
        from sklearn.svm import SVC
        # 获取参数调节列表，暂定为[1,2,5,10,20,100]
        C = self.component_config["C"]
        # 使用的是线性核：linear
        kernels = self.component_config["kernels"]
        # dirty str fix because sklearn is expecting
        # str not instance of basestr...
        tuned_parameters = [{"C": C,
                             "kernel": [str(k) for k in kernels]}]

        # aim for 5 examples in each fold
        # 每个fold应该要有5个样例
        cv_splits = self._num_cv_splits(y)
        # 返回网格搜索的训练器
        return GridSearchCV(SVC(C=1,
                                probability=True,
                                class_weight='balanced'),
                            param_grid=tuned_parameters,
                            n_jobs=num_threads,
                            cv=cv_splits,
                            scoring='f1_weighted',
                            verbose=1)

    def _num_cv_splits(self, y):
        folds = self.component_config["max_cross_validation_folds"]
        return max(2, min(folds, np.min(np.bincount(y)) // 5))

```
