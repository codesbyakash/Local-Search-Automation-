
import heapq


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.frequencies = {}

    def insert(self, word, frequency=1):
        word = word.strip()

        if not word:
            return

        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_end = True
        node.word = word
        self.frequencies[word] = int(frequency)

    def find_prefix_node(self, prefix):
        node = self.root

        for char in prefix:
            if char not in node.children:
                return None

            node = node.children[char]

        return node

    def collect_words(self, node, results):
        if node.is_end:
            results.append(node.word)

        for child in node.children.values():
            self.collect_words(child, results)

    def suggest(self, prefix, limit=8):
        prefix = prefix.strip()

        if not prefix:
            return []

        node = self.find_prefix_node(prefix)

        if node is None:
            return []

        matching_words = []
        self.collect_words(node, matching_words)

        # Priority queue: highest frequency first.
        # Alphabetical order breaks frequency ties.
        ranked = [
            (-self.frequencies.get(word, 1), word)
            for word in matching_words
        ]

        best_words = heapq.nsmallest(
            limit, ranked
        )

        return [
            {
                "word": word,
                "frequency": -negative_frequency
            }
            for negative_frequency, word in best_words
        ]

    def update_frequency(self, word, frequency):
        if word in self.frequencies:
            self.frequencies[word] = int(frequency)
