from .fasta import FastaReader, FastaRecord, read_fasta
from .fastq import FastqReader, FastqRecord, read_fastq

__version__ = "0.0.30"
__all__ = [
    "FastaRecord",
    "FastaReader",
    "read_fasta",
    "FastqRecord",
    "FastqReader",
    "read_fastq",
]
