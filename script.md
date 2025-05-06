# Joint demo script

This morning we've heard from each individual OMSF project about what they've been up to and where they're going next.
Throughout this afternoon, we'll be hearing from some industry partners about what they've built using OMSF products.
In between these spaces, I'm going to spend the next few minutes showing off how some OMSF products work with each
other in addition to diving slightly deeper into a few capabilities along the way. Everything will be something that
you can run right now, so as excited as we are about things like SMIRNOFF protein force fields or co-folding at scale
with OpenFold 3, I'll be focusing on released software you can install and use right now.

0:40

If you want to follow along, the materials are available on GitHub at the following link:
https://github.com/openforcefield/joint-demo

Let's say we're a team of computational chemists supporting a team of medicinal chemists designing ligands for
biological targets. We are interested in MCL-1, which is a well-known target for oncology, and trying to inhibit its
activity.

In the future we might start with an OpenFold3 prediction, which we could get from a one-liner with relatively few
arguments, like this ... but for now let's just use a well-established crystal structure of this target.

_show protein_

Imagine we've been given a set of ligands via a CSV file of SMILES.

_show ligand SMILES dataframe and 2-D structures_

Visual inspection will show you this this is a congeneric series based around a bi-heterocyclic core, with
substitution of the heterocycle and elaborations at both ends.

Our overarching goal is to asses how strongly each ligand binds to MCL1, but we also care if they'd have off-target
effects. Here, we'll use OpenADMET's CLI to evaluate this ligand set against a series of CYP anti-targets. A pass
through our dataset at this stage isn't free, but it's relatively quick and cheap, almost certainly more efficient than
trying to "fix" a series at a later stage, after lead optimization.

_go into notebook, run openadmet predict cell_

A reminder here that the models used in this notebook are simple demonstration models not fully ready for production.
More advanced models are currently being developed, and in the future models will also improve as the OpenADMET project
starts to receive data from their partners at Octant and UCSF.

For the purposes of our exercise lets hone in on CYP3A4 inhibition since CYP3A4 is responsible for large proportion of
hepatic metabolism relative to other CYPs. For starters, let's use use a cutoff of a predicted IC50 of 2.5 micromolar,
which corresponds to a pIC50 of 5.6. This is not realistic for a production run, but it's acceptable for our uses
today.

_run Pandas cells_

With a little bit of Pandas, we can quickly get a subset of the original ligand set which has PIC50 below our threshold
value. We are left with 14 ligands out of our original 18.

Having filtered out ligands with CYP3A4 issues, we are now moving on to free energy calculations of the remaining
ligands, which we will dow ith OpenFE. There are a few ways to use OpenFE's tooling, there is a CLI which provides easy
access to the most commonly-used features and a Python API which enables a wider set of more advanced features and
options.  Here we'll be using the CLI, but there's lots of cool stuff in the API too.

With our target and ligands already prepared, we will be using the OpenFE CLI in three parts to end with delta G
values. Basically, we prepare, run, and analyze these free energy calculations with three commands.

We will make use of YAML files which encode settings used in these commands. Our settings file is relatively simple,
leaving most things at their defaults, but there are many other options that can be enabled. We'll explore a couple of
these later.

_run plan-rbfe-network call_

This sets up a series of alchemical transformations between ligands. Based on our settings file, the Kartograph atom
mapper is used and a minimal spanning network is generated. Sage is used for small molecule parameters, so AM1-BCC
partial charges are used. We can see some valuable information is logged, and we can also see that AM1-BCC takes a few
seconds even having provided many cores.

The main output of this command is a bunch of JSON files, each describing a particular transformation. There's also a
GraphML file which describes the network, and OpenFE has some convenience tools used to visualize them.

_run `draw_ligand_network` cells_

If we had the right combination of GPUs and days to wait, we could run each of these simulations until they converge.
We would do this by calling `openfe quickrun` on each JSON file, which itself store each result in a JSON file. We
don't have an army of GPUs or a time machine, so I'm using some pre-computed results.

_run gather call_

After all simulations are run, the final step is to run `openfe gather` to get our relative binding free energies back.
With default options and the recent version 1.4.0, we get a pretty table of the dG of each ligand along with
corresponding uncertainty values.

So far we've taken a set of ligands and a known target, filtered out potential ADMET liabilities with OpenADMET's CLI,
and use OpenFE's CLI to predict relative binding free energies using OpenFF's small molecule force field Sage.

_pause_

8:10

Next, I want to dig deeper into some of these tools we've talked about so far in our HTS pipeline, and then finish up
with a few examples of other use cases enabled by OpenFF force fields and infrastructure.

Earlier I mentioned that we could use an OpenFold-predicted structure as the starting point, but we're holding off
until that's fully released. I do have a pre-production result to share here, one that co-folds MCL1 with a ligand not
in our data set. If we superimpose the prediction on top of a structure from the protein data bank, we see excellent
agreement with the crystallographic result.

_show OpenFold 3 prediction cell_

Let's have a closer look at the ADMET predictions. You may have noticed we ran models for 4 different CYPs and
only looked at one. Let's now have a look at predicted p values for each of these ligands with each anti-target.

_run plotting cell_

Reminder that smaller pIC50 values correspond to larger IC50, so weaker CYP binders are on the left and stronger
binders are on the right.

This data would suggest that these compounds have some off target CYP inhibition issues, most severely for CYP1A2
average pIC50 of ~6.

But how good are these models, really? Are all of these ligands really binding to CYPs in the range of 1-10 micromolar?

The OpenADMET team thinks these models generally over-predict p due to the pChEMBL data itself having a positive skew.
That is to say, the dataset probably skews towards CYP inhibitors (high p) and away from non-binders (low p) and
doesn't reflect very well the breadth of chemistry that you might design ligands with.

_show cell visualizing pChEMBL data_

We see that this underlying data from ChEMBL has a heavy skew towards strong CYP inhibitors and not much data on weaker
binders. This probably limits the applicability to arbitrary chemistries in an HTS context, and highlights the need for
vastly more data collection of broader chemistries, ideally guided by missing coverage in the datasets.

10:15

Next let's dig into the OpenFE CLI a little bit more.

Earlier when we ran `openfe plan-rbfe-network`, one of the steps involved assigning partial charges separately from how
other force field parameters are applied. AM1-BCC can occasionally give inconsistent results or meaningfully different
results with different hardware or software versions. Free energy calculations are also particularly sensitive to seemingly
small partial charge differences. So computing them once for each ligand helps mitigate these reproducibility issues.
There is a separate command in the CLI which controls this step.

_run openfe charge-molecules cell_

There are a number of other options that can be tinkered with in this command, just like other CLI calls, such as using
OpenEye to generate AM1-BCC ELF10 charges or using NAGL to generate GNN charges. These options can be passed in through
the `settings.yaml` file.

_run openfe charge-molecules cells with NAGL options_

Next, let's talk about network planning, something else a practitioner can tinker with via the settings file. Konnektor
has has implemented a bunch of different networks, and a subset of them have been integrated into OpenFE. The default
network, which we used earlier, is a minimal spanning tree, which minimizes the number of edges that can connect all
nodes in a network.

_show network visualization_

If we wanted to switch to, say, a radial or star map, which connects a single node to each other node like a wheel with
spokes, we can do that by defining it in the settings YAML and re-running the network planning command. This network
takes another argument for the central ligand, let's just use ligand 6.

_show radial.yaml, run plan-rbfe-network, show new visualization_

There are plenty more options exposed in the CLI and documented in the CLI reference, and further more functionality
available in the Python API.

14:00

Finally, I want to show off some things that we can do with OpenFF infrastructure. So far in this demo, OpenFF force
fields have been used by OpenFE under the hood, by default, for its small molecule parameters.  There's much more
functionality that can be accessed by interacting directly with OpenFF software, but it's also very easy to get on the
ground running for simple system. For starters, we'll show that with OpenFF it takes literal seconds to go from loading
a molecule into RDKit to visualizing a simulation trajectory.

Here we have an aspirin molecule in SDF, which we can load into RDKit and have a quick look at. We need to load a force
field; here I'll use a recent version in the Sage line, version 2.2.1. From here, it's a one-liner to prepare an OpenMM
system and a little bit of boilerplate to get the simulation running. I've wrapped that up into a separate function in 
the file `simulate.py` if you want to have a look. This function returns an NGLview widget of the trajectory, and
that's all it takes to run MD from RDKit.

(rdkit-to-MD section: 1:25)

Okay, that's a good start, but the more complex interesting systems are more valuable. OpenFF tooling fully supports
simulating protein-ligand complexes, and the process is similar to running simulations of a single molecule. The main
difference is that we need to prepare a topology, which is simply a collection of molecules, and that can take a couple
of extra steps.

For starters, we'll load a PDB file of a protein-ligand complex into a `Topology` object, also passing a SMILES pattern
representing the ligand. If we have a look, that looks good. Since we don't want to simulate this in vacuum, we need to
add some solvent. There are a few ways of doing this, and for systems with only water and canonical residues, PDBFixer
is a good choice. I'm just going to load a prepared solvated PDB file, but the code we used to make it is right here.
Now we have the same protein-ligand complex solvated in water with ions. The next step is to load a force field
appropriate for this system; we're going to use the same Sage force field for the small molecule parameters and for the
protein we'll use a SMIRNOFF port of ff14SB. One could slot in other force fields here, for ligand, protein, or both
chemistries, just by passing different file names to the class. The next step is to make an Interchange object out of
this topology and force field, which can take a few seconds so I'm just going to load a serialized representation of
this. This trick can also be useful if, for example, you want to prepare simulations on a laptop but actually run them
on clusters or compute services.

Finally, we can re-use some of that same boilerplate OpenMM code to get an MD simulation out of this state and then
again look at it with NGLview.

(protein-ligand complex section: 3:00)

Sometimes your amino acids may be non-canonical, or even simply a small molecule covalently linked to a side chain.
OpenFF has a prototype post-translational modification workflow, enabled by new science and infrastructure, which
enables simulating these systems with a modest amount of prep.

Let's say we have a flourescent dye somewhere on our protein. We can load our dye molecule like any other small
molecule and have a look. This molecule has has a maleimide group which can take part in a click reaction with the
thiol on a cysteine residue. That reaction can be written up in SMARTS and visualized with RDKit.

We're ultimately going to load this system as a PDB file through OpenFF Pablo, a new tool being developed for better
PDB interoperability throughout OpenFF infrastructure. A core feature is the ability to create custom residue
definitions, which can be defined in a few ways. In this case, it's easiest to define it from an OpenFF molecule. We
want the residue to represent the cysteine modified with the dye, so we need to get that into a single-molecule
representation. We have a function `react` which wraps RDKit to do this, the details of which are available in the
source Python file. It does just what you'd expect - take two reactant molecules and return the result. One added
wrinkle is the need to correct atom names, which we have encoded here. We can run this "reaction" and look at the
resulting molecule.

That's just about all the set up we need to do. The last step is creating our residue definition from this molecule and
a canned definition of a peptide bond. We can pass this to Pablo's `topology_from_pdb` function and have a look at the
result.

Now that we have a topology, we can do just what we did before - take it and a force field and pass it off to OpenMM,
then visualize the result.

22:20

(PTM section: 4:10)

(NAGL timings section: 2:00)
