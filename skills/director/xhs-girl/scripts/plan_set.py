"""Draw a varied shot plan for one xhs-girl photo set.

Run from the skill root:
  python3 scripts/plan_set.py --count 4
  python3 scripts/plan_set.py --count 3 --mode mixed
  python3 scripts/plan_set.py --count 4 --scene "便利店门口" --type 怼脸自拍

--focus face (default) favours close-ups; --focus outfit favours mirror, seated and full-body.
post  (default): one post, same makeup/hair/outfit/finish, every shot a different picture type.
mixed: independent images, each with its own look, scene and finish.
The draw is random by design; pass --seed only to reproduce a plan.
"""
import argparse
import datetime
import random

# name: (weight, distance, refs, fixed scenes or None)
SHOT_TYPES = {
    "怼脸自拍": (3, "近", "R06 R17 R25", None),
    "高位俯拍抬眼": (3, "近", "R03 R22 R28", None),
    "手势贴脸": (3, "近", "R09 R11 R12", None),
    "遮半脸": (3, "近", "R10 R19", None),
    "道具贴脸": (3, "近", "R21 R30", None),
    "隔桌对拍": (2, "中", "R23 R26", ["咖啡店靠窗小桌", "面包店外摆桌", "火锅店卡座", "甜品店吧台", "家里飘窗小桌"]),
    "镜前自拍": (2, "中", "R15", ["卧室全身镜", "电梯镜面", "商场试衣间", "玄关穿衣镜"]),
    "坐蹲半身": (2, "中", "R01 R07 R16 R20", None),
    "直闪夜拍": (2, "中", "R13 R29", ["便利店门口", "车内副驾", "小区楼下路灯", "夜市小摊", "霓虹老街"]),
    "暗调光影": (2, "中", "R08", ["暖光格子窗前", "傍晚卧室百叶窗光斑", "酒吧暖灯角落", "老式木窗前"]),
    "躺拍俯视": (2, "中", "R05", ["床上毛毯", "公园草地", "毛绒地毯", "落叶堆"]),
    "风景人像": (1, "中", "R02 R14 R18 R24", ["海边防波堤", "山顶观景台", "秋林小路", "跨海大桥边", "天台黄昏"]),
    "全身街拍": (1, "远", "R24 R29", None),
}

VIBES = {
    "韩系甜妹": "面中大面积粉色腮红、亮片卧蚕、浅棕美瞳、水光嘟嘟唇",
    "纯欲": "鼻尖和面中醉酒腮红、根根分明下睫毛、微红眼尾、透明水润唇",
    "冷感": "低饱和杏色腮红、上挑细眼线、浅灰美瞳、哑光豆沙唇",
    "甜酷": "斜飞眼线、银色眼头高光、裸粉唇、脸侧小痣",
    "辣妹": "深棕眼影晕染、浓密假睫毛、鼻梁高光、裸棕唇",
    "地雷系": "红色下眼尾、泪痣、粉红团状腮红、樱桃唇",
    "港风复古": "眉峰利落、正红唇、暖棕眼影、轻微油光肌",
    "清透伪素颜": "薄底妆露出雀斑、淡粉腮红、睫毛根部清楚、粉嫩唇",
}
HAIR_COLOR = ["黑长直", "奶茶棕", "米金浅发", "红棕", "樱花粉", "冷茶棕", "黑发里藏一缕浅色挑染"]
HAIR_CUT = ["空气刘海", "厚齐刘海", "八字刘海", "公主切", "鬓角碎发很多的中分", "侧分大刘海"]
HAIR_STYLE = ["大波浪", "蓬松羊毛卷", "内扣长发", "高马尾", "低丸子头", "双麻花辫", "半扎公主头"]
NAILS = ["裸粉猫眼长甲", "黑色短甲", "奶白钻饰长甲", "酒红短甲", "粉色法式甲", "银色镜面甲"]

SEASON = {
    "winter": {
        "head": ["猫耳毛线帽", "毛绒护耳雷锋帽", "毛绒耳罩", "粗针毛线帽", "贝雷帽", "一排彩色小发夹", "毛绒发箍", "无头饰"],
        "outfit": [
            "敞开的白色短款羽绒服配黑色小吊带和灰色百褶短裙",
            "毛领短款皮衣配白色蕾丝打底和格纹迷你裙、黑色过膝袜",
            "奶白长毛绒外套配牛仔热裤和灰色堆堆袜",
            "蓬松马海毛开衫半敞配粉色抹胸和低腰牛仔裤",
            "黑色露肩修身上衣配腰链和灰色低腰短裙",
            "戴上兜帽的毛领连帽外套配短裙和长筒腿袜",
            "仿皮草短外套配黑色吊带和低腰直筒牛仔裤",
            "粉色绒面短外套配白色泡泡袖衬衫和蓬蓬裙",
            "红白条纹厚毛衣配牛仔短裙和乐福鞋",
            "黑色长大衣配格纹围巾和短裙、乐福鞋",
            "机车皮夹克配露脐紧身打底和工装短裤",
            "灰色宽松连帽卫衣配白色短裙和腿袜",
        ],
        "props": ["毛绒玩偶挂件", "热可可纸杯", "烤红薯", "糖葫芦", "草莓蛋糕", "暖手宝", "拍立得", "长毛绒围巾一角", "可颂面包", "奶茶吸管"],
        "scenes": ["便利店门口", "车内副驾", "卧室飘窗", "冬日海边", "公园枯草地", "地铁车厢", "抓娃娃机前", "书店书架间", "面包店门口", "老街石板路", "游乐园旋转木马旁", "天台黄昏"],
    },
    "spring": {
        "head": ["蝴蝶结发带", "抓夹", "一排小发夹", "棒球帽", "渔夫帽", "无头饰"],
        "outfit": [
            "短款针织开衫配吊带和碎花迷你裙",
            "白色泡泡袖上衣配牛仔短裙",
            "浅粉色毛衣马甲配衬衫和百褶裙",
            "短款牛仔外套配露脐小背心和低腰长裤",
            "法式方领连衣裙配玛丽珍鞋",
            "运动外套配网球短裙和白袜",
        ],
        "props": ["花束", "冰美式", "草莓", "拍立得", "风筝", "小狗", "冰淇淋"],
        "scenes": ["樱花树下", "花店门口", "校园操场", "公园草地", "河边台阶", "老洋房街角", "咖啡店窗边", "车内副驾"],
    },
    "summer": {
        "head": ["发带", "抓夹", "草编帽", "棒球帽", "耳边别一朵花", "无头饰"],
        "outfit": [
            "细吊带背心配低腰热裤",
            "露背针织吊带配牛仔短裙",
            "碎花抹胸配亚麻短裤",
            "白色小背心配超短百褶裙",
            "比基尼外搭透明防晒衬衫",
            "印花度假吊带裙",
        ],
        "props": ["冰棍", "椰子", "西瓜", "冰美式", "水枪", "贝壳"],
        "scenes": ["海边沙滩", "泳池边", "便利店冰柜前", "夜市小摊", "海岛小路", "车内副驾", "天台黄昏"],
    },
    "autumn": {
        "head": ["贝雷帽", "棒球帽", "毛线帽", "抓夹", "一排小发夹", "无头饰"],
        "outfit": [
            "短款皮衣配白色打底和格纹短裙",
            "灰色针织开衫配蕾丝吊带和低腰牛仔裤",
            "棕色麂皮外套配露脐上衣和短裤",
            "条纹毛衣配百褶短裙和长袜",
            "风衣配黑色紧身上衣和迷你裙",
            "工装马甲配白T和短裙",
        ],
        "props": ["热拿铁", "栗子", "落叶", "面包", "拍立得", "毛绒挂件"],
        "scenes": ["银杏街道", "秋林小路", "面包店门口", "书店", "老街石板路", "车内副驾", "天台黄昏", "公园长椅"],
    },
}

EXPRESSIONS = ["单眼wink", "嘟嘴", "抿嘴笑、眼睛弯起来", "冷脸直视、嘴唇微张", "鼓腮", "歪头睁大眼装无辜",
               "闭眼仰脸", "轻咬下唇", "笑出一点牙", "微微吐舌", "斜眼看镜头", "回眸", "低头垂眼", "惊讶O型嘴", "眯眼笑"]
HANDS = ["手指点在唇边", "比耶贴在脸颊旁", "双手框住眼睛", "托腮", "捂嘴", "手指勾住帽檐往下拉", "撩起一边刘海",
         "捏住一缕头发放到唇边", "手背贴着脸颊", "长袖包住手、双手捧脸", "双手抱膝", "手握发尾", "手指比心贴脸", "双手捂住耳罩或帽子两侧"]
FINISHES = {
    "韩系清透": "冷白皮、低对比、轻柔焦，整体偏粉白干净",
    "暖调胶片": "暖黄偏橙、轻微颗粒、暗部微褪色",
    "直闪": "手机闪光正面直打，脸亮背景暗，高光硬、阴影短",
    "冷灰阴天": "蓝灰调低饱和，皮肤仍白净通透",
    "粉雾滤镜": "粉紫色高光、梦幻柔光、轻微光晕",
    "黑白高反差": "黑白画面，高反差，皮肤通透",
    "黄昏逆光": "逆光发丝金边、暖橙天空、脸部柔和补亮",
    "CCD复古": "CCD相机感，暗部偏绿、高光轻微溢出、细颗粒",
}

# finishes tied to a light situation; never used as the shared finish of a whole set
SITUATIONAL = {"直闪", "黄昏逆光"}

# picture types whose look only works with one finish
TYPE_FINISH = {"直闪夜拍": "直闪", "暗调光影": "暖调胶片", "风景人像": "黄昏逆光"}


def season_for(month):
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(month, "autumn" if month in (9, 10) else "winter")


OUTFIT_BOOST = {"全身街拍": 4, "镜前自拍": 4, "坐蹲半身": 4, "风景人像": 2}


def weighted_pick(rng, pool, focus):
    w = [OUTFIT_BOOST.get(n, SHOT_TYPES[n][0]) if focus == "outfit" else SHOT_TYPES[n][0] for n in pool]
    return rng.choices(pool, weights=w)[0]


def draw_types(rng, count, forced, focus):
    """face: at least half close-up, at most one full-body.
    outfit: at least one close-up, full-body and mid shots weighted up.
    No type repeats; the cover (first shot) is drawn first."""
    names = [n for n in forced if n in SHOT_TYPES][:count]
    quota = (count + 1) // 2 if focus == "face" else 1
    near_needed = quota - sum(SHOT_TYPES[n][1] == "近" for n in names)
    max_far = 1 if focus == "face" else 2
    while len(names) < count:
        used = set(names)
        if near_needed > 0:
            pool = [n for n in SHOT_TYPES if n not in used and SHOT_TYPES[n][1] == "近"]
        else:
            far = sum(SHOT_TYPES[n][1] == "远" for n in names)
            pool = [n for n in SHOT_TYPES if n not in used and not (far >= max_far and SHOT_TYPES[n][1] == "远")]
        if not pool:
            pool = [n for n in SHOT_TYPES if n not in used]
            if not pool:
                break
        if focus == "outfit" and not names and near_needed > 0:
            pool = [n for n in SHOT_TYPES if SHOT_TYPES[n][1] != "近"]
        # a set of 3+ all in close-up reads as one repeated picture: keep one mid/far slot
        if count >= 3 and len(names) == count - 1 and all(SHOT_TYPES[n][1] == "近" for n in names):
            pool = [n for n in SHOT_TYPES if n not in used and SHOT_TYPES[n][1] != "近"] or pool
        pick = weighted_pick(rng, pool, focus)
        names.append(pick)
        if SHOT_TYPES[pick][1] == "近":
            near_needed -= 1
    if not forced:
        rest = names[1:]
        rng.shuffle(rest)
        names = names[:1] + rest
    return names


def draw_look(rng, season):
    vibe = rng.choice(list(VIBES))
    s = SEASON[season]
    return {
        "气质": vibe,
        "妆容": VIBES[vibe],
        "发型": f"{rng.choice(HAIR_COLOR)}、{rng.choice(HAIR_CUT)}、{rng.choice(HAIR_STYLE)}",
        "头饰": rng.choice(s["head"]),
        "穿搭": rng.choice(s["outfit"]),
        "美甲": rng.choice(NAILS),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--mode", choices=["post", "mixed"], default="post")
    ap.add_argument("--focus", choices=["face", "outfit"], default="face",
                    help="face: 颜值氛围（默认）；outfit: 穿搭身材")
    ap.add_argument("--month", type=int, default=datetime.date.today().month)
    ap.add_argument("--type", action="append", default=[], help="force a picture type, repeatable")
    ap.add_argument("--scene", help="user-given location for the whole set")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    season = season_for(a.month)
    s = SEASON[season]
    types = draw_types(rng, a.count, a.type, a.focus)
    look = draw_look(rng, season)
    finish = rng.choice([f for f in FINISHES if f not in SITUATIONAL])
    base_scene = a.scene or rng.choice(s["scenes"])
    # post mode: two nearby spots in the same outing, alternated, so close-ups don't share one backdrop
    alt_scene = a.scene or rng.choice([x for x in s["scenes"] if x != base_scene])
    exprs = rng.sample(EXPRESSIONS, len(types))
    hands = rng.sample(HANDS, len(types))
    props = rng.sample(s["props"], len(types))

    print(f"# 抽签方案（{season}，{a.mode}，{a.focus}，{len(types)} 张）\n")
    print("用户已指定的人物、单品、地点或风格替换对应项；其余照用，不自行重抽。\n")
    if a.mode == "post":
        print("## 全组共用造型\n")
        for k, v in look.items():
            print(f"- {k}：{v}")
        print(f"- 后期：{finish}（{FINISHES[finish]}）")
        print(f"- 场景：{base_scene}；{alt_scene}（同一次出门的两个地点，各张交替）\n")
    for i, t in enumerate(types, 1):
        w, dist, refs, fixed = SHOT_TYPES[t]
        if a.mode == "mixed":
            look = draw_look(rng, season)
            finish = rng.choice([f for f in FINISHES if f not in SITUATIONAL])
            base_scene = a.scene or rng.choice(s["scenes"])
        here = base_scene if (a.mode == "mixed" or i % 2) else alt_scene
        scene = rng.choice(fixed) if (fixed and not a.scene) else here
        fin = TYPE_FINISH.get(t, finish)
        print(f"## 第 {i} 张 · {t}（{dist}景，参考 {refs}）\n")
        if a.mode == "mixed":
            for k, v in look.items():
                print(f"- {k}：{v}")
        print(f"- 场景：{scene}")
        print(f"- 表情：{exprs[i - 1]}（与画面类型冲突时改用该类型自带的视线）")
        print(f"- 手势：{hands[i - 1]}（与画面类型冲突时改用该类型自带的手部动作）")
        print(f"- 道具：{props[i - 1]}（画面里放不下就省略）")
        print(f"- 后期：{fin}（{FINISHES[fin]}）\n")


if __name__ == "__main__":
    main()
