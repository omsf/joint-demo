This morning we've heard from each individual OMSF project about what they've been up to and where they're going next.
Throughout this afternoon, we'll be hearing from some industry partners about what they've built using OMSF products.
In between these spaces, I'm going to spend the next few minutes showing off how some OMSF products work with each
other in addition to diving slightly deeper into a few capabilities along the way. Everything will be something that
you can run right now, so as excited as we are about things like cofolding with OpenFold3, running simulations with Rosemary, or 3-D ADMET predictions, I'll be focusing on software you can install right now and things you do with with it right now.

0:40

If you want to follow along, the materials are available on GitHub at the following link:

Let's say we're a team of computational chemists supporting a team of medicinal chemists designing ligands for
biological targets. In this case we're looking at MCL-1, which is a well-known target for concology, and trying to
inhibit its expression.

_go into notebook, show protein structure with NGLview_

Imagine we've been given a set of ligands via a CSV file of SMILES.

_go into notebook, show ligand CSV file and visualization_

Visual inspection will show you this this is a congeneric series based around a bi-heterocyclic core, with substittution of the heterocycle and elaborations at both ends.

We want to asses ligands by how strongly they bind to MCL1, but also care about if they'd be filtered out by the body
before they can get to a tumor cell - metabolism, toxicity, anything within ADMET. Likewise, we'd wnat to filter out
any compounds that may have some ADMET liabilities before continuing to lead optimization. A pass through our dataset
at this stage isn't free, but it's relatively quick and cheap, almost certainly more efficient than trying to "fix" a
series at a later stage, after lead optimization.

Here, we'll use OpenADMET's CLI to evaluate this ligand set against a series of CYP anti-targets.

_go into notebook, run `openadmet predict` cell_

**REMINDER** The models used here are simple demonstration models and have signficant shortcomings, a more sophisticated approache is reccomended in practice.

For the purposes of our excercise lets hone in on CYP3A4 inhibition since CYP3A4 is responsible for large proportion of hepatic metabolism relative to other CYPs. For starters, let's use use a cutoff of a predicted IC50 of 2.5 micromolar, which corresponds to a p value of 5.6. This is not realistic for a production run, but it's acceptable for our uses today.

We can filter this just with a little bit of Pandas, and quickly get a subset of the original ligand set which passes
this ADMET filtering.

Now we have a target, a set of ligands we want to look more closely at, and a desire to do some free calculations.
OpenFE's tooling makes this straightforward, and our next steps will set up some RBFE calculations. There are a few
ways to use OpenFE, a CLI which provides easy access to the most common functionality and a Python API which enables
a wider set of features and options. Here we'll be using the CLI, but there's lots of cool stuff in the API too.

Here we'll be using the API in three parts - okay, two and hand-waving one - to go from a protein in a PDB file and a
set of ligands in an SDF file to delta G values. Basically, we prepare, run, and analyze simulations with the following
three commands.

_run plan-rbfe-network call_

This sets up a series of alchemical transformations between ligands. By default, a minimal spanning network and the
Kartograph atom mapper are used and each transformation is run in triplicate. Also by default, Sage 2.1.1 is used for
small molecule parameters.

Each of these JSON files describes a particular transformation. It's human-readable so in principle you can inspect its
contents, but practically it's a large set of detailed instructions for `openfe` to run a each
transformation.

If we had the right combination of GPUs and days to wait, we could run all of these simulations until they converge.
We would do this by calling `openfe quickrun` a number of times on each JSON file, which itself store each result in a
JSON file. We don't have an army of GPUs or time to run all of this compute, so I'm using some pre-computed results.

_run gather call_

With default options, `openfe gather` prints a pretty table of the dG of each ligand along with uncertainy values.
