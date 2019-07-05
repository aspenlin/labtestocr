import re
from tesserocr import PyTessBaseAPI
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# initialize the dicts for different tests
def tests_dict():
	#create a dict for regular expression
	# the choice of keys here are important 
	# because only them will be used later for fuzzy match
	urine_dict = {}
	urine_dict['尿胆原'] = ['尿胆原','尿胆原\(URO\)','尿胆原\(UBG\)','尿胆原\s*URO']
	urine_dict['胆红素'] = ['胆红素','尿胆红素','胆红素\s*\(BIL\)','胆红素\s*BIL']
	urine_dict['酮体'] = ['酮体','尿酮体','酮体 \(KET\)','酮 体','酮体\(KET\)','酮体\s*KET']
	urine_dict['隐血'] = ['血','隐血','潜血','尿隐血','尿潜血','隐血或红细胞\(BLD\)','尿潜血\(BLD\)','隐血\s*BLD']
	urine_dict['尿蛋白'] = ['蛋白质','尿蛋白','蛋白质\(PRO\)','蛋白','蛋白质\s*PRO']
	urine_dict['亚硝酸盐'] = ['亚硝酸盐','尿亚硝酸盐','亚硝酸盐\(NIT\)','亚硝酸\s*NIT']
	urine_dict['葡萄糖'] = ['葡萄糖','尿糖','尿葡萄糖','尿糖\(GLU\)','葡萄糖\s*GLU']
	urine_dict['比重'] = ['比重','尿比重','比重 \(SG\)','比 重','比重\(SG\)']
	urine_dict['酸碱度'] = ['酸碱度','尿PH值','尿酸碱度','PH','酸碱度\(PH\)','尿PH','pH值\(PH\)','酸碱度\(pH\)','酸碱度\s*PH']
	urine_dict['颜色'] = ['颜色','颜色\s*\(COLOR\)','尿液外观']
	urine_dict['浑浊度'] = ['浊度','浑浊度','透明度\(TMD\)','透明度','尿透明度','外观','清晰度']
	urine_dict['电导率'] = ['电导率','电导率\s*Cond']
	urine_dict['电导率信息'] = ['电导率分级','电导率信息']
	urine_dict['结晶'] = ['结晶','结晶数量','结晶标记']
	urine_dict['类酵母菌'] = ['类酵母菌','类酵母细胞数量','类酵母细胞标记','酵母样菌','类酵母细胞数量\s*YLC']
	urine_dict['粘液丝'] = ['粘液丝','粘液丝数量','粘液','粘液丝数量\s*MCLS']
	urine_dict['细菌'] = ['细菌计数','细菌','细菌\s*BACT']
	urine_dict['维生素C'] = ['VC','维生素C','维生素C\s*VC']
	urine_dict['完整红细胞比率'] = ['完整红细胞比率','完整红细胞百分比','完整红细胞百分比\s*NL-RBC%']
	urine_dict['完整红细胞数量'] = ['完整红细胞数量','完整红细胞绝对值','完整红细胞绝对值\s*NL-RBC#']
	urine_dict['尿路感染信息'] = ['尿路感染信息']
	urine_dict['尿钙'] = ['尿钙']
	urine_dict['精子'] = ['精子']
	urine_dict['其他有形成份'] = ['其他有形成份']
	urine_dict['70%红细胞平均体积'] = ['70%红细胞平均体积','70%红细胞平均体积\s*RBC-P70']
	urine_dict['白细胞(高倍视野)'] = ['白细胞\(HPF\)','白细胞\(高倍\)','每高倍视野白细胞数','白细胞\(高倍视野\)']
	urine_dict['红细胞(高倍视野)'] = ['红细胞\(高倍\)','红细胞\(HPF\)','每高倍视野白细胞数','红细胞\(高倍视野\)','红细胞\s*(RBC)']
	urine_dict['上皮细胞(高倍视野)'] = ['上皮细胞\(高倍视野\)','上皮细胞\(高倍\)','每高倍视野上皮细胞数']
	urine_dict['红细胞信息'] = ['红细胞信息','红细胞形态信息','红细胞形态变异信息','红细胞信息\s*info']
	urine_dict['红细胞镜检'] = ['直接镜检-红细胞','镜检红细胞','红细胞\(镜检\)','镜检：红细胞\(RBC\)','红细胞镜检']
	urine_dict['白细胞镜检'] = ['直接镜检-白细胞','镜检白细胞','白细胞\(镜检\)','镜检：白细胞','白细胞镜检']
	urine_dict['上皮细胞镜检'] = ['上皮细胞\(镜检\)','上皮细胞镜检']
	urine_dict['小圆上皮细胞'] = ['小圆上皮','小圆上皮细胞','小圆上皮细胞标记','小圆上皮细胞数量','小圆细胞','上皮细胞','上皮细胞计数']
	urine_dict['管型'] = ['管型','管型计数','管型计数\s*\(CAST\)','管型\s*CAST']
	urine_dict['病理管型'] = ['病理管型','病理管型\s*P.CAST','病理管型标记']
	urine_dict['管型低倍'] =['管型低倍','管型\(低倍视野\)','管型\(低倍\)','管型\s* \(LPF\)','每低倍视野透明管型数']
	urine_dict['透明管型镜检'] = ['透明管型\(镜检\)','透明管型','镜检：透明管型','直接镜检-管型','透明管型']
	urine_dict['颗粒管型镜检'] = ['颗粒管型\(镜检\)','颗粒管型','镜检：粒状管型']
	urine_dict['细胞管型镜检'] = ['细胞管型\s*\(镜检\)']
	# pos/neg
	urine_dict['白细胞'] = ['白细胞','白细胞\(LEU\)','尿白细胞\(LEU\)','白细胞\s*WBC']
	# count
	urine_dict['白细胞计数'] = ['白细胞计数','白细胞计数(WBC)','白细胞\(UF\)','白细胞\(UF-1000i\)','白细胞','白细胞\(UF\)\s*WBC\(UF\)','尿白细胞计数']
	urine_dict['红细胞计数'] = ['红细胞计数','红细胞计数(RBC)','红细胞计数\s*\(RBC\)','红细胞\(UF\)','红细胞','尿红细胞计数']
	# sort the names according to their length, longest name first
	for k, names in urine_dict.items():
	    names.sort(key = lambda s: -len(s))
	# names of the tests as a list
	urine_tests = list(urine_dict.keys())
	# result is the dict where we store test names and values, 
	# initial value is None
	result = {}
	for test in urine_tests:
	    result.setdefault(test, [])
	return urine_dict, result

def result(img):
	# text result from tesseract
	text, text_split, characters, confidences = ocr(img)
	# tests dict and list
	urine_dict, result = tests_dict()
	return perfect_match(text, text_split, characters, confidences, urine_dict, result)

def conf_score(name, value, characters, confidences):
    index = characters.find(name.replace(' ', ''))
    length_name = len(name.replace(' ', ''))
    start = index + length_name
    end = index + length_name + len(value)
    c_sum = 0
    for i in range(start, end):
    	c_sum = c_sum + confidences[i]
    return c_sum/(len(value)*100)

def perfect_match(text, text_split, characters, confidences, urine_dict, result):
	# find the perfect match for test names
	for k, names in urine_dict.items():
	    for name in names:
	        value = re.findall(''.join([name, '(\s*)(\S{1,6})']), text)
	        if value:
	            result[k].append(value[0][1])
	            c = conf_score(name, value[0][1], characters, confidences)
	            result[k].append(c)

	            break
	return fuzzy_match(text, text_split, characters, confidences, result)

def fuzzy_match(text, text_split, characters, confidences, result):
	# fuzzy match the name of the tests, these names are from result.keys()
	for k, v in result.items():
		# if perfect match didn't find anything for a certain test
	    if not v:
	        fuzzy = process.extractOne(k, text_split, scorer=fuzz.ratio)
	        # if string matching acore is higher than 60
	        if fuzzy[1] >= 60:
	            name = fuzzy[0]

	            # add \ in front of ( and ) for regular expression
	            name_copy = name
	            if '(' in name:
	                    index = name.find('(')
	                    name = name[:index] + '\\' + name[index:]
	            if ')' in name:
	                    index = name.find(')')
	                    name = name[:index] + '\\' + name[index:]
	            # use regular expression to match the value of tests
	            value = re.findall(''.join([name, '(\s*)(\S{1,6})']), text)
	            if value:
	                result[k].append(value[0][1])
	                c = conf_score(name_copy, value[0][1], characters, confidences)
	                result[k].append(c*fuzzy[1]/100)



	char_allowed = '0123456789.+-()尿路感染?红色性弱阴阳未见异常提示检出无<= 清\
	分类正常见浅微黄澄清晰浑浊非均一型红细胞级NORMALNEGnegnormal/HP'
	# in preparation for jsonify
	rl = []
	for k, v in result.items():
	    r = {}
	    r['test_name'] = k
	    if v:
		    r['value'] = v[0]
		    r['confidence'] = v[1]
		    for c in v[0]:
		    	if c not in char_allowed:
		    		r['confidence'] = 0
		    		break
	    else:
		    r['value'] = ''
		    r['confidence'] = ''
	    rl.append(r)
	# return a list of dictionary 
	# with test_name/value as keys and their values as values
	return rl


def ocr(img):
	img = img
	with PyTessBaseAPI(lang='chi_sim', psm=6) as api:
	    api.SetVariable('tessedit_char_whitelist','<=?+().^~\
	    尿液分析胆原红素酮体血蛋白质亚硝酸盐细胞葡萄糖比重碱度镜检上皮管型结晶其他有形成份阴\
	    性无结果项目名称参考区间单位颜色黄浊清～/值隐-位相电导率仅供类酵母菌粘液丝计数病理量信息完整高倍提示低潜正常浑\
	    酯酶小圆非均一级标记视野平体积百阳微透明澄浅直接未见异维生外观晰个路感染态受损滴虫霉菌每鳞状柱粒草肌酐钙\
	    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	    api.SetVariable('preserve_interword_spaces','1')
	    api.SetImageFile(img)
	    # get text without space and confidence level of each char
	    api.Recognize()
	    words = api.MapWordConfidences()
	    characters = ''.join([word[0] for word in words])
	    characters = characters.replace(' ','')
	    confidences = []
	    for word in words:
	    	length = len(word[0].replace(' ',''))
	    	for i in range(length):
	    		confidences.append(word[1])
	    # tesseract result
	    text = api.GetUTF8Text()

	# remove space after dot, which is a common error in tesseract result
	num = 0
	for i in range(len(text)-1):
	    if num+i >= len(text)-1:
	        break
	    if (text[i] == '.') & (text[1+i] == ' '):
	        num += 1
	        text = text[:i+1] + text[i+2:]
	#split the text as a list of strings
	text_split = text.split()
	return text, text_split, characters, confidences







