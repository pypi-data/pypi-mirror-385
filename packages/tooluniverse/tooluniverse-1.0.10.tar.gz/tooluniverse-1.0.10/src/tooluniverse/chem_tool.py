import requests
from urllib.parse import quote

# from rdkit import Chem
from .base_tool import BaseTool
from .tool_registry import register_tool
from indigo import Indigo


@register_tool("ChEMBLTool")
class ChEMBLTool(BaseTool):
    """
    Tool to search for molecules similar to a given compound name or SMILES using the ChEMBL Web Services API.
    """

    def __init__(self, tool_config, base_url="https://www.ebi.ac.uk/chembl/api/data"):
        super().__init__(tool_config)
        self.base_url = base_url
        self.indigo = Indigo()

    def run(self, arguments):
        query = arguments.get("query")
        similarity_threshold = arguments.get("similarity_threshold", 80)
        max_results = arguments.get("max_results", 20)

        if not query:
            return {"error": "`query` parameter is required."}
        return self._search_similar_molecules(query, similarity_threshold, max_results)

    def get_chembl_id_by_name(self, compound_name):
        """
        Search ChEMBL for a compound by name and return the ChEMBL ID of the first match.
        """
        headers = {"Accept": "application/json"}
        search_url = f"{self.base_url}/molecule/search.json?q={quote(compound_name)}"
        print(search_url)
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        results = response.json().get("molecules", [])
        if not results or not isinstance(results, list):
            return {"error": "No valid results found for the compound name."}
        if not results:
            return {"error": "No results found for the compound name."}
        top_molecules = results[:3]  # Get the top 3 results
        chembl_ids = [
            molecule.get("molecule_chembl_id")
            for molecule in top_molecules
            if molecule.get("molecule_chembl_id")
        ]
        if not chembl_ids:
            return {"error": "No ChEMBL IDs found for the compound name."}
        return {"chembl_ids": chembl_ids}

    def get_smiles_pref_name_by_chembl_id(self, query):
        """
        Given a ChEMBL ID, return a dict with canonical SMILES and preferred name.
        """
        headers = {"Accept": "application/json"}
        if query.upper().startswith("CHEMBL"):
            molecule_url = f"{self.base_url}/molecule/{quote(query)}.json"
            response = requests.get(molecule_url, headers=headers)
            response.raise_for_status()
            molecule = response.json()
            if not molecule or not isinstance(molecule, dict):
                return {"error": "No valid molecule found for the given ChEMBL ID."}
            molecule_structures = molecule.get("molecule_structures")
            if not molecule_structures or not isinstance(molecule_structures, dict):
                return {
                    "error": "Molecule structures not found or invalid for the ChEMBL ID."
                }
            smiles = molecule_structures.get("canonical_smiles")
            pref_name = molecule.get("pref_name")
            if not smiles:
                return {"error": "SMILES not found for the given ChEMBL ID."}
            return {"smiles": smiles, "pref_name": pref_name}
        else:
            return None

    def get_chembl_smiles_pref_name_id_by_name(self, compound_name):
        """
        Search ChEMBL for a compound by name and return a list of dicts with ChEMBL ID, canonical SMILES, and preferred name for the top 5 matches.
        """
        headers = {"Accept": "application/json"}
        search_url = f"{self.base_url}/molecule/search.json?q={quote(compound_name)}"
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        results = response.json().get("molecules", [])
        if not results or not isinstance(results, list):
            return {"error": "No valid results found for the compound name."}
        top_molecules = results[:5]
        output = []
        for molecule in top_molecules:
            chembl_id = molecule.get("molecule_chembl_id", None)
            molecule_structures = molecule.get("molecule_structures", {})
            if molecule_structures is not None:
                smiles = molecule_structures.get("canonical_smiles", None)
            else:
                smiles = None
            pref_name = molecule.get("pref_name")
            if chembl_id and smiles:
                output.append(
                    {"chembl_id": chembl_id, "smiles": smiles, "pref_name": pref_name}
                )
            elif chembl_id and not smiles:
                smiles_pre_name_dict = self.get_smiles_pref_name_by_chembl_id(chembl_id)
                if (
                    isinstance(smiles_pre_name_dict, dict)
                    and "error" not in smiles_pre_name_dict
                ):
                    output.append(
                        {
                            "chembl_id": chembl_id,
                            "smiles": smiles_pre_name_dict["smiles"],
                            "pref_name": smiles_pre_name_dict.get("pref_name"),
                        }
                    )
        if not output:
            return {"error": "No ChEMBL IDs or SMILES found for the compound name."}
        return output

    def _search_similar_molecules(self, query, similarity_threshold, max_results):
        headers = {"Accept": "application/json"}

        smiles_info_list = []

        # If the query looks like a ChEMBL ID, fetch its SMILES and pref_name
        if isinstance(query, str) and query.upper().startswith("CHEMBL"):
            result = self.get_smiles_pref_name_by_chembl_id(query)
            if isinstance(result, dict) and "error" in result:
                return result
            smiles_info_list.append(
                {
                    "chembl_id": query,
                    "smiles": result["smiles"],
                    "pref_name": result.get("pref_name"),
                }
            )

        # If not a ChEMBL ID, use get_chembl_smiles_pref_name_id_by_name to get info
        if len(smiles_info_list) == 0 and isinstance(query, str):
            results = self.get_chembl_smiles_pref_name_id_by_name(query)
            if isinstance(results, dict) and "error" in results:
                return results
            for item in results:
                smiles_info_list.append(item)

        if len(smiles_info_list) == 0:
            return {"error": "SMILES representation not found for the compound."}

        results_list = []
        for info in smiles_info_list:
            smiles = info["smiles"]
            pref_name = info.get("pref_name")
            chembl_id = info.get("chembl_id")
            mol = self.indigo.loadMolecule(smiles)
            if mol is None:
                return {"error": "Failed to load molecule with Indigo."}

            encoded_smiles = quote(smiles)
            similarity_url = f"{self.base_url}/similarity/{encoded_smiles}/{similarity_threshold}.json?limit={max_results}"
            sim_response = requests.get(similarity_url, headers=headers)
            sim_response.raise_for_status()
            sim_results = sim_response.json().get("molecules", [])
            similar_molecules = []
            for mol in sim_results:
                sim_chembl_id = mol.get("molecule_chembl_id")
                sim_pref_name = mol.get("pref_name", "N/A")
                mol_structures = mol.get("molecule_structures", {})
                if mol_structures is None:
                    continue
                mol_smiles = mol_structures.get("canonical_smiles", "N/A")
                similarity = mol.get("similarity", "N/A")
                similar_molecules.append(
                    {
                        "chembl_id": sim_chembl_id,
                        "pref_name": sim_pref_name,
                        "smiles": mol_smiles,
                        "similarity": similarity,
                    }
                )
            if len(similar_molecules) == 0:
                continue
            results_list.append(
                {
                    "chembl_id": chembl_id,
                    "pref_name": pref_name,
                    "smiles": smiles,
                    "similar_molecules": similar_molecules,
                }
            )

        return results_list
