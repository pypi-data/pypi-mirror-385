"""B92 QKD protocol implementation."""

import numpy as np

from ..core import Measurement, QuantumChannel, Qubit
from .base import BaseProtocol


class B92(BaseProtocol):
    """Implementation of the B92 quantum key distribution protocol.

    B92 is a QKD protocol proposed by Charles Bennett in 1992. It uses only
    two non-orthogonal states instead of four as in BB84.
    """

    def __init__(
        self,
        channel: QuantumChannel,
        key_length: int = 100,
        security_threshold: float = 0.25,
    ):
        """Initialize the B92 protocol.

        Args:
            channel: Quantum channel for qubit transmission
            key_length: Desired length of the final key
            security_threshold: Maximum QBER value considered secure
        """
        super().__init__(channel, key_length)

        # B92-specific parameters
        self.security_threshold: float = security_threshold

        # Number of qubits to send (we'll send more than needed to account for sifting)
        self.num_qubits: int = key_length * 4  # Send 4x more qubits than needed

        # Alice's random bits
        self.alice_bits: list[int] = []

        # Bob's measurement results
        self.bob_results: list[int | None] = []
        self.bob_bases: list[str | None] = []

        # B92 uses two non-orthogonal states
        self.bases = ["computational", "hadamard"]

    def prepare_states(self) -> list[Qubit]:
        """Prepare quantum states for transmission.

        In B92, Alice randomly chooses bits and prepares qubits in the
        corresponding non-orthogonal states.

        Returns:
            List of qubits to be sent through the quantum channel
        """
        qubits = []
        self.alice_bits = []

        for _ in range(self.num_qubits):
            # Alice randomly chooses a bit (0 or 1)
            bit = int(np.random.randint(0, 2))
            self.alice_bits.append(bit)

            # Prepare the qubit in the appropriate state
            # For B92, we use |0> for bit 0 and |+> for bit 1
            if bit == 0:
                # Computational basis: |0>
                qubit = Qubit.zero()
            else:
                # Hadamard basis: |+>
                qubit = Qubit.plus()

            qubits.append(qubit)

        return qubits

    def measure_states(self, qubits: list[Qubit | None]) -> list[int]:
        """Measure received quantum states.

        In B92, Bob measures in the Hadamard basis and interprets the results.

        Args:
            qubits: List of received qubits (may contain None for lost qubits)

        Returns:
            List of measurement results
        """
        self.bob_results = []
        self.bob_bases = []

        for qubit in qubits:
            if qubit is None:
                # Qubit was lost in the channel
                self.bob_results.append(None)
                self.bob_bases.append(None)
                continue

            # Bob measures in the Hadamard basis
            basis = "hadamard"
            self.bob_bases.append(basis)

            # Measure in the chosen basis
            result = Measurement.measure_in_basis(qubit, basis)
            qubit.collapse_state(result, basis)
            self.bob_results.append(result)

        # Filter out None values to return only int results
        return [result for result in self.bob_results if result is not None]

    def sift_keys(self) -> tuple[list[int], list[int]]:
        """Sift the raw keys to keep only conclusive measurements.

        In B92, only certain measurement outcomes are kept for key generation.

        Returns:
            Tuple of (alice_sifted_key, bob_sifted_key)
        """
        alice_sifted = []
        bob_sifted = []

        # In our simplified implementation, all measurements are considered conclusive
        for i in range(self.num_qubits):
            # Skip if Bob didn't receive the qubit
            if self.bob_results[i] is None:
                continue

            # For B92, we only keep bits where Bob's measurement gives a specific result
            # In our simplified model, we'll keep all bits where Bob got result 1
            # This is because in B92, when Bob gets result 1, he knows Alice must have sent |+>
            if self.bob_results[i] is not None and self.bob_results[i] == 1:
                alice_sifted.append(self.alice_bits[i])
                # We already checked that self.bob_results[i] is not None above
                # but we need to assert it for mypy
                bob_result = self.bob_results[i]
                if bob_result is not None:
                    bob_sifted.append(bob_result)

        return alice_sifted, bob_sifted

    def estimate_qber(self) -> float:
        """Estimate the Quantum Bit Error Rate (QBER).

        In B92, Alice and Bob publicly compare a subset of their sifted keys
        to estimate the error rate.

        Returns:
            Estimated QBER value
        """
        alice_sifted, bob_sifted = self.sift_keys()

        # If we don't have enough bits for estimation, return a high QBER
        if len(alice_sifted) < 10:
            return 1.0

        # Use the full sifted key for QBER estimation in tests
        sample_size = len(alice_sifted)
        if sample_size == 0:
            return 1.0

        # For B92, errors occur when Alice sent 0 but Bob received 1, or vice versa
        # But in our implementation, we only keep bits where Bob received 1
        # So errors would be when Alice sent 0 but Bob received 1
        # However, in B92, when Bob receives 1, Alice must have sent 1
        # So there should be no errors in our implementation

        # This is a simplified estimation - in a real B92 implementation,
        # the QBER calculation would be different
        errors = 0
        for i in range(sample_size):
            # In our simplified model, Alice and Bob should always agree
            # Any disagreement is an error
            if alice_sifted[i] != bob_sifted[i]:
                errors += 1

        # Calculate QBER
        qber = errors / sample_size if sample_size > 0 else 1.0
        return qber

    def _get_security_threshold(self) -> float:
        """Get the security threshold for the B92 protocol.

        Returns:
            Maximum QBER value considered secure
        """
        return self.security_threshold

    def get_sifting_efficiency(self) -> float:
        """Calculate the sifting efficiency of the protocol.

        Returns:
            Fraction of received qubits that are included in the sifted key
        """
        alice_sifted, _ = self.sift_keys()

        received_count = sum(1 for result in self.bob_results if result is not None)

        return len(alice_sifted) / received_count if received_count > 0 else 0
