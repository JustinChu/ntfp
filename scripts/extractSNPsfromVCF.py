import argparse
from pyfaidx import Fasta
import os
import math
import sys

class VCFEntry:
    def __init__(self, chr, pos, wt, variant):
        self.chr = chr
        self.pos = int(pos)
        self.wt = wt
        self.variant = variant

class ExtractKmers:
    def __init__(self, vcf, fasta, k, prefix):
        self._vcf = vcf
        self._fasta = fasta
        self._k = k
        self._prefix = prefix
        self._vcfEntries = {}
    
    def _parseVCF(self):
        vcfFH = open(self._vcf, 'r')
        #chr1    45508256    rs2275276    A    G    .    .    .  
        lines = vcfFH.readlines()
        # Strips the newline character
        for line in lines:
            if line[0] != "#":
                tmpArr = line.rstrip().split("\t")
                #store chr, pos, variant
                info = VCFEntry(tmpArr[0], tmpArr[1], tmpArr[3], tmpArr[4])
                self._vcfEntries[tmpArr[2]] = info
            
    def extract(self):
        self._parseVCF()
        #open fasta file
        fastaFile = Fasta(self._fasta)
        refFH = open(self._prefix + "_ref.fa", 'w')
        varFH = open(self._prefix + "_var.fa", 'w')
        #for each vcf entry extract wildtype and variant into a string
        for id in self._vcfEntries.keys():
            # print string to repective files
            chr = self._vcfEntries[id].chr
            offset = self._vcfEntries[id].pos - 1
            pos1 = math.ceil(offset - self._k / 2)
            pos2 = pos1 + self._k
            tmpStr = str(fastaFile[self._vcfEntries[id].chr][pos1:pos2])
            if(self._vcfEntries[id].wt != tmpStr[int(self._k / 2)]):
                print("Wildtype allele does not match")
                print("ref:" + self._vcfEntries[id].wt)
                print("var:" + self._vcfEntries[id].variant)
                print("fasta:" + str(fastaFile[self._vcfEntries[id].chr][offset]))
                print("kmer:" + tmpStr)
                # exit(1)
            modStr = tmpStr[0:int(self._k / 2)] + self._vcfEntries[id].variant + tmpStr[int(self._k / 2) + 1:]
            varFH.write(">" + id + "\n")
            varFH.write(modStr + "\n")
            
            refFH.write(">" + id + "\n")
            refFH.write(tmpStr + "\n")
        refFH.close()
        varFH.close()
        
        
def main():
    parser = argparse.ArgumentParser(description='Extract k-mers listed from VCF file from reference. Produces 2 files (reference and variant)')
    parser.add_argument("-v", '--vcf', type=str, dest='vcf', help='vcf File')
    parser.add_argument("-f", '--fa', type=str, dest='fasta', help='fasta file with fai index')
    parser.add_argument("-k", '--kmer', type=int, dest='kmer', help='kmer size', default=25)
    parser.add_argument("-p", '--prefix', type=str, dest='prefix', help='output prefix', default = "")

    args = parser.parse_args()
    extractor = ExtractKmers(args.vcf, args.fasta, args.kmer, args.prefix)
    extractor.extract()
    

main()
    