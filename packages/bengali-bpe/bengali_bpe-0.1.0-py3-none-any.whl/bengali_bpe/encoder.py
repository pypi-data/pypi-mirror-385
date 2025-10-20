# bengali_bpe/encoder.py

class BengaliBPE:
    def __init__(self, num_merges=10):
        """
        Initialize the BengaliBPE model.

        Args:
            num_merges (int): Number of merge operations to perform during training.
        """
        self.num_merges = num_merges
        self.bpe_codes = {}  # Stores merge operations in the order they were applied.
        self.vocab = {}      # Vocabulary with word frequency counts.

    def build_vocab(self, corpus):
        """
        Build a vocabulary dictionary from a list of sentences.
        Each word is split into characters (with spaces between).

        Args:
            corpus (list of str): List of sentences in Bengali.

        Returns:
            dict: A dictionary mapping the space-separated representation of a word to its frequency.
        """
        vocab = {}
        for line in corpus:
            words = line.strip().split()
            for word in words:
                # Represent the word as a space-separated sequence of characters
                token = ' '.join(list(word))
                vocab[token] = vocab.get(token, 0) + 1
        return vocab

    def train(self, corpus):
        """
        Train the BPE model on the given corpus. Builds the vocabulary and applies merge operations.

        Args:
            corpus (list of str): List of sentences in Bengali.
        """
        self.vocab = self.build_vocab(corpus)
        for i in range(self.num_merges):
            pairs = self.get_stats(self.vocab)
            if not pairs:
                break
            # Select the most frequent adjacent pair of symbols
            best = max(pairs, key=pairs.get)
            self.bpe_codes[best] = i  # Record the merge operation and its order
            self.vocab = self.merge_vocab(best, self.vocab)
            # Uncomment the next line to print progress during training.
            # print(f"Merge {i+1}: {best}")

    def get_stats(self, vocab):
        """
        Calculate frequency counts for each adjacent pair of symbols in the vocabulary.

        Args:
            vocab (dict): The current vocabulary.

        Returns:
            dict: Mapping of symbol pairs to their aggregate frequency.
        """
        pairs = {}
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pair = (symbols[i], symbols[i + 1])
                pairs[pair] = pairs.get(pair, 0) + freq
        return pairs

    def merge_vocab(self, pair, vocab):
        """
        Merge all occurrences of the given pair in the vocabulary.

        Args:
            pair (tuple): The symbol pair to merge.
            vocab (dict): The current vocabulary.

        Returns:
            dict: New vocabulary with the pair merged.
        """
        new_vocab = {}
        bigram = ' '.join(pair)
        replacement = ''.join(pair)
        for word, freq in vocab.items():
            # Merge the chosen pair by replacing the space-separated pair with the concatenated symbol.
            new_word = word.replace(bigram, replacement)
            new_vocab[new_word] = freq
        return new_vocab

    def get_pairs(self, word):
        """
        Get a set of adjacent symbol pairs from a space-separated word string.

        Args:
            word (str): The word in space-separated format.

        Returns:
            set: Set of tuples representing adjacent symbol pairs.
        """
        symbols = word.split()
        pairs = set()
        for i in range(len(symbols) - 1):
            pairs.add((symbols[i], symbols[i + 1]))
        return pairs

    def encode_word(self, word):
        """
        Encode a single word by applying the learned BPE merges.

        Args:
            word (str): A Bengali word.

        Returns:
            list: A list of BPE tokens.
        """
        # Start with a space-separated list of characters.
        word_with_spaces = ' '.join(list(word))
        # Repeatedly apply merge operations as long as possible.
        while True:
            pairs = self.get_pairs(word_with_spaces)
            merge_candidates = {
                pair: self.bpe_codes.get(pair, float('inf')) for pair in pairs if pair in self.bpe_codes
            }
            if not merge_candidates:
                break
            # Choose the pair with the smallest merge order value.
            best = min(merge_candidates, key=lambda pair: merge_candidates[pair])
            pattern = ' '.join(best)
            replacement = ''.join(best)
            word_with_spaces = word_with_spaces.replace(pattern, replacement)
        return word_with_spaces.split()

    def encode(self, text):
        """
        Encode a sentence (or multiple words) using the BPE process.

        Args:
            text (str): A sentence in Bengali.

        Returns:
            list of list: Encoded tokens for each word.
        """
        words = text.strip().split()
        encoded_sentences = []
        for word in words:
            encoded = self.encode_word(word)
            encoded_sentences.append(encoded)
        return encoded_sentences

    def decode(self, encoded_words):
        """
        Decode a list of BPE-encoded words back into a normal sentence.
        Note: This is a simple join operation; further adjustments might be needed
        if you add special tokens (e.g., end-of-word markers) later.

        Args:
            encoded_words (list of list): BPE tokens for each word.

        Returns:
            str: The decoded sentence.
        """
        decoded_words = [''.join(tokens) for tokens in encoded_words]
        return ' '.join(decoded_words)
