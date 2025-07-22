#!/usr/bin/env python3
# %%
"""
=== Chemical Annotator ===
chemical_annotator.py: fetches drug annotations from public repositories based on exact match with query pattern.
"""
VERSION = "1.0"
AUTHOR = "Flavio Ballante"
INSTITUTION = "2025, CBCS-SciLifeLab-Karolinska Institutet"
CONTACT = "flavio.ballante@ki.se, flavioballante@gmail.com"

# %%
from argparse import ArgumentParser

def ParseArgs():
    """
    Function to parse command line arguments.
    """
    parser = ArgumentParser(description="Chemical Annotator")
    parser.add_argument('-v', '--version', action='store_true', help='Show version information and exit')
    parser.add_argument('-a', '--author', action='store_true', help='Show author information and exit')
    parser.add_argument('-i', '--input', help='Input .csv file')
    parser.add_argument('-o', '--output', help='Output .xlsx file')
    parser.add_argument('-f', '--format', help='Type of chemical notation to use as query (SMILES, InChI, or InChIKey)')
    parser.add_argument('-ct', '--confidence_threshold', type=int, default=8, help='Minimum confidence score value (default: 8)')
    parser.add_argument('-at', '--assay_type_in', type=str, default='B,F', help='Comma-separated list of assay types (default: B, F)')
    parser.add_argument('-pcm', '--pchembl_value_gte', type=float, default=6, help='Minimum pChEMBL value (default: 6)')
        
    return parser.parse_args()

# %%
def main():

    args = ParseArgs()

    # Show version and author information if requested
    if args.version:
        print(f"Chemical Annotator: {VERSION}")
        return
    if args.author:
        print(f"Author: {AUTHOR}")
        print(f"Contact: {CONTACT}")
        print(f"Institution: {INSTITUTION}")
        return

    if not args.input or not args.output or not args.format:
        print("Error: Input, output, and format arguments are required. Use -h for help.")
        return

    import logging
    import sys
    import os
    import pandas as pd
    from chemical_annotator.utils import (
            process_compounds,
            process_targets,
            get_pathways_from_ec,
            get_protein_classifications,
            trace_hierarchy,
            chembl_status
            )

      # Remove previous log file if it exists
    log_file = 'chemical_annotator.log'
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Configure logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    
    try:
        

        path = os.getcwd()

        # Add title/header to the log file
        logger.info("===========================================")
        logger.info("            Chemical Annotator             ")
        logger.info("Version:  1.0")
        logger.info("Format: txt")
        logger.info("Author: Flavio Ballante")
        logger.info("Contact: flavio.ballante@ki.se, flavioballante@gmail.com")
        logger.info("2025, CBCS-SciLifeLab-Karolinska Institutet")
        logger.info("===========================================")
        if chembl_status:
            logger.info(f"ChEMBL Database Version: {chembl_status['chembl_db_version']}")
            logger.info(f"ChEMBL Release Date: {chembl_status['chembl_release_date']}")
            logger.info(f"ChEMBL Status: {chembl_status['status']}")
            logger.info(f"Number of Activities: {chembl_status['activities']}")
            logger.info(f"Number of Distinct Compounds: {chembl_status['disinct_compounds']}")
            logger.info(f"Number of Targets: {chembl_status['targets']}")
        else:
            logger.warning("Unable to fetch ChEMBL status information")
        logger.info("===========================================")
        logger.info("")

        #Read input file
        compounds_list=pd.read_csv(args.input, delimiter=r",")

        #Fetch data from ChEMBL
        Drugs_data=process_compounds(
                compounds_list,
                args.format,
                confidence_threshold=args.confidence_threshold,
                assay_type_in=args.assay_type_in.split(','),
                pchembl_value_gte=args.pchembl_value_gte
                )

        
        #Shift index by 1
        Drugs_info=Drugs_data[0]
        Drugs_assay=Drugs_data[1]
        Drugs_MoA=Drugs_data[2]
        Drugs_info.index = Drugs_info.index + 1
        Drugs_assay.index = Drugs_assay.index + 1
        Drugs_MoA.index = Drugs_MoA.index + 1
     
        # Write data to separate .xlsx files
        Drugs_info_output = f"{args.output}_drugs_info.xlsx"
        Drugs_assay_output = f"{args.output}_drugs_assay.xlsx"
        Drugs_MoA_output = f"{args.output}_drugs_moa.xlsx"

        # Convert Drugs_info DataFrame to Excel file format using pandas
        with pd.ExcelWriter(Drugs_info_output, engine='openpyxl') as excel_writer:
            Drugs_info.to_excel(excel_writer, index=True)

        # Convert Drugs_assay DataFrame to Excel file format using pandas
        with pd.ExcelWriter(Drugs_assay_output, engine='openpyxl') as excel_writer:
            Drugs_assay.to_excel(excel_writer, index=True)

        # Convert Drugs_MoA DataFrame to Excel file format using pandas
        with pd.ExcelWriter(Drugs_MoA_output, engine='openpyxl') as excel_writer:
            Drugs_MoA.to_excel(excel_writer, index=True)

        
        print("All compounds have been processed and their data has been saved. Now processing targets data...")
        logger.info("All compounds have been processed and their data has been saved. Now processing targets data...")

       
        #Fetch target data from ChEMBL
        Targets_data=process_targets(Drugs_assay)
        Targets_data = Targets_data.reset_index(drop=True)
        Targets_data.index = Targets_data.index + 1
        
        # Process EC numbers and get pathway information
        print("Processing EC numbers and retrieving pathway information...")
        logger.info("Processing EC numbers and retrieving pathway information...")

        pathway_data = []

        unique_targets = Targets_data.drop_duplicates(subset=['target_chembl_id'])
        unique_targets = unique_targets.dropna(subset=['EC Numbers'])
        for _, row in unique_targets.iterrows():
            chembl_id = row['target_chembl_id']
            ec_list = row['EC Numbers']

            if pd.isna(ec_list):
                continue

            ec_numbers = ec_list.split(';')
            kegg_ids = []
            pathways = []

            for ec in ec_numbers:
                ec = ec.strip()  # Remove any leading/trailing whitespace
                ec_pathways = get_pathways_from_ec(ec)
    
                if not ec_pathways.empty:
                    kegg_ids.extend(ec_pathways['KEGG_ID'].unique())
                    pathways.extend(ec_pathways['Pathway'].unique())

            # Remove duplicates while preserving order
            kegg_ids = list(dict.fromkeys(kegg_ids))
            pathways = list(dict.fromkeys(pathways))
    
            pathway_data.append({
                'target_chembl_id': chembl_id,
                'EC Numbers': ec_list,
                'KEGG_ID': ';'.join(kegg_ids),
                'Pathway': ';'.join(pathways)
            })
        
            
        pathway_data = pd.DataFrame(pathway_data)

        # Write pathway data to a separate Excel file
        pathway_data_output = f"{args.output}_pathway_info.xlsx"
        with pd.ExcelWriter(pathway_data_output, engine='openpyxl') as excel_writer:
            pathway_data.to_excel(excel_writer, index=False)
    
        # Merge pathway_data with Targets_data
        Targets_data = Targets_data.drop(columns=['EC Numbers'], errors='ignore')
        Targets_data_with_pathways = pd.merge(Targets_data, pathway_data, on='target_chembl_id', how='left')
        
        # Process protein hierarchy data
        print("Retrieving protein hierarchy information...")
        logger.info("Retrieving protein hierarchy information...")
        unique_targets = Targets_data.drop_duplicates(subset=['target_chembl_id']).copy()
        unique_targets['protein_classifications'] = unique_targets['target_chembl_id'].apply(get_protein_classifications)
        unique_targets['protein_hierarchy'] = unique_targets['protein_classifications'].apply(trace_hierarchy)
        Targets_data_with_pathways_p_class = Targets_data_with_pathways.merge(unique_targets[['target_chembl_id', 'protein_classifications','protein_hierarchy']], on='target_chembl_id', how='left')

        Targets_data_with_pathways_p_class = Targets_data_with_pathways_p_class.reset_index(drop=True)
        Targets_data_with_pathways_p_class.index += 1


        # Step 2: Concatenate the dataframes horizontally
        Drugs_assay_Targets_data = pd.concat([Drugs_assay, Targets_data_with_pathways_p_class.drop('target_chembl_id', axis=1)], axis=1)

        #Reorder columns to ensure Targets_data columns follow 'target_chembl_id'
        #Get the list of columns from Targets_data excluding 'target_chembl_id'
        targets_columns = [col for col in Targets_data_with_pathways_p_class.columns if col != 'target_chembl_id']

        #Find the index of 'target_chembl_id' in the merged dataframe
        insert_position = Drugs_assay_Targets_data.columns.get_loc('target_chembl_id') + 1

        #Create the new column order
        new_column_order = (
        list(Drugs_assay_Targets_data.columns[:insert_position]) +
        targets_columns +
        [col for col in Drugs_assay_Targets_data.columns[insert_position:] if col not in targets_columns]
        )

        #Reorder the merged dataframe
        Drugs_assay_Targets_data = Drugs_assay_Targets_data[new_column_order]
        Drugs_assay_Targets_data = Drugs_assay_Targets_data.reset_index(drop=True)
        Drugs_assay_Targets_data.index = Drugs_assay_Targets_data.index + 1
        
        # Write data to separate .xlsx files
        Targets_data_output = f"{args.output}_targets_info.xlsx"
        Drugs_assay_Targets_data_output = f"{args.output}_drugs_assay_targets_info.xlsx"

        # Convert Targets_assay DataFrame to Excel file format using pandas
        with pd.ExcelWriter(Targets_data_output, engine='openpyxl') as excel_writer:
            Targets_data.to_excel(excel_writer, index=True)

        # Convert Drugs_assay_Targets_data DataFrame to Excel file format using pandas
        with pd.ExcelWriter(Drugs_assay_Targets_data_output, engine='openpyxl') as excel_writer:
            Drugs_assay_Targets_data.to_excel(excel_writer, index=True)           
        print("Script execution completed successfully.")
        logger.info("Script execution completed successfully.")
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))

# %%
if __name__ == "__main__":
    main()
