2026-03-28

- 是agent模式吗？
  - https://github.com/shareAI-lab/learn-claude-code/blob/main/README-zh.md
- 

人工试用

- 情绪打卡应该在对话框中
- 进入到积极情绪部分的效果非常好，符号我对wysa风格的期望。就是回复稍微多了点，我希望它再简短点。
- 我希望进去只有一个对话框，不希望有新对话这种。
- 要有时间感：我前两分钟刚聊了心情好，现在又聊了压力大。心雀没觉察到，我感觉是不是它没有把时间带上。
- 说话要像中国人。
- AI心雀真正需要什么样的记忆。
- 是否用到chatgpt 5.4的skill

2026-03-27

1、用claude code单llm的方式来构建

* [ ] 要有Agent的ReAct模式吧？
* [ ] 要让llm清楚地知道，和用户的对话是什么时候发生的
* [ ] assess的内容和输出结构，要以wysa的为主，结合limbic。
* [X] 危机要有自杀相关的
* [ ] 7.2 上下文特征提取与优先级中，P0, P1, P2, P3, P5，是用来判断用户想聊的具体内容或方向是什么，P4，对齐信号，是用来判断用户是否与AI心雀对齐，所以是不是不应该放在一起？另外，assess的内容与输出结构要和上下文特征提取与优先级整合起来。
* [ ] memory？
* [ ] 通常对话的过程是，（1）通过共情、倾听，了解用户的意图。（2）探索问题，建立工作联盟。与此同时分析与评估，进行case formulation。（3）case formulation成立时，推荐干预，鼓励用户同意实施干预。（4）带领用户完成干预。并了解感受与收获。

2026-03-26

1、搭建项目开发所需要的Harness

参考这个[Harness design for long-running application development]（https://www.anthropic.com/engineering/harness-design-long-running-apps)

2、用gpt-5.4的能力，参考资料https://developers.openai.com/api/docs/models/gpt-5.4

3、要用好prompt, context, harness。

4、要学习claude code经验。

5、要是真正的agent。

比如，claude.md

claude.md

- 文件命名规范
- 技术
