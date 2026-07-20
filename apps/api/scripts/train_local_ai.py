#!/usr/bin/env python3
"""Train the local website AI model (no external API required)."""

from app.ai_model.trainer import train_and_save


def main() -> None:
    meta = train_and_save()
    print("Local AI model trained successfully.")
    print(f"  Samples: {meta['training_samples']}")
    print(f"  Types:   {meta['website_types']}")
    print(f"  Catalog: {meta['catalog']}")


if __name__ == "__main__":
    main()
