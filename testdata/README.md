## Beacon test dataset
The testdata consists of

- Dataset `GRCh38:beacon_test:2030-01-01`, from file `ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes_testset.vcf`
   - 11 lines picked from the file 
     [`ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf`](ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/)
     from [the 1000 Genomes Project data](http://www.internationalgenome.org/data#download), Phase 3. Some lines are slightly modified.
     The lines are selected so that it includes variantion types `DEL`, `INS` and `SNP` and variation in the counts (especially the `variantCount`).
   
   - 2 line containing a breakend. Copied from the [VCF specification 4.3, section 5.4.6](https://samtools.github.io/hts-specs/VCFv4.3.pdf) (sligthly modified).
     **NB!** These lines are for testing v1.1.0. Remove these lines if your beacon does not support breakends/matenames/fusions.


- Dataset `GRCh38:beacon_test2:2030-01-01`, from file `dataset2.vcf`. Copies of lines from dataset `GRCh38:beacon_test:2030-01-01`.
