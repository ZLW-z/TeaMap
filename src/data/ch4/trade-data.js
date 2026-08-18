// ============================================================
// 一叶行远｜古代茶叶贸易数据
// 完整版 - 直接从 Excel 转换
// ============================================================

const RAW_TEA_TRADE_DATA = [
  // ===== 荷兰东印度公司 (id: 1-21) =====
  {"id":1,"yearText":"1607年","startYear":1607,"endYear":null,"origin":"澳门","destination":"万丹→阿姆斯特丹","type":"海上","note":"荷兰从澳门运茶到万丹，1610年转运至阿姆斯特丹。这是中国茶叶输入欧洲的最早记录。","source":"李明敏论文第16页","points":[{"name":"澳门","lon":113.5439,"lat":22.1987},{"name":"万丹","lon":106.1503,"lat":-6.4058},{"name":"阿姆斯特丹","lon":4.9041,"lat":52.3676}]},
  {"id":2,"yearText":"1610年","startYear":1610,"endYear":null,"origin":"中国/日本","destination":"荷兰","type":"海上","note":"荷兰人首次将茶叶从中国和日本引入欧洲","source":"刘勇《荷兰东印度公司对华直航贸易档案探析》第3页","points":[{"name":"中国/日本","lon":116.4074,"lat":39.9042},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":3,"yearText":"1637年","startYear":1637,"endYear":null,"origin":"中国","destination":"荷兰","type":"海上","note":"荷兰将茶叶作为饮料商品输入欧洲。1月2日荷印公司董事会指示巴城政府：'公司所有的船都应从中国和日本载些茶来。'","source":"李明敏论文第16页","points":[{"name":"中国","lon":116.4074,"lat":39.9042},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":4,"yearText":"1667年","startYear":1667,"endYear":null,"origin":"福建","destination":"荷兰","type":"海上","note":"大量中国茶叶运往欧洲，由荷兰商船运送。巴城政府致信董事会：'去年我们在福建接受了大量茶叶而无法处理，决定将一大部分运往祖国荷兰。'","source":"李明敏论文第16-17页","points":[{"name":"福建","lon":119.2965,"lat":26.0745},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":5,"yearText":"1685年","startYear":1685,"endYear":null,"origin":"巴达维亚","destination":"荷兰","type":"海上","note":"'十七绅士'指示巴城殖民政府供应2万磅上等茶叶","source":"李明敏论文第19页","points":[{"name":"巴达维亚","lon":106.8456,"lat":-6.2088},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":6,"yearText":"1694年","startYear":1694,"endYear":null,"origin":"巴达维亚","destination":"荷兰","type":"海上","note":"荷兰向巴达维亚的中国帆船购茶93,973磅，价值33,767荷盾","source":"李明敏论文第22页","points":[{"name":"巴达维亚","lon":106.8456,"lat":-6.2088},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":7,"yearText":"1701-1710年","startYear":1701,"endYear":1710,"origin":"巴达维亚","destination":"荷兰","type":"海上","note":"年均购茶400担（约53,320磅）","source":"包乐史《巴达维亚华人与中荷贸易》第140页","points":[{"name":"巴达维亚","lon":106.8456,"lat":-6.2088},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":8,"yearText":"1711-1720年","startYear":1711,"endYear":1720,"origin":"巴达维亚","destination":"荷兰","type":"海上","note":"年均购茶745担（约99,308磅）","source":"同上","points":[{"name":"巴达维亚","lon":106.8456,"lat":-6.2088},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":9,"yearText":"1721-1730年","startYear":1721,"endYear":1730,"origin":"巴达维亚","destination":"荷兰","type":"海上","note":"年均购茶4,339担（约578,388磅），是第一个十年的10倍多","source":"同上","points":[{"name":"巴达维亚","lon":106.8456,"lat":-6.2088},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":10,"yearText":"1728-1734年","startYear":1728,"endYear":1734,"origin":"广州","destination":"荷兰","type":"海上","note":"9艘商船直航中国，茶叶货值占返程总货值的73.9%。1729年利润147%，1733年升至194%。","source":"李明敏论文第45-46页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":11,"yearText":"1729年","startYear":1729,"endYear":null,"origin":"广州","destination":"荷兰","type":"海上","note":"每磅武夷茶广州售价0.43荷盾，荷兰售价1.44荷盾，是成本价的3倍多。","source":"李明敏论文第45页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":12,"yearText":"1730-1740年","startYear":1730,"endYear":1740,"origin":"巴达维亚+广州","destination":"荷兰","type":"海上","note":"巴城年均购茶740,880磅；广州年均购茶7,880,670磅。两者各占约50%。","source":"李明敏论文第46页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":13,"yearText":"1741-1750年","startYear":1741,"endYear":1750,"origin":"巴达维亚+广州","destination":"荷兰","type":"海上","note":"巴城购茶仅占6%（992,250磅），广州占94%（15,049,125磅）。间接贸易衰落。","source":"李明敏论文第46-47页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":14,"yearText":"1756-1759年","startYear":1756,"endYear":1759,"origin":"广州","destination":"荷兰","type":"海上","note":"茶叶贸易毛利润率219%。广州付款777,049荷盾，欧洲收款2,483,414荷盾。","source":"李明敏论文第49页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":15,"yearText":"1757年","startYear":1757,"endYear":null,"origin":"荷兰→巴城（补给）→广州","destination":"荷兰","type":"海上","note":"'斯劳滕号'1757年7月31日抵广州，1758年1月21日返航，9月6日抵荷兰。此后固定航行模式。","source":"刘勇《荷兰东印度公司对华直航贸易档案探析》第6页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":16,"yearText":"1759-1762年","startYear":1759,"endYear":1762,"origin":"广州","destination":"荷兰","type":"海上","note":"贸易毛利润率高达300%，主要得益于欧洲'七年战争'（1756-1763）期间竞争对手减少。","source":"李明敏论文第50页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":17,"yearText":"1756-1780年","startYear":1756,"endYear":1780,"origin":"广州","destination":"荷兰","type":"海上","note":"直接贸易的'黄金时代'，年均毛利润率约94%。","source":"李明敏论文第50-52页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":18,"yearText":"1762年","startYear":1762,"endYear":null,"origin":"广州","destination":"荷兰","type":"海上","note":"荷兰大班获准向行商租借楼舍，设立永久性商馆。","source":"刘勇《荷兰东印度公司对华直航贸易档案探析》第7页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":19,"yearText":"1784年","startYear":1784,"endYear":null,"origin":"广州","destination":"荷兰","type":"海上","note":"购茶40,011担，占广州出口总额20.6%，来华商船4艘。","source":"李明敏论文第58页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":20,"yearText":"1784-1793年","startYear":1784,"endYear":1793,"origin":"广州","destination":"荷兰","type":"海上","note":"购茶量逐年下降：1784年40,011担→1790年9,964担→1793年17,130担（仅占广州出口9.1%）。","source":"李明敏论文第58页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":21,"yearText":"1794年","startYear":1794,"endYear":null,"origin":"广州","destination":"荷兰","type":"海上","note":"最后一艘荷兰东印度公司商船'暹罗号'驶离广州，对华贸易终止。","source":"刘勇《荷兰东印度公司对华直航贸易档案探析》第4页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"荷兰","lon":4.9041,"lat":52.3676}]},
  {"id":22,"yearText":"1615年","startYear":1615,"endYear":null,"origin":"澳门","destination":"日本平户","type":"海上","note":"英国东印度公司驻日本代理人请求在澳门买'一罐好茶'。最早关于英国茶叶记载的文献。","source":"李明敏论文第15页","points":[{"name":"澳门","lon":113.5439,"lat":22.1987},{"name":"日本平户","lon":129.553,"lat":33.368}]},
  {"id":23,"yearText":"1637年","startYear":1637,"endYear":null,"origin":"广州","destination":"英国","type":"海上","note":"英国东印度公司第一次从广州运回12磅茶叶到英国销售","source":"潘毅《英国东印度公司与中国茶贸易》第1页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":24,"yearText":"1657年","startYear":1657,"endYear":null,"origin":"荷兰（转口）","destination":"伦敦","type":"海上","note":"第一家经营茶的伦敦商人托马斯·加尔威开始售卖茶叶，茶叶由荷兰传入。","source":"李明敏论文第17页","points":[{"name":"荷兰","lon":4.9041,"lat":52.3676},{"name":"伦敦","lon":-0.1276,"lat":51.5072}]},
  {"id":25,"yearText":"1664年","startYear":1664,"endYear":null,"origin":"荷兰/万丹","destination":"英国","type":"海上","note":"公司董事部以4镑5先令购2磅2盎司茶叶送呈查理二世","source":"李明敏论文第17页","points":[{"name":"荷兰","lon":4.9041,"lat":52.3676},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":26,"yearText":"1666年","startYear":1666,"endYear":null,"origin":"荷兰/万丹","destination":"英国","type":"海上","note":"以50镑17先令购得22磅12盎司茶叶送呈国王","source":"李明敏论文第17页","points":[{"name":"荷兰","lon":4.9041,"lat":52.3676},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":27,"yearText":"1669年","startYear":1669,"endYear":null,"origin":"万丹","destination":"英国","type":"海上","note":"英国东印度公司从万丹进口中国茶叶143磅，第一次较大量运载茶叶回国","source":"李明敏论文第17页","points":[{"name":"万丹","lon":106.1503,"lat":-6.4058},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":28,"yearText":"1700-1729年","startYear":1700,"endYear":1729,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量82,095担","source":"刘鉴唐《中英关系系年要录》","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":29,"yearText":"1730-1740年","startYear":1730,"endYear":1740,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量87,448担","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":30,"yearText":"1741-1750年","startYear":1741,"endYear":1750,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量129,015担","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":31,"yearText":"1751-1760年","startYear":1751,"endYear":1760,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量191,808担","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":32,"yearText":"1761-1775年","startYear":1761,"endYear":1775,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量790,570担","source":"严中平《中国近代经济史统计资料选辑》估算","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":33,"yearText":"1776-1794年","startYear":1776,"endYear":1794,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶总量1,912,211担","source":"马士《东印度公司对华贸易编年史》估算","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":34,"yearText":"1760-1764年","startYear":1760,"endYear":1764,"origin":"广州","destination":"英国","type":"海上","note":"年均茶叶货值806,242两，输入白银434,243两，白银占支付手段49.5%","source":"庄国土《茶叶、白银和鸦片》","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":35,"yearText":"1765-1769年","startYear":1765,"endYear":1769,"origin":"广州","destination":"英国","type":"海上","note":"年均茶叶货值1,179,854两，输入白银1,066,596两，白银占66.6%","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":36,"yearText":"1770-1774年","startYear":1770,"endYear":1774,"origin":"广州","destination":"英国","type":"海上","note":"年均茶叶货值963,287两，输入白银471,600两，白银占33.3%","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":37,"yearText":"1790-1794年","startYear":1790,"endYear":1794,"origin":"广州","destination":"英国","type":"海上","note":"年均茶叶货值3,575,409两，输入白银559,448两，白银占14%","source":"同上","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":38,"yearText":"1793年","startYear":1793,"endYear":null,"origin":"广州","destination":"英国","type":"海上","note":"英国购茶148,931担，荷兰仅17,130担，英国是荷兰的近9倍。","source":"李明敏论文第61页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"英国","lon":-0.1276,"lat":51.5072}]},
  {"id":39,"yearText":"1784年","startYear":1784,"endYear":null,"origin":"纽约","destination":"广州","type":"海上","note":"美国商船'中国皇后号'开启中美直接贸易","source":"李明敏论文第61页","points":[{"name":"纽约","lon":-74.006,"lat":40.7128},{"name":"广州","lon":113.2644,"lat":23.1291}]},
  {"id":40,"yearText":"1784-1795年","startYear":1784,"endYear":1795,"origin":"广州","destination":"美国","type":"海上","note":"美国来华商船65艘，购茶126,777担。在广州茶叶出口中的比重从1.6%上升到13.5%。","source":"李明敏论文第61页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"美国","lon":-77.0369,"lat":38.9072}]},
  {"id":41,"yearText":"1789年","startYear":1789,"endYear":null,"origin":"广州","destination":"美国","type":"海上","note":"美国超过法国、丹麦，成为仅次于英、荷的第三大茶叶贸易国","source":"李明敏论文第61页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"美国","lon":-77.0369,"lat":38.9072}]},
  {"id":42,"yearText":"1804年","startYear":1804,"endYear":null,"origin":"广州","destination":"美国","type":"海上","note":"美国超过荷兰，成为仅次于英国的第二大茶叶贸易国","source":"李明敏论文第61页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"美国","lon":-77.0369,"lat":38.9072}]},
  {"id":43,"yearText":"1636年","startYear":1636,"endYear":null,"origin":"荷兰（转口）","destination":"巴黎","type":"海上","note":"茶叶传入法国，据《警政全书》载巴黎最初有茶是在1636年","source":"李明敏论文第17页","points":[{"name":"荷兰","lon":4.9041,"lat":52.3676},{"name":"巴黎","lon":2.3522,"lat":48.8566}]},
  {"id":44,"yearText":"1650年","startYear":1650,"endYear":null,"origin":"荷兰（转口）","destination":"德国","type":"海上","note":"茶叶传入德国","source":"李明敏论文第17页","points":[{"name":"荷兰","lon":4.9041,"lat":52.3676},{"name":"德国","lon":13.405,"lat":52.52}]},
  {"id":45,"yearText":"1718年","startYear":1718,"endYear":null,"origin":"广州","destination":"欧洲","type":"海上","note":"维也纳哈布斯堡皇朝特许成立奥斯坦公司派船到中国贸易","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"欧洲","lon":4.3517,"lat":50.8503}]},
  {"id":46,"yearText":"1719年","startYear":1719,"endYear":null,"origin":"广州","destination":"欧洲","type":"海上","note":"奥斯坦公司首次从中国运回茶叶17万磅，同年荷兰购茶20万磅。","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"欧洲","lon":4.3517,"lat":50.8503}]},
  {"id":47,"yearText":"1720年","startYear":1720,"endYear":null,"origin":"广州","destination":"欧洲","type":"海上","note":"奥斯坦公司购茶1,500担（约183,750磅），直追荷兰。","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"欧洲","lon":4.3517,"lat":50.8503}]},
  {"id":48,"yearText":"1723年","startYear":1723,"endYear":null,"origin":"广州","destination":"欧洲","type":"海上","note":"奥斯坦公司购茶5,100担（624,750磅），竞争力极强。","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"欧洲","lon":4.3517,"lat":50.8503}]},
  {"id":49,"yearText":"1729年","startYear":1729,"endYear":null,"origin":"广州","destination":"丹麦","type":"海上","note":"丹麦东印度公司成立，参与茶叶贸易竞争","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"丹麦","lon":12.5683,"lat":55.6761}]},
  {"id":50,"yearText":"1732年","startYear":1732,"endYear":null,"origin":"广州","destination":"瑞典","type":"海上","note":"瑞典东印度公司成立，参与茶叶贸易竞争","source":"李明敏论文第35页","points":[{"name":"广州","lon":113.2644,"lat":23.1291},{"name":"瑞典","lon":18.0686,"lat":59.3293}]},

  // ===== 万里茶道 / 中俄贸易 (id: 51-90) =====
  {"id":51,"yearText":"1638-1640年","startYear":1638,"endYear":1640,"origin":"中国西北（阿勒坦汗驻地）","destination":"莫斯科","type":"陆路","note":"俄国使团访问蒙古阿勒坦汗，获赠200袋白毫茶（约248公斤），茶叶正式输入俄国。","source":"郭丁瑞论文第19页","points":[{"name":"中国西北","lon":105,"lat":38},{"name":"莫斯科","lon":37.6173,"lat":55.7558}]},
  {"id":52,"yearText":"1654年","startYear":1654,"endYear":null,"origin":"北京","destination":"莫斯科","type":"陆路","note":"费·巴依科夫使团出使中国，顺治帝赠予沙皇礼物中包含10普特茶叶。","source":"郭丁瑞论文第28页","points":[{"name":"北京","lon":116.4074,"lat":39.9042},{"name":"莫斯科","lon":37.6173,"lat":55.7558}]},
  {"id":53,"yearText":"1727年","startYear":1727,"endYear":null,"origin":"买卖城/恰克图","destination":"中俄边境口岸","type":"陆路","note":"《恰克图条约》签订，确立恰克图为中俄贸易口岸，万里茶道正式形成。","source":"郭丁瑞论文第26-27页","points":[{"name":"买卖城/恰克图","lon":106.45,"lat":50.35}]},
  {"id":54,"yearText":"1728年","startYear":1728,"endYear":null,"origin":"北京","destination":"恰克图","type":"陆路","note":"第一批抵达北京的俄国商队购买约3万磅茶叶；恰克图市场正式开始贸易。","source":"郭丁瑞论文第30-31页","points":[{"name":"北京","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":55,"yearText":"1730年","startYear":1730,"endYear":null,"origin":"中国内地","destination":"恰克图","type":"陆路","note":"清廷在恰克图俄商贸易区对面建买卖城，晋商开始垄断恰克图贸易。","source":"赖惠敏论文第9-10页","points":[{"name":"中国内地","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":56,"yearText":"1755-1762年","startYear":1755,"endYear":1762,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶出口量11,000-13,000普特，占恰克图进口总额15%。","source":"郭丁瑞论文第7页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":57,"yearText":"1768-1785年","startYear":1768,"endYear":1785,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶出口量约29,000普特。","source":"董晓汾论文第8页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":58,"yearText":"1792年","startYear":1792,"endYear":null,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶输俄货值达54万卢布，首次超过棉花货值。","source":"宋时磊论文第2页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":59,"yearText":"1798年","startYear":1798,"endYear":null,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"输俄茶叶12,729普特。","source":"齐运东论文第2页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":60,"yearText":"1799年","startYear":1799,"endYear":null,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"输俄茶叶14,178普特。","source":"同上","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":61,"yearText":"1800年","startYear":1800,"endYear":null,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"输俄茶叶18,931普特；恰克图贸易总额达8,382,846卢布。","source":"同上","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":62,"yearText":"1801-1810年","startYear":1801,"endYear":1810,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶输出量75,076普特。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":63,"yearText":"1802年","startYear":1802,"endYear":null,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶输俄货值达187万卢布，占输俄总货值40%。","source":"宋时磊论文第2页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":64,"yearText":"1811-1820年","startYear":1811,"endYear":1820,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶输出量96,145普特。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":65,"yearText":"1812-1817年","startYear":1812,"endYear":1817,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值60%。","source":"郭丁瑞论文第33页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":66,"yearText":"1816年","startYear":1816,"endYear":null,"origin":"中国产茶区（两湖）","destination":"恰克图","type":"陆路","note":"据蒙古国档案记载，在恰克图从事中俄贸易的商号约161家。","source":"赖惠敏论文第30页","points":[{"name":"两湖茶区","lon":112,"lat":29},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":67,"yearText":"1818-1824年","startYear":1818,"endYear":1824,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值75%。","source":"郭丁瑞论文第33页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":68,"yearText":"1821-1830年","startYear":1821,"endYear":1830,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶输出量143,196普特。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":69,"yearText":"1825-1831年","startYear":1825,"endYear":1831,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值86%。","source":"郭丁瑞论文第33页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":70,"yearText":"1831-1840年","startYear":1831,"endYear":1840,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶输出量190,228普特。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":71,"yearText":"1832-1838年","startYear":1832,"endYear":1838,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值89%。","source":"郭丁瑞论文第33页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":72,"yearText":"1836年","startYear":1836,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶135,019普特，砖茶73,044普特。","source":"郭丁瑞论文第44-45页","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":73,"yearText":"1837年","startYear":1837,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶134,234普特，砖茶56,161普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":74,"yearText":"1838年","startYear":1838,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶127,645普特，砖茶70,811普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":75,"yearText":"1839年","startYear":1839,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶141,997普特，砖茶64,698普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":76,"yearText":"1839-1845年","startYear":1839,"endYear":1845,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值91%。","source":"郭丁瑞论文第33页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":77,"yearText":"1840年","startYear":1840,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶149,731普特，砖茶64,475普特。","source":"郭丁瑞论文第44-45页","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":78,"yearText":"1840年代","startYear":1840,"endYear":1849,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"茶叶占中国对俄输出总值跃升至95%以上。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":79,"yearText":"1841-1850年","startYear":1841,"endYear":1850,"origin":"中国产茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶输出量270,591普特。","source":"郭丁瑞论文第34页","points":[{"name":"中国产茶区","lon":116.4074,"lat":39.9042},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":80,"yearText":"1841年","startYear":1841,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶168,218普特，砖茶74,390普特。","source":"郭丁瑞论文第44-45页","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":81,"yearText":"1842年","startYear":1842,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶193,413普特，砖茶64,382普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":82,"yearText":"1843年","startYear":1843,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶135,413普特，砖茶87,834普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":83,"yearText":"1844年","startYear":1844,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶175,254普特，砖茶82,402普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":84,"yearText":"1845年","startYear":1845,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶196,523普特，砖茶124,396普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":85,"yearText":"1846年","startYear":1846,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶227,452普特，砖茶109,695普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":86,"yearText":"1847年","startYear":1847,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶224,006普特，砖茶125,646普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":87,"yearText":"1848年","startYear":1848,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶253,746普特，砖茶116,249普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":88,"yearText":"1849年","startYear":1849,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶165,087普特，砖茶119,464普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":89,"yearText":"1850年","startYear":1850,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶212,178普特，砖茶85,440普特。1850年茶叶贸易额占对俄总输入额94.9%。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":90,"yearText":"1851年","startYear":1851,"endYear":null,"origin":"安化黑茶","destination":"恰克图→俄国","type":"陆路","note":"输俄白毫茶239,864普特，砖茶92,515普特。","source":"同上","points":[{"name":"安化","lon":111.7,"lat":28.3},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},

  // ===== 万里茶道后期 (id: 91-132) =====
  {"id":91,"yearText":"1851年","startYear":1851,"endYear":null,"origin":"福建武夷山","destination":"恰克图→俄国","type":"陆路","note":"太平天国运动爆发，切断福建茶路。晋商改以两湖茶为主。","source":"宋时磊论文第3页","points":[{"name":"武夷山","lon":117.9,"lat":27.8},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":92,"yearText":"1851-1855年","startYear":1851,"endYear":1855,"origin":"两湖茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶贸易额9,272,000卢布。","source":"杨育珍论文第43页","points":[{"name":"两湖茶区","lon":112,"lat":29},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":93,"yearText":"1856-1860年","startYear":1856,"endYear":1860,"origin":"两湖茶区","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶贸易额8,306,000卢布。","source":"同上","points":[{"name":"两湖茶区","lon":112,"lat":29},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":94,"yearText":"1861-1865年","startYear":1861,"endYear":1865,"origin":"汉口","destination":"恰克图","type":"陆路","note":"年均茶叶贸易额5,585,000卢布。恰克图山西行庄由100个缩减为六七十个。","source":"杨育珍论文第43页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":95,"yearText":"1862年","startYear":1862,"endYear":null,"origin":"汉口","destination":"天津→张家口→恰克图","type":"陆路","note":"汉口港出口茶叶21.6万担。","source":"齐运东论文第1页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"天津","lon":117.2,"lat":39.0842},{"name":"张家口","lon":114.886,"lat":40.768},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":96,"yearText":"1863年","startYear":1863,"endYear":null,"origin":"汉口","destination":"恰克图","type":"陆路","note":"俄商在汉口开设洋行，将红茶、砖茶装入轮船自汉运津，由津赴俄。","source":"赖惠敏论文第35页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":97,"yearText":"1865年","startYear":1865,"endYear":null,"origin":"汉口","destination":"天津→恰克图","type":"陆路","note":"天津运往恰克图茶叶1,647,888磅。","source":"宋时磊论文第4页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"天津","lon":117.2,"lat":39.0842},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":98,"yearText":"1866年","startYear":1866,"endYear":null,"origin":"汉口","destination":"天津→恰克图","type":"陆路","note":"天津运往恰克图茶叶2,399,291磅。恰克图买卖城只剩4个晋商商号。","source":"宋时磊论文第4页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"天津","lon":117.2,"lat":39.0842},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":99,"yearText":"1866-1870年","startYear":1866,"endYear":1870,"origin":"汉口","destination":"恰克图","type":"陆路","note":"年均茶叶贸易额4,635,000卢布。","source":"杨育珍论文第43页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":100,"yearText":"1867年","startYear":1867,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口65,293担，海关两517,500两。","source":"郭丁瑞论文第46页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":101,"yearText":"1868年","startYear":1868,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口53,143担，海关两531,407两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":102,"yearText":"1869年","startYear":1869,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口73,520担，海关两915,320两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":103,"yearText":"1870年","startYear":1870,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口62,896担，海关两503,867两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":104,"yearText":"1871年","startYear":1871,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口83,790担，海关两754,495两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":105,"yearText":"1871-1875年","startYear":1871,"endYear":1875,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶贸易额3,984,000卢布。","source":"杨育珍论文第43页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":106,"yearText":"1872年","startYear":1872,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口96,994担，海关两969,935两。","source":"赖惠敏论文第36页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":107,"yearText":"1873年","startYear":1873,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口107,330担，海关两1,046,939两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":108,"yearText":"1873年","startYear":1873,"endYear":null,"origin":"汉口","destination":"敖德萨","type":"陆路","note":"俄商'俄罗斯号'装茶2,012,757磅，从汉口运往黑海敖德萨口岸。","source":"宋时磊论文第6页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"敖德萨","lon":30.7233,"lat":46.4825}]},
  {"id":109,"yearText":"1874年","startYear":1874,"endYear":null,"origin":"汉口","destination":"敖德萨","type":"陆路","note":"俄商改用蒸汽机和水压机制作砖茶，成为武汉地区第一批近代工厂。","source":"齐运东论文第1页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"敖德萨","lon":30.7233,"lat":46.4825}]},
  {"id":110,"yearText":"1874-1894年","startYear":1874,"endYear":1894,"origin":"汉口","destination":"天津→张家口→恰克图","type":"陆路","note":"天津转口茶叶持续增长，晋商陆路运茶逐年减少，俄商成为市场主导。","source":"郭丁瑞论文第37页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"天津","lon":117.2,"lat":39.0842},{"name":"张家口","lon":114.886,"lat":40.768},{"name":"恰克图","lon":106.45,"lat":50.35}]},
  {"id":111,"yearText":"1875年","startYear":1875,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口166,900担，海关两1,976,448两。","source":"赖惠敏论文第36页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":112,"yearText":"1876年","startYear":1876,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口153,951担，海关两1,819,483两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":113,"yearText":"1877年","startYear":1877,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口147,810担，海关两1,759,028两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":114,"yearText":"1878年","startYear":1878,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口194,277担，海关两1,354,267两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":115,"yearText":"1879年","startYear":1879,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口275,540担，海关两1,392,616两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":116,"yearText":"1880年","startYear":1880,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口232,969担，海关两2,132,304两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":117,"yearText":"1880年","startYear":1880,"endYear":null,"origin":"汉口","destination":"敖德萨","type":"陆路","note":"汉口至敖德萨茶叶输出21,978,611千克。","source":"宋时磊论文第7页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"敖德萨","lon":30.7233,"lat":46.4825}]},
  {"id":118,"yearText":"1881年","startYear":1881,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口247,498担，海关两1,468,184两。","source":"赖惠敏论文第36页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":119,"yearText":"1882年","startYear":1882,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口219,027担，海关两1,303,964两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":120,"yearText":"1883年","startYear":1883,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口218,744担，海关两1,501,005两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":121,"yearText":"1884年","startYear":1884,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口244,996担，海关两1,482,575两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":122,"yearText":"1885年","startYear":1885,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口280,112担，海关两1,511,875两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":123,"yearText":"1886年","startYear":1886,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口361,492担，海关两2,218,092两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":124,"yearText":"1886-1890年","startYear":1886,"endYear":1890,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"年均茶叶贸易额2,186,000卢布。","source":"杨育珍论文第43页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":125,"yearText":"1887年","startYear":1887,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口331,281担，海关两2,312,145两。","source":"赖惠敏论文第36页","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":126,"yearText":"1888年","startYear":1888,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口412,642担，海关两2,453,417两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":127,"yearText":"1889年","startYear":1889,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口310,178担，海关两2,229,583两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":128,"yearText":"1890年","startYear":1890,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口297,168担，海关两2,136,720两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":129,"yearText":"1891年","startYear":1891,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口328,861担，海关两2,328,755两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":130,"yearText":"1892年","startYear":1892,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口323,112担，海关两2,313,179两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":131,"yearText":"1893年","startYear":1893,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口382,361担，海关两2,676,514两。恰克图贸易额降至90万卢布。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},
  {"id":132,"yearText":"1894年","startYear":1894,"endYear":null,"origin":"汉口","destination":"恰克图→俄国","type":"陆路","note":"砖茶出口395,506担，海关两2,798,913两。","source":"同上","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"恰克图","lon":106.45,"lat":50.35},{"name":"俄国","lon":37.6173,"lat":55.7558}]},

  // ===== 茶马古道 (id: 133-142) =====
  {"id":133,"yearText":"唐宋-明清","startYear":618,"endYear":1911,"origin":"云南西双版纳/普洱","destination":"大理→丽江→拉萨→印度","type":"陆路","note":"以普洱茶为主。丽江是滇藏贸易重要中转站。","source":"凌文锋论文第7页","points":[{"name":"普洱","lon":100.8,"lat":22},{"name":"大理","lon":100.2676,"lat":25.6065},{"name":"丽江","lon":100.2278,"lat":26.855},{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"印度","lon":77.209,"lat":28.6139}]},
  {"id":134,"yearText":"唐宋-明清","startYear":618,"endYear":1911,"origin":"四川雅安/邛崃","destination":"康定→昌都→拉萨→尼泊尔/印度","type":"陆路","note":"运输量最大、跨度最广。康定是川藏茶马贸易中心。","source":"凌文锋论文第3页","points":[{"name":"雅安","lon":103,"lat":30},{"name":"康定","lon":101.957,"lat":30.05},{"name":"昌都","lon":97.172,"lat":31.14},{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"印度","lon":77.209,"lat":28.6139}]},
  {"id":135,"yearText":"唐宋-明清","startYear":618,"endYear":1911,"origin":"陕西长安/紫阳","destination":"西安→兰州→西宁→拉萨","type":"陆路","note":"在唐蕃古道基础上形成，后演变为茶马贸易通道。","source":"凌文锋论文第3-4页","points":[{"name":"长安","lon":108.9,"lat":34.3},{"name":"西安","lon":108.94,"lat":34.341},{"name":"兰州","lon":103.834,"lat":36.061},{"name":"西宁","lon":101.778,"lat":36.617},{"name":"拉萨","lon":91.1322,"lat":29.66}]},
  {"id":136,"yearText":"1684年","startYear":1684,"endYear":null,"origin":"西藏拉萨","destination":"拉达克→克什米尔","type":"陆路","note":"《廷墨岗条约》签订后，拉萨每年派'茶巴使团'以200头牲畜驮运藏茶前往拉达克。","source":"孙博文论文第4页","points":[{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"拉达克","lon":77.577,"lat":34.152},{"name":"克什米尔","lon":74.797,"lat":34.084}]},
  {"id":137,"yearText":"17世纪","startYear":1600,"endYear":1699,"origin":"西藏","destination":"拉达克","type":"陆路","note":"1631年葡萄牙传教士记载：茶叶从卫藏传入拉达克，只有富人才能喝得起。","source":"孙博文论文第4页","points":[{"name":"西藏","lon":91,"lat":30},{"name":"拉达克","lon":77.577,"lat":34.152}]},
  {"id":138,"yearText":"乾隆-民国","startYear":1736,"endYear":1911,"origin":"西藏拉萨","destination":"拉达克→克什米尔→新疆","type":"陆路","note":"多格拉王朝时期，茶马贸易路线向北延伸至新疆南部。","source":"孙博文论文第5-6页","points":[{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"拉达克","lon":77.577,"lat":34.152},{"name":"克什米尔","lon":74.797,"lat":34.084},{"name":"新疆","lon":77,"lat":38}]},
  {"id":139,"yearText":"1942-1945年","startYear":1942,"endYear":1945,"origin":"云南丽江/四川康定","destination":"拉萨→印度噶伦堡","type":"陆路","note":"滇缅公路被日军切断后，茶马古道成为唯一能运送国际援华物资的陆上通道。","source":"王曼曼论文第43-44页","points":[{"name":"丽江","lon":100.2278,"lat":26.855},{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"噶伦堡","lon":88.474,"lat":27.059}]},
  {"id":140,"yearText":"1943年","startYear":1943,"endYear":null,"origin":"云南丽江","destination":"拉萨→印度噶伦堡","type":"陆路","note":"丽江至拉萨马帮由四五千匹增至10,000匹；货物达1,000多吨。","source":"王曼曼论文第45页","points":[{"name":"丽江","lon":100.2278,"lat":26.855},{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"噶伦堡","lon":88.474,"lat":27.059}]},
  {"id":141,"yearText":"1943年","startYear":1943,"endYear":null,"origin":"云南丽江","destination":"拉萨/印度","type":"陆路","note":"'达记'商号（李达三）运往拉萨和印度的货物3,000驮。","source":"王曼曼论文第44页","points":[{"name":"丽江","lon":100.2278,"lat":26.855},{"name":"拉萨","lon":91.1322,"lat":29.66}]},
  {"id":142,"yearText":"1944年","startYear":1944,"endYear":null,"origin":"成都/昆明","destination":"康定→拉萨→印度噶伦堡","type":"陆路","note":"国民政府交通部与藏商合资成立'康藏驮运股份有限公司'。","source":"王曼曼论文第44页","points":[{"name":"成都","lon":104,"lat":28},{"name":"康定","lon":101.957,"lat":30.05},{"name":"拉萨","lon":91.1322,"lat":29.66},{"name":"噶伦堡","lon":88.474,"lat":27.059}]},

  // ===== 其他路线 (id: 143-150) =====
  {"id":143,"yearText":"宋","startYear":960,"endYear":null,"origin":"泉州/广州","destination":"东南亚、阿拉伯","type":"海上","note":"宋代海上茶叶贸易繁荣，泉州、广州是重要港口。","source":"Excel补充","points":[{"name":"泉州","lon":118.5,"lat":24.9},{"name":"东南亚","lon":106.8456,"lat":-6.2088}]},
  {"id":144,"yearText":"1567年","startYear":1567,"endYear":null,"origin":"福建","destination":"月港→马尼拉→阿卡普尔科→欧洲","type":"海上","note":"月港出口茶叶，经菲律宾马尼拉转运至美洲和欧洲。","source":"Excel补充","points":[{"name":"福建","lon":119.2965,"lat":26.0745},{"name":"马尼拉","lon":120.9842,"lat":14.5995},{"name":"阿卡普尔科","lon":-99.9,"lat":16.85}]},
  {"id":145,"yearText":"1405-1433年","startYear":1405,"endYear":1433,"origin":"南京/泉州","destination":"爪哇→东南亚→印度→阿拉伯→非洲","type":"海上","note":"郑和下西洋，船队携带茶叶作为贸易品。","source":"Excel补充","points":[{"name":"泉州","lon":118.5,"lat":24.9},{"name":"爪哇","lon":106.1503,"lat":-6.4058},{"name":"印度","lon":77.209,"lat":28.6139},{"name":"阿拉伯","lon":45,"lat":20}]},
  {"id":146,"yearText":"唐宋-明清","startYear":618,"endYear":1911,"origin":"浙江/福建茶区","destination":"宁波→朝鲜/日本/东南亚","type":"海上","note":"宁波是中国最'长寿'的茶港。","source":"Excel补充","points":[{"name":"浙江茶区","lon":120,"lat":28},{"name":"宁波","lon":121.5439,"lat":29.8683},{"name":"日本","lon":139.6917,"lat":35.6895}]},
  {"id":147,"yearText":"1662年","startYear":1662,"endYear":null,"origin":"澳门","destination":"里斯本→伦敦","type":"海上","note":"葡萄牙公主凯瑟琳嫁入英国皇室，将饮茶习惯带入英国。","source":"Excel补充","points":[{"name":"澳门","lon":113.5439,"lat":22.1987},{"name":"里斯本","lon":-9.1393,"lat":38.7223},{"name":"伦敦","lon":-0.1276,"lat":51.5072}]},
  {"id":148,"yearText":"1851-1939年","startYear":1851,"endYear":1939,"origin":"福建","destination":"欧洲","type":"海上","note":"坦洋工夫红茶大量出口欧洲。","source":"Excel补充","points":[{"name":"福建","lon":119.2965,"lat":26.0745},{"name":"欧洲","lon":4.3517,"lat":50.8503}]},
  {"id":149,"yearText":"1905年","startYear":1905,"endYear":null,"origin":"汉口","destination":"海参崴→圣彼得堡","type":"陆路","note":"西伯利亚铁路开通后，茶叶经海参崴铁路直达圣彼得堡。","source":"Excel补充","points":[{"name":"汉口","lon":114.285,"lat":30.584},{"name":"海参崴","lon":131.9,"lat":43.1},{"name":"圣彼得堡","lon":30.3,"lat":59.9}]},
  {"id":150,"yearText":"汉-唐","startYear":202,"endYear":907,"origin":"四川/中原","destination":"河西走廊→新疆→中亚、波斯、阿拉伯","type":"陆路","note":"陆上丝绸之路是茶叶西传的重要通道。","source":"Excel补充","points":[{"name":"中原","lon":108,"lat":34},{"name":"河西走廊","lon":98,"lat":38},{"name":"新疆","lon":85,"lat":40},{"name":"中亚","lon":55,"lat":30}]}
];

// 时间轴阶段固定从唐代开始。跨越多个朝代只记录在路线生命周期中，
// 不会成为单独的时间轴节点。
export const DYNASTY_INFO = {
  '唐代': {
    title: '唐代｜茶入边疆，商路初成',
    feature: '唐代中期以后，饮茶风尚由南方向全国扩展，茶叶逐渐成为重要商品和国家税收来源。随着边疆往来增加，茶开始沿陆路进入西北和高原地区，并通过广州等港口参与海上贸易。',
    channels: '贞元年间已有回鹘驱马换茶的明确记载，茶马互市由此成为连接中原与边疆的重要方式。陆路上的茶、马和生活物资交换，与海上通往东南亚、南亚及更远地区的商路共同展开。',
    impact: '茶叶不仅是日常饮品，也成为跨区域交流的媒介。贸易推动了边疆饮茶习惯形成，并加强了中原与周边地区的经济和文化联系。',
    sourceRefs: [
      'https://www.neac.gov.cn/seac/c103391/202304/1162265.shtml',
      'https://scdfz.sc.gov.cn/scyx/ytsc/chuanchazhiyp/content_122144',
      'https://www.gz.gov.cn/zt/gzydyl/whjl/content/post_9125971.html',
    ],
  },
  '宋代': {
    title: '宋代｜制度成形，海陆并进',
    feature: '宋代茶叶生产和消费继续扩大，茶马贸易逐渐制度化。北宋熙宁以后，政府通过专门机构管理茶叶收购、运输和换马，使茶叶与边疆治理、军马供给产生更紧密的联系。',
    channels: '西南和西北茶马道路持续发展，南方港口的海外贸易也日益繁荣。1087年，北宋在泉州设置市舶司，管理海船、货物、关税和外商事务，茶叶与瓷器、丝绸等商品由此进入更广阔的海上市场。',
    impact: '宋代形成了陆路边贸与海上外贸并行的格局。茶叶既连接内地产区和边疆市场，也成为海外贸易商品体系的一部分。',
    sourceRefs: [
      'https://www.nopss.gov.cn/n1/2021/0125/c219544-32010620.html',
      'https://www.fujian.gov.cn/zwgk/ztzl/sxzygwzxsgzx/sdjj/wvjj/202501/t20250110_6698898.htm',
    ],
  },
  '元代': {
    title: '元代｜港通四海，茶随帆远',
    feature: '元代欧亚交通和海上贸易网络进一步扩展。泉州等港口汇集来自不同地区的商人和货物，成为连接中国沿海、东南亚、印度洋及更远市场的重要节点。',
    channels: '茶叶与丝绸、瓷器等货物从东南沿海港口装船，经东南亚进入印度洋贸易网络。陆路交通则继续连接中原、中亚和西亚地区，使海陆商路共同构成跨区域流通体系。',
    impact: '港口贸易的发展扩大了茶叶接触海外市场的范围，也使茶叶伴随人员、技术和生活方式的交流传播到更远地区。',
    sourceRefs: [
      'https://www.fujian.gov.cn/zwgk/ztzl/sxzygwzxsgzx/flsxkmh/202310/t20231012_6271639.htm',
      'https://www.fujian.gov.cn/zwgk/ztzl/sxzygwzxsgzx/sdjj/wvjj/202512/t20251212_7045336.htm',
    ],
  },
  '明代': {
    title: '明代｜边贸延续，茶入欧洲',
    feature: '明代茶马互市继续承担边疆贸易和治理功能，部分时期由政府加强控制。与此同时，广州、福建等沿海地区仍保持海外贸易联系，茶叶逐渐进入欧洲商人的远洋贸易网络。',
    channels: '17世纪初，中国茶经澳门和东南亚转运至荷兰。1607年已有荷兰商船贩运中国绿茶的记录，1610年茶叶运抵欧洲；到1637年前后，荷兰市场的茶叶进口规模进一步扩大。',
    impact: '茶叶由亚洲区域性商品逐步进入欧洲消费市场，荷兰商人及其转运网络在早期传播中发挥了重要作用，为清代更大规模的中欧茶叶贸易奠定基础。',
    sourceRefs: [
      'https://www.icm.gov.mo/rc/viewer/10099/2211',
      'https://www.gz.gov.cn/zt/gzydyl/whjl/content/post_9125971.html',
    ],
  },
  '清代': {
    title: '清代｜茶路万里，市场成网',
    feature: '清代中国茶叶对外贸易进入大规模发展阶段。海上贸易以广州为核心，陆上贸易则经恰克图连接俄国市场，逐渐形成横跨亚欧大陆的万里茶道。',
    channels: '1685年清廷开海设关，18世纪广州外贸体系逐渐成熟。1727年中俄签订相关条约并恢复恰克图互市，来自福建、湖北、湖南等地的茶叶经陆路北运，再转往莫斯科、圣彼得堡及欧洲其他地区。',
    impact: '茶叶成为中西贸易的重要商品。广州十三行、东印度公司和中俄商队共同构成跨海与跨大陆的贸易网络，也推动饮茶习惯在欧洲和俄罗斯传播。',
    sourceRefs: [
      'https://www.neac.gov.cn/seac/c103391/202210/1159337.shtml',
      'https://www.gz.gov.cn/zt/gzydyl/whjl/content/post_9125971.html',
    ],
  },
  '抗战时期': {
    title: '抗战时期｜以茶换汇，商路转移',
    feature: '全面抗战爆发后，传统港口、铁路和茶叶产区受到战争影响，茶叶生产与外销面临严重困难。为维持出口和获取外汇，茶叶收购、加工和运输逐渐转向统筹经营。',
    channels: '上海等传统出口中心受阻后，部分茶叶转由香港等口岸外销，并开展对苏易货贸易。云南、福建等地建设和改造茶厂，红茶、砖茶等产品承担出口换汇和物资交换任务。',
    impact: '茶叶出口不仅关系茶农生计，也成为战时换取外汇和物资的重要渠道。交通中断与市场变化同时推动了茶叶生产组织、机械加工和贸易管理方式的转变。',
    sourceRefs: [
      'https://www.chinacoop.gov.cn/HTML/2009/10/12/35590.html',
      'https://lzhbwg.mofcom.gov.cn/edi_ecms_web_front/thb/detail/e95f006b56c0415abda6be7945679c23',
    ],
  },
};

const ROUTE_DYNASTIES = [
  { name: '唐代', start: 618, end: 959 },
  { name: '宋代', start: 960, end: 1270 },
  { name: '元代', start: 1271, end: 1367 },
  { name: '明代', start: 1368, end: 1643 },
  { name: '清代', start: 1644, end: 1936 },
  { name: '抗战时期', start: 1937, end: 1945 },
];

function dynastyForRouteYear(year) {
  const y = Number(year);
  if (!Number.isFinite(y) || y <= ROUTE_DYNASTIES[0].start) return '唐代';
  for (const dynasty of ROUTE_DYNASTIES) {
    if (y >= dynasty.start && y <= dynasty.end) return dynasty.name;
  }
  return y > 1945 ? '抗战时期' : '清代';
}

function routeVia(route) {
  const names = (route.points || []).slice(1, -1).map(point => point.name).filter(Boolean);
  return names.length ? names : [];
}

function routePeriod(route, startDynasty, endDynasty) {
  if (route.yearText) return route.yearText;
  return startDynasty === endDynasty ? startDynasty : `${startDynasty}至${endDynasty}`;
}

function buildHistoricalBackground(route, startDynasty, endDynasty) {
  const span = startDynasty === endDynasty ? startDynasty : `${startDynasty}至${endDynasty}`;
  const network = /海上|海运/.test(route.type)
    ? '沿海港口、远洋航线与海外市场相互连接'
    : '内地产区、沿途商埠与边疆市场相互连接';
  return `${span}的茶叶流通不断扩展，${network}。这条由${route.origin}通往${route.destination}的路线，反映了当时茶叶生产、转运和消费网络的具体变化。原有记录指出：${route.note}`;
}

function buildRouteStory(route, period, via) {
  const viaText = via.length ? `，途经${via.join('、')}` : '';
  const transport = /海上|海运/.test(route.type)
    ? '商船依靠季风、港口补给和跨区域转运完成航程'
    : '商队借助驿道、河运与沿途集散地接续运输';
  return `${period}，茶叶从${route.origin}出发${viaText}，最终抵达${route.destination}。${transport}。${route.note} 这一记录把路线上的地点、贸易参与者与当时的市场变化联系起来。`;
}

function buildTradeSignificance(route) {
  return /海上|海运/.test(route.type)
    ? `该航线扩大了${route.origin}与${route.destination}之间的商品往来，使中国茶进入更广阔的海外消费和转口网络。`
    : `该商道加强了${route.origin}与${route.destination}之间的物资交换，并推动茶叶在边疆及欧亚内陆市场持续流通。`;
}

// 150 条原始记录全部在此规范为统一详情结构。每条路线的叙事都使用其
// 自身年代、起终点、途经节点和原始史实，不修改任何 points 坐标。
export const TEA_TRADE_DATA = RAW_TEA_TRADE_DATA.map((route, rawIndex) => {
  const startDynasty = dynastyForRouteYear(route.startYear);
  const endDynasty = dynastyForRouteYear(route.endYear == null ? route.startYear : route.endYear);
  const via = routeVia(route);
  const period = routePeriod(route, startDynasty, endDynasty);
  const routeType = /海上|海运/.test(route.type) ? '海路' : '陆路';
  return {
    ...route,
    id: route.id,
    title: route.title || `${route.origin}至${route.destination}茶叶贸易路线`,
    routeType,
    dynasty: startDynasty === endDynasty ? startDynasty : `${startDynasty}至${endDynasty}`,
    startDynasty,
    endDynasty,
    startYear: route.startYear,
    endYear: route.endYear,
    origin: route.origin,
    destination: route.destination,
    via,
    historicalBackground: route.historicalBackground || buildHistoricalBackground(route, startDynasty, endDynasty),
    routeStory: route.routeStory || buildRouteStory(route, period, via),
    tradeSignificance: route.tradeSignificance || buildTradeSignificance(route),
    sourceRefs: route.sourceRefs || (route.source ? [route.source] : []),
    rawIndex,
  };
});

// ============================================================
// 历史事件（来自"故事.docx"）
// ============================================================
export const HISTORICAL_EVENTS = {
  "唐代": [
    "公元641年，文成公主远嫁吐蕃，嫁妆里不仅有佛经、医药、种子、工匠，还带了一样看似不起眼却改变了高原命运的东西——茶叶。",
    "藏民世代以牛羊肉和奶制品为食，缺乏蔬菜，茶一进入藏区，立刻被发现能消食解腻。",
    "唐德宗年间，大臣常鲁公出使吐蕃，在帐中煮茶。吐蕃赞普让侍从拿出多种茶叶说：'我亦有之——此寿州者，此舒州者，此顾渚者……'湖南、湖北、安徽、浙江、四川的茶，那时已顺着古道进了藏。",
    "赞普专门设立'汉地五茶商'管理唐蕃茶马贸易。"
  ],
  "宋代": [
    "北宋常年缺少优良战马，西夏占据河西、契丹把控北方牧场，中原传统养马场地尽数丢失。朝廷找到一条破局之路：以内地茶叶交换藏区良马。",
    "1074年，宋神宗设立成都榷茶司、秦州买马司，统筹全国茶马交易。北宋西北茶马司每年以川茶交换战马两万匹以上。"
  ],
  "元代": [
    "元代延续了茶马贸易制度，但规模有所缩减。蒙古统治者对茶马贸易的管控相对宽松。"
  ],
  "明代": [
    "明代出台严苛律法，明文规定：'凡犯私茶者与私盐同罪'，走私茶叶重者论死，茶马贸易彻底上升为国家边防战略。",
    "川藏道、滇藏道、青藏道三条茶马主线完整成型。"
  ],
  "清代": [
    "清顺治十八年，五世达赖喇嘛上书朝廷，请求在云南北胜州开设茶马互市，获清廷准许，普洱茶自此大规模运往西藏。",
    "随着清朝实现全国大一统，延续数百年的官营茶马制度逐步放开，民间自由贸易成为主流。",
    "乾隆二十五年，朝廷裁撤全国各地茶马司，近七百年官方主导的茶马互市正式退出历史舞台。",
    "官办体系落幕，但茶马古道并未衰败，反而迎来民间商贸鼎盛期。清代鼎盛阶段，每年经康定出关销往藏区的川茶超过1400万斤。",
    "普洱茶、川南边茶源源不断输入雪域，藏地的药材、羊毛、马匹也顺着古道销往内地，丽江、大理、康定等沿线商贸城镇空前繁荣。"
  ],
  "抗战时期": [
    "1942年，滇缅公路被日军切断，国内大后方海外援华补给通道断绝，抗战物资供给陷入绝境。",
    "危急时刻，千年茶马古道扛起重任，成为彼时唯一可运输国际物资的陆上通道。",
    "丽江参与运输的骡马规模从四五千匹暴涨至一万匹，年运输物资超1000吨，商贸总值达千万元。小小的丽江城内新增1200多家商号，中央银行等9家金融机构纷纷入驻。",
    "马背上的货物早已不止茶叶：药品、轮胎、汽油、机械零件络绎不绝入滇，每一队马帮，都驮着支撑抗战的生命补给。",
    "2013年，茶马古道被列入全国重点文物保护单位。"
  ]
};

// ============================================================
// 朝代映射
// ============================================================
const DYNASTY_MAP = {
  "唐代": [618, 907],
  "宋代": [960, 1279],
  "元代": [1271, 1368],
  "明代": [1368, 1644],
  "清代": [1644, 1911],
  "抗战时期": [1937, 1945]
};

export function getDynasty(year) {
  for (const [name, [start, end]] of Object.entries(DYNASTY_MAP)) {
    if (year >= start && year <= end) return name;
  }
  return null;
};

export function getEventsByYear(year) {
  const dynasty = getDynasty(year);
  if (!dynasty) return [];
  return HISTORICAL_EVENTS[dynasty] || [];
};
