"""Draw a varied shot plan for one xhs-girl photo set.

Run from the skill root:
  python3 scripts/plan_set.py --look-only            # 只抽造型（出造型板时）
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
        "props": ["毛绒玩偶挂件", "热可可纸杯", "烤红薯", "糖葫芦", "草莓蛋糕", "暖手宝", "拍立得", "长毛绒围巾一角", "可颂面包", "奶茶吸管"],
        "scenes": ["便利店门口", "车内副驾", "卧室飘窗", "冬日海边", "公园枯草地", "地铁车厢", "抓娃娃机前", "书店书架间", "面包店门口", "老街石板路", "游乐园旋转木马旁", "天台黄昏"],
    },
    "spring": {
        "head": ["蝴蝶结发带", "抓夹", "一排小发夹", "棒球帽", "渔夫帽", "无头饰"],
        "props": ["花束", "冰美式", "草莓", "拍立得", "风筝", "小狗", "冰淇淋"],
        "scenes": ["樱花树下", "花店门口", "校园操场", "公园草地", "河边台阶", "老洋房街角", "咖啡店窗边", "车内副驾"],
    },
    "summer": {
        "head": ["发带", "抓夹", "草编帽", "棒球帽", "耳边别一朵花", "无头饰"],
        "props": ["冰棍", "椰子", "西瓜", "冰美式", "水枪", "贝壳"],
        "scenes": ["海边沙滩", "泳池边", "便利店冰柜前", "夜市小摊", "海岛小路", "车内副驾", "天台黄昏"],
    },
    "autumn": {
        "head": ["贝雷帽", "棒球帽", "毛线帽", "抓夹", "一排小发夹", "无头饰"],
        "props": ["热拿铁", "栗子", "落叶", "面包", "拍立得", "毛绒挂件"],
        "scenes": ["银杏街道", "秋林小路", "面包店门口", "书店", "老街石板路", "车内副驾", "天台黄昏", "公园长椅"],
    },
}


# 造型按部件组合抽取，不存整套搭配：整套示例会被模型照抄，组合才有变化。
DIRECTIONS = {
    "美式辣妹": "黑、牛仔蓝、银",
    "韩系甜辣": "粉、白、黑",
    "Y2K 千禧": "亮银、浅蓝、粉紫",
    "芭蕾风": "奶白、浅粉、裸色",
    "学院辣妹": "藏青、红格纹、白",
    "机车酷女": "黑、深灰、银",
    "运动辣妹": "白、亮蓝或草绿、灰",
    "法式慵懒": "奶油白、酒红、棕",
    "地雷甜酷": "黑、粉、白蕾丝",
    "港风复古": "酒红、墨绿、黑",
    "奶油温柔": "奶油黄、燕麦、白",
    "美拉德": "焦糖、咖啡、奶白",
}
TOPS = [  # 主单品，每件都自带露肤点
    "一字肩紧身短上衣（露肩露腰）", "斜肩单袖针织短上衣（露一侧肩）", "交叉绑带露背短上衣",
    "蕾丝边小抹胸", "胸前系蝴蝶结的细吊带短背心", "镂空罗纹露脐长袖", "只扣两颗扣的 V 领短开衫（当上衣穿）",
    "下摆系在胸下的绑结衬衫（露腰）", "方领泡泡袖短上衣（露锁骨和腰）", "挂脖露背针织背心",
    "半拉链运动短上衣（拉到锁骨下）", "缎面细吊带背心", "侧边抽绳露腰长袖", "毛绒边小抹胸",
    "领口带金属环的削肩背心", "网纱长袖叠穿小吊带",
]
BOTTOMS = [  # 下装全部是短款，保证露腿
    "低腰牛仔超短裙", "低腰皮质包臀短裙", "百褶迷你裙", "白色蓬蓬蛋糕短裙", "不对称叠片短裙",
    "牛仔热裤", "低腰工装短裤", "针织包臀短裙", "缎面斜裁迷你裙", "网球短裙", "蕾丝边南瓜短裤",
]
OUTERS = {
    "winter": ["浅灰长毛绒短外套", "奶白短款羽绒服", "毛领短皮衣", "焦糖色毛毛短外套", "格纹毛呢短外套", "粗针短开衫", "仿皮草短外套"],
    "spring": ["短款牛仔外套", "机车皮夹克", "短款针织开衫", "短西装", "运动夹克", "无外套"],
    "summer": ["透明防晒衬衫", "无外套", "无外套", "无外套"],
    "autumn": ["机车皮夹克", "麂皮短外套", "短款针织开衫", "短风衣", "格纹短外套", "无外套"],
}
WEAR = ["敞开穿", "滑到手肘", "披在肩上", "一侧滑落露肩"]
LEGS = {
    "winter": ["灰色堆堆袜", "黑色过膝袜", "蝴蝶结腿袜", "白色长筒袜", "黑色薄丝袜", "光腿"],
    "spring": ["白色短袜", "蕾丝短袜", "光腿", "过膝袜"],
    "summer": ["光腿", "白色短袜"],
    "autumn": ["黑色过膝袜", "灰色堆堆袜", "黑色薄丝袜", "光腿", "白色长筒袜"],
}
SHOES = ["厚底玛丽珍", "乐福鞋", "复古德训鞋", "厚底短靴", "芭蕾平底鞋", "毛绒短靴", "尖头小猫跟", "厚底板鞋"]
ACCESSORIES = ["大圈银耳环", "珍珠耳钉", "choker", "细项链叠戴", "金属腰链", "铆钉皮腰带", "星星发夹",
               "蝴蝶结发夹", "毛绒包挂", "小方包斜挎", "腋下包", "细框眼镜", "手机挂链", "多枚戒指叠戴"]

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


def draw_look(rng, season, direction=None):
    vibe = rng.choice(list(VIBES))
    d = direction if direction in DIRECTIONS else rng.choice(list(DIRECTIONS))
    s = SEASON[season]
    outer = rng.choice(OUTERS[season])
    outer = "无外套" if outer == "无外套" else f"{outer}，{rng.choice(WEAR)}"
    return {
        "风格方向": f"{d}（配色：{DIRECTIONS[d]}，按配色给下面每件定颜色）",
        "主单品": rng.choice(TOPS),
        "下装": rng.choice(BOTTOMS),
        "外层": outer,
        "腿和鞋": f"{rng.choice(LEGS[season])}，{rng.choice(SHOES)}",
        "饰品": "、".join(rng.sample(ACCESSORIES, 3)),
        "头饰": rng.choice(s["head"]),
        "妆容": f"{vibe}：{VIBES[vibe]}",
        "发型": f"{rng.choice(HAIR_COLOR)}、{rng.choice(HAIR_CUT)}、{rng.choice(HAIR_STYLE)}",
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
    ap.add_argument("--direction", help="user-given style direction, one of DIRECTIONS")
    ap.add_argument("--look-only", action="store_true", help="only draw a look, for a styling board")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    season = season_for(a.month)
    s = SEASON[season]
    types = draw_types(rng, a.count, a.type, a.focus)
    look = draw_look(rng, season, a.direction)
    if a.look_only:
        print(f"# 造型抽签（{season}）\n")
        print("按 references/styling.md 的六要素把每项写成具体款式和颜色；用户已指定的项直接替换。\n")
        for k, v in look.items():
            print(f"- {k}：{v}")
        return
    finish = rng.choice([f for f in FINISHES if f not in SITUATIONAL])
    base_scene = a.scene or rng.choice(s["scenes"])
    # post mode: two nearby spots in the same outing, alternated, so close-ups don't share one backdrop
    alt_scene = a.scene or rng.choice([x for x in s["scenes"] if x != base_scene])
    exprs = rng.sample(EXPRESSIONS, len(types))
    hands = rng.sample(HANDS, len(types))
    props = rng.sample(s["props"], len(types))
    BODY_FOCUS = ["腰线", "长腿", "上围曲线", "肩颈锁骨", "整体比例", "背部"]
    body_focuses = [BODY_FOCUS[i % len(BODY_FOCUS)] for i in range(len(types))]
    rng.shuffle(body_focuses)

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
            look = draw_look(rng, season, a.direction)
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
        if a.focus == "outfit":
            print(f"- 展示重点：{body_focuses[i - 1]}（读 references/silhouette-studies.md 对应行，写穿搭细节和机位）")
        print(f"- 表情：{exprs[i - 1]}（与画面类型冲突时改用该类型自带的视线）")
        print(f"- 手势：{hands[i - 1]}（与画面类型冲突时改用该类型自带的手部动作）")
        print(f"- 道具：{props[i - 1]}（画面里放不下就省略）")
        print(f"- 后期：{fin}（{FINISHES[fin]}）\n")


if __name__ == "__main__":
    main()
