"""
Sequence Manager for EzDB RDBMS
Implements Oracle-style sequences for auto-generating unique numbers
"""

from typing import Dict, Any, Optional
from datetime import datetime
import threading


class Sequence:
    """Represents a database sequence"""

    def __init__(
        self,
        name: str,
        start_with: int = 1,
        increment_by: int = 1,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        cycle: bool = False,
        cache: int = 1
    ):
        """
        Initialize a sequence.

        Args:
            name: Sequence name
            start_with: Starting value (default: 1)
            increment_by: Increment step (default: 1)
            min_value: Minimum value (default: 1 for positive, -max for negative)
            max_value: Maximum value (default: 9999999999)
            cycle: Whether to cycle when reaching max/min (default: False)
            cache: Number of values to pre-allocate (default: 1)
        """
        self.name = name
        self.increment_by = increment_by
        self.cycle = cycle
        self.cache = cache

        # Set defaults based on increment direction
        if increment_by > 0:
            self.min_value = min_value if min_value is not None else 1
            self.max_value = max_value if max_value is not None else 9999999999
        else:
            self.min_value = min_value if min_value is not None else -9999999999
            self.max_value = max_value if max_value is not None else -1

        # Validate min/max (allow any values for negative increment)
        if increment_by > 0 and self.min_value >= self.max_value:
            raise ValueError(f"For positive INCREMENT BY, MINVALUE must be less than MAXVALUE")
        elif increment_by < 0 and self.min_value >= self.max_value:
            raise ValueError(f"For negative INCREMENT BY, MINVALUE must be less than MAXVALUE")

        # Initialize current value
        self._current_value = start_with
        self._last_fetched_value = None

        # Thread safety
        self._lock = threading.Lock()

        # Metadata
        self.created_at = datetime.now()
        self.last_used_at = None

    def nextval(self) -> int:
        """
        Get the next value from the sequence.

        Returns:
            Next sequence value

        Raises:
            ValueError: If sequence has reached max/min and NOCYCLE is set
        """
        with self._lock:
            # Check if we need to cycle
            if self.increment_by > 0:
                if self._current_value > self.max_value:
                    if self.cycle:
                        self._current_value = self.min_value
                    else:
                        raise ValueError(
                            f"Sequence {self.name} has exceeded MAXVALUE "
                            f"({self.max_value}) and NOCYCLE is specified"
                        )
            else:  # negative increment
                if self._current_value < self.min_value:
                    if self.cycle:
                        self._current_value = self.max_value
                    else:
                        raise ValueError(
                            f"Sequence {self.name} has exceeded MINVALUE "
                            f"({self.min_value}) and NOCYCLE is specified"
                        )

            # Get current value
            value = self._current_value

            # Store as last fetched for CURRVAL
            self._last_fetched_value = value
            self.last_used_at = datetime.now()

            # Increment for next call
            self._current_value += self.increment_by

            return value

    def currval(self) -> int:
        """
        Get the current value of the sequence (last value returned by NEXTVAL).

        Returns:
            Current sequence value

        Raises:
            ValueError: If NEXTVAL has not been called yet in this session
        """
        with self._lock:
            if self._last_fetched_value is None:
                raise ValueError(
                    f"CURRVAL is not yet defined in this session for sequence {self.name}. "
                    f"You must call NEXTVAL first."
                )
            return self._last_fetched_value

    def alter(
        self,
        increment_by: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        cycle: Optional[bool] = None,
        cache: Optional[int] = None
    ):
        """
        Alter sequence parameters.

        Args:
            increment_by: New increment value
            min_value: New minimum value
            max_value: New maximum value
            cycle: New cycle setting
            cache: New cache size
        """
        with self._lock:
            if increment_by is not None:
                self.increment_by = increment_by
            if min_value is not None:
                self.min_value = min_value
            if max_value is not None:
                self.max_value = max_value
            if cycle is not None:
                self.cycle = cycle
            if cache is not None:
                self.cache = cache

            # Validate min/max
            if self.min_value >= self.max_value:
                raise ValueError(f"MINVALUE must be less than MAXVALUE")

    def reset(self, value: Optional[int] = None):
        """
        Reset the sequence to a specific value or back to start.

        Args:
            value: Value to reset to (default: original start_with)
        """
        with self._lock:
            if value is not None:
                self._current_value = value
            self._last_fetched_value = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert sequence to dictionary representation"""
        return {
            'name': self.name,
            'current_value': self._current_value,
            'increment_by': self.increment_by,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'cycle': self.cycle,
            'cache': self.cache,
            'last_fetched_value': self._last_fetched_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }


class SequenceManager:
    """Manages all sequences in the database"""

    def __init__(self):
        """Initialize sequence manager"""
        self.sequences: Dict[str, Sequence] = {}
        self._lock = threading.Lock()

    def create_sequence(
        self,
        name: str,
        start_with: int = 1,
        increment_by: int = 1,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        cycle: bool = False,
        cache: int = 1,
        if_not_exists: bool = False
    ) -> Sequence:
        """
        Create a new sequence.

        Args:
            name: Sequence name
            start_with: Starting value
            increment_by: Increment step
            min_value: Minimum value
            max_value: Maximum value
            cycle: Whether to cycle
            cache: Cache size
            if_not_exists: Don't error if sequence already exists

        Returns:
            Created Sequence object

        Raises:
            ValueError: If sequence already exists (and if_not_exists is False)
        """
        name_upper = name.upper()

        with self._lock:
            if name_upper in self.sequences:
                if if_not_exists:
                    return self.sequences[name_upper]
                else:
                    raise ValueError(f"Sequence '{name}' already exists")

            sequence = Sequence(
                name=name_upper,
                start_with=start_with,
                increment_by=increment_by,
                min_value=min_value,
                max_value=max_value,
                cycle=cycle,
                cache=cache
            )

            self.sequences[name_upper] = sequence
            return sequence

    def drop_sequence(self, name: str, if_exists: bool = False) -> bool:
        """
        Drop a sequence.

        Args:
            name: Sequence name
            if_exists: Don't error if sequence doesn't exist

        Returns:
            True if dropped, False if didn't exist (when if_exists=True)

        Raises:
            ValueError: If sequence doesn't exist (and if_exists is False)
        """
        name_upper = name.upper()

        with self._lock:
            if name_upper not in self.sequences:
                if if_exists:
                    return False
                else:
                    raise ValueError(f"Sequence '{name}' does not exist")

            del self.sequences[name_upper]
            return True

    def alter_sequence(
        self,
        name: str,
        increment_by: Optional[int] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        cycle: Optional[bool] = None,
        cache: Optional[int] = None
    ):
        """
        Alter an existing sequence.

        Args:
            name: Sequence name
            increment_by: New increment value
            min_value: New minimum value
            max_value: New maximum value
            cycle: New cycle setting
            cache: New cache size

        Raises:
            ValueError: If sequence doesn't exist
        """
        name_upper = name.upper()

        sequence = self.get_sequence(name)
        if not sequence:
            raise ValueError(f"Sequence '{name}' does not exist")

        sequence.alter(
            increment_by=increment_by,
            min_value=min_value,
            max_value=max_value,
            cycle=cycle,
            cache=cache
        )

    def get_sequence(self, name: str) -> Optional[Sequence]:
        """
        Get a sequence by name.

        Args:
            name: Sequence name

        Returns:
            Sequence object or None if not found
        """
        name_upper = name.upper()
        return self.sequences.get(name_upper)

    def nextval(self, name: str) -> int:
        """
        Get next value from a sequence.

        Args:
            name: Sequence name

        Returns:
            Next sequence value

        Raises:
            ValueError: If sequence doesn't exist or has reached limit
        """
        sequence = self.get_sequence(name)
        if not sequence:
            raise ValueError(f"Sequence '{name}' does not exist")

        return sequence.nextval()

    def currval(self, name: str) -> int:
        """
        Get current value from a sequence.

        Args:
            name: Sequence name

        Returns:
            Current sequence value

        Raises:
            ValueError: If sequence doesn't exist or NEXTVAL not yet called
        """
        sequence = self.get_sequence(name)
        if not sequence:
            raise ValueError(f"Sequence '{name}' does not exist")

        return sequence.currval()

    def list_sequences(self) -> list[str]:
        """
        Get list of all sequence names.

        Returns:
            List of sequence names
        """
        return list(self.sequences.keys())

    def get_all_sequences_info(self) -> list[Dict[str, Any]]:
        """
        Get information about all sequences.

        Returns:
            List of sequence info dictionaries
        """
        return [seq.to_dict() for seq in self.sequences.values()]

    def clear(self):
        """Remove all sequences"""
        with self._lock:
            self.sequences.clear()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize all sequences to dictionary.

        Returns:
            Dictionary representation of all sequences
        """
        return {
            name: seq.to_dict()
            for name, seq in self.sequences.items()
        }

    def from_dict(self, data: Dict[str, Any]):
        """
        Load sequences from dictionary.

        Args:
            data: Dictionary containing sequence data
        """
        with self._lock:
            self.sequences.clear()
            for name, seq_data in data.items():
                sequence = Sequence(
                    name=name,
                    start_with=seq_data['current_value'],  # Start from current
                    increment_by=seq_data['increment_by'],
                    min_value=seq_data['min_value'],
                    max_value=seq_data['max_value'],
                    cycle=seq_data['cycle'],
                    cache=seq_data.get('cache', 1)
                )
                # Restore last fetched value
                sequence._last_fetched_value = seq_data.get('last_fetched_value')
                self.sequences[name] = sequence
