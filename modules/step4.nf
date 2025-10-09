// Generate summary
process METHYLATION_SUMMARY {
    tag "$sample-METHYLATION_SUMMARY"
    publishDir "${params.outdir}/${sample}_methy/"
    
    input:
    tuple val(sample),path(bismark_forward_report), path(bismark_reverse_report), path(allcools_cells_csv_output), 
    path(filtered_barcode),path(filtered_barcode_reads_counts), path(summary_json), path(allcools_extract_allc), path(cpg_sites)
    
    output:
    tuple val(sample), path("${sample}_summary.json"), path("${sample}_wgs_summary.csv")
    
    script:
    """
    export PATH=${params.seeksoultools_path}/bin:\$PATH

    # Generate summary report
    step4_wgs_summary.py \
        --outdir . \
        --samplename ${sample} \
        --summary_json ${sample}_summary.json \
        --genome_info_json ${cpg_sites}
    """
}

// LSI or PCA reduction and clustering analysis
process METHYLATION_LSI_PCA_CLUSTERING {
    tag "$sample"
    publishDir "${params.outdir}/${sample}_methy/step4"
    
    input:
    tuple val(sample), path(mcds_file), path(filtered_barcode)
    
    output:
    path "*.h5ad"
    path "*.pdf"
    path "*.png"
    
    script:
    """
    export PATH=${params.seeksoultools_path}/bin:\$PATH   
    step4_allcools_PCA_cluster.py \
        --mcds_path ${mcds_file} \
        --samplename ${sample} \
        --var_dim chrom20k \
        --filtered_barcode_file ${filtered_barcode} \
        --outdir . \
        --reduc lsi
    """
}