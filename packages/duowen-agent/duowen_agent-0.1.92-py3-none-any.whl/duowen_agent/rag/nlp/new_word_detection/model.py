import math


class Node(object):
    """
    建立字典树的节点 - 优化版本
    """

    def __init__(self, char):
        self.char = char
        # 记录是否完成
        self.word_finish = False
        # 用来计数
        self.count = 0
        # 使用字典代替列表，提高查找效率 O(1) vs O(n)
        self.child = {}
        # 方便计算 左右熵
        # 判断是否是后缀（标识后缀用的，也就是记录 b->c->a 变换后的标记）
        self.isback = False


class TrieNode(object):
    """
    建立前缀树，并且包含统计词频，计算左右熵，计算互信息的方法 - 优化版本
    """

    def __init__(self, node, data=None, pmi_limit=20):
        """
        初始函数，data为外部词频数据集
        :param node:
        :param data:
        """
        self.root = Node(node)
        self.pmi_limit = pmi_limit
        if not data:
            return
        node = self.root
        for key, values in data.items():
            new_node = Node(key)
            new_node.count = int(values)
            new_node.word_finish = True
            node.child[key] = new_node

    def add(self, word):
        """
        添加节点 - 优化版本，使用字典查找提高效率
        对于左熵计算时，这里采用了一个trick，用a->b<-c 来表示 cba
        具体实现是利用 self.isback 来进行判断
        :param word:
        :return:  相当于对 [a, b, c] a->b->c, [b, c, a] b->c->a
        """
        node = self.root
        # 正常加载 - 使用 O(1) 字典查找
        for count, char in enumerate(word):
            # 直接查找或创建子节点，避免线性搜索
            if char not in node.child:
                new_node = Node(char)
                node.child[char] = new_node
            node = node.child[char]

            # 判断是否是最后一个节点，这个词每出现一次就+1
            if count == len(word) - 1:
                node.count += 1
                node.word_finish = True

        # 建立后缀表示 - 仅对长度为3的词处理
        length = len(word)
        if length == 3:
            word = list(word)
            word[0], word[1], word[2] = word[1], word[2], word[0]
            node = self.root

            for count, char in enumerate(word):
                # 在节点中找字符（不是最后的后缀词）
                if count != length - 1:
                    if char not in node.child:
                        new_node = Node(char)
                        node.child[char] = new_node
                    node = node.child[char]
                else:
                    # 最后一个字符需要检查 isback 标记
                    found_key = None
                    for child_char, child_node in node.child.items():
                        if child_char == char and child_node.isback:
                            found_key = child_char
                            break

                    if found_key:
                        node = node.child[found_key]
                    else:
                        new_node = Node(char)
                        new_node.isback = True
                        node.child[char] = new_node
                        node = new_node

                # 判断是否是最后一个节点，这个词每出现一次就+1
                if count == len(word) - 1:
                    node.count += 1
                    node.isback = True
                    node.word_finish = True

    def search_one(self):
        """
        计算互信息: 寻找一阶共现，并返回词概率 - 优化版本
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return {}, 0

        # 计算 1 gram 总的出现次数
        total = 0
        for child in node.child.values():
            if child.word_finish is True:
                total += child.count

        if total == 0:
            return {}, 0

        # 计算 当前词 占整体的比例
        for child_char, child in node.child.items():
            if child.word_finish is True:
                result[child_char] = child.count / total
        return result, total

    def search_bi(self):
        """
        计算互信息: 寻找二阶共现，并返回 log2( P(X,Y) / (P(X) * P(Y)) 和词概率 - 优化版本
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return {}

        total = 0
        # 1 grem 各词的占比，和 1 grem 的总次数
        one_dict, total_one = self.search_one()
        if not one_dict:
            return {}

        # 优化：预计算log值，避免重复计算，添加数值保护
        log_one_dict = {k: math.log2(max(v, 1e-10)) for k, v in one_dict.items() if v > 0}

        for child in node.child.values():
            for ch in child.child.values():
                if ch.word_finish is True:
                    total += ch.count

        if total == 0:
            return {}

        log_total = math.log2(total)

        for child_char, child in node.child.items():
            if child_char not in log_one_dict:
                continue

            for ch_char, ch in child.child.items():
                if ch.word_finish is True and ch_char in log_one_dict:
                    # 互信息值越大，说明 a,b 两个词相关性越大
                    # 优化：使用预计算的log值，添加安全检查
                    log_child = log_one_dict[child_char]
                    log_ch = log_one_dict[ch_char]
                    PMI = math.log2(max(ch.count, 1)) - log_total - log_child - log_ch

                    # 这里做了PMI阈值约束
                    if PMI > self.pmi_limit:
                        # 例如: dict{ "a_b": (PMI, 出现概率), .. }
                        result[f"{child_char}_{ch_char}"] = (PMI, ch.count / total)
        return result

    def search_left(self):
        """
        寻找左频次 - 优化版本
        统计左熵， 并返回左熵 (bc - a 这个算的是 abc|bc 所以是左熵)
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return {}

        for child_char, child in node.child.items():
            for cha_char, cha in child.child.items():
                # 收集所有符合条件的子节点计数
                back_counts = []
                for ch in cha.child.values():
                    if ch.word_finish is True and ch.isback:
                        back_counts.append(ch.count)

                if back_counts:
                    total = sum(back_counts)
                    if total > 0:
                        # 计算信息熵，添加数值保护
                        p = sum((count / total) * math.log2(count / total) for count in back_counts if count > 0)
                        result[f"{child_char}{cha_char}"] = -p
        return result

    def search_right(self):
        """
        寻找右频次 - 优化版本
        统计右熵，并返回右熵 (ab - c 这个算的是 abc|ab 所以是右熵)
        :return:
        """
        result = {}
        node = self.root
        if not node.child:
            return {}

        for child_char, child in node.child.items():
            for cha_char, cha in child.child.items():
                # 收集所有符合条件的子节点计数
                normal_counts = []
                for ch in cha.child.values():
                    if ch.word_finish is True and not ch.isback:
                        normal_counts.append(ch.count)

                if normal_counts:
                    total = sum(normal_counts)
                    if total > 0:
                        # 计算信息熵，添加数值保护
                        p = sum((count / total) * math.log2(count / total) for count in normal_counts if count > 0)
                        result[f"{child_char}{cha_char}"] = -p
        return result

    def find_word(self, N):
        # 通过搜索得到互信息
        # 例如: dict{ "a_b": (PMI, 出现概率), .. }
        bi = self.search_bi()
        # 通过搜索得到左右熵
        left = self.search_left()
        right = self.search_right()

        if not bi:
            return [], {}

        result = {}
        for key, values in bi.items():
            d = "".join(key.split('_'))
            # 计算公式 score = PMI + min(左熵， 右熵) => 熵越小，说明越有序，这词再一次可能性更大！
            # 添加安全访问，避免 KeyError
            left_entropy = left.get(d, 0)
            right_entropy = right.get(d, 0)
            result[key] = (values[0] + min(left_entropy, right_entropy)) * values[1]

        # 按照 大到小倒序排列，value 值越大，说明是组合词的概率越大
        # result变成 => [('世界卫生_大会', 0.4380419441616299), ('蔡_英文', 0.28882968751888893) ..]
        result = sorted(result.items(), key=lambda x: x[1], reverse=True)

        if not result:
            return [], {}

        dict_list = [result[0][0]]
        add_word = {}
        new_word = "".join(dict_list[0].split('_'))
        # 获得概率
        add_word[new_word] = result[0][1]

        # 取前 N 个
        for d in result[1: N]:
            flag = True
            for tmp in dict_list:
                pre = tmp.split('_')[0]
                # 新出现单词后缀，再老词的前缀中 or 如果发现新词，出现在列表中; 则跳出循环
                # 前面的逻辑是： 如果A和B组合，那么B和C就不能组合(这个逻辑有点问题)，例如：`蔡_英文` 出现，那么 `英文_也` 这个不是新词
                # 疑惑: **后面的逻辑，这个是完全可能出现，毕竟没有重复**
                if d[0].split('_')[-1] == pre or "".join(tmp.split('_')) in "".join(d[0].split('_')):
                    flag = False
                    break
            if flag:
                new_word = "".join(d[0].split('_'))
                add_word[new_word] = d[1]
                dict_list.append(d[0])

        return result, add_word