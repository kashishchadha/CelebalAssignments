# Azure Cloud Fundamentals & Data Pipeline using Azure Data Factory

**Week 4 Assignment — Celebal Technologies Summer Internship (Data Engineering)**

## Overview

This repository documents an end-to-end data pipeline built on Microsoft Azure. It uses a
Storage Account as the landing zone for a CSV dataset, and Azure Data Factory (ADF) to
validate and copy that file from source to destination using a metadata-check-then-copy
pattern.

Pipeline: **`PL_CopyAndValidate`**
```
Get Metadata1  ─────▶  Copy data1
(validate source)      (copy to destination)
```

## Architecture

| Component | Purpose |
|---|---|
| Resource Group | Logical container for all resources used in this project |
| Storage Account + Blob Container | Landing zone for the raw CSV file |
| Azure Data Factory | Orchestrates validation + copy of the file |
| Linked Service | Authenticated connection between ADF and Blob Storage |
| Datasets (`DS_RawCSV`, `DS_ProcessedCSV`) | Pointers to the source and destination files |
| IAM Roles (Reader, Storage Blob Data Contributor) | Scoped, least-privilege access for ADF's managed identity on the storage account |

## Dataset

Source data: [Sample Superstore dataset (Kaggle)](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)

## What the pipeline does

1. **Get Metadata1** checks the source file in Blob Storage — confirms it exists and reads
   properties such as size and last-modified timestamp.
2. On success, **Copy data1** copies the file from the source container to a destination
   location in Blob Storage.
3. The pipeline run status, activity durations, and metadata output are all visible in the
   ADF Monitor / Output pane.

## Repository structure

```
.
├── README.md
├── report/
│   └── Week4_Assignment_Report.docx     # Full write-up with explanations & screenshots
└── screenshots/
    ├── 01_resource_group.png
    ├── 02_storage_account.png
    ├── 03_blob_container.png
    ├── 04_adf_overview.png
    ├── 05_linked_service.png
    ├── 06_dataset_source.png
    ├── 07_dataset_destination.png
    ├── 08_get_metadata_output.png
    ├── 09_pipeline_design.png
    ├── 10_pipeline_run_succeeded.png
    └── 11_pipeline_run_details.png
```

## Key learnings

- Resource Groups make IAM scoping, cost tracking, and cleanup much simpler once more
  than one resource is involved.
- Linked Services (the connection) and Datasets (a named pointer to a specific file/table)
  are deliberately separate concepts in ADF.
- `Get Metadata` is a cheap, effective way to fail a pipeline early if the source file is
  missing or malformed.
- Azure IAM has a control-plane vs. data-plane distinction: the built-in **Contributor**
  role manages the storage account resource itself but does **not** grant permission to
  read/write blob data — that requires **Storage Blob Data Contributor** separately.
- ADF Debug runs are useful for fast iteration since they surface per-activity status and
  duration without publishing or triggering a full pipeline run.

## IAM roles assigned to ADF's managed identity (on the Storage Account)

| Role | Why |
|---|---|
| Reader | View the storage account and its configuration |
| Storage Blob Data Contributor | Actual read/write access to blob data (required for Copy Data to work) |

## Author

**Kashish Chadha**
Data Engineering Intern · B.Tech (CSE), DIT University · Batch 1
