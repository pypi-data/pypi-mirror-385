r"""
.. include:: ../README.md

# Examples

Most of these examples include external packages. If you want to set up an appropriate environment to run these 
examples, run:

```
pip install tce-lib[examples]
```

## ⚛️ Using Atomic Simulation Environment (ASE)

Below is an example of converting an `ase.Atoms` object into a feature vector $\mathbf{t}$. The mapping is not exactly
one-to-one, since an `ase.Atoms` object sits on a dynamic lattice rather than a static one, but we can regardless
provide `tce-lib` sufficient information to compute $\mathbf{t}$. The code snippet below uses the version `ase==3.26.0`.

```py
.. include:: ../examples/using-ase.py
```

## 💎 Exotic Lattice Structures

Below is an example of injecting a custom lattice structure into `tce-lib`. To do this, we must extend the
`LatticeStructure` class using `tce.constants.register_new_lattice_structure`. We use a cubic diamond structure here as
an example, but this extends to any atomic basis in any tetragonal unit cell. Three body labels will be automatically
computed if not specified, but this can be decently expensive, so it's recommended to compute them once and then
specify them later.

```py
.. include:: ../examples/exotic-lattice.py
```

We are also more than happy to include new lattice types as native options in `tce-lib`! Please either open an issue
[here](https://github.com/MUEXLY/tce-lib/issues), or a pull request [here](https://github.com/MUEXLY/tce-lib/pulls) if
you are familiar with GitHub.

If your unit cell is available via `ase`'s functionalities (below is using `ase.build.bulk`, but you can also load
in a `.cif` file or something similar), you don't have to waste your time finding atomic bases and cutoffs every time.
For example, for a [fluorite structure](https://en.wikipedia.org/wiki/Fluorite_structure) with U and Th cations:

```py
.. include:: ../examples/exotic-lattice2.py
```

You'll notice that a lot of the features are $0$. This is not uncommon for exotic lattice types, especially when not
all lattice sites are equivalent. This is not a problem - we just likely need to feature reduce later using something
like [PCA](https://en.wikipedia.org/wiki/Principal_component_analysis), which is relatively easy with an
`sklearn.pipeline.Pipeline` object (docs are
[here](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)). This will be elaborated
upon in an example more focused on training ([here](https://muexly.github.io/tce-lib/tce.html#custom-training-advanced)).

## 🔩 FeCr + EAM (basic)

Below is a very basic example of computing a best-fit interaction vector from LAMMPS data. We use LAMMPS and an EAM
potential from Eich et al. (paper [here](https://doi.org/10.1016/j.commatsci.2015.03.047), NIST interatomic potential 
repository entry [here](https://www.ctcms.nist.gov/potentials/entry/2015--Eich-S-M-Beinke-D-Schmitz-G--Fe-Cr/)), 
use `tce-lib` to build a best-fit interaction vector from a sequence of random samples, and cross-validate the results 
using `scikit-learn`.

```py
.. include:: ../examples/iron-chrome-lammps.py
```

Above, we avoided a lot of convenience functions, like constructing a feature vector calculator from a feature vector
computer factory in the prior examples. You can very easily still use these factories, but the above example shows that
you should not feel obligated to use them for more advanced use cases.

This generates the plot below:

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cross-val.png"
    width=100%
    alt="Residual errors during cross-validation"
    title="Residual errors"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cross-val.png)

The errors are not great here (a good absolute error is on the order of 1-10 meV/atom as a rule of thumb). The fit
would be much better if we included partially ordered samples as well. We emphasize that this is a very basic example,
and that a real production fit should be done against a more diverse training set than just purely random samples.

This example serves as a good template for using programs other than LAMMPS to compute energies. For example, one could
define a constructor that creates a `Calculator` instance that wraps VASP:

```py
from ase.calculators.vasp import Vasp

calculator_constructor = lambda: Vasp(
    prec="Accurate",
    encut=500,
    istart=0,
    ismear=1,
    sigma=0.1,
    nsw=400,
    nelmin=5,
    nelm=100,
    ibrion=1,
    potim=0.5,
    isif=3,
    isym=2,
    ediff=1e-5,
    ediffg=-5e-4,
    lreal=False,
    lwave=False,
    lcharg=False
)
```

See ASE's documentation [here](https://ase-lib.org/ase/calculators/vasp.html) for how to properly set this up!

## 🏋️‍♀️ Training + Monte Carlo

Below is a slightly more involved example of creating a model and deploying it for a Monte Carlo run.

This showcases two utility modules, namely `tce.training` and `tce.monte_carlo`. These mostly contain wrappers, so
feel free to avoid them! If you are using this for a novel research idea, it is likely that these wrappers are too
basic (which is a good thing for you!).

The first script is training a CuNi model using an EAM potential from Fischer et al.
(paper [here](https://doi.org/10.1016/j.actamat.2019.06.027)). In this script, we generate a bunch of random CuNi
solid solutions, attach an `ase.calculators.eam.EAM` calculator to each configuration, compute their energies, and
then train using the `tce.training.train` method, which returns a `tce.training.ClusterExpansion` instance. The
container is then saved to be used for later.

**IMPORTANT**: These are unrelaxed energies! A real production environment should optimize the structure - see the
prior example on how to do this within a LAMMPS calculator.

```py
.. include:: ../examples/0-copper-nickel-training.py
```

The next script uses the saved container to run a canonical Monte Carlo simulation on a $10\times 10\times 10$
supercell, storing the configuration (saved in an `ase.Atoms` object) every 100 frames. We also set up a `logging`
configuration here, which will tell you how far-along the simulation is. Note that `trajectory` looks complicated, but
is just a list of `ase.Atoms` objects, so you have a lot of freedom to do what you wish with this trajectory later.

```py
.. include:: ../examples/1-copper-nickel-mc.py
```

You can also change the logging level here! For example, changing to `logging.DEBUG` will display more things:

```py
logging.getLogger("numba").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
```

`sparse` uses `numba` so you will also get a lot of `numba` logging messages if you don't manually set `numba`'s
logger to a higher level. You can also do much more advanced things - see this
[video by mCoding](https://www.youtube.com/watch?v=9L77QExPmI0) on the `logging` library.

The configurations generated by the MC run are then visualizable with a number of softwares, including
[OVITO](https://www.ovito.org/). An example of such a rendering is below:

<div style="padding:50% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/1117980384?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerpolicy="strict-origin-when-cross-origin" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="animation"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

Just from the animation, it doesn't look like much is happening at all. The animation is not the whole story, though -
you can also use the trajectory to do some analysis. We can use OVITO's Python library [here](https://pypi.org/p/ovito)
and any of its plugins to do some analysis, as if our files are from any other atomistic simulation software. Below
we'll compute the Cowley short range order parameter using the
`cowley-sro-parameters` plugin [here](https://pypi.org/p/cowley-sro-parameters) (shameless plug... I'm the author 🙂).

```py
.. include:: ../examples/2-copper-nickel-sro.py
```

This generates the plot below. A negative value indicates attraction between two atom types. So, the solution is
clearly not fully random! We probably need a lot more than 10,000 steps too - this curve should bottom out once we
reach steady state. Note we can also just grab the potential energy from the `ase.Atoms` instances - the Monte Carlo
run stores this information using `ase.calculators.singlepoint.SinglePointCalculator` instances.

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cu-ni-sro.png"
    width=100%
    alt="CuNi SRO parameter from CE"
    title="SRO parameter"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cu-ni-sro.png)

We can also use the model to sample a different ensemble. For the prototypical canonical ensemble, the acceptance rule
for a swap with energy difference $\Delta E$ is $\exp(-\beta\Delta E) > u$, where $u$ is a random number drawn from
$[0, 1]$. For the grand canonical ensemble, the acceptance rule is instead:

$$ \exp\left(-\beta\left(\Delta E - \sum_\alpha \mu_\alpha \Delta N_\alpha\right)\right) = \exp\left(-\beta\left(\Delta E - \boldsymbol{\mu}\cdot\Delta \mathbf{N}\right)\right) > u $$

where $\mu_\alpha$ is the chemical potential of type $\alpha$ and $\Delta N_\alpha$ is the change in the number of
$\alpha$ atoms in the swap. You can inject this into `tce.monte_carlo.monte_carlo` by defining an `energy_modifier`,
which adds a term to $\Delta E$:

```py
.. include:: ../examples/1-copper-nickel-mc2.py
```

We also can specify our own Monte Carlo step, which is done above. This plot generates a curve which is useful for
computing phase diagrams:

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cu-ni-sgcmc.png"
    width=100%
    alt="CuNi SGCMC curve"
    title="CuNi curve"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/cu-ni-sgcmc.png)

Note that the curve is continuous, which denotes no phase transitions at the temperature. This matches experimental
phase diagrams - CuNi forms a solid solution along the whole composition range below the melting point.

<div style="text-align: center;">
  <a href="https://sv.rkriz.net/classes/MSE2094_NoteBook/96ClassProj/OLD/examples/cu_ni.jpg">
    <img
      src="https://sv.rkriz.net/classes/MSE2094_NoteBook/96ClassProj/OLD/examples/cu_ni.jpg"
      width="50%"
      alt="CuNi phase diagram"
      title="CuNi"
    />
  </a>
</div>

Image credit: Ron Kriz, MSE 2094 @ Virginia Tech ([url](https://sv.rkriz.net/classes/MSE2094_NoteBook/96ClassProj/OLD/examples/cu-ni.html))

## 💻 Custom Training (Advanced)

Below is an example of using a custom training method to train the CE model. There are many reasons one might want to do
this. The example below is a very typical one - using [lasso](https://en.wikipedia.org/wiki/Lasso_(statistics)). This
regularization technique minimizes the loss:

$$ L(\beta\; |\;\lambda) = \|X\beta - y\|_2^2 + \lambda \|\beta\|_1 $$

which better-supports sparse best-fit parameters $\hat{\beta}$, which may be useful if you only want to exclude
non-important clusters. We'll use `scikit-learn`'s interface for providing a model. You can really use any linear
model here (without an intercept...), see `scikit-learn`'s docs
[here](https://scikit-learn.org/stable/modules/linear_model.html) for more examples of these.

```py
.. include:: ../examples/3-sklearn-fitting.py
```

This script (it will be quite slow...) will calculate the number of nonzero cluster interaction coefficients as a
function of the regularization parameter. For larger regularization parameters, the number of nonzero coefficients
should decrease.

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/regularization.png"
    width=100%
    alt="Lasso regularization"
    title="Lasso"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/regularization.png)


## 🧲 Learning a tensorial property

In general, one might also want to learn tensorial properties. This can be done by vectorizing the property in some
way, like [Voigt notation](https://en.wikipedia.org/wiki/Voigt_notation):

$$ \sigma = (\sigma_{xx}, \sigma_{yy}, \sigma_{zz}, \sigma_{yz}, \sigma_{xz}, \sigma_{xy}) $$

Below is an example of changing the target property to stress rather than energy. It also showcases an important point
about `tce-lib`: our feature vectors are **extensive**, not intensive like other CE libraries. This matters when
training on intensive properties, like stress. Here, we can inject custom behavior, i.e. train on intensive features.
Of course, it is also fine to use this same pattern to train a CE model on other scalar properties.

```py
.. include:: ../examples/4-tensorial-property.py
```

## 🔔 Callback functionality

The `tce.monte_carlo.monte_carlo` routine also has a `callback` argument that lets you inject a notification system
into the Monte Carlo run. This argument needs to be a function with signature:

```py
def callback(step: int, num_steps: int) -> None:
    ...
```

If it is not provided, it defaults to calling the `logging` library:

```py
import logging

LOGGER = logging.getLogger(__name__)

def callback(step_: int, num_steps_: int):
    LOGGER.info(f"MC step {step_:.0f}/{num_steps_:.0f}")
```

But, you can do very cool things with this. It's a bit of a cute example that might not be practical, but you can
send notifications to third party systems like [Discord](https://en.wikipedia.org/wiki/Discord) using webhooks.

```py
.. include:: ../examples/5-callbacking.py
```

which will send a notification in whatever Discord channel once the MC run is finished. See
[Discord's documentation on webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for
a tutorial on how to set up your own webhook URL. You can get really creative here too, like Slack's similar
functionality [here](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/), or the
[Gmail API](https://developers.google.com/workspace/gmail/api/guides). None of these are particularly useful for what I
have done above (sending a single email once the run is finished), but really shine for long runs where you want to
be periodicially notified.

## 🕵️ Loading and Visualizing Datasets

Below is an example of using one of our pre-set training datasets using `tce.datasets`. When you install `tce-lib`, you
automatically install some toy datasets that are mostly of pedagogical benefit, i.e. you can look at one of these datasets 
and see examples of what you can train on. Since `ovito` has an `ase` interface, you can also use `ovito` to visualize the 
dataset, which might be of interest.

```py
.. include:: ../examples/load-dataset-and-visualize.py
```

which generates the figure below:

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/visualized.png"
    width=100%
    alt="TaW dataset visualization from genetic algorithm"
    title="TaW"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/visualized.png)

Each dataset has a metadata object as well, which is stored in `json` format:

```json
.. include:: ../tce/datasets/tungsten_tantalum_genetic/metadata.json
```

which tells you some info, and (should) additionally give you contact information to inquire about the dataset. Note
that `tce.datasets.Dataset.configurations` is of type `list[ase.Atoms]`, so you can directly plug this into a training
routine. Please contact me directly (email above) if you have datasets you would like to be added 😊

## 🎁 ASE Calculator Wrapper

We have also provided an `ase.calculator.Calculator` child class that wraps `tce-lib`. This is mostly a convenience
feature for those that already have an `ase.calculator.Calculator`-driven workflow.

```py
.. include:: ../examples/calculator-interface.py
```

One note here is that this is a great way to wrap multiple cluster expansions for different properties into one object.
There's no guarantee that any property will be well-predicted, though. For example, the off-diagonal stress
$\sigma_{xy}$ above: the predictive strength is very weak because the property is largely $0$ across the whole
training set. In a real workflow, though, this will likely not be a problem, since the stresses are very
concentrated along the diagonal elements. Also, again, the default behavior of `tce-lib` is to assume that the target
property is **extensive**, so make sure that each training routine is computing the correct feature vectors!

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/calculator-interface.png"
    width=100%
    alt="Multi-property cluster expansion in an ASE calculator"
    title="Calculator interface"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/calculator-interface.png)

# Sharp Edges

`tce-lib` has a couple of sharp edges (or gotcha's) that one needs to look out for.

## Extensivity of features

In traditional cluster expansion packages, correlation functions are usually intensive (i.e. independent of size). This
is not the case for `tce-lib`. We can showcase this by creating some feature vectors for an FCC lattice of varying
sizes:

```py
.. include:: ../examples/size-dependence.py
```

[<img
    src="https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/size-dependence.png"
    width=100%
    alt="Size dependence of features"
    title="Size dependence"
/>](https://raw.githubusercontent.com/MUEXLY/tce-lib/refs/heads/main/examples/size-dependence.png)

So, be careful if you are training an intensive property! By default, you will be training intensive properties on
extensive features, which does not make sense. You can fix this by training on an equivalent extensive feature, and
then make the property intensive later, or more preferably defining features with a strategy that makes them intensive,
as done in [the stress example above](https://muexly.github.io/tce-lib/tce.html#learning-a-tensorial-property).

## Loading your own data

You've probably noticed that the input to the typical training routines is a list of configurations, rather than a 
list of configurations and a list of energies like one might expect. This is because we can store energy inside of 
the `ase.Atoms` object that represents a configuration.

This makes it easier to generate data - but what if you already have data sitting around? Most atomistic software
(all that I am familiar with) stores the energy separate from the configuration. You can load these in by attaching a
`ase.calculators.singlepoint.SinglePointCalculator` to a configuration. For example, if I have a directory with data 
that looks like:

```
data/
├── run1/
│   ├── configuration.xyz
│   └── energy.txt
├── run2/
│   ├── configuration.xyz
│   └── energy.txt
├── run3/
│   ├── configuration.xyz
│   └── energy.txt
├── run4/
│   ├── configuration.xyz
│   └── energy.txt
├── run5/
│   ├── configuration.xyz
│   └── energy.txt
```

you can load in this dataset using `ase` entirely:

```py
from pathlib import Path

from ase import io, Atoms
import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator

configurations: list[Atoms] = []
for path in Path("data").iterdir():
    configuration: Atoms = io.read(path / "configuration.xyz", format="extxyz")
    energy: float = np.loadtxt(path / "energy.txt")
    configuration.calc = SinglePointCalculator(configuration, energy=energy)
    configurations.append(configuration)

# do whatever with tce here
...
```

where I have assumed that all configurations are of [Extended XYZ format](https://ase-lib.org/ase/io/formatoptions.html#extxyz). 
It is very easy to, however, load in a different format. For example, replace `"extxyz"` with `"vasp"` if you have `POSCAR` files 
generated by VASP, or with `"lammps-data"` if you have LAMMPS data files. There is quite a large set of supported formats, 
which you can find [here](https://ase-lib.org/ase/io/io.html#ase.io.read).

## Fitting with an intercept → MC

If you choose to fit using `scikit-learn`, models will include an intercept by default. This is not a problem if you
just want to compute energies, but you likely want to feed this into `tce.monte_carlo.monte_carlo` later, which expects a linear 
transformation, rather than an affine transformation.

If your model is affine, i.e. includes an intercept:

$$ f(\mathbf{t}) = \alpha + \boldsymbol{\beta}^\intercal\mathbf{t} $$

Then, the resulting energy difference will be computed as:

$$ f(\Delta\mathbf{t}) = \alpha + \boldsymbol{\beta}^\intercal\Delta\mathbf{t} $$

which is invalid unless $\alpha = 0$. `tce.monte_carlo.monte_carlo` will warn the user if they input a `model` argument that has 
a nonzero `.intercept_` attribute like `sklearn` models do.

For simple models, e.g. if you train using `sklearn.linear_model.LinearRegression`, you  can simply ignore the intercept term 
during training:

```py
from tce.training import train
from sklearn.linear_model import LinearRegression

ce = train(
    configurations=...
    basis=...
    model=LinearRegression(fit_intercept=False)    
)
```

However, it is often the case that results are extremely sensitive on the individual interaction energies. In this case, ones first 
instinct is to use PCA to reduce the feature space dimensionality, and to scale the features to have zero mean and unit variance:

```py
from tce.training import train
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ce = train(
    configurations=...
    basis=...
    model=Pipeline([
        ("scale", StandardScaler()),
        ("reduce", PCA(n_components=...)),
        ("fit", LinearRegression(fit_intercept=False))
    ]) 
)
```

However, this routine is almost certain to produce garbage results, and for a very subtle reason. Both `StandardScaler` and `PCA` 
recenter the data to have zero mean, which introduces an intercept. This can be changed within `StandardScaler`, but not `PCA`. 
We need to make sure that the data is not recentered, and that we replace `PCA` with a decomposition method that also does 
not recenter the data, such as `TruncatedSVD`:

```py
from tce.training import train
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ce = train(
    configurations=...
    basis=...
    model=Pipeline([
        ("scale", StandardScaler(with_mean=False)),
        ("reduce", TruncatedSVD(n_components=...)),
        ("fit", LinearRegression(fit_intercept=False))
    ]) 
)
```

Of course, you can replace `sklearn.linear_model.LinearRegression` with something more robust, e.g. 
`sklearn.linear_model.ElasticNetCV`, which uses [elastic net regularization](https://en.wikipedia.org/wiki/Elastic_net_regularization) 
and [leave-one-out cross validation](https://www.statology.org/leave-one-out-cross-validation/).

"""

__version__ = "0.8.3"
__authors__ = ["Jacob Jeffries"]

__url__ = "https://github.com/MUEXLY/tce-lib"

import warnings

from . import calculator as calculator
from . import constants as constants
from . import datasets as datasets
from . import monte_carlo as monte_carlo
from . import structures as structures
from . import topology as topology
from . import training as training


if __version__.startswith("0."):
    warnings.simplefilter("once", UserWarning)

    warnings.warn(
        f"{__name__} is in alpha. APIs are unstable and may change without notice. "
        f"Please report any problems at {__url__}/issues",
        UserWarning,
        stacklevel=2,
    )
