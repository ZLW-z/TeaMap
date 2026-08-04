import { assetUrl } from '../utils/base.js'

// ============================================================
// 世界共饮 · 全球茶文化数据
// ============================================================

// 8个茶文化地标点
const RAW_POINTS = [
  {
    id: 'china',
    country: '中国',
    title: '茶道之源',
    lon: 116.4074,
    lat: 39.9042,
    drinkStyle: '功夫茶 / 抹茶 / 清饮',
    teaType: '绿茶·红茶·乌龙·白茶·黄茶·黑茶',
    image: '/data/6/images/china.jpg',
    intro: '中国是茶的故乡，拥有数千年的饮茶历史。从唐代陆羽《茶经》奠定茶道根基，到宋代点茶、明清泡茶，形成了"和、敬、清、寂"的东方茶道精神。中国茶类齐全，六大茶类各具风韵。功夫茶讲究"关公巡城、韩信点兵"的冲泡技艺，每一泡都追求香气、滋味与回甘的极致平衡。茶不仅是饮品，更是中国人待客、修心、社交的文化载体。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'india',
    country: '印度',
    title: '香料与红茶的交响',
    lon: 78.9629,
    lat: 20.5937,
    drinkStyle: '马萨拉香料茶（Masala Chai）',
    teaType: '阿萨姆红茶·大吉岭红茶',
    image: '/data/6/images/india.jpg',
    intro: '印度是世界第二大茶叶生产国，也是全球最大的红茶消费市场之一。阿萨姆的红茶浓烈醇厚，大吉岭的春摘茶被誉为"红茶中的香槟"。但印度最具代表性的饮茶方式是"马萨拉茶"——将阿萨姆红茶与牛奶、豆蔻、丁香、肉桂、生姜等香料一同熬煮，甜辣交融，香气扑鼻。在印度街头，柴瓦拉（Chaiwala）的煮茶声是每个城市最鲜活的日常背景。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'turkey',
    country: '土耳其',
    title: '郁金香杯里的社交密码',
    lon: 35.2433,
    lat: 38.9637,
    drinkStyle: '土耳其红茶 / 煮茶（Çay）',
    teaType: '里泽红茶',
    image: '/data/6/images/turkey.jpg',
    intro: '土耳其是全球人均茶叶消费量最高的国家，每人年均饮用超过3公斤茶叶。土耳其茶采用独特的双层茶壶（Çaydanlık）烹煮：上层浓茶、下层沸水，饮用时按口味勾兑，盛装于郁金香形透明玻璃杯中，配上一块方糖，色泽红亮如琥珀。茶在土耳其不仅是饮品，更是社交生活的核心——从家庭聚会到市集商谈，一杯红茶递出的不仅是温暖，更是"欢迎"与"信任"。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'uk',
    country: '英国',
    title: '下午茶的优雅仪式',
    lon: -0.1276,
    lat: 51.5072,
    drinkStyle: '英式下午茶 / 红茶加奶',
    teaType: '英式早餐茶·伯爵茶',
    image: '/data/6/images/uk.jpg',
    intro: '英式下午茶起源于19世纪初期，由贝德福德公爵夫人安娜引入，如今已成为英国最具标志性的文化符号之一。下午四时左右，三层点心架搭配一壶经典的红茶，先加奶、后倒茶，轻搅慢饮，构成了优雅的"茶歇"礼仪。英国并非茶叶产地，却凭借强大的贸易网络和殖民历史，将红茶文化推广至全球，成为世界最大茶叶进口国之一。',
    importRate: '9.8%',
    isOrigin: false,
  },
  {
    id: 'japan',
    country: '日本',
    title: '抹茶的禅意美学',
    lon: 138.2529,
    lat: 36.2048,
    drinkStyle: '抹茶 / 煎茶 / 玉露',
    teaType: '静冈绿茶·宇治抹茶',
    image: '/data/6/images/japan.jpg',
    intro: '日本茶道（茶の湯）将饮茶提升至哲学与美学的层面。抹茶是日本茶道的核心，将覆盖栽培的茶叶研磨成粉末，点茶时以茶筅快速搅打，形成绵密泡沫，入口先苦后甘，回味悠长。煎茶则是日本日常消费最广的绿茶，清香鲜爽。日本茶文化强调"一期一会"，即每一次茶会都是独一无二的缘分，体现了对自然与当下的极致珍视。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'kenya',
    country: '肯尼亚',
    title: '红碎茶的全球力量',
    lon: 36.8219,
    lat: -0.0236,
    drinkStyle: 'CTC红茶 / 奶茶基底',
    teaType: '凯里乔高原红茶',
    image: '/data/6/images/kenya.jpg',
    intro: '肯尼亚是全球最大的红茶出口国，其茶叶以CTC工艺制成的红碎茶为主，茶汤色泽深红、滋味强劲，是全世界奶茶、袋泡茶和冰茶饮料的重要基底。肯尼亚茶园主要分布在海拔1500-2700米的高原地区，赤道阳光与火山土壤赋予了茶叶独特的"肯尼亚风味"——麦芽香浓郁、口感醇厚。茶叶是肯尼亚最重要的出口经济作物，支撑着数百万小农的生计。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'srilanka',
    country: '斯里兰卡',
    title: '锡兰红茶的纯净之味',
    lon: 80.7718,
    lat: 7.8731,
    drinkStyle: '锡兰红茶 / 加奶或柠檬',
    teaType: '努沃勒埃利耶·乌瓦·康提',
    image: '/data/6/images/srilanka.jpg',
    intro: '斯里兰卡旧称"锡兰"（Ceylon），其生产的红茶与印度大吉岭红茶、中国祁门红茶并称"世界三大高香红茶"。锡兰红茶按产区风味各异：努沃勒埃利耶的茶叶带有玫瑰与柑橘清香，康提产区醇厚顺滑，乌瓦则以强劲的薄荷香气著称。茶业为斯里兰卡国家经济支柱，茶园多采用"垂直管理"的种植模式，以严格的农残标准享誉国际市场。',
    importRate: null,
    isOrigin: true,
  },
  {
    id: 'usa',
    country: '美国',
    title: '冰茶的快节奏风潮',
    lon: -77.0369,
    lat: 38.9072,
    drinkStyle: '冰茶 / 甜茶 / 袋泡茶',
    teaType: '进口红茶·绿茶',
    image: '/data/6/images/usa.jpg',
    intro: '美国是全球最大的茶叶进口国之一，进口额占比约13.7%。与东方热饮传统不同，美国人偏爱冰茶——将红茶冷却后加冰块、柠檬和糖浆，是夏日标配饮品。南方各州的"甜茶"（Sweet Tea）更是地方文化标志。1904年圣路易斯世博会上，理查德·布莱钦登因天气炎热将热茶冷却售卖，冰茶由此风靡全美。如今，袋泡茶和即饮瓶装茶占据美国茶叶消费的主流。',
    importRate: '13.7%',
    isOrigin: false,
  },
]

export const TEA_CULTURE_POINTS = RAW_POINTS.map(p => ({
  ...p,
  image: assetUrl(p.image),
}))

// TOP5茶叶进口国数据
export const TOP_IMPORTERS = [
  { country: '美国', rate: 13.7, color: '#D4875E' },
  { country: '俄罗斯', rate: 12.2, color: '#B28F4C' },
  { country: '英国', rate: 9.8, color: '#7BA05B' },
  { country: '巴基斯坦', rate: 7.5, color: '#6B4C3B' },
  { country: '其他国家', rate: 56.8, color: '#C3C19A' },
]

// 全球茶数据看板
export const GLOBAL_STATS = [
  { label: '全球茶叶总产量', value: '635', unit: '万吨/年', icon: '🌿' },
  { label: '全球茶叶出口量', value: '180', unit: '万吨/年', icon: '🚢' },
  { label: '全球茶叶进口量', value: '175', unit: '万吨/年', icon: '📦' },
  { label: '产茶国家/地区', value: '60+', unit: '个', icon: '🌍' },
]
