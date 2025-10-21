# tests/test_encoder.py

import unittest
from bengali_bpe.encoder import BengaliBPE

class TestBengaliBPE(unittest.TestCase):
    def setUp(self):
        # A simple corpus of Bengali sentences.
        self.corpus = [
            "বাংলা ভাষা সুন্দর",
            "আমি বাংলা পড়ি",
            "বাংলা ভয়ানক নয়"
        ]
        self.bpe = BengaliBPE(num_merges=5)
        self.bpe.train(self.corpus)

    def test_encode_word(self):
        word = "বাংলা"
        encoded = self.bpe.encode_word(word)
        # The encoded output should be a non-empty list.
        self.assertIsInstance(encoded, list)
        self.assertGreater(len(encoded), 0)

    def test_encode_decode(self):
        sentence = "বাংলা ভাষা"
        encoded = self.bpe.encode(sentence)
        decoded = self.bpe.decode(encoded)
        # A basic test to check that the decoded sentence contains the original words.
        self.assertIn("বাংলা", decoded)
        self.assertIn("ভাষা", decoded)

if __name__ == "__main__":
    unittest.main()
