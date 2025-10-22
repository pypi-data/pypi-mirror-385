from yxseq.seq import read_fastq_big, read_fasta_big, FastaRecord, read_fasta_by_faidx, write_fasta
from yxutil import logging_init, tsv_file_parse, mkdir, cmd_run, get_file_dir
from yxmath.set import uniqify
from pyfaidx import Fasta
import re
from yxseq.feature import Genome, Gene, write_gff_file, genome_rename, cds_judgment
from copy import deepcopy
from collections import OrderedDict


def fq2fa_main(args):
    if args.pair1 is None:
        raise ValueError("pair1 is None")

    if args.pair1.split(".")[-1] == "gz":
        gzip_flag = True
    else:
        gzip_flag = False

    with open(args.output, "w") as f:
        for i in read_fastq_big(args.pair1, args.pair2, gzip_flag=gzip_flag):
            if len(i) == 2:
                i1, i2 = i
                f.write(">%s\n%s\n" % (i1.seqname_short() + "/1", i1.seq))
                f.write(">%s\n%s\n" % (i2.seqname_short() + "/2", i2.seq))
            else:
                i1 = i[0]
                f.write(">%s\n%s\n" % (i1.seqname_short(), i1.seq))


def subfa_main(args):

    db_fasta_file = args.db_fasta_file
    output_file = args.output_file
    log_file = args.log_file
    old_way = args.old_way

    ID_file = args.ID_file
    ID_list = args.ID_list
    if ID_file:
        ID_list = tsv_file_parse(ID_file, key_col=1)
        ID_list = ID_list.keys()
    elif ID_list:
        ID_list = ID_list.split(",")

    if not old_way:
        FastaByID(ID_list, db_fasta_file, output_file,
                  log_file, args.invert_flag)
    else:
        FastaByID_xyx(ID_list, db_fasta_file, output_file, log_file)


def FastaByID(ID_list, fasta_file, output_file, log_file, invert_flag=False):
    logger = logging_init("FastaByID", log_file)

    logger.info("Step1: parsing query ID list")
    if output_file is not None:
        F1 = open(output_file, 'w')
    ID_list_short = [re.search('^(\S+)', i).group(1) for i in ID_list]
    logger.info("Step1: finished")

    logger.info("Step2: loading fasta file")
    fasta_dict = Fasta(fasta_file)
    logger.info("Step2: finished")

    num = 0

    if invert_flag is False:
        for query_id in ID_list_short:
            if query_id in fasta_dict:
                num = num + 1
                seq_record = fasta_dict[query_id]
                full_name = seq_record.long_name
                # print(full_name)
                if output_file is not None:
                    F1.write(">%s\n" % full_name)
                    for line in seq_record:
                        F1.write(str(line) + "\n")
                else:
                    print(">%s" % full_name)
                    for line in seq_record:
                        print(line)
    elif invert_flag is True:
        ID_list_short = set(ID_list_short)
        for query_id in fasta_dict.keys():
            if query_id not in ID_list_short:
                num = num + 1
                seq_record = fasta_dict[query_id]
                full_name = seq_record.long_name
                if output_file is not None:
                    F1.write(">%s\n" % full_name)
                    for line in seq_record:
                        F1.write(str(line) + "\n")
                else:
                    print(">%s" % full_name)
                    for line in seq_record:
                        print(line)

    if output_file is not None:
        F1.close()
    logger.info("Found query sequences")
    logger.critical("%d records found in %d queries" %
                    (num, len(ID_list_short)))
    del logger.handlers[:]


def FastaByID_xyx(ID_list, db_fasta_file, output_file, log_file):
    logger = logging_init("FastaByID", log_file)
    logger.info("Loading fasta file")
    if output_file is not None:
        F1 = open(output_file, 'w')
    ID_list_short = [re.search('^(\S+)', i).group(1) for i in ID_list]
    output_dict = []
    for record in read_fasta_big(db_fasta_file, upper=False, log_file=log_file):
        if record.seqname_short() in ID_list_short or record.seqname in ID_list:
            output_dict.append(record)
    output_dict = uniqify(output_dict)
    logger.info("Loaded fasta file")
    logger.info("Finding query sequences")
    for record in output_dict:
        record.wrap()
        if output_file is not None:
            F1.write(">%s\n%s" % (record.seqname_short(), record.seq))
        else:
            print(">%s\n%s" % (record.seqname_short(), record.seq))
    if output_file is not None:
        F1.close()
    logger.info("Found query sequences")
    logger.critical("%d records found in %d queries" %
                    (len(output_dict), len(ID_list)))


def read_given_gene_seq(args):
    given_cds_dict = None
    given_aa_dict = None

    if not args.cds_fasta_file is None:
        given_cds_dict = read_fasta_by_faidx(args.cds_fasta_file)
        if args.mode == 'ncbi':
            given_cds_dict_new = {}
            for i in given_cds_dict:
                record = given_cds_dict[i]
                protein_id = [j[1]
                              for j in record.qualifiers if j[0] == 'protein_id'][0]
                given_cds_dict_new[protein_id] = record
            given_cds_dict = given_cds_dict_new

        test_cds = True
    else:
        test_cds = False

    if not args.protein_fasta_file is None:
        given_aa_dict = read_fasta_by_faidx(args.protein_fasta_file)
        if args.mode == 'ncbi':
            given_aa_dict_new = {}
            for i in given_aa_dict:
                record = given_aa_dict[i]
                protein_id = [j[1]
                              for j in record.qualifiers if j[0] == 'protein_id'][0]
                given_aa_dict_new[protein_id] = record
            given_aa_dict = given_aa_dict_new
        test_pt = True
    else:
        test_pt = False

    return test_cds, test_pt, given_cds_dict, given_aa_dict


def cleanup_main(args):
    mkdir(args.output_dir, True)

    # gunzip all file
    for file_tmp in ['genome_fasta_file', 'gff_file', 'protein_fasta_file', 'cds_fasta_file']:
        if not getattr(args, file_tmp) is None:
            file_path = getattr(args, file_tmp)
            if re.match(r'.*\.gz$', file_path):
                cmd_string = "gunzip %s" % file_path
                cmd_run(cmd_string, silence=True)
                file_path = re.sub(r'\.gz$', '', file_path)
                setattr(args, file_tmp, file_path)

    # if have genome and gff file, I will use it to extract cDNA, CDS and protein, other file will just use to check
    if args.gff_file is None:
        raise ValueError("must have gff file")

    if args.mode == 'ncbi':
        new_gff = args.gff_file + ".xyx"
        cmd_string = "grep \"exception=\" -v %s|grep \"^#\" -P -v |awk '{if ($5-$4 >= 0) print($_)}'> %s" % (
            args.gff_file, new_gff)
        cmd_run(cmd_string, cwd=get_file_dir(args.gff_file))
        args.gff_file = new_gff

    # create a genome object
    phyto_genome = Genome(genome_file=args.genome_fasta_file, gff_file=args.gff_file, cds_file=args.cds_fasta_file,
                          aa_file=args.protein_fasta_file)

    phyto_genome.genome_feature_parse()

    # bad gigascience
    if args.mode == 'normal' and 'mRNA' in phyto_genome.feature_dict:
        gene_dict = {}
        for mRNA_id in phyto_genome.feature_dict['mRNA']:
            mRNA_gf = phyto_genome.feature_dict['mRNA'][mRNA_id]
            gene_id = "gene." + mRNA_id
            gene_dict[gene_id] = Gene(
                id=gene_id, chr_loci=mRNA_gf.chr_loci, sub_features=[mRNA_gf])
            gene_dict[gene_id].type = 'gene'

        phyto_genome.feature_dict['gene'] = gene_dict

    # bad ncbi DDBJ gff
    if args.mode == 'ncbi':
        if phyto_genome.feature_dict['gene'][list(phyto_genome.feature_dict['gene'].keys())[0]].qualifiers['source'][0] == 'DDBJ':

            gene_dict = {}

            for g_id in phyto_genome.feature_dict['gene']:
                naked_cds_flag = False

                gene_gf = phyto_genome.feature_dict['gene'][g_id]
                if gene_gf.sub_features:
                    for cds in gene_gf.sub_features:
                        if cds.type == 'CDS':
                            naked_cds_flag = True
                        if cds.type == 'mRNA':
                            naked_cds_flag = False

                if naked_cds_flag:
                    mRNA_gf = deepcopy(gene_gf)

                    gene_gf.id = gene_gf.id + ".gene"
                    gene_gf.qualifiers['ID'][0] = gene_gf.qualifiers['ID'][0] + ".gene"

                    mRNA_gf.type = 'mRNA'
                    mRNA_gf.qualifiers['Parent'] = [gene_gf.id]

                    gene_gf.sub_features = [mRNA_gf]

                gene_dict[gene_gf.id] = gene_gf

            phyto_genome.feature_dict['gene'] = gene_dict

    # filter non mRNA gene
    mRNA_gene_dict = OrderedDict()
    for g_id in phyto_genome.feature_dict['gene']:
        gf = phyto_genome.feature_dict['gene'][g_id]
        if gf.sub_features and gf.sub_features[0].type == 'mRNA':
            mRNA_gene_dict[g_id] = gf

    phyto_genome.feature_dict = {'gene': mRNA_gene_dict}

    #
    if args.genome_fasta_file is not None:
        phyto_genome.genome_file_parse()
        phyto_genome.build_gene_sequence()

        # Compare builded seq and given seq
        test_cds, test_pt, given_cds_dict, given_aa_dict = read_given_gene_seq(
            args)

        # gene_number, match_cds_num, match_pt_num, match_cdna_num, cds_good_orf
        report_list = [0, 0, 0, 0]
        for gene_id in phyto_genome.feature_dict['gene']:
            gene_tmp = phyto_genome.feature_dict['gene'][gene_id]

            model_mRNA = [
                i for i in gene_tmp.sub_features if i.id == gene_tmp.model_mRNA_id][0]

            if args.mode == 'phytozome':
                model_id = model_mRNA.qualifiers['Name'][0]
            elif args.mode == 'ncbi':
                model_id = [i.qualifiers['protein_id'][0]
                            for i in model_mRNA.sub_features if i.type == 'CDS'][0]
            else:
                model_id = model_mRNA.qualifiers['ID'][0]

            report_list[0] += 1

            if test_cds and model_id in given_cds_dict and given_cds_dict[
                    model_id].seq.upper() == gene_tmp.model_cds_seq.upper():
                report_list[1] += 1

            if test_pt:
                if model_id in given_aa_dict:
                    if re.sub(r'\*', '', given_aa_dict[model_id].seq).upper() == gene_tmp.model_aa_seq.upper():
                        report_list[2] += 1
                    else:
                        print(re.sub(r'\*', '', given_aa_dict[model_id].seq))
                        print(gene_tmp.model_aa_seq)
                        print(model_id)

            if gene_tmp.model_cds_good_orf:
                report_list[3] += 1
            else:
                print(gene_id)

    else:
        phyto_genome.get_chromosome_from_gff()
        phyto_genome.build_gene_sequence()

        # read given seq
        test_cds, test_pt, given_cds_dict, given_aa_dict = read_given_gene_seq(
            args)

        # gene_number, find_cds_num, match_pt_num, cds_good_orf
        report_list = [0, 0, 0, 0]
        for gene_id in phyto_genome.feature_dict['gene']:
            gene_tmp = phyto_genome.feature_dict['gene'][gene_id]

            model_mRNA = [
                i for i in gene_tmp.sub_features if i.id == gene_tmp.model_mRNA_id][0]

            if args.mode == 'phytozome':
                model_id = model_mRNA.qualifiers['Name'][0]
            elif args.mode == 'ncbi':
                model_id = [i.qualifiers['protein_id']
                            for i in model_mRNA.sub_features if i.type == 'CDS'][0]
            else:
                model_id = model_mRNA.qualifiers['ID'][0]

            report_list[0] += 1

            if test_cds and model_id in given_cds_dict:
                report_list[1] += 1

                gene_tmp.model_cds_seq = given_cds_dict[model_id].seq
                good_orf, phase, aa_seq = cds_judgment(gene_tmp.model_cds_seq)

                if good_orf:
                    report_list[3] += 1
                # else:
                #     print(gene_id)

                gene_tmp.model_cds_good_orf = good_orf
                gene_tmp.model_aa_seq = aa_seq

                if test_pt:
                    if model_id in given_aa_dict:
                        if re.sub(r'\*', '', given_aa_dict[model_id].seq).upper() == gene_tmp.model_aa_seq.upper():
                            report_list[2] += 1
                        else:
                            print(
                                re.sub(r'\*', '', given_aa_dict[model_id].seq))
                            print(gene_tmp.model_aa_seq)
                            print(model_id)

            if test_pt and model_id in given_aa_dict:
                report_list[2] += 1
                aa_seq = re.sub(r'\*', '', given_aa_dict[model_id].seq)
                gene_tmp.model_aa_seq = aa_seq

    print("gene_num_in_gff: %d\nfind_cds_num: %d\nmatch_pt_num: %d\ngood_orf_cds: %d\n" %
          tuple(report_list))

    phyto_genome, chr_rename_dict, gene_rename_dict = genome_rename(
        phyto_genome, args.rename_prefix, args.keep_raw_contig_id)

    # write gff file
    new_gff_file = args.output_dir + "/" + args.rename_prefix + ".genome.gff3"
    gene_feature_dict = phyto_genome.feature_dict['gene']
    gf_list = [gene_feature_dict[i] for i in gene_feature_dict]
    write_gff_file(gf_list, new_gff_file)
    phyto_genome.gff_file = new_gff_file

    # write rename map
    rename_chr_map_file = args.output_dir + "/" + \
        args.rename_prefix + ".rename.chr.map"
    with open(rename_chr_map_file, 'w') as f:
        for raw_ctg_id in chr_rename_dict:
            chr_new_name = chr_rename_dict[raw_ctg_id]
            f.write("%s\t%s\n" % (raw_ctg_id, chr_new_name))

    rename_gene_map_file = args.output_dir + "/" + \
        args.rename_prefix + ".rename.gene.map"
    with open(rename_gene_map_file, 'w') as f:
        for raw_ctg_id in gene_rename_dict:
            chr_new_name = gene_rename_dict[raw_ctg_id]
            f.write("%s\t%s\n" % (raw_ctg_id, chr_new_name))

    # write genome file
    if args.genome_fasta_file is not None:
        new_genome_file = args.output_dir + "/" + args.rename_prefix + ".genome.fasta"

        genome_fasta_dict = read_fasta_by_faidx(args.genome_fasta_file)
        for new_chr_id in phyto_genome.chromosomes:
            old_id = phyto_genome.chromosomes[new_chr_id].old_id
            genome_fasta_dict[old_id].seqname = new_chr_id

        fasta_record_list = [genome_fasta_dict[i] for i in genome_fasta_dict]
        write_fasta(fasta_record_list, new_genome_file,
                    wrap_length=75, upper=True)
        phyto_genome.genome_file = new_genome_file

    # write protein, CDS, cDNA file
    cds_record_list = []
    cdna_record_list = []
    pt_record_list = []
    for gene_id in phyto_genome.feature_dict['gene']:
        gene_tmp = phyto_genome.feature_dict['gene'][gene_id]

        if hasattr(gene_tmp, 'model_cds_good_orf') and gene_tmp.model_cds_good_orf:
            if not gene_tmp.model_cds_seq == '':
                cds_record_list.append(FastaRecord(
                    gene_id, seq=gene_tmp.model_cds_seq))

            if not gene_tmp.model_cDNA_seq == '':
                cdna_record_list.append(FastaRecord(
                    gene_id, seq=gene_tmp.model_cDNA_seq))

            if not gene_tmp.model_aa_seq == '':
                pt_record_list.append(FastaRecord(
                    gene_id, seq=gene_tmp.model_aa_seq))

    new_cds_file = args.output_dir + "/" + \
        args.rename_prefix + ".gene_model.cds.fasta"
    write_fasta(cds_record_list, new_cds_file, wrap_length=75, upper=True)
    phyto_genome.cds_file = new_cds_file

    # new_cDNA_file = args.output_dir + "/" + args.rename_prefix + ".gene_model.cDNA.fasta"
    # write_fasta(cdna_record_list, new_cDNA_file, wrap_length=75)
    # phyto_genome.cDNA_file = new_cDNA_file

    new_pt_file = args.output_dir + "/" + \
        args.rename_prefix + ".gene_model.protein.fasta"
    write_fasta(pt_record_list, new_pt_file, wrap_length=75, upper=True)
    phyto_genome.aa_file = new_pt_file

    # phyto_genome.genome_file_parse()
    #
    # OUT = open(args.output_dir + "/" + args.rename_prefix + ".pyb", 'wb')
    # pickle.dump(phyto_genome, OUT)
    # OUT.close()

    # # gzip all file
    # for file_tmp in ['genome_fasta_file', 'gff_file', 'protein_fasta_file', 'cds_fasta_file', 'cdna_fasta_file']:
    #     if hasattr(args, file_tmp):
    #         file_path = getattr(args, file_tmp)
    #         cmd_string = "gzip %s" % file_path
    #         cmd_run(cmd_string, silence=True)
    #
    # for file_tmp in [new_genome_file, new_gff_file, new_cds_file, new_cDNA_file, new_pt_file]:
    #     cmd_string = "gzip %s" % file_path
    #     cmd_run(cmd_string, silence=True)


if __name__ == "__main__":
    class abc():
        pass

    args = abc()
    args.pair1 = "/lustre/home/xuyuxing/Database/Orchid/Apostasia/survey/Ni_clean_1.fq.gz"
    args.pair2 = "/lustre/home/xuyuxing/Database/Orchid/Apostasia/survey/Ni_clean_2.fq.gz"
    args.output = "output.fa"

    fq2fa_main(args)
