#!/usr/bin/env python3
"""Basic example of using Onymancer to generate fantasy names."""


from onymancer import generate, generate_batch, set_token


def main() -> None:
    """Generate and display fantasy names."""
    print("Generating fantasy names...")

    # Generate a simple name
    name1 = generate("s(dim)", seed=42)
    print(f"Simple name: {name1}")

    # Generate a fantasy name with capitalization
    name2 = generate("!s!v!c", seed=123)
    print(f"Capitalized name: {name2}")

    # Use groups for variety
    name3 = generate("<s|v>c", seed=456)
    print(f"Grouped name: {name3}")

    # Generate a title
    title = generate("!t !T", seed=789)
    print(f"Title: {title}")

    # Generate multiple names with batch generation
    names = generate_batch(
        "!s!v",
        count=3,
        seed=42,
    )
    print(f"Batch of names: {names}")

    # Generate names with length constraints
    constrained_names = generate_batch(
        "!s!v!c",
        count=3,
        seed=123,
        min_length=4,
        max_length=8,
    )
    print(f"Constrained names (4-8 chars): {constrained_names}")

    # Generate names with character constraints. Note: constraints may not
    # always be satisfiable depending on pattern and tokens.
    char_constrained = generate_batch(
        "A!s!v",
        count=3,
        seed=456,
        starts_with="A",
        contains="a",
    )
    print(f"Character constrained names: {char_constrained}")

    # Set custom token
    set_token("x", ["dragon", "phoenix", "griffin"])
    name4 = generate("!x", seed=101)
    print(f"Custom token name: {name4}")

    print("\nName generation complete!")


if __name__ == "__main__":
    main()
