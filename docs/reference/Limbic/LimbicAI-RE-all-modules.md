# LimbicAI All Modules

本文档基于专利 `Dialogue system and a dialogue method` 中出现的模块/组件命名整理。

## 1. 模块及层级图

```text
DialogueSystem
├─ InputOutputComponent
├─ SubjectSafetyModule
│  └─ CrisisDetectionModule
├─ FirstModule
│  ├─ SubjectUnderstandingModule
│  │  ├─ CognitiveUnderstandingModule
│  │  │  └─ CognitiveDistortionUnderstandingModel
│  │  ├─ BehaviouralUnderstandingModule
│  │  ├─ ThoughtDetectionModel
│  │  ├─ DistortedThoughtDetectionModel
│  │  ├─ SentimentAnalysisModel
│  │  ├─ BehaviouralPatternDetectionModel
│  │  ├─ CoreBeliefsModel
│  │  └─ TopicModel
│  ├─ SubjectRecommendationModule
│  ├─ RecommenderModule
│  ├─ KnowledgeBank
│  └─ HistoryModule
├─ PromptGenerationModule
│  ├─ FirstPromptGenerator
│  ├─ SecondPromptGenerator
│  ├─ ThirdPromptGenerator
│  └─ FourthPromptGenerator
├─ InteractionModule
│  ├─ FlowModule
│  └─ SecondModule
│     └─ LanguageModel
│        ├─ Tokeniser
│        ├─ VectorRepresentationModule
│        ├─ RepeatedTransformerBlock
│        │  ├─ AttentionModule
│        │  ├─ AdditionAndLayerNormalisationModule
│        │  └─ FeedForwardNeuralNetwork
│        └─ TextPredictionModule
├─ OutputSafetyModule
├─ ASRModule
├─ TextToSpeechModule
└─ ActionLogic
```

## 2. 主流程图示

```text
User Input
  ↓
InputOutputComponent
  ↓
SubjectSafetyModule
  ↓
InteractionModule
  ├─ FlowModule
  └─ PromptGenerationModule
       ↓
   First/Second/Third/FourthPromptGenerator
       ↓
FirstModule
  ├─ SubjectUnderstandingModule
  ├─ RecommenderModule
  └─ KnowledgeBank
       ↓
SecondModule
  └─ LanguageModel
       ↓
OutputSafetyModule
       ↓
InputOutputComponent
       ↓
User Output
```

## 3. 说明

1. 本清单以专利文本中明确出现的 `module`、`model`、`component` 等核心结构为主。
2. `SubjectRecommendationModule` 与 `RecommenderModule` 在不同段落中有交叉使用，这里两者都保留。
3. `CoreBeliefsModel`、`TopicModel` 在文中更偏扩展性能力，但仍纳入清单。
4. `LanguageModel` 内部的 `Tokeniser`、`AttentionModule` 等属于实现级子模块，也一并列出，方便后续做系统还原或映射分析。
