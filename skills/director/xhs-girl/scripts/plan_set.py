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

# name: (weight, distance, references, required scene features)
SHOT_TYPES = {
    "怼脸自拍": (3, "近", "R06 R17 R25 R36 R89 R108", set()),
    "高位俯拍抬眼": (3, "近", "R03 R22 R28 R66 R81 R102 R114", set()),
    "手势贴脸": (3, "近", "R09 R11 R12 R33 R100 R110", set()),
    "遮半脸": (3, "近", "R10 R19 R105", set()),
    "道具贴脸": (3, "近", "R21 R30 R82 R105 R109", set()),
    "隔桌对拍": (2, "中", "R23 R26 R92 R96 R106 R107", {"桌面"}),
    "镜前自拍": (2, "中", "R15 R35 R42 R43 R54 R74", {"镜子"}),
    "坐蹲半身": (2, "中", "R01 R07 R16 R20 R38 R47 R50 R68 R80 R104", {"可坐"}),
    "直闪夜拍": (2, "中", "R13 R29 R46 R55 R69 R78 R90", {"暗光"}),
    "暗调光影": (2, "中", "R08 R32 R83 R96 R101", {"侧光"}),
    "躺拍俯视": (2, "中", "R05 R73 R95", {"可躺"}),
    "风景人像": (1, "中", "R02 R14 R18 R24 R62 R70 R71 R79 R91 R112", {"风景"}),
    "全身街拍": (1, "远", "R24 R29 R41 R58 R60 R75 R98", {"全身空间"}),
    "居家侧倚": (2, "中", "R31 R34 R44 R45 R72 R77 R83 R86 R93", {"可倚"}),
    "背侧回望": (2, "中", "R53 R67 R76 R88", set()),
    "宠物同框": (1, "近", "R94", set()),
    "低位仰拍": (1, "中", "R115", set()),
}

# 场景名 -> (同一地点的可见锚点, 拍法所需资源)。扩池只增加组间选择。
SCENES = {
    "格窗棕色扶手椅": ("黑框格窗在左、米色窗帘、棕布扶手椅，左侧日光", {"可坐", "可倚", "侧光", "桌面"}),
    "白沙发灰墙客厅": ("灰墙、白布沙发和右侧靠垫，窗光从画面右边进来", {"可坐", "可倚", "可躺", "侧光"}),
    "榻榻米格纹沙发房间": ("榻榻米接缝、棕沙发、格纹靠垫，木窗外绿色树影", {"可坐", "可倚", "可躺", "桌面", "侧光"}),
    "卧室全身镜": ("白门旁同一面落地镜、木地板、米色床沿，室内日光", {"镜子", "可坐", "可倚", "可躺", "全身空间"}),
    "玄关椅子与穿衣镜": ("黑色单椅、奶白柜门、浅木地板和同一面穿衣镜", {"镜子", "可坐", "可倚", "全身空间"}),
    "床上毛毯": ("同一块灰毯、白枕套和床头边缘，侧窗散射光", {"可坐", "可倚", "可躺"}),
    "玩偶地毯": ("米色地毯、蓝白条纹靠垫和固定几只玩偶，室内柔和顶光", {"可坐", "可躺"}),
    "瓷砖墙木桌": ("白色小砖的接缝、深色手写招牌和浅木桌，室内顶光", {"桌面", "可坐"}),
    "居酒屋木墙卡座": ("深木墙、竖向菜单牌、同一张木桌和皮座，暖色顶灯", {"桌面", "可坐", "可倚", "暗光"}),
    "窗边黑桌": ("黑框窗、圆黑桌、白瓷盘，窗光从后侧照进来", {"桌面", "可坐", "侧光"}),
    "蓝桌椅店外": ("蓝色圆桌和折椅、浅灰地板、白框涂鸦玻璃，阴天散射光", {"桌面", "可坐", "全身空间"}),
    "红砖店铺门边": ("红砖、黑色金属门框、木长凳和橱窗反光，街边日光", {"可坐", "全身空间"}),
    "黑木楼梯平台": ("黑色踏步、金属扶手和黄黑边缘标记，楼道暗光", {"可坐", "全身空间", "暗光"}),
    "白门台阶": ("白色凹凸门板、灰台阶和地面排水缝，阴天光", {"可坐", "全身空间"}),
    "混凝土玻璃走廊": ("灰水泥柱、黑框玻璃门、反光地面，侧向窗光", {"可坐", "全身空间", "侧光"}),
    "停车场围栏": ("白网格围栏、水泥柱、顶上管线，固定顶灯", {"可坐", "全身空间"}),
    "灰墙碎石边": ("灰色颗粒墙面、下沿灰碎石、顶部窄百叶窗，散射日光", {"可坐", "全身空间"}),
    "天台涂鸦墙": ("矮水泥墙上的涂鸦、地面停车线和蓝天，日光", {"可坐", "全身空间", "风景"}),
    "田野木窗台": ("深色木窗框、米色窗帘、窗外水田格线，室内暗窗外亮", {"可坐", "可倚", "侧光", "风景"}),
    "海边沙滩": ("浅色沙面、近处浪边和蓝色海平线，晴天日光", {"可坐", "全身空间", "风景"}),
    "冬日海边": ("灰蓝海面、石质矮堤和褐色草丛，冬日阴天光", {"可坐", "全身空间", "风景"}),
    "水边遮阳伞": ("米色遮阳伞、木桌椅、水面亮点和远岸绿树，晴天日光", {"桌面", "可坐", "风景"}),
    "海边车门旁": ("停好的白车、打开的车门、棕榈树和海平线，晴天日光", {"可倚", "全身空间", "风景"}),
    "船上蓝色座椅": ("蓝色船座、白色船舷和远处小船，晴天海面反光", {"可坐", "可倚", "风景"}),
    "车内副驾": ("停驶车内的黑座椅、车门红色缝线和侧窗，窗外微亮", {"可坐", "可倚", "暗光"}),
    "夜间罐墙": ("彩色罐身排成竖列、狭窄过道和暗色地面，现场偏暗", {"暗光", "全身空间"}),
    "夜间路口": ("斑马线、黑路桩、石墙店面和信号灯，天色已暗", {"暗光", "全身空间"}),
    "暗室弧形顶沙发": ("弧形暖灯顶、同一张棕沙发和竖排金属装饰，低照度暖光", {"暗光", "可坐", "可倚"}),
    "地铁车厢": ("浅绿车门、金属边条、车窗反射，车厢顶灯", {"可坐"}),
    "主题公园绿门": ("深绿木门、固定灯牌和石板路，冬日侧向日光", {"可坐", "全身空间"}),
    "秋林木长椅": ("同一张木长椅、棕黄落叶和树干，低角度秋日光", {"可坐", "全身空间", "风景"}),
    "樱花树下": ("树干旁浅粉花枝、石径和绿草，春日散射光", {"可坐", "全身空间", "风景"}),
    "公园草地": ("同一片短草、后方低矮灌木和树影，日光", {"可坐", "可躺", "全身空间", "风景"}),
    '便利店门口': ('白框玻璃门、门侧价签与室内货架，店内顶灯照到门外', {'全身空间', '暗光'}),
    '卧室飘窗': ('白色窗框、米色窗垫和同一只灰靠枕，侧向日光', {'可倚', '可坐', '侧光'}),
    '公园枯草地': ('褐色短草、石径和后方低矮灌木，冬日散射光', {'全身空间', '可坐', '风景'}),
    '抓娃娃机前': ('同一排粉白娃娃机、玻璃内的玩偶与地砖，机器灯和室内顶光', {'全身空间'}),
    '书店书架间': ('深木书架、封面朝外的书和窄过道，暖顶灯', {'全身空间'}),
    '面包店门口': ('木框玻璃门、窗内面包托盘与门边长凳，日光', {'全身空间', '可坐'}),
    '老街石板路': ('灰石板接缝、红砖墙和深木门，阴天散射光', {'全身空间'}),
    '游乐园旋转木马旁': ('金色栏杆、固定一匹白色木马和红色顶棚，傍晚装饰灯', {'全身空间', '暗光'}),
    '天台黄昏': ('水泥矮墙、灰色地面与同一段楼群天际线，低角度夕照', {'全身空间', '可坐', '风景', '侧光'}),
    '花店门口': ('绿色门框、门边花桶与木阶，阴天光', {'全身空间', '可坐'}),
    '校园操场': ('红色跑道、白线和绿色围网，春日日光', {'全身空间', '可坐'}),
    '河边台阶': ('灰石台阶、金属栏杆和河对岸树影，日光', {'全身空间', '可坐', '风景'}),
    '老洋房街角': ('米色石墙、拱形木门和街角路桩，日光', {'全身空间'}),
    '咖啡店窗边': ('黑框窗、木桌、玻璃水杯与棕色椅子，侧窗日光', {'桌面', '可坐', '侧光'}),
    '泳池边': ('蓝色池砖、白色池沿和固定一把躺椅，晴天日光', {'可倚', '可躺', '全身空间', '可坐', '风景'}),
    '便利店冰柜前': ('白色冰柜边框、柜内价签和浅灰地砖，室内顶光', {'全身空间'}),
    '夜市小摊': ('红色棚布、同一张折叠桌和金属摊车，夜间暖灯', {'桌面', '可坐', '暗光'}),
    '海岛小路': ('浅色路面、低矮石墙、棕榈叶和远处海面，日光', {'全身空间', '风景'}),
    '银杏街道': ('金黄银杏、灰路缘和木长椅，秋日侧光', {'全身空间', '可坐', '风景', '侧光'}),
    '秋林小路': ('褐色落叶、石径和固定几株树干，秋日散射光', {'全身空间', '可坐', '风景'}),
    '书店': ('浅木书架、同一张长桌与台灯，暖室内光', {'全身空间', '可坐', '桌面'}),
    '公园长椅': ('绿色木长椅、石径和后方灌木，秋日散射光', {'可倚', '全身空间', '可坐', '风景'}),
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
HAIR_COLOR = ["黑色", "奶茶棕", "米金浅发", "红棕", "樱花粉", "冷茶棕", "黑发里藏一缕浅色挑染"]
HAIR_CUT = ["空气刘海", "厚齐刘海", "八字刘海", "公主切", "鬓角碎发很多的中分", "侧分大刘海"]
HAIR_STYLE = ["大波浪", "蓬松羊毛卷", "内扣长发", "高马尾", "低丸子头", "双麻花辫", "半扎公主头", "利落短发", "松散花苞盘发"]
NAILS = ["裸粉猫眼长甲", "黑色短甲", "奶白钻饰长甲", "酒红短甲", "粉色法式甲", "银色镜面甲"]

SEASON = {
    "winter": {
        "head": ["猫耳毛线帽", "毛绒护耳雷锋帽", "毛绒耳罩", "粗针毛线帽", "贝雷帽", "一排彩色小发夹", "毛绒发箍", "无头饰"],
        "props": ["毛绒玩偶挂件", "热可可纸杯", "烤红薯", "糖葫芦", "草莓蛋糕", "暖手宝", "拍立得", "长毛绒围巾一角", "可颂面包", "奶茶吸管"],
        "scenes": ['格窗棕色扶手椅', '白沙发灰墙客厅', '卧室全身镜', '瓷砖墙木桌', '居酒屋木墙卡座', '冬日海边', '地铁车厢', '黑木楼梯平台', '车内副驾', '主题公园绿门', '夜间罐墙', '暗室弧形顶沙发', '玄关椅子与穿衣镜', '便利店门口', '卧室飘窗', '公园枯草地', '抓娃娃机前', '书店书架间', '面包店门口', '老街石板路', '游乐园旋转木马旁', '天台黄昏'],
    },
    "spring": {
        "head": ["蝴蝶结发带", "抓夹", "一排小发夹", "棒球帽", "渔夫帽", "无头饰"],
        "props": ["花束", "冰美式", "草莓", "拍立得", "风筝", "冰淇淋"],
        "scenes": ['樱花树下', '公园草地', '红砖店铺门边', '蓝桌椅店外', '榻榻米格纹沙发房间', '田野木窗台', '混凝土玻璃走廊', '白门台阶', '天台涂鸦墙', '卧室全身镜', '床上毛毯', '夜间路口', '便利店门口', '车内副驾', '卧室飘窗', '冬日海边', '公园枯草地', '地铁车厢', '抓娃娃机前', '书店书架间', '面包店门口', '老街石板路', '游乐园旋转木马旁', '天台黄昏'],
    },
    "summer": {
        "head": ["发带", "抓夹", "草编帽", "棒球帽", "耳边别一朵花", "无头饰"],
        "props": ["冰棍", "椰子", "西瓜", "冰美式", "水枪", "贝壳"],
        "scenes": ['海边沙滩', '水边遮阳伞', '海边车门旁', '船上蓝色座椅', '田野木窗台', '白沙发灰墙客厅', '卧室全身镜', '瓷砖墙木桌', '夜间路口', '夜间罐墙', '停车场围栏', '天台涂鸦墙', '便利店门口', '车内副驾', '卧室飘窗', '冬日海边', '公园枯草地', '地铁车厢', '抓娃娃机前', '书店书架间', '面包店门口', '老街石板路', '游乐园旋转木马旁', '天台黄昏'],
    },
    "autumn": {
        "head": ["贝雷帽", "棒球帽", "毛线帽", "抓夹", "一排小发夹", "无头饰"],
        "props": ["热拿铁", "栗子", "落叶", "面包", "拍立得", "毛绒挂件"],
        "scenes": ['秋林木长椅', '红砖店铺门边', '窗边黑桌', '格窗棕色扶手椅', '灰墙碎石边', '榻榻米格纹沙发房间', '玩偶地毯', '卧室全身镜', '车内副驾', '蓝桌椅店外', '暗室弧形顶沙发', '混凝土玻璃走廊', '便利店门口', '卧室飘窗', '冬日海边', '公园枯草地', '地铁车厢', '抓娃娃机前', '书店书架间', '面包店门口', '老街石板路', '游乐园旋转木马旁', '天台黄昏'],
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
    "都市轻熟": "黑、奶油白、香槟金",
    "居家复古": "灰蓝、米白、旧玫瑰粉",
    "极简贴身": "炭灰、白、少量银",
    "海岸度假": "海蓝、珊瑚粉、奶白",
}
TOPS = [  # 主单品，每件都自带露肤点
    "一字肩紧身短上衣（露肩露腰）", "斜肩单袖针织短上衣（露一侧肩）", "交叉绑带露背短上衣",
    "蕾丝边小抹胸", "胸前系蝴蝶结的细吊带短背心", "镂空罗纹露脐长袖", "只扣两颗扣的 V 领短开衫（当上衣穿）",
    "下摆系在胸下的绑结衬衫（露腰）", "方领泡泡袖短上衣（露锁骨和腰）", "挂脖露背针织背心",
    "半拉链运动短上衣（拉到锁骨下）", "缎面细吊带背心", "侧边抽绳露腰长袖", "毛绒边小抹胸",
    "领口带金属环的削肩背心", "网纱长袖叠穿小吊带",
    "宽方领罗纹背心", "腰侧收省的贴身短 T", "长袖蕾丝小开衫叠穿吊带",
    "撞色滚边运动背心", "背后细绳交叉短 T", "前襟双排扣短马甲", "细肩带垂坠领上衣",
]
BOTTOMS = [  # 短款与长裤都可展示比例，根据成图取景选择
    "低腰牛仔超短裙", "低腰皮质包臀短裙", "百褶迷你裙", "白色蓬蓬蛋糕短裙", "不对称叠片短裙",
    "牛仔热裤", "低腰工装短裤", "针织包臀短裙", "缎面斜裁迷你裙", "网球短裙", "蕾丝边南瓜短裤",
    "低腰宽松牛仔长裤", "垂坠直筒长裤", "侧袋工装长裤", "微喇牛仔长裤", "条纹针织短裤",
]
DRESSES = ["斜肩修身针织连衣裙", "蕾丝拼边收腰连衣裙", "细肩带低背裙", "挂脖修身短裙", "方领缎面吊带裙"]
OUTERS = {
    "winter": ["浅灰长毛绒短外套", "奶白短款羽绒服", "毛领短皮衣", "焦糖色毛毛短外套", "格纹毛呢短外套", "粗针短开衫", "仿皮草短外套", "酒红系带长外套", "宽松毛绒开衫"],
    "spring": ["短款牛仔外套", "机车皮夹克", "短款针织开衫", "短西装", "运动夹克", "条纹运动拉链外套", "迷彩薄夹克", "无外套"],
    "summer": ["透明防晒衬衫", "无外套", "无外套", "无外套"],
    "autumn": ["机车皮夹克", "麂皮短外套", "短款针织开衫", "短风衣", "格纹短外套", "迷彩薄夹克", "酒红绞花短开衫", "无外套"],
}
WEAR = ["敞开穿", "滑到手肘", "披在肩上", "一侧滑落露肩"]
LEGS = {
    "winter": ["灰色堆堆袜", "黑色过膝袜", "蝴蝶结腿袜", "白色长筒袜", "黑色薄丝袜", "光腿"],
    "spring": ["白色短袜", "蕾丝短袜", "光腿", "过膝袜"],
    "summer": ["光腿", "白色短袜"],
    "autumn": ["黑色过膝袜", "灰色堆堆袜", "黑色薄丝袜", "光腿", "白色长筒袜"],
}
SHOES = ["厚底玛丽珍", "乐福鞋", "复古德训鞋", "厚底短靴", "芭蕾平底鞋", "毛绒短靴", "尖头小猫跟", "厚底板鞋"]
ACCESSORIES = {
    "耳饰": ["大圈银耳环", "珍珠耳钉", "垂坠长耳饰"],
    "颈饰": ["choker", "细项链叠戴", "短珍珠项链"],
    "腰饰": ["金属腰链", "铆钉皮腰带"],
    "发饰": ["星星发夹", "蝴蝶结发夹"],
    "包": ["带毛绒包挂的小方包", "腋下包", "机车肩包"],
    "其他": ["细框眼镜", "手机挂链", "戒指叠戴", "挂颈耳机"],
}

EXPRESSIONS = ["单眼wink", "嘟嘴", "抿嘴笑、眼睛弯起来", "冷脸直视、嘴唇微张", "鼓腮", "歪头睁大眼装无辜",
               "闭眼仰脸", "轻咬下唇", "笑出一点牙", "微微吐舌", "斜眼看镜头", "回眸", "低头垂眼", "惊讶O型嘴", "眯眼笑"]
HANDS = ["手指点在唇边", "比耶贴在脸颊旁", "双手框住眼睛", "托腮", "捂嘴", "手指勾住帽檐往下拉", "撩起一边刘海",
         "捏住一缕头发放到唇边", "手背贴着脸颊", "长袖包住手、双手捧脸", "双手抱膝", "手握发尾", "手指比心贴脸", "双手捂住耳罩或帽子两侧"]
FINISHES = {
    "韩系清透": "低对比、肤色明亮通透，保留人物原有肤色与五官",
    "暖调胶片": "暖黄偏橙、轻微颗粒、暗部微褪色",
    "直闪": "手机闪光正面直打，脸亮背景暗，高光硬、阴影短",
    "冷灰阴天": "蓝灰调低饱和，人物肤色保持可信",
    "粉雾滤镜": "粉紫色高光、梦幻柔光、轻微光晕",
    "黑白高反差": "黑白画面，高反差，皮肤通透",
    "黄昏逆光": "逆光发丝金边、暖橙天空、脸部柔和补亮",
    "CCD复古": "复古数码调色，暗部偏绿、高光轻微溢出、细颗粒，保留手机近距透视",
}

# 闪光改变整组照明；默认调色不改变场景的时间与光源。
SITUATIONAL = {"直闪", "黄昏逆光"}

def season_for(month):
    return {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
            6: "summer", 7: "summer", 8: "summer"}.get(month, "autumn" if month in (9, 10) else "winter")


OUTFIT_BOOST = {"全身街拍": 4, "镜前自拍": 4, "坐蹲半身": 4, "风景人像": 2, "居家侧倚": 4, "背侧回望": 4, "低位仰拍": 2}


def weighted_pick(rng, pool, focus):
    w = [OUTFIT_BOOST.get(n, SHOT_TYPES[n][0]) if focus == "outfit" else SHOT_TYPES[n][0] for n in pool]
    return rng.choices(pool, weights=w)[0]


def draw_types(rng, count, forced, focus, available=None):
    """face: at least half close-up, at most one full-body.
    outfit: at least one close-up, full-body and mid shots weighted up.
    No type repeats; the cover (first shot) is drawn first."""
    available = list(SHOT_TYPES) if available is None else available
    names = list(forced)
    quota = (count + 1) // 2 if focus == "face" else 1
    near_needed = quota - sum(SHOT_TYPES[n][1] == "近" for n in names)
    max_far = 1 if focus == "face" else 2
    while len(names) < count:
        used = set(names)
        if near_needed > 0:
            pool = [n for n in available if n not in used and SHOT_TYPES[n][1] == "近"]
        else:
            far = sum(SHOT_TYPES[n][1] == "远" for n in names)
            pool = [n for n in available if n not in used and not (far >= max_far and SHOT_TYPES[n][1] == "远")]
        if not pool:
            pool = [n for n in available if n not in used]
            if not pool:
                break
        if focus == "outfit" and not names and near_needed > 0:
            pool = [n for n in available if SHOT_TYPES[n][1] != "近"]
        # a set of 3+ all in close-up reads as one repeated picture: keep one mid/far slot
        if count >= 3 and len(names) == count - 1 and all(SHOT_TYPES[n][1] == "近" for n in names):
            pool = [n for n in available if n not in used and SHOT_TYPES[n][1] != "近"] or pool
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
    one_piece = rng.random() < 0.25
    bottom = None if one_piece else rng.choice(BOTTOMS)
    long_trousers = bottom is not None and "长裤" in bottom
    groups = rng.sample(list(ACCESSORIES), rng.randint(1, 3))
    return {
        "风格方向": f"{d}（配色：{DIRECTIONS[d]}，按配色给下面每件定颜色）",
        "主单品": rng.choice(DRESSES if one_piece else TOPS),
        "下装": "连衣裙一体，无需另加下装" if one_piece else bottom,
        "外层": outer,
        "腿和鞋": f"{rng.choice(['袜子藏在裤内', '短袜']) if long_trousers else rng.choice(LEGS[season])}，{rng.choice(SHOES)}",
        "饰品": "、".join(rng.choice(ACCESSORIES[g]) for g in groups),
        "头饰": rng.choice(s["head"]),
        "妆容": f"{vibe}：{VIBES[vibe]}",
        "发型": f"{rng.choice(HAIR_COLOR)}、{rng.choice(HAIR_CUT)}、{rng.choice(HAIR_STYLE)}",
        "美甲": rng.choice(NAILS),
    }


def types_for_scene(scene, forced=()):
    features = SCENES.get(scene, ("", set()))[1]
    return [name for name, (_, _, _, required) in SHOT_TYPES.items()
            if (name != "宠物同框" or name in forced)
            and (required <= features or (scene not in SCENES and name in forced))]


def choose_scene(rng, season, types, count=1):
    candidates = [name for name in SEASON[season]["scenes"]
                  if all(t in types_for_scene(name, types) for t in types)
                  and len(types_for_scene(name, types)) >= count]
    if not candidates:
        candidates = [name for name in SCENES
                      if all(t in types_for_scene(name, types) for t in types)
                      and len(types_for_scene(name, types)) >= count]
    if not candidates:
        raise ValueError("这些画面类型无法在现有同一场景中成立；减少张数或调整类型，保留用户指定地点。")
    return rng.choice(candidates)


def draw_body_focus(rng, types):
    """Prefer a different focus where framing permits it; never force diversity."""
    choices = {
        "怼脸自拍": ["面部与妆发"], "高位俯拍抬眼": ["面部与妆发", "肩颈锁骨"],
        "手势贴脸": ["肩颈锁骨", "上围曲线"], "遮半脸": ["面部与妆发"],
        "道具贴脸": ["面部与妆发", "肩颈锁骨"], "宠物同框": ["面部与妆发"],
        "隔桌对拍": ["肩颈锁骨", "上围曲线"],
        "镜前自拍": ["腰线", "长腿", "整体比例", "背部"],
        "坐蹲半身": ["腰线", "长腿", "整体比例"],
        "直闪夜拍": ["腰线", "肩颈锁骨", "上围曲线"],
        "暗调光影": ["肩颈锁骨", "背部", "腰线"],
        "躺拍俯视": ["肩颈锁骨", "腰线"],
        "风景人像": ["肩颈锁骨", "腰线", "背部"],
        "全身街拍": ["整体比例", "长腿", "腰线"],
        "居家侧倚": ["腰线", "长腿", "整体比例", "上围曲线"],
        "背侧回望": ["背部", "腰线", "肩颈锁骨"],
        "低位仰拍": ["肩颈锁骨", "腰线"],
    }
    selected = []
    for name in types:
        pool = choices[name]
        selected.append(rng.choice([x for x in pool if x not in selected] or pool))
    return selected


def draw_details(rng, pool, count):
    """Exhaust one shuffled cycle before repeating, even for a large set."""
    result = []
    while len(result) < count:
        result.extend(rng.sample(pool, len(pool)))
    return result[:count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--mode", choices=["post", "mixed"], default="post")
    ap.add_argument("--focus", choices=["face", "outfit"], default="face")
    ap.add_argument("--month", type=int, choices=range(1, 13), default=datetime.date.today().month)
    ap.add_argument("--type", action="append", choices=list(SHOT_TYPES), default=[])
    ap.add_argument("--scene", help="user-given location; retained in both modes")
    ap.add_argument("--direction", help="known direction or a custom direction to develop")
    ap.add_argument("--look-only", action="store_true")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    season = season_for(a.month)
    s = SEASON[season]
    if a.direction and a.direction not in DIRECTIONS:
        # Keep the user's custom direction instead of silently replacing it.
        DIRECTIONS[a.direction] = "按用户方向设计配色"
    look = draw_look(rng, season, a.direction)
    if a.look_only:
        print(f"# 造型抽签（{season}）\n")
        print("按 references/styling.md 将部件设计成一套衣服；已指定项保持，冲突项调整并说明。\n")
        for k, v in look.items():
            print(f"- {k}：{v}")
        return
    if not 1 <= a.count <= len(SHOT_TYPES):
        ap.error(f"--count 必须在 1–{len(SHOT_TYPES)} 之间；同一场景的可用类型数可能更少")
    if len(set(a.type)) != len(a.type) or len(a.type) > a.count:
        ap.error("指定类型不能重复，数量不能超过 --count")
    try:
        base_scene = a.scene
        if a.mode == "post" and not base_scene:
            base_scene = choose_scene(rng, season, a.type, a.count)
        available = types_for_scene(base_scene, a.type) if base_scene else [
            n for n in SHOT_TYPES if n != "宠物同框" or n in a.type]
        if any(t not in available for t in a.type):
            ap.error("指定场景不具备该类型需要的资源；请调整类型或明确场景资源")
        if a.count > len(available):
            ap.error(f"该场景可用 {len(available)} 种画面类型；减少 --count 或补充具体场景资源")
        types = draw_types(rng, a.count, a.type, a.focus, available)
    except ValueError as exc:
        ap.error(str(exc))
    finish_pool = [f for f in FINISHES if f not in SITUATIONAL]
    finish = "直闪" if "直闪夜拍" in types and a.mode == "post" else rng.choice(finish_pool)
    exprs = draw_details(rng, EXPRESSIONS, len(types))
    hands = draw_details(rng, HANDS, len(types))
    props = draw_details(rng, s["props"], len(types))
    body_focuses = draw_body_focus(rng, types)
    print(f"# 抽签方案（{season}，{a.mode}，{a.focus}，{len(types)} 张）\n")
    print("人物与已确认造型优先于抽签；检查部件与现场兼容性，调整时说明原因。\n")
    if "宠物同框" in types:
        print("宠物同框按用户明确要求加入；种类和外观使用用户设定，全组保持同一只。\n")
    if a.mode == "post":
        print("## 全组共用造型\n")
        for k, v in look.items():
            print(f"- {k}：{v}")
        print(f"- 后期：{finish}（{FINISHES[finish]}）")
        print(f"- 场景：{base_scene}（全组共用，时间与光源固定）\n")
    for i, t in enumerate(types):
        _, dist, refs, required = SHOT_TYPES[t]
        scene = base_scene
        if a.mode == "mixed":
            look = draw_look(rng, season, a.direction)
            scene = a.scene or choose_scene(rng, season, [t])
            finish = "直闪" if t == "直闪夜拍" else rng.choice(finish_pool)
        anchors = SCENES.get(scene, ("依据用户地点固定两三处可见物件、相对位置与一套光线；逐张复用", set()))[0]
        print(f"## 第 {i + 1} 张 · {t}（{dist}景，参考 {refs}）\n")
        if a.mode == "mixed":
            for k, v in look.items():
                print(f"- {k}：{v}")
        print(f"- 场景：{scene}")
        print(f"- 环境锚点：{anchors}")
        if scene not in SCENES and required:
            print(f"- 现场核对：此类型需要{'、'.join(sorted(required))}；缺少时改拍法，保持地点")
        if a.focus == "outfit":
            print(f"- 展示重点：{body_focuses[i]}（按已确认衣服的实际剪裁和可见范围调整，读 references/silhouette-studies.md）")
        print(f"- 表情：{exprs[i]}（与类型冲突时按类型卡选择视线）")
        print(f"- 手势：{hands[i]}（与类型冲突时按类型卡选择支撑与持机动作）")
        print(f"- 道具：{props[i]}（无关或放不下时省略；宠物同框先保证抱持动作）")
        print(f"- 后期：{finish}（{FINISHES[finish]}）\n")


if __name__ == "__main__":
    main()
