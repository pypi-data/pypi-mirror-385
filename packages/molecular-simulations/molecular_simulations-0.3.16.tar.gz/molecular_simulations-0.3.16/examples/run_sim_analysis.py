from natsort import natsorted
from molecular_simulations.analysis import Fingerprinter
from pathlib import Path
from tqdm import tqdm

path = Path('/path/to/simulation/dirs')
for sim_path in tqdm(natsorted(path.glob('*'))):
    topology = sim_path / 'system.prmtop'
    trajectory = sim_path / 'prod.dcd'
    target_selection = 'segid A' # MDAnalysis selection language

    fingerprinter = Fingerprinter(
        topology,
        trajectory=trajectory,
        target_selection=target_selection,
    )

    fingerprinter.run()
    fingerprinter.save()
