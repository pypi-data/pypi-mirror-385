import argparse

class Job(object):
    def __init__(self):
        pass

    def run_arg_parser(self):
        # argument parse
        parser = argparse.ArgumentParser(
            prog='yxseq',
        )

        subparsers = parser.add_subparsers(
            title='subcommands', dest="subcommand_name")

        # argparse for fq2fa
        parser_a = subparsers.add_parser('fq2fa',
                                         help='Convert fastq to fasta',
                                         description='Convert fastq to fasta\n')

        parser_a.add_argument('-1', '--pair1', type=str,
                                help='input fastq pair1')
        parser_a.add_argument('-2', '--pair2', type=str,
                                help='input fastq pair2')
        parser_a.add_argument('-o', '--output', type=str,
                                help='output fasta', default="output.fa")

        # argparse for subfa
        parser_a = subparsers.add_parser('subfa',
                                        help='Extract sub fasta by seq id',
                                         description='Extract sub fasta by seq id\n')
        parser_a.add_argument('db_fasta_file', type=str,
                            help='a database fasta file')
        parser_a.add_argument('-i', "--ID_list", type=str,
                            help='ID list like ID1,ID2,ID3')
        parser_a.add_argument('-f', '--ID_file', type=str,
                            help='file with ID in a column')
        parser_a.add_argument('-o', "--output_file", type=str, help='output file')
        parser_a.add_argument('-l', "--log_file", type=str,
                            help='path for log file (default:None)', default=None)
        parser_a.add_argument(
            "-old", "--old_way", help="not use pyfaidx, just split file by \">\", good for misaligned fasta file", action='store_true')
        parser_a.add_argument(
            "-v", "--invert_flag", help="invert the flag, output the seqs not in the list", action='store_true')

        # argparse for cleanup 
        parser_a = subparsers.add_parser('cleanup',
                                        help='Clean up and rename genome annotation files',
                                        description='')

        parser_a.add_argument('gff_file', type=str,
                            help='Path of genome feature gff file')
        parser_a.add_argument('rename_prefix', type=str,
                            help='prefix of rename, like: Ath')
        parser_a.add_argument('output_dir', type=str, help='Path of output dir')
        parser_a.add_argument('-g', '--genome_fasta_file', type=str,
                            help='Path of genome fasta file', default=None)
        parser_a.add_argument('-p', '--protein_fasta_file', type=str,
                            help='Path of protein fasta file', default=None)
        parser_a.add_argument('-c', '--cds_fasta_file', type=str,
                            help='Path of CDS fasta file', default=None)
        parser_a.add_argument("-m", "--mode", help='raw data mode, which related to source of data',
                            default="normal", choices=['normal', 'phytozome', 'ncbi'])
        parser_a.add_argument("-k", "--keep_raw_contig_id", help="keep raw contig id, just change gene name",
                            action='store_true')

        self.arg_parser = parser

        self.args = parser.parse_args()

        # parser.set_defaults(func=parser.print_help())

    def run(self):
        self.run_arg_parser()

        if self.args.subcommand_name == 'fq2fa':
            from yxseq.pipeline import fq2fa_main
            fq2fa_main(self.args)
        elif self.args.subcommand_name == 'subfa':
            from yxseq.pipeline import subfa_main
            subfa_main(self.args)            
        elif self.args.subcommand_name == 'cleanup':
            from yxseq.pipeline import cleanup_main
            cleanup_main(self.args)
        else:
            self.arg_parser.print_help()

def main():
    job = Job()
    job.run()


if __name__ == '__main__':
    main()
