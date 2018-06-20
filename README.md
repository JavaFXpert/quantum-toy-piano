# Quantum Music Composer for Rigetti quantum computers

The Quantum Music Composer application enables a user to compose music that is performed by a quantum computer or quantum simulator. The musical *composition* consists of a series of quantum circuits. Each quantum musical tone [[1]](#references) in the *performance* of a composition is a quantum state, which when measured results in a pitch determined by quantum mechanical behavior. This normally results in unique melodies and harmonies each time a given composition is performed by a quantum computer or simulator. Fig. 1 contains a musical score captured from one such performance.

![third-species-performance](docimages/third-species-performance.png)

FIG. 1. Musical score captured from the performance of a quantum musical composition

## Creating a quantum musical composition

To create a quantum musical composition, the user first supplies the desired probabilities for a given pitch to follow another given pitch *melodically*. Take a moment to examine the music score in Fig. 1 and notice that the staff labeled **Melody** contains an eight-note melody. Please also realize that the staff labeled **Harmony** actually contains seven four-note melodies.  Users enter their desired probabilities into the [doubly-stochastic matrix](https://en.wikipedia.org/wiki/Doubly_stochastic_matrix) located on the left side of the **MELODY MATRICES** tab, shown in Fig 2. 

![melody-tab-orthogonal-matrix](docimages/melody-tab-orthogonal-matrix.png)

FIG. 2. User interface for composing quantum melodic progressions

Clicking the **Optimize Rotations** button updates the [orthogonal matrix](https://en.wikipedia.org/wiki/Orthogonal_matrix) on the right to contain values, that when squared, comprise a [unistochastic matrix](https://en.wikipedia.org/wiki/Unistochastic_matrix) that approximates the user's desired probabilities. Deselecting and selecting the **Show Probabilities** checkbox toggles between showing the orthogonal matrix and the unistochastic matrix, respectively. The application optimizes the unistochastic matrix by gradually changing the angles of the six degree-of-freedom rotations in four-dimensional vector space until the difference between the doubly-stochastic matrix and the unistochastic matrix is minimized.  You can experiment with the effects of each rotation on the matrix on the right by using the sliders in the **Degree of Freedom Rotations** region of this tab. Each slider has the range ![eqn_range_0_pi2](docimages/eqn_range_0_pi2.gif) radians.

To continue creating the quantum musical composition, the user supplies the desired probabilities for a given pitch to be played *harmonically* with another given pitch. Take another moment to examine the musical score in Fig. 1 and notice that each of the notes in the staff labeled **Melody** have a note in the staff labeled **Harmony** directly above it. Users enter their desired probabilities into the [doubly-stochastic matrix](https://en.wikipedia.org/wiki/Doubly_stochastic_matrix) located on the left side of the **HARMONY MATRICES** tab, shown in Fig 3.

![harmony-tab-unistochastic-matrix](docimages/harmony-tab-unistochastic-matrix.png)

FIG. 3. User interface for composing quantum harmonic intervals

The harmonic probabilities entered will apply to all of the notes played harmonically in the performance except for the final note on each staff, as those two notes will have the same pitch class as the first note in the melody staff. These notes provide a sense of resolution and finality to the performance, and are the only two notes in the performance that aren't determined by the quantum computer.

## Performing a quantum musical composition

To have the quantum computer or simulator perform your quantum musical composition, navigate to the **Performance** tab shown in Fig 4.

![performance-tab](docimages/performance-tab.png)

FIG. 4. User interface for performing quantum musical composition



## Installation

To install.

## References

[1] Volkmar Putz and Karl Svozil, “Quantum music,” (2015), [ arXiv:1503.09045](https://arxiv.org/abs/1503.09045) [quant-ph]