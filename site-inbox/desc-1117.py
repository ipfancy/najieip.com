import os, json
p = os.path.expanduser("~/wiki/najieip-verify/articles.json")
raw = open(p, encoding="utf-8").read()
old = '"description": "德芙被罚80万，罚单上却不是德芙：广告法罚的是角色，不是商标"'
new_desc = ("德芙被罚80万，罚单当事人却是第三方代运营上海宗正食品。广告法第2条按行为认定「广告主」，第9条第7项定性、"
            "第57条罚20万至100万；今年前三季度全国广告违法案均值4888元，本案是均值的164倍。代运营合同要写负面清单、"
            "终审留痕与全额追偿，但改不了对外的行政当事人认定。")
new = '"description": ' + json.dumps(new_desc, ensure_ascii=False)
assert raw.count(old) == 1, raw.count(old)
raw = raw.replace(old, new)
json.loads(raw)
open(p, "w", encoding="utf-8").write(raw)
print("desc updated; entries", len(json.loads(raw)))
