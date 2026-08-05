#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 伊菲学习管理系统 的本地题库 questionbank.js
- 每个考点（point）至少 50 题，目标 50~100。
- 结构：questionbank[subjectKey][point] = [ {q, options:[...], answer, explain}, ... ]
- 前端 今日任务 直接 require 本文件抽取练习，不依赖云函数。
"""
import json, math, random

random.seed(20260804)

bank = {"english": {}, "math": {}}


def build_form(items, point):
    """词性转换：给原词，选正确派生形式。distractors 用其它真实派生词（更真实）。"""
    answers = [it[1] for it in items]
    qs = []
    for base, form, _ in items:
        others = [a for a in answers if a != form]
        random.shuffle(others)
        opts = [form] + others[:3]
        random.shuffle(opts)
        qs.append({
            "q": f"词性转换：将 “{base}” 变为正确形式填到句中。",
            "options": opts,
            "answer": form,
            "explain": f"“{base}” 的该考点形式为 “{form}”。"
        })
    return qs


# ============================================================
# fill 产出型题目（2026-08-04 方案 §四，契约见 17-题库题型扩展方案-给甲）
# 结构: {q, answer(含 | 等价表), explain, type:"fill", match:"exact"|"keywords"}
# 运行: python build_questionbank.py --fill  → 输出 questionbank_fill.js（本地样例，不推云端）
# 渲染/判分由甲侧 tasks 页答题模式实现；老选择题不受影响。
# ============================================================

def build_fill_words(items):
    """词性转换 fill：给真实句子的空，写出正确派生形式。answer=派生词。"""
    qs = []
    for base, form, sentence in items:
        qs.append({
            "q": f"用所给词的适当形式填空：{sentence}（{base}）",
            "answer": form,
            "explain": f"“{base}” 在该句应变为 “{form}”。",
            "type": "fill",
            "match": "exact",
        })
    return qs


# 名→形 fill 样例（真实句 + 派生词）
N2A_FILL = [
    ("care", "careful", "Be ______ with your homework."),
    ("help", "helpful", "The old man is very ______ to others."),
    ("hope", "hopeful", "We are ______ that he can win the game."),
    ("meaning", "meaningful", "It is ______ to help those in need."),
    ("success", "successful", "She is a ______ businesswoman."),
    ("beauty", "beautiful", "What a ______ flower it is!"),
    ("danger", "dangerous", "It is ______ to swim in the river alone."),
    ("noise", "noisy", "The street is too ______ at night."),
    ("health", "healthy", "Eating vegetables keeps us ______."),
    ("luck", "lucky", "He was ______ to catch the last train."),
    ("fun", "funny", "The clown is very ______."),
    ("sun", "sunny", "It is a ______ day today."),
    ("wind", "windy", "It is ______ in autumn in Beijing."),
    ("rain", "rainy", "Take an umbrella; it is ______ outside."),
    ("snow", "snowy", "The mountain is ______ in winter."),
    ("cloud", "cloudy", "The sky is ______ this morning."),
    ("fog", "foggy", "It is ______ today, so drive slowly."),
    ("sleep", "sleepy", "I feel ______ after the long trip."),
    ("hunger", "hungry", "The little boy is very ______."),
    ("thirst", "thirsty", "After running, he felt ______."),
    ("friend", "friendly", "People in this village are very ______."),
    ("love", "lovely", "The baby is really ______."),
    ("day", "daily", "Reading is part of my ______ life."),
    ("week", "weekly", "We have a ______ meeting every Monday."),
    ("month", "monthly", "This magazine is published ______."),
    ("year", "yearly", "The school holds a ______ sports meeting."),
    ("education", "educational", "This is an ______ program for children."),
    ("tradition", "traditional", "They celebrate the ______ festival together."),
    ("nature", "natural", "I like ______ beauty best."),
    ("culture", "cultural", "The city is rich in ______ heritage."),
    ("music", "musical", "She is a ______ girl."),
    ("practice", "practical", "This is a ______ suggestion."),
    ("science", "scientific", "We should follow a ______ method."),
    ("energy", "energetic", "The young man is always ______."),
    ("gold", "golden", "The sky is ______ at sunset."),
    ("wood", "wooden", "The chair is made of ______."),
    ("anger", "angry", "He was ______ with me for being late."),
    ("silence", "silent", "The classroom was ______ during the test."),
    ("pride", "proud", "Her parents are ______ of her."),
    ("colour", "colourful", "The garden is ______ in spring."),
    ("use", "useful", "This tool is very ______ for cooking."),
    ("pain", "painful", "The cut on his arm is ______."),
    ("peace", "peaceful", "The village is quiet and ______."),
    ("power", "powerful", "The car has a ______ engine."),
    ("wonder", "wonderful", "We had a ______ time at the beach."),
    ("poison", "poisonous", "That snake is ______."),
    ("wealth", "wealthy", "The family is very ______."),
    ("dirt", "dirty", "Wash your hands; they are ______."),
    ("salt", "salty", "The soup is too ______."),
    ("fool", "foolish", "It is ______ to waste food."),
    ("child", "childish", "Don't be so ______."),
    ("live", "lively", "The party was really ______."),
    ("nation", "national", "May Day is a ______ holiday."),
    ("person", "personal", "This is my ______ opinion."),
]

# 名→形**选择题**词表（恢复原 63 项，保证现有题库不变化；N2A_FILL 仅用于 fill）
n2a = [
    ("care", "careful"), ("use", "useful"), ("help", "helpful"), ("hope", "hopeful"),
    ("pain", "painful"), ("meaning", "meaningful"), ("peace", "peaceful"), ("power", "powerful"),
    ("success", "successful"), ("wonder", "wonderful"), ("beauty", "beautiful"), ("danger", "dangerous"),
    ("poison", "poisonous"), ("noise", "noisy"), ("health", "healthy"), ("wealth", "wealthy"),
    ("luck", "lucky"), ("fun", "funny"), ("sun", "sunny"), ("wind", "windy"), ("rain", "rainy"),
    ("snow", "snowy"), ("cloud", "cloudy"), ("fog", "foggy"), ("sleep", "sleepy"), ("hunger", "hungry"),
    ("thirst", "thirsty"), ("dirt", "dirty"), ("salt", "salty"), ("fool", "foolish"), ("child", "childish"),
    ("friend", "friendly"), ("love", "lovely"), ("live", "lively"), ("day", "daily"), ("week", "weekly"),
    ("month", "monthly"), ("year", "yearly"), ("nation", "national"), ("person", "personal"),
    ("education", "educational"), ("tradition", "traditional"), ("nature", "natural"), ("culture", "cultural"),
    ("music", "musical"), ("practice", "practical"), ("politics", "political"), ("science", "scientific"),
    ("history", "historical"), ("economy", "economic"), ("energy", "energetic"), ("gold", "golden"),
    ("wood", "wooden"), ("wool", "woolen"), ("self", "selfish"), ("base", "basic"), ("centre", "central"),
    ("form", "formal"), ("universe", "universal"), ("globe", "global"), ("atom", "atomic"),
    ("colour", "colourful"), ("pride", "proud"), ("anger", "angry"), ("silence", "silent"),
]
bank["english"]["词性转换·名→形"] = build_form([(b, f, "") for b, f in n2a], "词性转换·名→形")


# ---------------- 英语：词性转换 动→名 ----------------
v2n = [
    ("act", "action"), ("achieve", "achievement"), ("advise", "advice"), ("agree", "agreement"),
    ("appear", "appearance"), ("argue", "argument"), ("arrive", "arrival"), ("assist", "assistance"),
    ("attract", "attraction"), ("behave", "behaviour"), ("believe", "belief"), ("build", "building"),
    ("celebrate", "celebration"), ("collect", "collection"), ("compete", "competition"), ("complain", "complaint"),
    ("conclude", "conclusion"), ("connect", "connection"), ("consider", "consideration"), ("construct", "construction"),
    ("contribute", "contribution"), ("decide", "decision"), ("decorate", "decoration"), ("describe", "description"),
    ("develop", "development"), ("discuss", "discussion"), ("educate", "education"), ("encourage", "encouragement"),
    ("enjoy", "enjoyment"), ("excite", "excitement"), ("explain", "explanation"), ("express", "expression"),
    ("fail", "failure"), ("govern", "government"), ("improve", "improvement"), ("invent", "invention"),
    ("invite", "invitation"), ("judge", "judgement"), ("know", "knowledge"), ("learn", "learning"),
    ("manage", "management"), ("marry", "marriage"), ("move", "movement"), ("operate", "operation"),
    ("organize", "organization"), ("perform", "performance"), ("pollute", "pollution"), ("prefer", "preference"),
    ("prepare", "preparation"), ("produce", "production"), ("pronounce", "pronunciation"), ("protect", "protection"),
    ("recommend", "recommendation"), ("refuse", "refusal"), ("suggest", "suggestion"), ("survive", "survival"),
    ("teach", "teaching"), ("understand", "understanding"), ("use", "use"), ("win", "winner"),
    ("die", "death"), ("fly", "flight"), ("choose", "choice"), ("please", "pleasure"),
]
bank["english"]["词性转换·动→名"] = build_form([(b, f, "") for b, f in v2n], "词性转换·动→名")


# ---------------- 英语：词汇辨析/易混词 ----------------
vocab = [
    ("You can _____ my pen for a day.", ["borrow", "lend", "keep", "use"], "borrow", "borrow 借入；lend 借出。"),
    ("Please _____ your book to school tomorrow.", ["bring", "take", "carry", "fetch"], "bring", "bring 带来；take 带走。"),
    ("He _____ English very well.", ["speaks", "says", "talks", "tells"], "speaks", "说某种语言用 speak。"),
    ("Please _____ me a story.", ["tell", "say", "speak", "talk"], "tell", "tell a story 讲故事。"),
    ("She _____ she is tired.", ["says", "speaks", "talks", "tells"], "says", "say 后接所说内容。"),
    ("They are _____ about the film.", ["talking", "saying", "speaking", "telling"], "talking", "talk about 谈论。"),
    ("I like to _____ to music.", ["listen", "hear", "sound", "look"], "listen", "listen 强调听的动作。"),
    ("I _____ a strange sound just now.", ["heard", "listened", "sound", "looked"], "heard", "hear 强调听的结果。"),
    ("_____ at the blackboard, please.", ["Look", "See", "Watch", "Read"], "Look", "look at 看（动作）。"),
    ("I _____ a bird in the tree.", ["saw", "looked", "watched", "read"], "saw", "see 看见（结果）。"),
    ("Let's _____ TV together.", ["watch", "see", "look", "read"], "watch", "watch TV 看电视。"),
    ("There are only _____ apples left.", ["few", "little", "a little", "much"], "few", "few 接可数名词。"),
    ("There is _____ time before the train.", ["little", "few", "a few", "many"], "little", "little 接不可数名词。"),
    ("Would you like _____ water?", ["some", "any", "many", "few"], "some", "希望得到肯定回答用 some。"),
    ("I don't have _____ money.", ["any", "some", "many", "few"], "any", "否定句用 any。"),
    ("I like apples, and I like oranges _____.", ["too", "either", "also", "neither"], "too", "肯定句句末用 too。"),
    ("I don't like tea, and I don't like coffee _____.", ["either", "too", "also", "neither"], "either", "否定句句末用 either。"),
    ("The book is _____ the two boxes.", ["between", "among", "in", "on"], "between", "两者之间用 between。"),
    ("_____ the students, he is the tallest.", ["Among", "Between", "In", "On"], "Among", "三者及以上用 among。"),
    ("The old man lives _____, but he is not lonely.", ["alone", "lonely", "lone", "along"], "alone", "alone 独自（状态）；lonely 孤独（感受）。"),
    ("The flower is _____.", ["dead", "died", "death", "dying"], "dead", "dead 形容词，死的。"),
    ("He _____ yesterday.", ["died", "dead", "death", "dying"], "died", "die 动词，过去式 died。"),
    ("His _____ made us sad.", ["death", "die", "dead", "dying"], "death", "death 名词，死亡。"),
    ("Please _____ down and rest.", ["lie", "lay", "lain", "laid"], "lie", "lie 躺（原形）；lay 放置。"),
    ("The hen _____ an egg every day.", ["lays", "lies", "laid", "laying"], "lays", "lay 下蛋（三单 lays）。"),
    ("The sun _____ in the east.", ["rises", "raises", "rose", "rise"], "rises", "rise 升起（不及物）；raise 举起（及物）。"),
    ("Please _____ your hand if you know.", ["raise", "rise", "arise", "arouse"], "raise", "raise 举起（及物）。"),
    ("The rain will _____ our plan.", ["affect", "effect", "effort", "offer"], "affect", "affect 动词，影响。"),
    ("What is the _____ of the news?", ["effect", "affect", "effort", "offer"], "effect", "effect 名词，效果。"),
    ("I _____ your gift happily.", ["accept", "except", "expect", "excerpt"], "accept", "accept 接受；except 除…外。"),
    ("Everyone came _____ Tom.", ["except", "accept", "expect", "excerpt"], "except", "except 除…之外。"),
    ("Come and sit _____ me.", ["beside", "besides", "except", "accept"], "beside", "beside 在…旁边；besides 除…之外（还）。"),
    ("_____ English, he also speaks French.", ["Besides", "Beside", "Except", "Accept"], "Besides", "besides 此外还。"),
    ("The room is very _____.", ["quiet", "quite", "quit", "quilt"], "quiet", "quiet 安静的；quite 相当。"),
    ("It is _____ cold today.", ["quite", "quiet", "quilt", "quit"], "quite", "quite 相当。"),
    ("She will _____ a red coat to the party.", ["wear", "put on", "dress", "in"], "wear", "wear 穿着（状态）。"),
    ("_____ your coat, it is cold outside.", ["Put on", "Wear", "Dress", "In"], "Put on", "put on 穿上（动作）。"),
    ("The mother _____ her baby every morning.", ["dresses", "wears", "puts on", "in"], "dresses", "dress 宾语是人。"),
    ("A large _____ of students are on the playground.", ["number", "amount", "deal", "plenty"], "number", "number 接可数；amount 接不可数。"),
    ("We need a large _____ of water.", ["amount", "number", "deal", "plenty"], "amount", "amount 接不可数。"),
    ("He has a good _____ in a big company.", ["job", "work", "works", "working"], "job", "job 可数工作；work 不可数。"),
    ("Our team _____ the game at last.", ["won", "beat", "beaten", "winned"], "won", "win 后接比赛/奖品；beat 后接对手。"),
    ("We _____ them by two points.", ["beat", "won", "winned", "beaten"], "beat", "beat 后接对手。"),
    ("The book _____ 20 yuan.", ["costs", "spends", "takes", "pays"], "costs", "cost 物作主语。"),
    ("I _____ two hours on this homework.", ["spent", "cost", "took", "paid"], "spent", "spend 人作主语，接 on。"),
    ("It _____ me two hours to finish it.", ["took", "spent", "cost", "paid"], "took", "It takes sb time. 固定句型。"),
    ("I _____ 20 yuan for the book.", ["paid", "spent", "cost", "took"], "paid", "pay for 为…付款。"),
    ("Please _____ my question.", ["answer", "reply", "respond", "say"], "answer", "answer a question 回答问题。"),
    ("He didn't _____ to my letter.", ["reply", "answer", "respond", "say"], "reply", "reply to 回复。"),
    ("Can you solve this math _____?", ["problem", "question", "trouble", "matter"], "problem", "problem 需解决的难题。"),
    ("May I ask you a _____?", ["question", "problem", "trouble", "matter"], "question", "question 提问。"),
    ("_____ of the two books is interesting.", ["Neither", "Either", "Both", "None"], "Neither", "两者都不用 neither。"),
    ("I have _____ finished my homework.", ["already", "yet", "still", "ever"], "already", "already 用于肯定句。"),
    ("Have you eaten _____?", ["yet", "already", "still", "ever"], "yet", "yet 用于否定/疑问句。"),
    ("He is _____ here waiting for you.", ["still", "yet", "already", "ever"], "still", "still 仍然。"),
    ("He left two days _____.", ["ago", "before", "later", "after"], "ago", "ago 用于过去时，表…前。"),
    ("I have never seen it _____.", ["before", "ago", "later", "after"], "before", "before 用于现在完成时。"),
    ("It rained _____ two hours.", ["for", "since", "during", "from"], "for", "for + 时间段。"),
    ("He has lived here _____ 2010.", ["since", "for", "during", "from"], "since", "since + 时间点。"),
    ("_____ the holiday, we visited Beijing.", ["During", "For", "Since", "From"], "During", "during 在…期间。"),
    ("_____ Monday morning we have a test.", ["On", "In", "At", "By"], "On", "具体某天上午用 on。"),
    ("We have P.E. _____ the morning.", ["in", "on", "at", "by"], "in", "泛指上午用 in。"),
    ("The meeting starts _____ 7 o'clock.", ["at", "in", "on", "by"], "at", "具体时刻用 at。"),
    ("He stayed home _____ he was ill.", ["because", "so", "but", "or"], "because", "because 因为。"),
    ("I don't know _____ he will come.", ["whether", "if", "that", "what"], "whether", "whether 是否（后接或不定式）。"),
    ("_____ it rains, we will stay inside.", ["If", "Whether", "That", "What"], "If", "if 如果。"),
    ("_____ book is this on the desk?", ["Whose", "Who", "Whom", "Which"], "Whose", "whose 谁的。"),
    ("_____ did you meet at the gate?", ["Whom", "Who", "Whose", "Which"], "Whom", "whom 作宾语（谁）。"),
    ("The boy _____ is standing there is my brother.", ["who", "which", "that", "whom"], "who", "who 指人作主语。"),
    ("The book _____ is on the desk is mine.", ["which", "who", "whom", "that"], "which", "which 指物。"),
    ("The news _____ he told me is true.", ["that", "who", "which", "whom"], "that", "that 引导定语从句。"),
]
bank["english"]["词汇辨析/易混词"] = [
    {"q": q, "options": opts, "answer": ans, "explain": exp} for (q, opts, ans, exp) in vocab
]


# ---------------- 英语：完形填空·长语境（句子级微练） ----------------
cloze = [
    ("My mother _____ early every morning to make breakfast.", ["gets up", "gets on", "gets off", "gets down"], "gets up", "get up 起床。"),
    ("He _____ his homework before dinner yesterday.", ["finished", "finishes", "finishing", "finish"], "finished", "yesterday 用过去式。"),
    ("The students are _____ a history lesson now.", ["having", "have", "has", "had"], "having", "now 用现在进行时。"),
    ("If it _____ tomorrow, we will stay at home.", ["rains", "will rain", "rained", "raining"], "rains", "if 主将从现。"),
    ("She is good _____ playing the piano.", ["at", "in", "on", "for"], "at", "be good at 擅长。"),
    ("We should listen _____ the teacher carefully.", ["to", "for", "at", "with"], "to", "listen to 听。"),
    ("The girl was so _____ that she couldn't say a word.", ["nervous", "happy", "excited", "tired"], "nervous", "紧张得说不出话。"),
    ("He walked _____ the road and entered the shop.", ["across", "cross", "through", "over"], "across", "across 横穿（表面）。"),
    ("My brother is two years _____ than me.", ["older", "old", "elder", "the oldest"], "older", "older 年龄较大。"),
    ("There is a bridge _____ the river.", ["over", "above", "on", "under"], "over", "over 在…正上方。"),
    ("The teacher asked us _____ quiet in the library.", ["to keep", "keep", "keeping", "kept"], "to keep", "ask sb to do。"),
    ("I was _____ in the book and forgot the time.", ["lost", "lose", "losing", "loss"], "lost", "be lost in 沉浸于。"),
    ("She decided _____ harder this term.", ["to study", "study", "studying", "studied"], "to study", "decide to do。"),
    ("The weather today is much _____ than yesterday.", ["better", "good", "best", "well"], "better", "good 比较级 better。"),
    ("He ran as _____ as he could to catch the bus.", ["fast", "faster", "fastest", "fastly"], "fast", "as+原级+as。"),
    ("We must _____ the rules of the school.", ["follow", "make", "break", "find"], "follow", "follow the rules 遵守规则。"),
    ("The little boy looked _____ because he lost his toy.", ["sad", "sadly", "sadness", "sadder"], "sad", "look 系动词后接形容词。"),
    ("Please turn _____ the light, it's too dark.", ["on", "off", "down", "up"], "on", "turn on 打开。"),
    ("They arrived _____ the station at 8 o'clock.", ["at", "in", "on", "to"], "at", "arrive at 小地点。"),
    ("The story _____ me think about my own life.", ["made", "makes", "making", "make"], "made", "make sb do；过去式 made。"),
    ("He is the _____ of the three brothers.", ["tallest", "taller", "tall", "most tall"], "tallest", "三者及以上用最高级。"),
    ("I borrowed this book _____ the library.", ["from", "to", "with", "for"], "from", "borrow from 从…借。"),
    ("The food tastes _____, so we ate a lot.", ["delicious", "deliciously", "well", "bad"], "delicious", "taste 系动词后接形容词。"),
    ("She spoke _____ so that everyone could hear her.", ["loudly", "loud", "aloud", "louder"], "loudly", "修饰动词用副词。"),
    ("We need to _____ our classroom every day.", ["clean", "clear", "cure", "care"], "clean", "clean the classroom 打扫。"),
    ("The boy is _____ enough to go to school by himself.", ["old", "older", "elder", "young"], "old", "old enough 足够大。"),
    ("He _____ his keys at home this morning.", ["left", "forgot", "lost", "missed"], "left", "leave 落下（东西在某处）。"),
    ("The movie was so boring that I almost fell _____.", ["asleep", "sleep", "sleepy", "sleeping"], "asleep", "fall asleep 入睡。"),
    ("She is very kind and always _____ others.", ["helps", "help", "helping", "helped"], "helps", "主语三单用 helps。"),
    ("The cat is hiding _____ the door.", ["behind", "in front of", "above", "below"], "behind", "behind 在…后面。"),
    ("We were _____ about the good news.", ["excited", "exciting", "excite", "excitement"], "excited", "人感到 excited。"),
    ("He solved the problem _____ his own.", ["on", "by", "with", "in"], "on", "on one's own 独自。"),
    ("The teacher was _____ with our progress.", ["pleased", "please", "pleasing", "pleasure"], "pleased", "be pleased with 对…满意。"),
    ("I _____ you will pass the exam.", ["believe", "belief", "believed", "believing"], "believe", "believe 相信。"),
    ("The children played _____ in the park all afternoon.", ["happily", "happy", "happiness", "happier"], "happily", "修饰动词用副词。"),
    ("He is not only smart but _____ hard-working.", ["also", "too", "either", "as well"], "also", "not only...but also。"),
    ("The train left _____ we got to the station.", ["before", "after", "when", "while"], "before", "before 在…之前。"),
    ("She _____ the letter and put it in the envelope.", ["folded", "fold", "folding", "folds"], "folded", "过去式 folded。"),
    ("It is important to drink _____ water every day.", ["enough", "many", "few", "lot"], "enough", "enough 足够的。"),
    ("The dog _____ at the stranger loudly.", ["barked", "bark", "barking", "barks"], "barked", "过去式 barked。"),
    ("He felt _____ after running for an hour.", ["tired", "tiring", "tire", "tiredly"], "tired", "人感到 tired。"),
    ("The books on the desk _____ mine.", ["are", "is", "was", "be"], "are", "复数用 are。"),
    ("We should save _____ and protect the earth.", ["energy", "energies", "an energy", "energetic"], "energy", "energy 能源（不可数）。"),
    ("She _____ a beautiful song at the party.", ["sang", "sung", "sing", "singing"], "sang", "sing 过去式 sang。"),
    ("The question is too difficult for me _____.", ["to answer", "answer", "answering", "answered"], "to answer", "too...to 太…而不能。"),
    ("He _____ to bed late last night.", ["went", "goes", "go", "going"], "went", "go to bed 过去式 went。"),
    ("The ice cream _____ good in summer.", ["tastes", "taste", "tasting", "tasted"], "tastes", "主语三单 tastes。"),
    ("They are planning _____ a trip next month.", ["to take", "take", "taking", "took"], "to take", "plan to do。"),
    ("The window is open; please _____ it.", ["close", "closed", "closing", "shut"], "close", "close 关上。"),
    ("He works _____ a doctor in a big hospital.", ["as", "like", "for", "to"], "as", "work as 作为。"),
    ("The baby fell _____ as soon as the light went out.", ["asleep", "sleep", "sleepy", "sleeping"], "asleep", "fall asleep。"),
    ("We _____ a lot of photos during the trip.", ["took", "take", "taking", "taken"], "took", "take photos 过去式 took。"),
    ("She is afraid _____ speaking in public.", ["of", "to", "for", "with"], "of", "be afraid of doing。"),
    ("The old man lives a _____ life in the village.", ["quiet", "quietly", "quite", "quilt"], "quiet", "quiet 平静的。"),
]
bank["english"]["完形填空·长语境"] = [
    {"q": q, "options": opts, "answer": ans, "explain": exp} for (q, opts, ans, exp) in cloze
]


# ---------------- 英语：阅读问答（开放题 / 短篇理解） ----------------
reading = [
    ("Tom is ten years old. He likes reading books. Every weekend he goes to the library.",
     "What does Tom like doing?", ["Reading books.", "Playing football.", "Watching TV.", "Swimming."], "Reading books.", "原文 He likes reading books。"),
    ("Lucy is from London. She moved to Shanghai with her family last year. She likes Chinese food.",
     "Where is Lucy from?", ["London.", "Shanghai.", "New York.", "Paris."], "London.", "原文 from London。"),
    ("The sun is much bigger than the earth. It gives us light and heat every day.",
     "What does the sun give us?", ["Light and heat.", "Water and air.", "Food and clothes.", "Books and pens."], "Light and heat.", "原文 gives light and heat。"),
    ("Mike gets up at 6:30 every day. He eats breakfast at 7:00 and goes to school by bus.",
     "How does Mike go to school?", ["By bus.", "By bike.", "On foot.", "By car."], "By bus.", "原文 by bus。"),
    ("Birds can fly because they have wings. Fish can swim because they have fins.",
     "Why can birds fly?", ["They have wings.", "They have fins.", "They have legs.", "They have tails."], "They have wings.", "原文 because they have wings。"),
    ("Anna wants to be a doctor when she grows up. She studies hard at school.",
     "What does Anna want to be?", ["A doctor.", "A teacher.", "A nurse.", "A driver."], "A doctor.", "原文 wants to be a doctor。"),
    ("The Yangtze River is the longest river in China. Many people live near it.",
     "What is the longest river in China?", ["The Yangtze River.", "The Yellow River.", "The Nile.", "The Amazon."], "The Yangtze River.", "原文 the longest river in China。"),
    ("We should eat more vegetables and less sugar. That helps us stay healthy.",
     "What helps us stay healthy?", ["More vegetables and less sugar.", "More sugar and less water.", "More meat only.", "No vegetables."], "More vegetables and less sugar.", "原文 eat more vegetables and less sugar。"),
    ("Peter broke his leg yesterday. Now he has to stay in bed for a week.",
     "Why does Peter stay in bed?", ["He broke his leg.", "He is tired.", "He is hungry.", "He is sleepy."], "He broke his leg.", "原文 broke his leg。"),
    ("The library closes at 5 p.m. on weekdays and at 4 p.m. on weekends.",
     "When does the library close on weekends?", ["At 4 p.m.", "At 5 p.m.", "At 6 p.m.", "At 3 p.m."], "At 4 p.m.", "原文 at 4 p.m. on weekends。"),
    ("Snow is white. When it is cold enough, water becomes ice or snow.",
     "When does water become snow?", ["When it is cold enough.", "When it is hot.", "When it rains.", "When it is windy."], "When it is cold enough.", "原文 cold enough。"),
    ("Emma won the first prize in the painting contest. Her parents were very proud.",
     "What did Emma win?", ["The first prize.", "The second prize.", "A book.", "A pen."], "The first prize.", "原文 won the first prize。"),
    ("The earth goes around the sun. It takes 365 days to finish one circle.",
     "How long does the earth take to go around the sun?", ["365 days.", "30 days.", "24 hours.", "12 months only."], "365 days.", "原文 365 days。"),
    ("Tim forgot his umbrella, so he got wet in the rain.",
     "Why did Tim get wet?", ["He forgot his umbrella.", "He fell in water.", "He swam.", "He took a bath."], "He forgot his umbrella.", "原文 forgot his umbrella。"),
    ("A healthy diet means eating fruit, vegetables, and exercising often.",
     "What is a healthy diet?", ["Fruit, vegetables and exercise.", "Only meat.", "Only sweets.", "No exercise."], "Fruit, vegetables and exercise.", "原文 eating fruit, vegetables, and exercising。"),
    ("The panda eats bamboo almost every day. It lives only in China.",
     "What does the panda eat?", ["Bamboo.", "Meat.", "Fish.", "Grass only."], "Bamboo.", "原文 eats bamboo。"),
    ("My grandfather reads the newspaper every morning. He likes the sports page best.",
     "Which page does grandfather like best?", ["The sports page.", "The food page.", "The weather page.", "The cartoon page."], "The sports page.", "原文 likes the sports page best。"),
    ("The school sports meeting will be held next Friday. Many students will join.",
     "When is the sports meeting?", ["Next Friday.", "This Monday.", "Next Sunday.", "Yesterday."], "Next Friday.", "原文 next Friday。"),
    ("Water boils at 100℃. When it boils, it turns into steam.",
     "At what temperature does water boil?", ["100℃.", "0℃.", "50℃.", "200℃."], "100℃.", "原文 boils at 100℃。"),
    ("Cats sleep a lot during the day. They are more active at night.",
     "When are cats more active?", ["At night.", "In the morning.", "At noon.", "In the afternoon."], "At night.", "原文 more active at night。"),
    ("Helen Keller could not see or hear, but she learned to read and write.",
     "What could Helen not do?", ["See or hear.", "Walk or run.", "Eat or drink.", "Speak only."], "See or hear.", "原文 could not see or hear。"),
    ("The museum is free for children under 12. Others need to buy a ticket.",
     "Who can enter the museum for free?", ["Children under 12.", "Adults.", "Teachers.", "Everyone."], "Children under 12.", "原文 free for children under 12。"),
    ("Summer in Shanghai is hot and wet. Many people go to the beach to cool down.",
     "What is summer like in Shanghai?", ["Hot and wet.", "Cold and dry.", "Warm and windy.", "Cool and sunny."], "Hot and wet.", "原文 hot and wet。"),
    ("The baby panda was born in the zoo. Visitors come to see it every day.",
     "Where was the baby panda born?", ["In the zoo.", "In the forest.", "At home.", "In a park."], "In the zoo.", "原文 born in the zoo。"),
    ("Reading in poor light is bad for your eyes. You should turn on a lamp.",
     "Why is reading in poor light bad?", ["It hurts your eyes.", "It makes you sleepy.", "It is boring.", "It wastes time."], "It hurts your eyes.", "原文 bad for your eyes。"),
    ("The train runs faster than the bus. The plane is the fastest of all.",
     "Which is the fastest?", ["The plane.", "The train.", "The bus.", "The car."], "The plane.", "原文 the fastest of all。"),
    ("Lisa helps her mother cook dinner. She can wash the vegetables.",
     "What can Lisa do?", ["Wash the vegetables.", "Drive a car.", "Fix the TV.", "Paint the wall."], "Wash the vegetables.", "原文 can wash the vegetables。"),
    ("The moon looks bright at night because it reflects the sun's light.",
     "Why does the moon look bright?", ["It reflects the sun's light.", "It makes its own light.", "It is on fire.", "It is made of gold."], "It reflects the sun's light.", "原文 reflects the sun's light。"),
    ("We planted a tree in the garden. We water it every day and hope it grows.",
     "What do we do to the tree?", ["Water it every day.", "Cut it down.", "Leave it alone.", "Paint it."], "Water it every day.", "原文 water it every day。"),
    ("The Internet helps us find information quickly. But we must be careful online.",
     "What helps us find information quickly?", ["The Internet.", "The radio.", "The TV.", "The newspaper."], "The Internet.", "原文 helps us find information quickly。"),
    ("Ben studied for the test for two weeks. He got a high score at last.",
     "Why did Ben get a high score?", ["He studied for two weeks.", "He guessed.", "He copied.", "He slept."], "He studied for two weeks.", "原文 studied for two weeks。"),
    ("The giraffe has a very long neck. It can eat leaves from tall trees.",
     "Why is the giraffe's long neck useful?", ["It eats leaves from tall trees.", "It runs fast.", "It swims well.", "It flies high."], "It eats leaves from tall trees.", "原文 eat leaves from tall trees。"),
    ("In autumn, leaves turn yellow and red. Then they fall from the trees.",
     "What happens to leaves in autumn?", ["They turn yellow and red.", "They turn green.", "They stay the same.", "They grow bigger."], "They turn yellow and red.", "原文 turn yellow and red。"),
    ("The doctor told him to drink more water and have a good rest.",
     "What did the doctor say?", ["Drink more water and rest.", "Eat more sugar.", "Run every day.", "Stay up late."], "Drink more water and rest.", "原文 drink more water and have a good rest。"),
    ("A year has four seasons: spring, summer, autumn and winter.",
     "How many seasons are there in a year?", ["Four.", "Two.", "Three.", "Six."], "Four.", "原文 four seasons。"),
    ("The little dog followed the boy all the way home. They became good friends.",
     "What did the dog do?", ["Followed the boy home.", "Ran away.", "Bit the boy.", "Slept all day."], "Followed the boy home.", "原文 followed the boy home。"),
    ("We should turn off the lights when we leave the room to save electricity.",
     "Why turn off the lights?", ["To save electricity.", "To make it dark.", "To sleep.", "To watch TV."], "To save electricity.", "原文 to save electricity。"),
    ("The cake was made by my mother. It tastes sweet and soft.",
     "How does the cake taste?", ["Sweet and soft.", "Salty and hard.", "Sour and cold.", "Bitter and dry."], "Sweet and soft.", "原文 tastes sweet and soft。"),
    ("Fish breathe through gills, not lungs. That is why they live in water.",
     "How do fish breathe?", ["Through gills.", "Through lungs.", "Through noses.", "Through skin."], "Through gills.", "原文 breathe through gills。"),
    ("The postman delivers letters to our house every day except Sunday.",
     "When does the postman NOT come?", ["On Sunday.", "On Monday.", "On Saturday.", "On Friday."], "On Sunday.", "原文 except Sunday。"),
    ("The kite flew high in the blue sky. The children laughed happily.",
     "How did the children feel?", ["Happy.", "Sad.", "Angry.", "Tired."], "Happy.", "原文 laughed happily。"),
    ("Recycling paper and plastic helps protect the environment.",
     "What helps protect the environment?", ["Recycling paper and plastic.", "Burning trash.", "Cutting trees.", "Wasting water."], "Recycling paper and plastic.", "原文 Recycling... helps protect。"),
    ("The old clock on the wall has worked for fifty years. It is still correct.",
     "How long has the clock worked?", ["Fifty years.", "Five years.", "Ten years.", "One year."], "Fifty years.", "原文 for fifty years。"),
    ("Tom's family went camping last weekend. They cooked food over a fire.",
     "How did they cook the food?", ["Over a fire.", "In a microwave.", "On a stove.", "In an oven."], "Over a fire.", "原文 cooked food over a fire。"),
    ("The computer is a useful tool for both study and work.",
     "What is the computer?", ["A useful tool.", "A toy only.", "A book.", "A game only."], "A useful tool.", "原文 a useful tool。"),
    ("Snow White is a famous story. It teaches us to be kind to others.",
     "What does Snow White teach us?", ["To be kind to others.", "To be rich.", "To be lazy.", "To be angry."], "To be kind to others.", "原文 teaches us to be kind。"),
    ("The football match started at 3 p.m. and ended two hours later.",
     "When did the match end?", ["At 5 p.m.", "At 4 p.m.", "At 6 p.m.", "At 3 p.m."], "At 5 p.m.", "3 p.m. + two hours = 5 p.m。"),
    ("Birds build nests in trees to lay their eggs and raise babies.",
     "Why do birds build nests?", ["To lay eggs and raise babies.", "To sleep all winter.", "To fly higher.", "To hide from the sun."], "To lay eggs and raise babies.", "原文 to lay eggs and raise babies。"),
    ("The river was frozen in winter. Children went skating on it.",
     "What did children do on the frozen river?", ["Went skating.", "Went swimming.", "Went fishing.", "Went boating."], "Went skating.", "原文 went skating。"),
    ("We should wash our hands before meals to keep healthy.",
     "When should we wash hands?", ["Before meals.", "After sleeping.", "During class.", "While watching TV."], "Before meals.", "原文 before meals。"),
    ("The sun rises in the east and sets in the west every day.",
     "Where does the sun set?", ["In the west.", "In the east.", "In the north.", "In the south."], "In the west.", "原文 sets in the west。"),
    ("The little girl saved her pocket money to buy a gift for her mother.",
     "What did the girl save money for?", ["A gift for her mother.", "A toy for herself.", "Some candy.", "A book for school."], "A gift for her mother.", "原文 buy a gift for her mother。"),
    ("A good friend listens to you and shares your joy and sadness.",
     "What does a good friend do?", ["Listens and shares feelings.", "Only plays games.", "Never talks.", "Always argues."], "Listens and shares feelings.", "原文 listens and shares。"),
]
bank["english"]["阅读问答（开放题）"] = [
    {"q": f"{p}\n问：{qu}", "options": opts, "answer": ans, "explain": exp}
    for (p, qu, opts, ans, exp) in reading
]


# ---------------- 数学：符号管理（负号奇偶/去括号分配） ----------------
def gen_sign():
    qs = []
    for _ in range(60):
        t = random.choice(["neg", "par", "pow_pos", "pow_neg", "sub"])
        if t == "neg":
            n = random.randint(2, 15)
            ans = str(n)
            wrong = [str(-n), str(2 * n), str(n - 1)]
        elif t == "par":
            a, b = random.randint(2, 9), random.randint(2, 9)
            ans = str(b - a)  # -(a-b) = b-a
            wrong = [str(a - b), str(-(a + b)), str(a + b)]
        elif t == "pow_pos":
            n = random.randint(2, 9)
            ans = str(n * n)
            wrong = [f"-{n*n}", str(n), f"-{n}"]
        elif t == "pow_neg":
            n = random.randint(2, 9)
            ans = f"-{n*n}"
            wrong = [str(n * n), f"-{n}", str(n)]
        else:  # sub
            n = random.randint(2, 9)
            ans = str(n)  # -x where x=-n
            wrong = [f"-{n}", str(-n), str(2 * n)]
        opts = [ans] + [w for w in wrong if w != ans]
        # 补足到 4 个且不重复
        extra = 0
        while len(opts) < 4:
            extra += 1
            cand = str(int(ans) + extra) if ans.lstrip('-').isdigit() else f"x{extra}"
            if cand not in opts:
                opts.append(cand)
        random.shuffle(opts)
        qs.append({"q": _sign_q(t, n if t != 'par' else a, b if t == 'par' else None),
                   "options": opts, "answer": ans,
                   "explain": "负号与括号：先定符号再算数；奇次幂保留负号、偶次幂变正。"})
    return qs


def _sign_q(t, n, b):
    if t == "neg":
        return f"化简：-( -{n} ) = ?"
    if t == "par":
        return f"化简：-( {n} - {b} ) = ?"
    if t == "pow_pos":
        return f"计算：(-{n})^2 = ?"
    if t == "pow_neg":
        return f"计算：-{n}^2 = ?（注意：先平方再加负号）"
    return f"当 x = -{n} 时，求 -x = ?"


bank["math"]["符号管理（负号奇偶/去括号分配）"] = gen_sign()


# ---------------- 数学：指数法则混淆 ----------------
def gen_exp():
    qs = []
    for _ in range(60):
        t = random.choice(["mul", "pow", "pro", "zero", "neg", "div"])
        m, n = random.randint(2, 5), random.randint(2, 5)
        if t == "mul":
            ans = f"x^{m+n}"
            opts = [ans, f"x^{m*n}", f"x^{m-n}", f"x^{m}+x^{n}"]
            q = f"化简：x^{m} · x^{n} = ?"
        elif t == "pow":
            ans = f"x^{m*n}"
            opts = [ans, f"x^{m+n}", f"x^{m//n if n else 1}", f"x^{m}+x^{n}"]
            q = f"化简：(x^{m})^{n} = ?"
        elif t == "pro":
            ans = f"x^{n}y^{n}"
            opts = [ans, f"x^{n}+y^{n}", f"x^{n}y", f"xy^{n}"]
            q = f"化简：(xy)^{n} = ?"
        elif t == "zero":
            base = random.choice([2, 3, 5, 7, 10])
            ans = "1"
            opts = ["1", "0", str(base), f"{base}0"]
            q = f"计算：{base}^0 = ?"
        elif t == "neg":
            ans = f"1/2^{n}"
            opts = [ans, f"2^{n}", f"-2^{n}", f"1/{n}"]
            q = f"计算：2^(-{n}) = ?"
        else:
            ans = f"x^{m-n}" if m > n else f"1/x^{n-m}"
            opts = [ans, f"x^{m+n}", f"x^{m//n if n else 1}", f"x^{1}"]
            q = f"化简：x^{m} ÷ x^{n} = ?"
        opts = list(dict.fromkeys(opts))
        random.shuffle(opts)
        qs.append({"q": q, "options": opts, "answer": ans,
                   "explain": "同底数幂相乘指数相加；幂的乘方指数相乘；(ab)^n=a^n b^n；a^0=1；a^(-n)=1/a^n。"})
    return qs


bank["math"]["指数法则混淆"] = gen_exp()


# ---------------- 数学：分配律漏项 ----------------
def gen_dist():
    qs = []
    for _ in range(60):
        a = random.randint(2, 9)
        c = random.randint(1, 9)
        if random.random() < 0.5:
            ans = f"{a}x+{a*c}"
            wrong = [f"{a}x+{c}", f"{a}x{c}", f"{a+c}x"]
            q = f"化简：{a}(x+{c}) = ?"
        else:
            ans = f"-{a}x+{a*c}"
            wrong = [f"-{a}x-{a*c}", f"{a}x-{a*c}", f"-{a}x-{c}"]
            q = f"化简：-{a}(x-{c}) = ?"
        opts = [ans] + [w for w in wrong if w != ans]
        while len(opts) < 4:
            opts.append(f"{a}x+{c+len(opts)}")
        opts = list(dict.fromkeys(opts))
        random.shuffle(opts)
        qs.append({"q": q, "options": opts, "answer": ans,
                   "explain": "分配律 a(b+c)=ab+ac，括号前是负号时每一项都要变号。"})
    return qs


bank["math"]["分配律漏项"] = gen_dist()


# ---------------- 数学：完全平方变形与逆用 ----------------
def gen_square():
    qs = []
    for _ in range(60):
        a = random.randint(2, 9)
        if random.random() < 0.4:
            ans = f"(x-{a})(x+{a})"
            wrong = [f"(x-{a})^2", f"x(x-{a})", f"(x+{a})^2"]
            q = f"因式分解：x^2 - {a*a} = ?"
        elif random.random() < 0.7:
            ans = f"x^2+{2*a}x+{a*a}"
            wrong = [f"x^2+{a}x+{a*a}", f"x^2+{a*a}", f"x^2+{a}x+{a}"]
            q = f"展开：(x+{a})^2 = ?"
        else:
            ans = f"x^2-{2*a}x+{a*a}"
            wrong = [f"x^2-{a}x+{a*a}", f"x^2-{a*a}", f"x^2-{a}x+{a}"]
            q = f"展开：(x-{a})^2 = ?"
        opts = [ans] + [w for w in wrong if w != ans]
        while len(opts) < 4:
            opts.append(f"x^2+{a+len(opts)}x+{a*a}")
        opts = list(dict.fromkeys(opts))
        random.shuffle(opts)
        qs.append({"q": q, "options": opts, "answer": ans,
                   "explain": "(a±b)^2=a^2±2ab+b^2；a^2-b^2=(a-b)(a+b)。"})
    return qs


bank["math"]["完全平方变形与逆用"] = gen_square()


# ---------------- 数学：多项式除以单项式 ----------------
def gen_divpoly():
    qs = []
    for _ in range(60):
        c = random.choice([2, 3])
        a = c * random.randint(2, 6)
        b = c * random.randint(1, 5)
        if random.random() < 0.5:
            ans = f"{a//c}x+{b//c}"
            wrong = [f"{a//c}x+{b}x", f"{a}x+{b//c}", f"{a//c}x{b//c}"]
            q = f"化简：({a}x^2+{b}x) ÷ {c}x = ?"
        else:
            ans = f"{a//c}x-{b//c}"
            wrong = [f"{a//c}x+{b//c}", f"{a}x-{b//c}", f"{a//c}x-{b}x"]
            q = f"化简：({a}x^2-{b}x) ÷ {c}x = ?"
        opts = [ans] + [w for w in wrong if w != ans]
        while len(opts) < 4:
            opts.append(f"{a//c+len(opts)}x+{b//c}")
        opts = list(dict.fromkeys(opts))
        random.shuffle(opts)
        qs.append({"q": q, "options": opts, "answer": ans,
                   "explain": "多项式除以单项式：每一项分别除，再把商相加。"})
    return qs


bank["math"]["多项式除以单项式"] = gen_divpoly()


# ---------------- 数学：分数系数合并同类项 ----------------
def reduce(num, den):
    g = math.gcd(abs(num), abs(den))
    return num // g, den // g


def gen_frac():
    qs = []
    # 系统生成 60 个互异的分数系数合并题
    bases = [2, 3, 4, 6]
    pairs = []
    for b in bases:
        for d in bases:
            for a in range(1, b + 1):
                for c in range(1, d + 1):
                    pairs.append((a, b, c, d))
    random.shuffle(pairs)
    for (a, b, c, d) in pairs:
        num = a * d + b * c
        den = b * d
        n, dd = reduce(num, den)
        ans = (f"{n}x" if dd == 1 else f"{n}/{dd}x")
        cands = [ans,
                 f"{a+c}/{b*d}x",
                 f"{a+c}/{b}x",
                 f"{num}/{dd+1}x",
                 f"{n+1}/{dd}x",
                 f"{a}/{b}x",
                 f"{c}/{d}x"]
        opts = list(dict.fromkeys([x for x in cands if x != ans]))
        opts = [ans] + opts[:3]
        while len(opts) < 4:
            opts.append(f"{n+len(opts)}/{dd+1}x")
        opts = list(dict.fromkeys(opts))
        random.shuffle(opts)
        qs.append({"q": f"合并同类项：{a}/{b} x + {c}/{d} x = ?",
                   "options": opts, "answer": ans,
                   "explain": "通分后分子相加、分母不变，再约分。"})
        if len(qs) >= 60:
            break
    return qs


bank["math"]["分数系数合并同类项"] = gen_frac()


# ============================================================
# fill 产出型题库（--fill 输出 questionbank_fill.js，本地样例）
# ============================================================

# 动→名 fill 样例（真实句 + 派生名词）
V2N_FILL = [
    ("act", "action", "We should take ______ to protect the environment."),
    ("decide", "decision", "It is not easy to make a ______."),
    ("develop", "development", "The ______ of science changes our life."),
    ("compete", "competition", "She won first prize in the ______."),
    ("discuss", "discussion", "We had a hot ______ about the film."),
    ("educate", "education", "______ is important for everyone."),
    ("improve", "improvement", "There is much ______ in his writing."),
    ("achieve", "achievement", "Winning the match was a great ______."),
    ("invite", "invitation", "Thank you for your ______."),
    ("protect", "protection", "The forest needs our ______."),
    ("suggest", "suggestion", "Could you give me some ______?"),
    ("celebrate", "celebration", "The whole city was in ______ that night."),
    ("invent", "invention", "The ______ of the wheel changed the world."),
    ("attract", "attraction", "The Great Wall is a great ______."),
    ("collect", "collection", "He has a big ______ of stamps."),
    ("prepare", "preparation", "We need good ______ for the exam."),
    ("perform", "performance", "Her ______ on the stage was wonderful."),
    ("express", "expression", "There was a happy ______ on his face."),
    ("explain", "explanation", "Please give me an ______."),
    ("introduce", "introduction", "Let me give a brief ______ of our school."),
    ("agree", "agreement", "They finally reached an ______ after the talk."),
    ("believe", "belief", "I have great ______ in you."),
    ("build", "building", "The new ______ is very tall."),
    ("choose", "choice", "It is hard to make a ______ between them."),
    ("win", "winner", "She is the ______ of the game."),
    ("die", "death", "The ______ of the old man saddened us."),
    ("act", "action", "We should take ______ to save water."),
    ("speak", "speech", "Her ______ was clear and loud."),
    ("grow", "growth", "The ______ of the city is very fast."),
    ("know", "knowledge", "______ is power."),
    ("teach", "teaching", "He loves ______ very much."),
    ("learn", "learning", "______ is a lifelong task."),
    ("visit", "visitor", "The ______ brought us many gifts."),
]

# 形→副 / 其他 fill 样例（point=词性转换·形→副/其他；题库暂未建该 point，扩题时同步建）
A2ADV_FILL = [
    ("exact", "exactly", "Tell me ______ what happened."),
    ("confident", "confidently", "She answered the question ______."),
    ("official", "officially", "The news was ______ announced."),
    ("final", "finally", "______, we finished the work."),
    ("simple", "simply", "It is ______ a matter of time."),
    ("quick", "quickly", "He finished his homework ______."),
    ("careful", "carefully", "Read the question ______ before answering."),
    ("happy", "happily", "The children played ______ in the park."),
    ("lucky", "luckily", "______, no one was hurt in the accident."),
    ("angry", "angrily", "He looked at me ______."),
    ("noisy", "noisily", "The boys talked ______ in the hall."),
    ("slow", "slowly", "The old man walked ______."),
    ("good", "well", "She can speak English very ______."),
    ("hard", "hard", "Work ______ and you will succeed."),
    ("easy", "easily", "He can solve the problem ______."),
    ("bad", "badly", "He did ______ in the final exam."),
    ("late", "late", "He came ______ to school this morning."),
    ("early", "early", "She gets up ______ every day."),
    ("fast", "fast", "He runs ______ and wins the race."),
    ("wide", "widely", "The news spread ______ across the city."),
    ("deep", "deeply", "He was ______ moved by the story."),
    ("high", "highly", "We ______ value your suggestion."),
    ("strong", "strongly", "I ______ advise you to see a doctor."),
    ("real", "really", "It is ______ cold outside today."),
    ("busy", "busily", "The bees work ______ among the flowers."),
    ("quiet", "quietly", "Please speak ______ in the library."),
    ("brave", "bravely", "The young soldier fought ______."),
    ("soft", "softly", "She spoke ______ to the baby."),
    ("sad", "sadly", "He looked at the broken toy ______."),
    ("polite", "politely", "You should ask for help ______."),
]

# 动→名选择题仍用上方 v2n（60 题）；V2N_FILL 仅用于 fill 产出型（见 build_fill_bank）。


def gen_math_fill():
    """数学 fill：写出结果，每考点 30 题。answer 用 | 分隔等价形式。"""
    qs = []
    # 符号管理（30）
    for _ in range(30):
        a = random.randint(1, 9)
        b = random.randint(a + 1, a + 12)
        qs.append({"q": f"化简：-( {a} - {b} ) = ?",
                   "answer": str(b - a),
                   "explain": "括号前是负号，去括号后每一项变号：-(a-b)=b-a。",
                   "type": "fill", "match": "exact"})
    # 指数法则（30 = 15 组 x 2）
    for _ in range(15):
        m, n = random.randint(2, 6), random.randint(2, 5)
        qs.append({"q": f"化简：x^{m} · x^{n} = ?",
                   "answer": f"x^{m+n}",
                   "explain": "同底数幂相乘，指数相加。",
                   "type": "fill", "match": "exact"})
        qs.append({"q": f"化简：(x^{m})^{n} = ?",
                   "answer": f"x^{m*n}",
                   "explain": "幂的乘方，指数相乘。",
                   "type": "fill", "match": "exact"})
    # 分配律（30）
    for _ in range(30):
        a, c = random.randint(2, 9), random.randint(1, 9)
        qs.append({"q": f"化简：{a}(x + {c}) = ?",
                   "answer": f"{a}x+{a*c}|{a}x + {a*c}",
                   "explain": f"分配律：{a}(x+{c})={a}x+{a*c}，每项都要乘。",
                   "type": "fill", "match": "exact"})
    # 完全平方（30）
    for _ in range(30):
        n = random.randint(1, 10)
        qs.append({"q": f"计算：(x + {n})^2 = ?",
                   "answer": f"x^2+{2*n}x+{n*n}|x^2 + {2*n}x + {n*n}",
                   "explain": f"(x±a)^2=x^2±2ax+a^2：中间项=2×{n}x，常数项={n*n}。",
                   "type": "fill", "match": "exact"})
    # 平方差（30）
    for _ in range(30):
        a = random.randint(2, 11)
        qs.append({"q": f"计算：(x + {a})(x - {a}) = ?",
                   "answer": f"x^2-{a*a}|x^2 - {a*a}",
                   "explain": f"平方差公式：(x+a)(x-a)=x^2-a^2={a*a}。",
                   "type": "fill", "match": "exact"})
    # 因式分解·平方差（30）
    for _ in range(30):
        a = random.randint(2, 12)
        qs.append({"q": f"因式分解：x^2 - {a*a} = ?",
                   "answer": f"(x-{a})(x+{a})|(x+{a})(x-{a})",
                   "explain": f"x^2-{a*a}=(x-{a})(x+{a})。",
                   "type": "fill", "match": "exact"})
    return qs


def build_fill_bank():
    """组装 fill 题库：英语词性转换（名→形/动→名/形→副）+ 数学写出结果，每考点 ≥30。"""
    mq = gen_math_fill()   # 顺序: 符号30 / 指数30 / 分配30 / 完全平方30 / 平方差30 / 因式分解30
    fb = {"english": {}, "math": {}}
    fb["english"]["词性转换·名→形"] = build_fill_words(N2A_FILL)         # 55
    fb["english"]["词性转换·动→名"] = build_fill_words(V2N_FILL)         # 33
    fb["english"]["词性转换·形→副/其他"] = build_fill_words(A2ADV_FILL)    # 30
    fb["math"]["符号管理（负号奇偶/去括号分配）"] = mq[0:30]
    fb["math"]["指数法则混淆"] = mq[30:60]
    fb["math"]["分配律漏项"] = mq[60:90]
    fb["math"]["完全平方变形与逆用"] = mq[90:120]
    fb["math"]["平方差公式"] = mq[120:150]
    fb["math"]["因式分解-平方差"] = mq[150:180]
    return fb


# ---------------- 写出 questionbank.js / questionbank_fill.js ----------------
def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fill", action="store_true",
                    help="额外输出 questionbank_fill.js（产出型 fill 样例，本地不推云端）")
    args = ap.parse_args()

    # 校验数量
    report = []
    for subj, pts in bank.items():
        for point, qs in pts.items():
            report.append((subj, point, len(qs)))
            if len(qs) < 50:
                print(f"[WARN] 不足 50: {subj} / {point} = {len(qs)}")
    total = sum(r[2] for r in report)
    print("题库统计：")
    for subj, point, n in report:
        print(f"  {subj:8s} {point:24s} {n}")
    print(f"总计 {len(report)} 个考点，{total} 题")

    out = "// 自动生成，请勿手改；由 pipeline/build_questionbank.py 生成\n"
    out += "// 结构: questionbank[subjectKey][point] = [{q, options, answer, explain}]\n"
    out += "module.exports = " + json.dumps(bank, ensure_ascii=False, indent=1) + ";\n"
    with open("questionbank.js", "w", encoding="utf-8") as f:
        f.write(out)
    print("已写出 questionbank.js")

    if args.fill:
        fb = build_fill_bank()
        fout = "// 产出型 fill 题库（样例，本地不推云端）——契约见 Obsidian 17-题库题型扩展方案-给甲\n"
        fout += "// 结构: questionbankFill[subject][point] = [{q, answer(可含 | 等价), explain, type:'fill', match:'exact'}]\n"
        fout += "// 渲染/判分由甲侧 tasks 页答题模式实现；当前 App 选择题不受影响。\n"
        fout += "module.exports = " + json.dumps(fb, ensure_ascii=False, indent=1) + ";\n"
        with open("questionbank_fill.js", "w", encoding="utf-8") as f:
            f.write(fout)
        fr = [(s, p, len(q)) for s, pts in fb.items() for p, q in pts.items()]
        print("fill 样例统计：")
        for s, p, n in fr:
            print(f"  {s:8s} {p:24s} {n}")
        print(f"fill 总计 {sum(x[2] for x in fr)} 题 → questionbank_fill.js")


if __name__ == "__main__":
    main()
