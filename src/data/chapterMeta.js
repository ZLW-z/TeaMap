export const CHAPTER_META = Object.freeze({
  ch1: Object.freeze({
    number: '壹',
    title: '茶生山水间',
    description: '群山蕴灵气，活水育新芽。茶自山野萌芽扎根，循着山川脉络散落四方，这片广袤土地，便是茶叶最初的故乡。'
  }),
  ch2: Object.freeze({
    number: '贰',
    title: '何以生茶',
    description: '得天独厚的光照、气候与土壤条件，编织出适配茶树生长的天然温床，一方水土的禀赋，悄悄决定了茶叶的诞生与品质。'
  }),
  ch3: Object.freeze({
    number: '叁',
    title: '云雾深处',
    description: '云雾藏佳茗，寻访散落山河的传统名茶，看名山滋养珍味、岁月沉淀风味，深谷氤氲茶香藏着一代代茗茶佳话。'
  }),
  ch4: Object.freeze({
    number: '肆',
    title: '一叶行远',
    description: '小小一叶茶叶踏出深山，顺着古道、江河辗转流通，从地方风物变成流通四方的货品，开启漫长的远行之路。'
  }),
  ch5: Object.freeze({
    number: '伍',
    title: '今日茶境',
    description: '千年茶脉绵延至今，国内茶园规模稳步扩张，茶叶外销步履不停，现代产业续写着茶业蓬勃发展的新篇章。'
  }),
  ch6: Object.freeze({
    number: '陆',
    title: '世界共饮',
    description: '茶香跨越山海国界，从中国走向全球各地，融入不同地域生活日常，多元饮茶习俗共生交融，编织出异彩纷呈的世界茶文化图景。'
  })
})

export function getChapterMeta(chapterKey) {
  return CHAPTER_META[chapterKey] || null
}
