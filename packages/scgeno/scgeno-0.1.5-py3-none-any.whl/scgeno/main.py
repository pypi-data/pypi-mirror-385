import argparse
import csv
import scanpy as sc
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from random import sample
from hmmlearn.hmm import CategoricalHMM
from natsort import natsorted
from functools import reduce

def get_chr_list():

    """Returns a list of chromosomes, like: ['chr1', 'chr2', ... 'chr19']"""

    chromosomes = list()
    for i in range(1, 19+1):
        chromosomes.append(f"chr{i}")

    return chromosomes

def get_chrom_genes_dict(chromosomes, aggr_matrix, simple_gtf_path):

    """Read a simpified version of a gtf file and returns
    a dictionary having chromosomes as keys and matching 
    genes as values"""

    print("Getting chromosomes' genes dcitionary...")
    chr_genes_dict = {chr:list() for chr in chromosomes}

    with open(simple_gtf_path) as gtf:
        reader = csv.reader(gtf, delimiter=',')
        for row in tqdm(reader):
            if row[5] in list(aggr_matrix.var_names):
                chr_genes_dict[row[0]].append(row[5])

    return chr_genes_dict


def filter_G1_G2(sample_dict, imp_genes_csv_path):

    """Filter G1 and G2 matrixes based on:
    1. shared cells with aggr matrix
    2. expressed genes in at least 1 cell in all matrixes
    3. shared genes with aggr matrix
    4. shared expressed genes between G1 and G2
    5. ignore mito genes
    6. ignore imprinted genes"""
    
    print("Filtering G1 and G2 matrixes...")
    #1
    sample_dict['G1'] = sample_dict['G1'][sample_dict['G1'].obs.index.isin(sample_dict['aggr'].obs.index), :]
    sample_dict['G2'] = sample_dict['G2'][sample_dict['G2'].obs.index.isin(sample_dict['aggr'].obs.index), :]
    sample_dict['G1'].obs = sample_dict['G1'].obs.merge(sample_dict['aggr'].obs, how='inner',left_index=True, right_index=True)
    sample_dict['G2'].obs = sample_dict['G2'].obs.merge(sample_dict['aggr'].obs, how='inner',left_index=True, right_index=True)
    
    #2
    for key in sample_dict.keys():
        sc.pp.filter_genes(sample_dict[key], min_cells=100, inplace=True)
    
    #3
    sample_dict['G1'] = sample_dict['G1'][:, sample_dict['G1'].var.index.isin(sample_dict['aggr'].var.index)]
    sample_dict['G2'] = sample_dict['G2'][:, sample_dict['G2'].var.index.isin(sample_dict['aggr'].var.index)]

    #4
    sample_dict['G1'] = sample_dict['G1'][:, sample_dict['G1'].var.index.isin(sample_dict['G2'].var.index)]
    sample_dict['G2'] = sample_dict['G2'][:, sample_dict['G2'].var.index.isin(sample_dict['G1'].var.index)]

    #5
    for key in sample_dict.keys():
        sample_dict[key] = sample_dict[key][:, ~sample_dict[key].var_names.str.startswith("mt-")]

    #6
    imp_genes_csv = pd.read_csv(imp_genes_csv_path, sep=';')
    imp_genes = list(imp_genes_csv.Gene)
    for key in sample_dict.keys():
        sample_dict[key] = sample_dict[key][:, ~sample_dict[key].var.index.isin(imp_genes)]    


def split_by_rep(sample_dict, rep):

    """Split G1 and G2 matrixed based on replicates (rep): returns
    a dictionary of dictionaries that looks like 
    {'aggr':{'rep1': AnnData, 'rep2': AnnData, ...}, 
    'G1':{'rep1': AnnData, 'rep2': AnnData, ...},
    'G2':{'rep1': AnnData, 'rep2': AnnData, ...}}"""
    
    print("Splitting sample by replicates...")
    samples = list(sample_dict.keys())
    reps = list(sample_dict['aggr'].obs[rep].unique())
    sample_rep_dict = dict.fromkeys(samples)

    for sample in tqdm(samples):
        sample_rep_dict[sample] = dict.fromkeys(reps)
        for i in reps:
            sample_rep_dict[sample][i] = sample_dict[sample][sample_dict[sample].obs[rep] == i]

    return reps, sample_rep_dict


def filter_rep(reps, sample_rep_dict):

    """For each rep:
    1. Filter out genes that are not expressed in G1
    2. Filter out genes expressed just in G2
    3. Filter out cells not shared between G1 and G2 matrix
    """

    print("Filtering reps matrixes...")
    for i in tqdm(reps):
        #1
        sc.pp.filter_genes(sample_rep_dict['G1'][i], min_cells=1, inplace=True)
        
        #2
        sample_rep_dict['G2'][i] = sample_rep_dict['G2'][i][:, sample_rep_dict['G2'][i].var.index.isin(sample_rep_dict['G1'][i].var.index)]
        
        #3
        sample_rep_dict['G1'][i] = sample_rep_dict['G1'][i][sample_rep_dict['G1'][i].obs.index.isin(sample_rep_dict['G2'][i].obs.index)]
        sample_rep_dict['G2'][i] = sample_rep_dict['G2'][i][sample_rep_dict['G2'][i].obs.index.isin(sample_rep_dict['G1'][i].obs.index)]


def get_ratio(G1, G2):     
    if G1 == 0 and G2 == 0:
        ratio = np.nan
    else:
        ratio = G1/(G1+G2)
    return ratio


def compute_ratio(reps, chromosomes, sample_rep_dict, chr_genes_dict):

    """Compute ratio G2/G1+G2 for each cell, for each gene,
    for each replicate and stores the ratio matrixes in a dictionary that 
    looks like: 
    {'rep1':{'chr1': matrix, 'chr2':matrix, ...},
    'rep2':{'chr1': matrix, 'chr2':matrix, ...}, 
    ...}"""

    print("Computing ratio per single replicate, per cell, by gene...")
    rep_chr_ratio_dict = {i:dict() for i in reps}
    for i in tqdm(reps):
        for chro in chromosomes:
            genes = [gene for gene in sample_rep_dict['G1'][i].var_names if gene in chr_genes_dict[chro]]
            G1_obs_df = sc.get.obs_df(sample_rep_dict['G1'][i], keys=genes)
            G2_obs_df = sc.get.obs_df(sample_rep_dict['G2'][i], keys=genes)
            
            ratio_df = G1_obs_df.copy()
        
            for gene in genes:
                ratio_df[gene] = list(map(get_ratio, G1_obs_df[gene], G2_obs_df[gene]))

            rep_chr_ratio_dict[i][chro] = ratio_df
            
    return rep_chr_ratio_dict


def plot_ratio_dist(reps, chromosomes, rep_chr_ratio_dict, sample_name, out_path):

    """Plot ratio distribution by chromosome and chromosomes heatmaps 
    (each replicate will have its own pdf files)"""

    for i in reps:
        print(f"Plotting distributions of ratio per chromosome for {i}...")
        dfs = list()
        for chr in chromosomes:
            ratio_avg_cell = pd.DataFrame(rep_chr_ratio_dict[i][chr].mean(axis=0), columns=['ratio']).reset_index(drop=True)
            ratio_avg_cell['chr'] = chr
            dfs.append(ratio_avg_cell)
        all_chr_df = pd.concat(dfs).reset_index(drop=True)

        g = sns.displot(data=all_chr_df, x='ratio', col="chr", kind="kde", col_wrap=4, height=3, aspect=1)
        g.set_axis_labels("G1/G1+G2", "Density")
        g.set_titles("{col_name}")
        plt.savefig(f"{out_path}/{sample_name}_ratio_distribution_per_chr_{i}.pdf")

        print(f"Plotting chromosomes' heatmaps for {i}...")
        fig = plt.figure(figsize=(30, 30))
        gs = fig.add_gridspec(19, hspace=1)
        ax = gs.subplots()
        fig.suptitle('G1/G1+G2 values computed as average over cells for each gene', fontsize=30)
        
        n = 0
        for chro in chromosomes:
            df = all_chr_df[all_chr_df.chr == chro]["ratio"].to_frame()
            df = df.T
            sns.heatmap(df, ax=ax[n], xticklabels=False, yticklabels=False, cmap="copper_r", vmin=0, vmax=1, rasterized=True)
            ax[n].set_title(f"chromosome {chro[3:]}", fontsize = 25)
            n += 1
        plt.savefig(f"{out_path}/{sample_name}_chr_heatmaps_{i}.pdf")
        plt.close()
    

# Implement and train HMM model
def ratio2int(df):
    df.dropna(inplace=True)
    df.loc[df['ratio'] < 0.5, 'obs_state_pro'] = 0
    df.loc[((df['ratio'] >= 0.5) & (df['ratio'] < 0.6)), 'obs_state_pro'] = 1
    df.loc[((df['ratio'] >= 0.6) & (df['ratio'] < 0.7)), 'obs_state_pro'] = 2
    df.loc[((df['ratio'] >= 0.7) & (df['ratio'] < 0.8)), 'obs_state_pro'] = 3
    df.loc[((df['ratio'] >= 0.8) & (df['ratio'] < 0.9)), 'obs_state_pro'] = 4
    df.loc[((df['ratio'] >= 0.9) & (df['ratio'] <= 1)), 'obs_state_pro'] = 5

    return df

def hmm_train(rep_chr_ratio_dict, chromosomes, r, c):

    """Implement a Categorical HMM model, set all the parameters,
    and update them during training.
    The model is trained on a set of random replicates and chromosomes,
    and then used to decode all the chromosomes of all replicates in 
    the sample.
    """

    fit_reps = sample(list(rep_chr_ratio_dict.keys()), r)
    fit_chromosomes = sample(chromosomes, c)

    X = list()
    lengths = list()
    for i in fit_reps:
        print(f"Preprocessing {i} sequences for HMM training...")
        for chr in fit_chromosomes:
            df = pd.DataFrame(
                rep_chr_ratio_dict[i][chr].mean(axis=0), 
                columns=['ratio']).reset_index().rename(columns={"index":"gene"})

            # convert ratio numbers into integers
            df = ratio2int(df)
            
            X_train = df.obs_state_pro.to_numpy()
            lengths.append(X_train.shape[0])

            X_train = X_train.reshape(-1, 1)
            X_train = X_train.astype(int)

            X.append(X_train)

    X = np.concatenate(X)

    model = CategoricalHMM(n_components=2, params='ste', init_params='', random_state=23, n_iter=10000)

    model.startprob_ = np.array([0.5, 0.5])

    model.transmat_ = np.array([[0.998, 0.002],
                                [0.002, 0.998]])

    model.emissionprob_ = np.array([[0.30, 0.15, 0.15, 0.30, 0.05, 0.05],
                                    [0.001, 0.05, 0.05, 0.299, 0.30, 0.30]])

    model.fit(X, lengths)
    return model

def hmm_decode(model, rep_chr_ratio_dict, chromosomes, sample_name, simple_gtf_path, out_path):

    """Decode the sequence of states for each chromosome in each replicate
    using the trained HMM model."""

    allRep_list = list() # list of dataframes containing all genes decoded states for all replicates
    
    reps = list(rep_chr_ratio_dict.keys())
    for i in reps:
        print(f"Decoding sequence per chromosome for {i}...")

        allchrom_list = list() # list of dataframes of decoded states for each chromosome of a replicate

        fig = plt.figure(figsize=(30, 30))
        gs = fig.add_gridspec(19, hspace=1)
        ax = gs.subplots()
        fig.suptitle(f'HMM predicted haplotype for all chromosomes of {i}', fontsize=30)
        n = 0
        for chro in chromosomes:
            df_ratio = pd.DataFrame(
                rep_chr_ratio_dict[i][chro].mean(axis=0), 
                columns=['ratio']).reset_index().rename(columns={"index":"gene"})

            df_ratio = ratio2int(df_ratio)

            X = df_ratio.obs_state_pro.to_numpy()
            X = X.reshape(-1, 1)
            X = X.astype(int)

            proba, state_sequence = model.decode(X)

            df_decoded = pd.DataFrame(state_sequence)
            sns.heatmap(df_decoded.T, ax=ax[n], xticklabels=False, yticklabels=False, cmap="copper_r", vmin=0, vmax=1, linewidths=0, rasterized=True)
            
            # Prepare output dataframe containg gene names, ratio, observed state and hidden state (per rep)
            df_comb = pd.concat([df_ratio, df_decoded], axis=1, ignore_index=True)
            df_comb.columns = ['gene', 'ratio', 'observed_state', 'hidden_state']
            df_comb.insert(0, 'chr', chro)
            allchrom_list.append(df_comb)

            n += 1

        # Save the heatmap of decoded states for all chromosomes
        plt.savefig(f"{out_path}/{sample_name}_chr_heatmaps_{i}_decoded.pdf")
        plt.close()

        # Concatenate all chromosomes dataframes into a single df (per rep)
        chrom_df = pd.concat(allchrom_list, axis=0, ignore_index=True)

        # plot the distribution of predicted states per chromosome
        g = sns.displot(data=chrom_df, x='hidden_state', col="chr", col_wrap=4, height=3, aspect=1)
        g.set_axis_labels("Predicted state", "Density")
        g.set_titles("{col_name}")
        plt.savefig(f"{out_path}/{sample_name}_predstate_distribution_per_chr_{i}.pdf")
        plt.close()

        # Add this replicate dataframe to the list of all replicates
        df_rep = chrom_df[['gene', 'hidden_state']].rename(columns={'hidden_state': i})
        allRep_list.append(df_rep)

        # Prepare output dataframe containing coordinates of the segments (per rep)
        with open(simple_gtf_path) as gtf:
            reader = csv.reader(gtf, delimiter=',')
            filtered_rows = list()
            for row in tqdm(reader):
                if row[5] in chrom_df['gene'].values:
                    filtered_rows.append(row)
        ref_df = pd.DataFrame(filtered_rows)
        ref_df.columns = ['chr', 'Type', 'start', 'end', 'gene_type', 'gene']
        
        seg_df = pd.merge(chrom_df[['chr', 'gene', 'hidden_state']], ref_df[['chr', 'start', 'end', 'gene']], on=['chr', 'gene'], how='inner')
        seg_df['block'] = (seg_df['hidden_state'] != seg_df['hidden_state'].shift()) | (seg_df['chr'] != seg_df['chr'].shift())
        seg_df['block_id'] = seg_df['block'].cumsum()

        block_df = seg_df.groupby(['chr', 'hidden_state', 'block_id']).agg({
            'start': 'first',
            'end': 'last'
        }).reset_index()

        block_df = block_df.drop(columns=['block_id'])
        sorted_indexes = natsorted(block_df.index, key=lambda i: block_df.loc[i, 'chr'])
        block_df = block_df.loc[sorted_indexes].reset_index(drop=True)

        print(f"Saving decoded dataframes for {i}...")
        chrom_df.to_csv(f"{out_path}/{sample_name}_decoded_{i}.csv", index=False, sep='\t')
        block_df.to_csv(f"{out_path}/{sample_name}_decoded_segments_{i}.bed", index=False, sep='\t')
    
    # Save all replicates dataframe containing all genes and their decoded states
    print("Saving all replicates decoded dataframe...")
    allRep_df = reduce(lambda left, right: pd.merge(left, right, on='gene', how='outer'), allRep_list)
    allRep_df.to_csv(f"{out_path}/{sample_name}_decoded_all_reps.csv", index=False, sep='\t')


def main():

    sns.set_style("white")
    sc.settings.verbosity = 3

    parser = argparse.ArgumentParser(description="This scripts determines the haplotype of all genes, by replicate.")
    parser.add_argument("-s", "--sample", type=str, help="Name of the sample (e.g. wt85, Dnmt1...)")
    parser.add_argument("-gtf", "--gtf", help="Path to a simplified gtf file")
    parser.add_argument("-imp", "--imprinted_genes", help="Path to a csv file containing imprinted genes")
    parser.add_argument("-rep", "--replicate", type=str, help="Name of the replicate column (e.g. embryo)")
    parser.add_argument("-a", "--aggr", help="Path to filtered and annotated feature barcode matrix h5")
    parser.add_argument("-G1", "--G1_matrix", help="Path to G1 (B6) filtered and annotated feature barcode matrix h5ad")
    parser.add_argument("-G2", "--G2_matrix", help="Path to G2 (CAST) filtered and annotated feature barcode matrix h5ad")
    parser.add_argument("-r", "--n_rep_train", help="Number of random replicates to use for HMM training", type=int, default=8)
    parser.add_argument("-c", "--n_chromosome_train", help="Number of random chromosomes per replicate to use for HMM training", type=int, default=9)
    parser.add_argument("-o", "--out_plots", help="Path of directory were to save plots and output files")
    args = parser.parse_args()

    print("Loading feature barcode matrixes into scanpy objects...")

    sample_dict = dict()
    sample_dict['aggr'] = sc.read_h5ad(args.aggr)
    sample_dict['aggr'].obs.set_index("BC", inplace=True)
    sample_dict['G1'] = sc.read_10x_h5(args.G1_matrix)
    sample_dict['G2'] = sc.read_10x_h5(args.G2_matrix)

    for key in sample_dict.keys():
        sample_dict[key].var_names_make_unique()

    chromosomes = get_chr_list()
    chr_genes_dict = get_chrom_genes_dict(chromosomes, sample_dict['aggr'], args.gtf)
    filter_G1_G2(sample_dict, args.imprinted_genes)
    reps, sample_rep_dict = split_by_rep(sample_dict, args.replicate)
    filter_rep(reps, sample_rep_dict)
    rep_chr_ratio_dict = compute_ratio(reps, chromosomes, sample_rep_dict, chr_genes_dict)
    plot_ratio_dist(reps, chromosomes, rep_chr_ratio_dict, args.sample, args.out_plots)
    model = hmm_train(rep_chr_ratio_dict, chromosomes, args.n_rep_train, args.n_chromosome_train)
    hmm_decode(model, rep_chr_ratio_dict, chromosomes, args.sample, args.gtf, args.out_plots)
    print("HMM model trained and decoded sequences plotted!")
    print(f"Finished processing {args.sample}!")

if __name__ == '__main__':
    main()