#!/usr/bin/env python3
"""
Minimal working example: Latent space Bayesian optimization for molecular design

This script demonstrates how to:
1. Encode molecules into continuous latent space using a simplified VAE
2. Perform Bayesian optimization in latent space using Ax
3. Optimize molecular drug-likeness (QED scores)
"""

import logging
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Ax platform imports
from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties

warnings.filterwarnings("ignore")
logging.getLogger("ax").setLevel(logging.WARNING)

from rdkit import Chem
from rdkit.Chem import QED, Descriptors


def generate_molecular_dataset(n_molecules=100, seed=42):
    """Generate simplified molecular dataset"""
    np.random.seed(seed)

    base_smiles = [
        "CCO",
        "CC(=O)OC1=CC=CC=C1C(=O)O",
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "CC(C)(C)C1=CC=C(C=C1)C(C)(C)C",
    ]

    molecules = []
    for i in range(n_molecules):
        base_smi = np.random.choice(base_smiles)
        mol = Chem.MolFromSmiles(base_smi)
        if mol is not None:
            molecules.append(
                {
                    "molecular_weight": Descriptors.MolWt(mol),
                    "logp": Descriptors.MolLogP(mol),
                    "tpsa": Descriptors.TPSA(mol),
                    "qed": QED.qed(mol),
                }
            )
    return pd.DataFrame(molecules)


class SimplifiedMolecularVAE:
    """Simplified molecular VAE using PCA encoder + Random Forest decoder"""

    def __init__(self, latent_dim=3):
        self.latent_dim = latent_dim
        self.encoder = None
        self.decoder = None
        self.scaler = StandardScaler()
        self.feature_columns = ["molecular_weight", "logp", "tpsa"]

    def fit(self, molecular_data):
        """Train the VAE on molecular data"""
        features = molecular_data[self.feature_columns].values
        features_scaled = self.scaler.fit_transform(features)

        # PCA encoder
        self.encoder = PCA(n_components=self.latent_dim)
        latent_repr = self.encoder.fit_transform(features_scaled)

        # Random Forest decoder
        self.decoder = RandomForestRegressor(n_estimators=50, random_state=42)
        self.decoder.fit(latent_repr, features_scaled)

        return latent_repr

    def decode(self, latent_points):
        """Decode latent points to molecular features"""
        features_scaled = self.decoder.predict(latent_points)
        features = self.scaler.inverse_transform(features_scaled)

        decoded = pd.DataFrame(features, columns=self.feature_columns)
        decoded["molecular_weight"] = np.clip(decoded["molecular_weight"], 50, 1000)
        decoded["tpsa"] = np.clip(decoded["tpsa"], 0, 200)

        return decoded

    def get_latent_bounds(self, molecular_data, percentile=95):
        """Get bounds for latent space optimization"""
        latent_repr = self.encoder.transform(
            self.scaler.transform(molecular_data[self.feature_columns].values)
        )
        bounds = []
        for i in range(self.latent_dim):
            lower = np.percentile(latent_repr[:, i], 100 - percentile)
            upper = np.percentile(latent_repr[:, i], percentile)
            bounds.append((lower, upper))
        return bounds


print("Generating molecular dataset...")
molecular_data = generate_molecular_dataset(n_molecules=100)
print(f"Generated {len(molecular_data)} molecules")

print("Training molecular VAE...")
vae = SimplifiedMolecularVAE(latent_dim=3)
vae.fit(molecular_data)
latent_bounds = vae.get_latent_bounds(molecular_data)
print(f"Latent space bounds: {latent_bounds}")


def molecular_objective_function(latent_coords):
    """Objective function: predict QED score from latent coordinates"""
    decoded_mol = vae.decode(np.array(latent_coords).reshape(1, -1)).iloc[0]

    # Simplified QED-like scoring
    mw = decoded_mol["molecular_weight"]
    logp = decoded_mol["logp"]
    tpsa = decoded_mol["tpsa"]

    # Lipinski's rule-inspired scoring
    mw_score = 1.0 if 150 <= mw <= 500 else max(0, 1 - abs(mw - 325) / 325)
    logp_score = 1.0 if -0.4 <= logp <= 5.6 else max(0, 1 - abs(logp - 2.6) / 3.0)
    tpsa_score = 1.0 if tpsa <= 140 else max(0, 1 - (tpsa - 140) / 140)

    qed_estimate = (mw_score * logp_score * tpsa_score) ** (1 / 3)
    return qed_estimate


print("Setting up Bayesian optimization...")
ax_client = AxClient()
ax_client.create_experiment(
    parameters=[
        {
            "name": f"latent_{i}",
            "type": "range",
            "bounds": [float(latent_bounds[i][0]), float(latent_bounds[i][1])],
        }
        for i in range(3)
    ],
    objectives={"qed_score": ObjectiveProperties(minimize=False)},
)

print("Running optimization...")
n_iterations = 30
results = []

for iteration in range(n_iterations):
    parameters, trial_index = ax_client.get_next_trial()
    latent_coords = [parameters[f"latent_{i}"] for i in range(3)]
    qed_score = molecular_objective_function(latent_coords)

    ax_client.complete_trial(trial_index=trial_index, raw_data=qed_score)

    decoded_mol = vae.decode(np.array(latent_coords).reshape(1, -1)).iloc[0]
    results.append(
        {
            "iteration": iteration + 1,
            "qed_score": qed_score,
            "molecular_weight": decoded_mol["molecular_weight"],
            "logp": decoded_mol["logp"],
            "tpsa": decoded_mol["tpsa"],
        }
    )

    if iteration % 5 == 0:
        print(f"Iteration {iteration}: QED = {qed_score:.3f}")

# Print results
results_df = pd.DataFrame(results)
best_result = results_df.loc[results_df["qed_score"].idxmax()]

print("\nOptimization complete!")
print(f"Best QED score: {best_result['qed_score']:.3f}")
print("Best molecule properties:")
print(f"  Molecular Weight: {best_result['molecular_weight']:.1f}")
print(f"  LogP: {best_result['logp']:.2f}")
print(f"  TPSA: {best_result['tpsa']:.1f}")

print("\nImprovement over iterations:")
print(f"  Initial best: {results_df['qed_score'][:5].max():.3f}")
print(f"  Final best: {results_df['qed_score'].max():.3f}")

# Create best so far trace plot
best_so_far = results_df['qed_score'].cummax()
plt.figure(figsize=(8, 5))
plt.plot(range(1, len(best_so_far) + 1), best_so_far, 'b-', linewidth=2, marker='o', markersize=4)
plt.xlabel('Iteration')
plt.ylabel('Best QED Score So Far')
plt.title('Bayesian Optimization Progress')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('best_so_far_trace.png', dpi=150, bbox_inches='tight')
print(f"\nBest so far trace plot saved to: best_so_far_trace.png")
