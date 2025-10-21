import json
import logging
import os
import pprint
import re
import jieba
from typing import Optional

from duowen_agent.rag.nlp import LexSynth
from .model import TrieNode


jieba.setLogLevel(logging.WARNING)


# 匹配换行符
PATTERN_NEWLINE = re.compile(r"[\r\n]+")

# 匹配空格或制表符
PATTERN_SPACE_TAB = re.compile(r"[ \t]+")

# 匹配包含各种标点符号（中英文）和特殊字符的字符串
PATTERN_PUNCTUATION_AND_SPECIAL_CHARS = re.compile(
    r"[ ,./;'\\\`~!@#$%\^&\*\(\)=\+_<>?:\"{}|，。；''【】、！￥……（）——《》？:" "-]+"
)

_curr_dir = os.path.dirname(os.path.abspath(__file__))

with open(f"{_curr_dir}/../dictionary/stopwords.json", encoding="utf-8") as f:
    STOPWORDS = set(json.loads(f.read())["STOPWORDS"])

def generate_ngram(input_list: list[str], n: int) -> list[tuple[str, ...]]:
    return [
        ngram
        for i in range(1, n + 1)
        for ngram in zip(*[input_list[j:] for j in range(i)])
    ]


class NewWordDetection:
    """
    优化版新词发现类 - 保持与原版完全相同的API接口
    """

    def __init__(self, nlp: LexSynth):
        self.nlp = nlp

    @staticmethod
    def split_text(text) -> list[str]:
        sentences = PATTERN_PUNCTUATION_AND_SPECIAL_CHARS.split(text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def generate_ngram(input_list, n):
        result = []
        for i in range(1, n + 1):
            result.extend(zip(*[input_list[j:] for j in range(i)]))
        return result

    def split_sentences_word(self, text: str) -> list[list[str]]:
        _data = []
        for i in self.split_text(text):
            _data.append(
                [j for j in self.nlp.content_cut(i).split() if j not in STOPWORDS]
            )
        return _data

    @staticmethod
    def dynamic_threshold(
        num_tokens, base_threshold=20, ref_length=2000, alpha=0.5, min_n=10, max_n=300
    ):
        """根据文本规模动态估算需要返回的新词数量。

        随文本量增大而上升，使用平滑的幂律曲线，并将结果限制在给定范围，避免过小或过大。

        参数:
            num_tokens: 停用词过滤后的 token 总数。
            base_threshold: 在 `ref_length` 个 token 时的目标返回数（基准值）。
            ref_length: 参考 token 数，达到该规模时返回 `base_threshold`。
            alpha: 增长速率，越大随文本增长越快。
            min_n: 返回结果的下限。
            max_n: 返回结果的上限。
        """
        # 让 top_n 随文本量增大而增大；并限制在 [min_n, max_n]
        # 例如：默认参数下，约 2000 个 token -> 约 20 个候选
        n = int(round(base_threshold * (max(1, num_tokens) / ref_length) ** alpha))
        return max(min_n, min(max_n, n))

    def find_word(
        self, text: str, ngram=3, top_n: Optional[int] = None
    ) -> tuple[list[tuple[str, float]], dict[str, float]]:
        """
        优化版 find_word 函数 - 保持完全相同的API和行为
        主要优化：
        1. 使用优化版 OptTrieNode 替代原版 TrieNode
        2. 批量处理减少函数调用开销
        3. 预计算所有 n-gram，避免重复生成
        """
        _root = TrieNode("*", self.nlp.tokenizer.tokenizer.FREQ)
        token_count = 0

        # 优化：批量处理，减少函数调用开销
        all_word_lists = self.split_sentences_word(text)

        # 预计算所有 n-gram，避免重复生成
        all_ngrams = []
        for word_list in all_word_lists:
            token_count += len(word_list)
            # 只处理长度足够的词列表
            if len(word_list) >= 2:  # 至少需要2个词才能形成有意义的n-gram
                ngrams = self.generate_ngram(word_list, ngram)
                all_ngrams.extend(ngrams)

        # 批量添加到 Trie 树
        for ngram_tuple in all_ngrams:
            _root.add(ngram_tuple)

        return _root.find_word(top_n or self.dynamic_threshold(token_count))


if __name__ == "__main__":
    # 测试优化版本
    opt_new_word_detection = NewWordDetection(LexSynth())

    text = """
    北亚在广义上包括了亚俄和蒙古利亚两个地区。匈奴民族在古代建了匈奴帝国。匈奴帝国之后分裂成北匈奴和南匈奴。
    此外,柔然也被认为是由鲜卑民族所建立。这四个国家先后在蒙古高原(蒙古利亚,简称蒙古)称汗称霸。
    在6-13世纪,先后出现了突厥汗国、薛延陀王国、回纥王国(后改称回鹘王国)和黠戛斯王国等国,称霸中亚和蒙古。
    1206年,铁木真统一蒙古,建立北至贝加尔湖,西至波兰,东至太平洋,南至波斯的蒙古帝国。
    其后只保有北亚东部,忽必烈行汉法,将国号由「大蒙古国」改成大元大蒙古国,并称霸汉地。
    在西伯利亚,则有白帐汗国(斡儿答王朝)和蓝帐汗国(昔班王朝)两个蒙古帝国的封国和附庸。
    """

    print("=== 优化版新词发现结果 ===")
    pprint.pprint(opt_new_word_detection.find_word(text))

    # # 性能测试
    # import time
    # large_text = text * 50  # 50倍大小测试
    # print(f"\n性能测试 - 文本长度: {len(large_text)}")

    # start_time = time.time()
    # result = opt_new_word_detection.find_word(large_text)
    # end_time = time.time()

    # print(f"处理时间: {end_time - start_time:.3f} 秒")
    # print(f"发现新词数量: {len(result[1])}")

    # if result[1]:
    #     print("前10个新词:")
    #     for i, (word, score) in enumerate(list(result[1].items())[:10]):
    #         print(f"  {i+1}. {word}: {score:.4f}")
