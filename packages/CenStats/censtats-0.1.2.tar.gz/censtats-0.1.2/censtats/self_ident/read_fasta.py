# ModDotPlot
# https://github.com/marbl/ModDotPlot/commit/0f593a7b7b317cdfc00ef350491e17239eda594f
from typing import Generator
import pyfaidx
import mmh3

tab_b = bytes.maketrans(b"ACTG", b"TGAC")


def generateKmersFromFasta(seq: str, k: int) -> Generator[int, None, None]:
    n = len(seq)
    for i in range(n - k + 1):
        # Remove case sensitivity
        kmer = seq[i : i + k].upper()
        fh = mmh3.hash(kmer)

        # Calculate reverse complement hash directly without the need for translation
        rc = mmh3.hash(kmer[::-1].translate(tab_b))

        yield fh if fh < rc else rc


def readKmersFromFile(
    filename: str, ksize: int
) -> Generator[tuple[str, list[int]], None, None]:
    """
    Given a filename and an integer k, returns a list of all k-mers found in the sequences in the file.
    """
    seq = pyfaidx.Fasta(filename)

    for seq_rec in seq:
        kmers_for_seq = [
            kmer_hash for kmer_hash in generateKmersFromFasta(str(seq_rec), ksize)
        ]
        yield seq_rec.name, kmers_for_seq
