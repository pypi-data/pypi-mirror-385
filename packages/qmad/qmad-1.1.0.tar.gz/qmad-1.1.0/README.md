# QMAD/QMultiAdapt

Welcome to the **QMultiAdapt** repository! This repository is currently undergoing a significant transformation to enhance the usability and execution of adaptive variational techniques. Our goal is to make the code more accessible and seamlessly executable for users. As part of this ongoing morphing process, we will be appending more adaptive variational techniques and offering further optimizations to improve the overall user experience.

---

## Overview

This repository contains the companion code for the paper *Adaptive Variational Simulation for Open Quantum Systems*. The core of the adaptive variational algorithm resides in the `AVQD` directory, which houses the entire package. The root directory is configured as the primary project space, tailored specifically for execution within a cluster computing environment.

## Examples and Applications

The **QMultiAdapt** repository demonstrates the versatility and applicability of the UAVQD (Unrestricted Adaptive Variational Quantum Dynamics) vectorization method across multiple open quantum system scenarios. The examples provided include:

- **Amplitude Damping Channel**
- **FMO Complex**
- **Dicke Superradiance**

### Key Insights:
- The vectorization method excels in handling continuous updates, particularly in complex scenarios like Dicke Superradiance, where the state evolves through numerous possible pathways due to successive emissions.
- The UAVQD operator pool developed here is well-suited to manage the complexity of multi-qubit systems with polynomial runtime scaling (as opposed to exponential scaling in classical methods).
- An appendix demonstrates how the scaling can be further improved to linear with a scheme requiring only \( O(\log_2 N) \) gates, given all-to-all connectivity in qubits. Trapped ion quantum computers have shown promise for handling such ansatz constructions.

**Note**: The repository is under active development and will be incrementally updated. Contributions and feedback are welcome.

---

### Citation
For academic use, please cite our work as mentioned in the related paper *Designing variational ansatz for quantum-enabled simulation of non-unitary dynamical evolution an excursion into Dicke supperradiance.*


Feel free to reach out with any questions, suggestions, or contributions!
