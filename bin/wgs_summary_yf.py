import json
import os
import re
import click


def extract_percentage(text, pattern):
    """Extract percentage from text"""
    match = re.search(pattern, text)
    return float(match.group(1)) if match else 0.0


def extract_number(text, pattern):
    """Extract number from text"""
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0


def parse_bismark_report(report_file):
    """
    Parse bismark report file and extract methylation context metrics
    
    Args:
        report_file: Path to bismark report file
        
    Returns:
        dict: Dictionary containing methylation metrics
    """
    metrics = {}
    
    try:
        with open(report_file, 'r') as f:
            content = f.read()
        
        # Extract methylation rates
        metrics['cpg_methylation_rate'] = extract_percentage(content, r'C methylated in CpG context:\s*([\d.]+)%')
        metrics['chg_methylation_rate'] = extract_percentage(content, r'C methylated in CHG context:\s*([\d.]+)%')
        metrics['chh_methylation_rate'] = extract_percentage(content, r'C methylated in CHH context:\s*([\d.]+)%')
        metrics['unknown_methylation_rate'] = extract_percentage(content, r'C methylated in Unknown context \(CN or CHN\):\s*([\d.]+)%')
        
        # Extract methylated and unmethylated C counts (for calculating average methylation rate)
        metrics['methylated_cpg'] = extract_number(content, r'Total methylated C\'s in CpG context:\s*(\d+)')
        metrics['unmethylated_cpg'] = extract_number(content, r'Total unmethylated C\'s in CpG context:\s*(\d+)')
        metrics['methylated_chg'] = extract_number(content, r'Total methylated C\'s in CHG context:\s*(\d+)')
        metrics['unmethylated_chg'] = extract_number(content, r'Total unmethylated C\'s in CHG context:\s*(\d+)')
        metrics['methylated_chh'] = extract_number(content, r'Total methylated C\'s in CHH context:\s*(\d+)')
        metrics['unmethylated_chh'] = extract_number(content, r'Total unmethylated C\'s in CHH context:\s*(\d+)')
        metrics['methylated_unknown'] = extract_number(content, r'Total methylated C\'s in Unknown context:\s*(\d+)')
        metrics['unmethylated_unknown'] = extract_number(content, r'Total unmethylated C\'s in Unknown context:\s*(\d+)')
        
    except Exception as e:
        print(f"Error parsing {report_file}: {e}")
        return None
    
    return metrics


def get_methylation_metrics(samplename, outdir):
    """
    Get methylation context metrics
    
    Args:
        samplename: Sample name
        outdir: Output directory (containing step2/bismark subdirectory)
        
    Returns:
        dict: Dictionary containing methylation metrics, returns default values if unable to obtain
    """
    bismark_dir = os.path.join(outdir, 'step2', 'bismark')
    if not os.path.exists(bismark_dir):
        bismark_dir = outdir
    
    # Case 1: Check if single report file exists
    single_report = os.path.join(bismark_dir, f'{samplename}_1_bismark_bt2_PE_report.txt')
    if os.path.exists(single_report):
        print(f"Found single bismark report: {single_report}")
        metrics = parse_bismark_report(single_report)
        if metrics:
            return {
                'cpg_methylation_rate': metrics['cpg_methylation_rate'],
                'chg_methylation_rate': metrics['chg_methylation_rate'],
                'chh_methylation_rate': metrics['chh_methylation_rate'],
                'unknown_methylation_rate': metrics['unknown_methylation_rate']
            }
    
    # Case 2: Check if forward and reverse report files exist
    forward_report = os.path.join(bismark_dir, f'{samplename}_forward_1_bismark_bt2_PE_report.txt')
    reverse_report = os.path.join(bismark_dir, f'{samplename}_reverse_1_bismark_bt2_PE_report.txt')
    
    if os.path.exists(forward_report) and os.path.exists(reverse_report):
        print(f"Found forward and reverse bismark reports: {forward_report}, {reverse_report}")
        forward_metrics = parse_bismark_report(forward_report)
        reverse_metrics = parse_bismark_report(reverse_report)
        
        if forward_metrics and reverse_metrics:
            # Calculate average methylation rate
            # For CpG: (forward_methylated + reverse_methylated) / (forward_total + reverse_total) * 100
            cpg_methylated_total = forward_metrics['methylated_cpg'] + reverse_metrics['methylated_cpg']
            cpg_unmethylated_total = forward_metrics['unmethylated_cpg'] + reverse_metrics['unmethylated_cpg']
            cpg_total = cpg_methylated_total + cpg_unmethylated_total
            cpg_rate = (cpg_methylated_total / cpg_total * 100) if cpg_total > 0 else 0.0
            
            chg_methylated_total = forward_metrics['methylated_chg'] + reverse_metrics['methylated_chg']
            chg_unmethylated_total = forward_metrics['unmethylated_chg'] + reverse_metrics['unmethylated_chg']
            chg_total = chg_methylated_total + chg_unmethylated_total
            chg_rate = (chg_methylated_total / chg_total * 100) if chg_total > 0 else 0.0
            
            chh_methylated_total = forward_metrics['methylated_chh'] + reverse_metrics['methylated_chh']
            chh_unmethylated_total = forward_metrics['unmethylated_chh'] + reverse_metrics['unmethylated_chh']
            chh_total = chh_methylated_total + chh_unmethylated_total
            chh_rate = (chh_methylated_total / chh_total * 100) if chh_total > 0 else 0.0
            
            unknown_methylated_total = forward_metrics['methylated_unknown'] + reverse_metrics['methylated_unknown']
            unknown_unmethylated_total = forward_metrics['unmethylated_unknown'] + reverse_metrics['unmethylated_unknown']
            unknown_total = unknown_methylated_total + unknown_unmethylated_total
            unknown_rate = (unknown_methylated_total / unknown_total * 100) if unknown_total > 0 else 0.0
            
            return {
                'cpg_methylation_rate': cpg_rate,
                'chg_methylation_rate': chg_rate,
                'chh_methylation_rate': chh_rate,
                'unknown_methylation_rate': unknown_rate
            }
    
    # If none are found, return default values
    print(f"Warning: No bismark report files found for {samplename}")
    return {
        'cpg_methylation_rate': 0.0,
        'chg_methylation_rate': 0.0,
        'chh_methylation_rate': 0.0,
        'unknown_methylation_rate': 0.0
    }


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--outdir", help="outdir.")
@click.option("--samplename", help="samplename.")
@click.option("--summary_json", help="summary json.")
def outcsv(outdir, samplename, summary_json):
    os.makedirs(outdir, exist_ok = True)
    with open(summary_json,'r') as fh:
        summary = json.load(fh)
    
    rawreads = summary["stat"]["total"]
    vaildreads = summary["stat"]["valid"]
    vaildratio = vaildreads / rawreads
    rate_7fratio = float(summary["stat"]["rate_7f"])
    rate_17lmeratio = float(summary["stat"]["rate_17lme"])
    rate_7f17lmeratio = float(summary["stat"]["rate_7f17lme"])
    conversion = float(summary["stat"]["ct_mean"])
    cc_ratio = float(summary["stat"]["cc_mean"])
    
    # Calculate new quality control metrics
    too_short = summary["stat"]["too_short"]
    forward = summary["stat"]["forward"]
    reverse = summary["stat"]["reverse"]
    
    # Get chimeric statistics, set to 0 if not present
    forward_chimeric = summary["stat"].get("forward_chimeric", 0)
    reverse_chimeric = summary["stat"].get("reverse_chimeric", 0)
    
    # Dropped_Too_Short: (valid-too_short)/total*100%
    dropped_too_short_ratio = (vaildreads - too_short) / rawreads
    
    # Dropped_Chimeric: (valid-too_short-forward_chimeric-reverse_chimeric)/total*100%
    dropped_chimeric_ratio = (vaildreads - too_short - forward_chimeric - reverse_chimeric) / rawreads
    
    # Get methylation context metrics
    methylation_metrics = get_methylation_metrics(samplename, outdir)

    raw = f'{summary["stat"]["total"]}'
    vaild = f'{vaildratio:.2%}'
    dropped_too_short = f'{dropped_too_short_ratio:.2%}'
    dropped_chimeric = f'{dropped_chimeric_ratio:.2%}'
    cpg_methylation = f'{methylation_metrics["cpg_methylation_rate"]:.1f}%'
    chg_methylation = f'{methylation_metrics["chg_methylation_rate"]:.1f}%'
    chh_methylation = f'{methylation_metrics["chh_methylation_rate"]:.1f}%'
    unknown_methylation = f'{methylation_metrics["unknown_methylation_rate"]:.1f}%'
    rate_7f = f'{rate_7fratio:.2%}'
    rate_17lme = f'{rate_17lmeratio:.2%}'
    rate_7f17lme = f'{rate_7f17lmeratio:.2%}'

    mapgenome = f'{summary["mapping"]["Reads Mapped to Genome"]:.2%}'
    confidently = f'{summary["mapping"]["Reads Mapped Confidently to Genome"]:.2%}'
    coverage = f'{summary["coverage"]["Genome Coverage rate"]:.2%}'
    total_cpgs = f'{summary["cells"]["Total CPGs Detected"]}'
    cov_max_cell = f'{summary["cells"]["Genome Coverage rate of max cell"]:.2%}'
    cpgs_max_cell = f'{summary["cells"]["CPGs of max cell"]}'
    umi_max_cell = f'{summary["cells"]["UMIs of max cell"]}'
    reads_max_cell = f'{summary["cells"]["Reads of max cell"]}'
    saturation_max_cell = f'{summary["cells"]["Saturation of max cell"]:.2%}'
    cov_median_cell = f'{summary["cells"]["Genome Coverage rate of median cell"]:.2%}'
    cpgs_median_cell = f'{summary["cells"]["CPGs of median cell"]}'
    umi_median_cell = f'{summary["cells"]["UMIs of median cell"]}'
    reads_median_cell = f'{summary["cells"]["Reads of median cell"]}'
    saturation_median_cell = f'{summary["cells"]["Saturation of median cell"]:.2%}'
    cellnum = f'{summary["cells"]["Estimated Number of Cells"]}'
    fraction = f'{summary["cells"]["Fraction Reads in Cells"]:.2%}'
    


    header=('Samplename,Estimated_Number_of_Cells,Number_of_Reads,Valid_Barcode_Ratio,Dropped_Too_Short,Dropped_Chimeric,Valid_7F_Reads_Rate,Valid_17LME_Reads_Rate,Valid_7F17LME_Reads_Rate,C-T_Conversion,C-C_Ratio,'
            'Reads_Mapped_to_Genome,Reads_Mapped_Confidently_to_Genome,CpG_Methylation_Rate,CHG_Methylation_Rate,CHH_Methylation_Rate,Unknown_Methylation_Rate,Total_Genome_Coverage_Rate,'
            'Total_CPGs_Detected,Genome_Coverage_Rate_of_Max_Cell,CPGs_of_Max_Cell,UMIs_of_Max_Cell,Reads_of_Max_Cell,Saturation_of_Max_Cell,'
            'Genome_Coverage_Rate_of_Median_Cell,CPGs_of_Median_Cell,UMIs_of_Median_Cell,Reads_of_Median_Cell,Saturation_of_Median_Cell,Fraction_Reads_in_Cells')

    summary_data = [
             samplename,
             cellnum,
             raw,
             vaild,
             dropped_too_short,
             dropped_chimeric,
             rate_7f,
             rate_17lme,
             rate_7f17lme,
             conversion,
             cc_ratio,
             mapgenome,
             confidently,
             cpg_methylation,
             chg_methylation,
             chh_methylation,
             unknown_methylation,
             coverage,
             total_cpgs,
             cov_max_cell,
             cpgs_max_cell,
             umi_max_cell,
             reads_max_cell,
             saturation_max_cell,
             cov_median_cell,
             cpgs_median_cell,
             umi_median_cell,
             reads_median_cell,
             saturation_median_cell,
             fraction
           ]

    with open(os.path.join(outdir, f'{samplename}_wgs_summary.csv'), 'w') as fh:
        fh.write(header + '\n')
        fh.write(','.join(str(_).replace(',', '') for _ in summary_data)+ '\n')

if __name__ == "__main__":
    outcsv()