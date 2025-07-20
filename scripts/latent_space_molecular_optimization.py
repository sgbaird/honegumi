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
    rng = np.random.default_rng(seed)

    base_smiles = [
        "CCO",
        "CC(=O)OC1=CC=CC=C1C(=O)O",
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "CC(C)(C)C1=CC=C(C=C1)C(C)(C)C",
    ]

    molecules = []
    for i in range(n_molecules):
        base_smi = rng.choice(base_smiles)
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

    def get_latent_bounds(self, molecular_data):
        """Get bounds for latent space optimization"""
        latent_repr = self.encoder.transform(
            self.scaler.transform(molecular_data[self.feature_columns].values)
        )
        bounds = []
        for i in range(self.latent_dim):
            lower = np.min(latent_repr[:, i])
            upper = np.max(latent_repr[:, i])
            bounds.append((lower, upper))
        return bounds


molecular_data = generate_molecular_dataset(n_molecules=100)
vae = SimplifiedMolecularVAE(latent_dim=3)
vae.fit(molecular_data)
latent_bounds = vae.get_latent_bounds(molecular_data)


def molecular_objective_function(latent_coords):
    """Objective function: predict QED score from latent coordinates"""
    decoded_mol = vae.decode(np.array(latent_coords).reshape(1, -1)).iloc[0]

    # More complex QED-like scoring with noise and nonlinearities
    mw = decoded_mol["molecular_weight"]
    logp = decoded_mol["logp"]
    tpsa = decoded_mol["tpsa"]

    # Complex multi-modal scoring function
    # MW component: bimodal preference around 200 and 400
    mw_score1 = np.exp(-((mw - 200) / 100) ** 2)
    mw_score2 = np.exp(-((mw - 400) / 120) ** 2)
    mw_score = 0.6 * mw_score1 + 0.4 * mw_score2
    
    # LogP component: optimal around 2.5 with penalties for extremes
    logp_score = np.exp(-((logp - 2.5) / 2.0) ** 2) * (1 - np.exp(-((logp + 1) / 3.0) ** 2))
    
    # TPSA component: sigmoid with optimal around 60-80
    tpsa_score = 1 / (1 + np.exp((tpsa - 70) / 20))
    
    # Add cross-term interactions
    interaction_term = 0.1 * np.sin(mw / 100) * np.cos(logp * 2) * np.exp(-tpsa / 200)
    
    # Combine with weighted geometric mean and add interaction
    qed_estimate = (mw_score * logp_score * tpsa_score) ** (1 / 3) + interaction_term
    
    # Add small amount of noise to prevent exact reproducibility
    noise = 0.02 * np.sin(mw * logp * tpsa / 10000)
    qed_estimate += noise
    
    # Clip to valid range
    return max(0, min(1, qed_estimate))


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

# Print results
results_df = pd.DataFrame(results)
best_result = results_df.loc[results_df["qed_score"].idxmax()]

print(f"Best QED score: {best_result['qed_score']:.3f}")
print(f"Final best: {results_df['qed_score'].max():.3f}")

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
print("Best so far trace plot saved to: best_so_far_trace.png")
