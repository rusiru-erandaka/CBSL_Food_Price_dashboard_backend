from __future__ import annotations

from app.core.config import Settings
from app.repositories.huggingface_repository import HuggingFaceRepository
from app.transformers.dataset_normalizer import DatasetNormalizer


def test_huggingface_repository_downloads_and_normalizes(monkeypatch, tmp_path) -> None:
    csv_payload = "\n".join(
        [
            "date,retail_pettah_Tomato,wholesale_dambulla_Beans,rainfall_nuwara_eliya_mm",
            "2026-01-01,100,80,12",
            "2026-01-02,110,82,16",
        ]
    )
    dataset_path = tmp_path / "price_dataset.csv"
    dataset_path.write_text(csv_payload, encoding="utf-8")

    def mock_hf_hub_download(
        repo_id: str,
        filename: str,
        repo_type: str,
        etag_timeout: float,
    ) -> str:
        assert repo_id == "Rusiru-erandaka/Srilanka-vegetable-prices"
        assert filename == "price_dataset.csv"
        assert repo_type == "dataset"
        assert etag_timeout == 30.0
        return str(dataset_path)

    monkeypatch.setattr(
        "app.repositories.huggingface_repository.hf_hub_download",
        mock_hf_hub_download,
    )

    repository = HuggingFaceRepository(
        settings=Settings(
            hf_dataset_id="Rusiru-erandaka/Srilanka-vegetable-prices",
            hf_dataset_file="price_dataset.csv",
            request_timeout_seconds=30,
        ),
        normalizer=DatasetNormalizer(),
    )

    dataset = repository.get_dataset()
    rainfall = repository.get_rainfall_dataset()

    assert len(dataset) == 4
    assert set(repository.get_foods()) == {"Beans", "Tomato"}
    assert set(repository.get_markets()) == {"Dambulla", "Pettah"}
    assert repository.get_price_types() == ["retail", "wholesale"]
    assert len(rainfall) == 2
