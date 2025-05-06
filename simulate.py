import mdtraj
import nglview
import openmm
import openmm.app
import openmm.unit
from openff.interchange import Interchange
from openff.toolkit import ForceField, Molecule
from rdkit import Chem


def simulate_and_visualize(
    rdmol: Chem.Mol,
    force_field: ForceField,
) -> nglview.NGLWidget:

    interchange = force_field.create_interchange(
        Molecule.from_rdkit(rdmol).to_topology(),
    )

    integrator = openmm.LangevinMiddleIntegrator(
        300 * openmm.unit.kelvin,
        1 / openmm.unit.picosecond,
        0.002 * openmm.unit.picoseconds,
    )

    simulation = interchange.to_openmm_simulation(integrator)

    # OpenMM setup boilerplate
    simulation.minimizeEnergy()
    dcd_reporter = openmm.app.DCDReporter(file="trajectory.dcd", reportInterval=20)
    simulation.reporters.append(dcd_reporter)
    simulation.step(1000)

    # Visualize the trajectory
    trajectory: mdtraj.Trajectory = mdtraj.load(
        "trajectory.dcd",
        top=mdtraj.Topology.from_openmm(interchange.topology.to_openmm()),
    )
    view = nglview.show_mdtraj(trajectory)
    view.add_representation("line", selection="protein")
    view.add_line(selection="water")

    return view

def run_openmm_half_minute(interchange: Interchange, trj_file):
    integrator = openmm.LangevinMiddleIntegrator(
        300 * openmm.unit.kelvin,
        1 / openmm.unit.picosecond,
        0.002 * openmm.unit.picoseconds,
    )

    simulation = interchange.to_openmm_simulation(integrator)

    simulation.minimizeEnergy(tolerance=100)

    dcd_reporter = openmm.app.DCDReporter(
        file=trj_file,
        reportInterval=100,
    )
    simulation.reporters.append(dcd_reporter)

    # run for (literally) half a minute
    simulation.runForClockTime(0.5 * openmm.unit.minute)
