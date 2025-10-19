'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
from .utils.versions import require_version, require_version_core
from .dependency_versions_table import deps
pkgs_to_check_at_runtime = 'python requests filelock numpy'.split()
for pkg in pkgs_to_check_at_runtime:
    if pkg in deps: require_version_core(deps[pkg])
    else: raise ValueError(f"can't find {pkg} in {deps.keys()}, check dependency_versions_table.py")
def dep_version_check(pkg, hint=None): require_version(deps[pkg], hint)
'''
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
'''
