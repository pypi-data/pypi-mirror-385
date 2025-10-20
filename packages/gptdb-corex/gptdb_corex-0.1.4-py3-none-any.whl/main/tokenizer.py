# db_gpt/tokenizer.py
from dataclasses import dataclass

@dataclass
class ByteTokenizer:
    BOS: int = 256   # <BOS>
    EOS: int = 257   # <EOS>
    PAD: int = 258   # <PAD>
    vocab_size: int = 259
    def encode(self, text: str, add_bos=True, add_eos=False):
        b = text.encode('utf-8', errors='replace')
        ids = list(b)
        if add_bos: ids = [self.BOS] + ids
        if add_eos: ids = ids + [self.EOS]
        return ids
    def decode(self, ids):
        out = bytearray()
        for t in ids:
            if t < 256: out.append(t)
        return out.decode('utf-8', errors='replace')