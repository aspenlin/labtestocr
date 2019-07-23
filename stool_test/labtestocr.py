import re
from tesserocr import PyTessBaseAPI
from wand.image import Image
from fuzzywuzzy import fuzz, process

class stooltest:
    
    def __init__(self, imgpath, width_pixel=3000):
        # path of the image, a string
        self.imgpath = imgpath
        # width pixel expected, if resize the image if image smaller than this
        self.width_pixel = width_pixel
        # dict of tests' names and their variations
        self.test_items_dict = self.test_items_dict()
        # dict to be returned, contains test_names/value/confidences
        self.result_dict = self.result_dict()
        # whitelist for different kinds of labtest, for example, we'll have one for bloodtest
        # one for stooltest and one for urinetest, respectively
        self.whitelist = self.whitelist()
        # chars allowed in values, if not allowed, will set the confidence level to 0
        self.result_char_allowed = self.result_char_allowed()
        # result of tesseractocr
        self.text, self.text_split, self.characters, self.confidences = self.tess_result()

    def whitelist(self):
        return '()+-、\
                颜色硬度大便性状外观镜下白细胞红脓上皮其他脂肪滴球隐血试验群轮病毒草绿黄棕\
                软糊弱阴阳寄生原虫卵霉菌孢子体未见异常检出\
                肌肉纤维植物颗粒它抗水粘液淀粉样本胶体金法\
                abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def result_char_allowed(self):
        return '草绿棕黄红色糊状弱阴阳性粘液稀软水样便0123456789+-~～\
                未检出见异常() /HP少量'
        
    def test_items_dict(self):
        stool_dict = {}
        stool_dict['颜色'] = ['颜色','外观','颜色形态','颜色\s*\(\s*Colour\s*\)']
        stool_dict['性状'] = ['性状','大便性状','硬度','外观','性状\s*\(\s*Colour\s*\)']
        stool_dict['粘液'] = ['粘液','粘液\s*\(\s*Mucus\s*\)']
        stool_dict['白细胞'] = ['白细胞','镜下白细胞','白细胞\s*\(\s*WBC\s*\)','\(\s*白细胞\s*\)']
        stool_dict['红细胞'] = ['红细胞','镜下红细胞','红细胞\s*\(\s*RBC\s*\)','\(\s*红细胞\s*\)']
        stool_dict['脓细胞'] = ['脓细胞','脓球']
        stool_dict['上皮细胞'] = ['上皮细胞']
        stool_dict['植物细胞'] = ['\(\s*植物细胞\s*\)','植物细胞\s*\(\s*Plant\s*cells\s*\)']
        stool_dict['肌肉纤维'] = ['\(\s*肌肉纤维\s*\)']
        stool_dict['脂肪球'] = ['脂肪滴','脂肪球','\(\s*脂肪球\s*\)','脂肪球\s*\(\s*Fat\s*globules\s*\)']
        stool_dict['结合脂肪酸'] = ['结合脂肪酸\s*\(\s*Conjugated\s*fattvacid\s*\)']
        stool_dict['隐血'] = ['隐血','隐血试验','血','潜血\s*\(\s*FOB\s*\)']
        stool_dict['吞噬细胞'] = ['便吞噬细胞']
        stool_dict['寄生虫'] = ['寄生虫','寄生原虫','寄生虫虫体','寄生虫\s*\(\s*成虫\s*\)\s*卵检查']
        stool_dict['虫卵'] = ['虫卵','\(\s*虫卵\s*\)','虫卵\s*\(\s*Parasite\s*ova\s*\)']
        stool_dict['轮状病毒'] = ['A群轮状病毒\s*\(\s*胶体金法\s*\)','A群轮状病毒抗原','A群轮状病毒抗原测定','轮状病毒','快速轮状病毒鉴定','轮状病毒']
        stool_dict['霉菌'] = ['霉菌','霉菌孢子']
        stool_dict['淀粉颗粒'] = ['淀粉样体','\(\s*淀粉样颗粒\s*\)','淀粉颗粒\s*\(\s*Starch\s*granule\s*\)']
        stool_dict['其他'] = ['其他','\(\s*其它成份\s*\)']
#       sort the different names, longest first, thus reducing error when doing regex
        for k, v in stool_dict.items():
            v.sort(key = lambda s: -len(s))
        return stool_dict
    
    # initialize a dict for holding the result
    def result_dict(self):
        result = {}
        tests = list(self.test_items_dict.keys())
        [result.setdefault(test, []) for test in tests]
        return result
    
    # process image (resize and add border) and save the processed image
    def image_process(self): 
        with Image(filename=self.imgpath) as img:
        #     get the original image width
            pixel_x = img.size[0]
        #     how many times we need to scale up/down
            scale = int(self.width_pixel / pixel_x)
            if scale < 1:
                scale = 1
            with img.clone() as i:
        #         resize image to this width and this height
                i.resize(int(i.width * scale), int(i.height * scale))
        #     add a 5*5pixel black border to the image, this will in general increase the accuracy of tesseract
                i.border('black', 5, 5)
                if self.imgpath[-4] == '.':
                    self.imgpath = ''.join([self.imgpath[:-4], '_processed', self.imgpath[-4:]])
                else:
                    self.imgpath = ''.join([self.imgpath[:-5], '_processed', self.imgpath[-5:]])
                i.save(filename=self.imgpath)
                
    # getting result from tesseract
    def tess_result(self):
        with PyTessBaseAPI(lang='chi_sim',psm=6) as api:
            api.SetVariable('tessedit_char_whitelist',self.whitelist)
            api.SetVariable('preserve_interword_spaces','1')
            api.SetImageFile(self.imgpath)
            text = api.GetUTF8Text()
            characters, confidences = self.get_characters_and_confidences(api)

        
        # remove space after dot, which is a common error in tesseract result
        text = self.remove_space_after_dot(text)
        #split the text as a list of strings, for fuzzy match later
        text_split = text.split()
        return text, text_split, characters, confidences
    
    def perfect_match(self):
    # find the perfect match for test names
        for k, names in self.test_items_dict.items():
            for name in names:
                value = re.findall(self.regex_rule(name), self.text)
                if value:
                    self.result_dict[k].append(value[0][1])
                    conf = self.conf_score(name, value[0][1])
                    self.result_dict[k].append(conf)
                    break

    def fuzzy_match(self):
        for k, v in self.result_dict.items():
            # if perfect match didn't find anything for a certain test
            if not v:
                fuzzy = process.extractOne(k, self.text_split, scorer=fuzz.ratio)
                # go through all the different variations of names, find the one with highest score 
                for name in v:
                    fuzzy_new = process.extractOne(name, self.text_split, scorer=fuzz.ratio)
                    if fuzzy_new[1] > fuzzy[1]:
                        fuzzy = fuzzy_new
                # if string matching acore is higher than 60
                if fuzzy[1] >= 60:
                    match = fuzzy[0]
                    match_copy = match
                    match = self.convert_for_regex(match)
                    value = re.findall(self.regex_rule(match), self.text)
                    if value:
                        self.result_dict[k].append(value[0][1])
                        conf = self.conf_score(match_copy, value[0][1])
                        self.result_dict[k].append(conf*fuzzy[1]/100)

    # the method to be called to return the final result
    def result(self):
        self.image_process()
        self.perfect_match()
        self.fuzzy_match()
        self.save_text()
        result_list = []
        for k, v in self.result_dict.items():
            item = {}
            item['test_name'] = k
            if v:
                item['value'] = v[0]
                item['confidence'] = v[1]
                for c in v[0]:
                    if c not in self.result_char_allowed:
                        item['confidence'] = 0
                        break
            else:
                item['value'] = ''
                item['confidence'] = ''
            result_list.append(item)
        # return a list of dictionary 
        # with test_name/value/confidences as keys and their values as values
        return result_list

    # save tesseract result as .txt file for debug purpose
    def save_text(self): 
        print('text saved')   
        if self.imgpath[-4] == '.':
            txt_filename = ''.join([self.imgpath[:-4], '.txt'])
        else:
            txt_filename = ''.join([self.imgpath[:-5], '.txt'])
        with open(txt_filename, 'rd') as file:
            file.write(self.text)
    
    # get text without space and confidence level of each char
    def get_characters_and_confidences(self, api):
        api.Recognize()
        words = api.MapWordConfidences()
        characters = ''.join([word[0] for word in words])
        characters = characters.replace(' ','')
        confidences = []
        for word in words:
            length = len(word[0].replace(' ',''))
            for i in range(length):
                confidences.append(word[1])
        return characters, confidences
    
    # remove space after dot, which is a common error in tesseract result
    def remove_space_after_dot(self, text):
        num = 0
        for i in range(len(text)-1):
            if num+i >= len(text)-1:
                break
            if (text[i] == '.') & (text[1+i] == ' '):
                num += 1
                text = text[:i+1] + text[i+2:]
        return text
    
    # calculate conf score for a string in tesseract result
    def conf_score(self, match, value):
        index = self.characters.find(match.replace(' ', ''))
        length_match = len(match.replace(' ', ''))
        start = index + length_match
        end = index + length_match + len(value)
        conf, total = 0, 100*len(value)
        for i in range(start, end):
            conf += self.confidences[i]
        return conf/total
    
    # adding \ before ( or ) for regex
    def convert_for_regex(self, match):
        if '(' in match:
            index = match.find('(')
            match = match[:index] + '\\' + match[index:]
        if ')' in match:
            index = match.find(')')
            match = match[:index] + '\\' + match[index:]
        return match

    def regex_rule(self, name):
        return ''.join([name, '(\s*)(\S{1,6})'])



class urinetest(stooltest):

    def whitelist(self):
        return '<=?+().^~\
                尿液分析胆原红素酮体血蛋白质亚硝酸盐细胞葡萄糖比重碱度镜检上皮管型结晶其他有形成份阴\
                性无结果项目名称参考区间单位颜色黄浊清～/值隐-位相电导率仅供类酵母菌粘液丝计数病理量信息完整高倍提示低潜正常浑\
                酯酶小圆非均一级标记视野平体积百阳微透明澄浅直接未见异维生外观晰个路感染态受损滴虫霉菌每鳞状柱粒草肌酐钙\
                abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def result_char_allowed(self):
        return '0123456789.+-()尿路感染?红色性弱阴阳未见异常提示检出无<= 清\
                分类正常见浅微黄澄清晰浑浊非均一型红细胞级NORMALNEGnegnormal/HP'

    def test_items_dict(self):
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
        urine_dict['红细胞(高倍视野)'] = ['红细胞\(高倍\)','红细胞\(HPF\)','每高倍视野红细胞数','红细胞\(高倍视野\)','红细胞\s*(RBC)']
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
        for k, v in urine_dict.items():
            v.sort(key = lambda s: -len(s))
        return urine_dict


class bloodtest(stooltest):
# '肺炎支原体IgM/C反应蛋白' sometimes give not digital result, other tests give number as results
    def regex_rule(self, name):
        exceptions = self.test_items_dict['肺炎支原体IgM'] + self.test_items_dict['C反应蛋白']
        if all(e not in name for e in exceptions):
            return ''.join([name, '(\D*)(\d+\.?\d{0,3})'])
        else:
            return ''.join([name, '(\s*)(\S{1,3})'])

    def whitelist(self):
        return '<=-～()+-abcdefghijklmnopqrstuvwxyz/\
                葡萄糖白细胞计数中性目百变异系标准差网织率总比↑\
                ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.\
                %淋巴细胞单核细胞嗜酸粒细胞碱绝对值红蛋血压积平均体积量\
                浓度分布宽小板体性沉大'

    def result_char_allowed(self):
        return '0123456789.+-()弱阴阳性↑'

    def test_items_dict(self):
        blood_dict = {}
        blood_dict['C反应蛋白'] = ['CRP','C-反应蛋白','C反应蛋白']
        blood_dict['白细胞计数'] = ['白细胞计数','白细胞数目','白细胞数目\s*WBC','白细胞']
        blood_dict['红细胞计数'] = ['红细胞计数','红细胞数目','红细胞数目\s*RBC','红细胞']
        blood_dict['中性粒细胞百分比'] = ['中性粒细胞%','中性粒细胞百分比','中性粒细胞百分比\s*Neu%','中性粒细胞比率','嗜中性粒细胞比值']
        blood_dict['中性粒细胞绝对值'] = ['中性粒细胞绝对值','中性粒细胞#','中性粒细胞数目','中性粒细胞数目\s*Neu#','中性粒细胞计数','中性粒细胞数','嗜中性粒细胞数','中性细胞数']
        blood_dict['中间细胞绝对值'] = ['中间细胞绝对值']
        blood_dict['中间细胞百分比'] = ['中间细胞百分比']
        blood_dict['淋巴细胞百分比'] = ['淋巴细胞%','淋巴细胞百分比','淋巴细胞百分比\s*Lym%','淋巴细胞比值','淋巴细胞比率']
        blood_dict['淋巴细胞绝对值'] = ['淋巴细胞#','淋巴细胞数目','淋巴细胞数目\s*Lym#','淋巴细胞计数','淋巴细胞数','淋巴细胞绝对值']
        blood_dict['单核细胞百分比'] = ['单核细胞%','单核细胞百分比','单核细胞百分比\s*Mon%','单核细胞比值']
        blood_dict['单核细胞绝对值'] = ['单核细胞绝对值','单核细胞#','单核细胞数目','单核细胞数目\s*Mon#','单核细胞计数','单核细胞数','单核细胞']
        blood_dict['嗜酸性粒细胞百分比'] = ['嗜酸粒细胞%','嗜酸性粒细胞%','嗜酸性粒细胞百分比','嗜酸性粒细胞百分比\s*Eos%','嗜酸性粒细胞比值','嗜酸性细胞百分比','嗜酸性粒细胞比率']
        blood_dict['嗜碱性粒细胞百分比'] = ['嗜碱粒细胞%','嗜碱性粒细胞%','嗜碱性粒细胞百分比','嗜碱性粒细胞百分比\s*Bas%','嗜碱性粒细胞比值','嗜碱性细胞百分比','嗜碱性粒细胞比率']
        blood_dict['嗜酸粒细胞绝对值'] = ['嗜酸粒细胞绝对值','嗜酸性粒细胞绝对值#','嗜酸性粒细胞数目','嗜酸性粒细胞数目\s*Eos#','嗜酸性粒细胞计数','嗜酸性粒细胞数','嗜酸性细胞计数','嗜酸性粒细胞']
        blood_dict['嗜碱粒细胞绝对值'] = ['嗜碱粒细胞绝对值','嗜碱性粒细胞绝对值#','嗜碱性粒细胞数目','嗜碱性粒细胞数目\s*Bas#','嗜碱性细胞计数','嗜碱性细胞','嗜碱性细胞数','嗜碱性细胞计数','嗜碱性粒细胞']
        blood_dict['血红蛋白'] = ['血红蛋白','血红蛋白测定','血红蛋白\s*HGB','血红蛋白浓度']
        blood_dict['血红蛋白分布宽度'] = ['血红蛋白分布宽度']
        blood_dict['红细胞压积'] = ['红细胞压积','红细胞压积\s*HCT','红细胞比积']
        blood_dict['平均红细胞体积'] = ['平均红细胞体积','平均红细胞体积\s*MCV','红细胞平均体积']
        blood_dict['平均血红蛋白量'] = ['平均血红蛋白量','平均红细胞血红蛋白含量','平均红细胞血红蛋白含量\s*MCH','平均红细胞血红蛋白量','平均红细胞血红蛋白','平均RBC血红蛋白量','平均红细胞Hb含量']
        blood_dict['平均血红蛋白浓度'] = ['平均血红蛋白浓度','平均红细胞血红蛋白浓度','平均红细胞血红蛋白浓度\s*MCHC','平均RBC血红蛋白浓度','平均红细胞Hb浓度']
        blood_dict['单个细胞血红蛋白浓度'] = ['单个细胞血红蛋白浓度']
        blood_dict['单个细胞血红蛋白'] = ['单个细胞血红蛋白']
        blood_dict['红细胞分布宽度'] = ['红细胞分布宽度','红细胞体积分布-W','红细胞体积分布宽度']
        blood_dict['红细胞分布宽度变异系数'] = ['红细胞分布宽度变异系数','红细胞分布宽度变异系数\s*RDW-CV','红细胞分布宽度\s*CV','红细胞分布宽度变异','RBC分布宽度变异系数','RDW-CV']
        blood_dict['红细胞分布宽度标准差'] = ['红细胞分布宽度标准差','红细胞分布宽度标准差\s*RDW-SD','红细胞分布宽度\s*','RBC分布宽度标准差']
        blood_dict['血小板计数'] = ['血小板计数','血小板数目','血小板数目\s*PLT','血小板']
        blood_dict['血小板压积'] = ['血小板压积','血小板压积\s*PCT','血小板比积']
        blood_dict['平均血小板体积'] = ['平均血小板体积','平均血小板体积\s*MPV']
        blood_dict['大型血小板比率'] = ['大型血小板比率']
        blood_dict['血小板分布宽度'] = ['血小板分布宽度','血小板体积分布-W','血小板分布宽度\s*PDW','血小板平均分布宽度','血小板体积分布宽度']
        blood_dict['血淀粉样蛋白A'] = ['血淀粉样蛋白A','血清淀粉样蛋白A']
        blood_dict['肺炎支原体IgM'] = ['肺炎支原体IgM']
        blood_dict['红细胞比容'] = ['红细胞比容测定','红细胞比容']
        blood_dict['网织红细胞计数'] = ['网织红细胞计数']
        blood_dict['网织红细胞百分比'] = ['网织红细胞百分比']
        blood_dict['网织红细胞血红蛋白含量'] = ['网织红细胞血红蛋白含量']
        blood_dict['未染色大细胞百分比'] = ['未染色大细胞百分比']
        blood_dict['随机葡萄糖测定'] = ['随机葡萄糖测定']
        for k, v in blood_dict.items():
            v.sort(key = lambda s: -len(s))
        return blood_dict




















    