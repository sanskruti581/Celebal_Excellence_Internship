# Azure Cloud Fundamentals and Data Pipeline Implementation using ADF

## 📌 Overview
This repository contains the complete submission for the assignment **"Azure Cloud 
Fundamentals and Data Pipeline Implementation using ADF"**, where core Azure cloud 
concepts were explored and an end-to-end data pipeline was built using an 
**Azure Storage Account** and **Azure Data Factory (ADF)**.

## 🎯 Objective
To understand Azure cloud concepts and build a complete data pipeline using a 
Storage Account and Azure Data Factory — covering resource provisioning, secure 
connectivity, pipeline orchestration, execution, and identity-based access control.

## 🗂️ Repository Contents
| File | Description |
|------|-------------|
| `Azure_Assignment.pdf` | Final report with all screenshots, explanations, and results |

## 🛠️ Tools & Services Used
- **Azure Resource Group** — logical container for all project resources
- **Azure Storage Account (Blob Storage)** — source and destination for the CSV data
- **Azure Data Factory (ADF)** — pipeline orchestration and data movement
- **Linked Services & Datasets** — connectivity between ADF and Blob Storage
- **Get Metadata Activity** — validates file existence before processing
- **Copy Data Activity** — transfers data from source to destination
- **Azure IAM (RBAC)** — Reader and Storage Blob Data Contributor roles assigned 
  to ADF's Managed Identity for secure, key-free access

## 📋 Tasks Completed

### Task 1: Explore Azure Portal & Create a Resource Group
- Created a Resource Group (`rg-dataengineering`) to organize all project resources.

### Task 2: Storage Setup
- Created a Storage Account.
- Created a Blob Container (`input`).
- Uploaded the source CSV file (`Sample - Superstore.csv`).

### Task 3: ADF Basics
- Created an Azure Data Factory instance.
- Explored the ADF Studio interface (Author, Monitor, Manage).
- Created a Linked Service connecting ADF to Blob Storage.
- Created Source and Destination datasets.
- Used the Get Metadata activity to validate the source file.

### Task 4: Pipeline Development
- Built a pipeline using the Copy Data activity.
- Configured source and destination datasets.
- Connected Get Metadata → Copy Data activities.

### Task 5: Pipeline Execution
- Ran the pipeline using Debug mode.
- Verified both activities completed with status **Succeeded**.

### Task 6: IAM Roles
- Assigned **Reader** and **Storage Blob Data Contributor** roles.
- Granted access to ADF's Managed Identity on the Storage Account (instead of 
  a personal account), following the principle of least privilege.

### Mini Project: End-to-End Pipeline
- **Source:** CSV file in Blob Storage (`input` container).
- **Components used:** Linked Service + Dataset + Pipeline.
- **Process:** Copy Data activity + Get Metadata validation.
- **Destination:** New `output` container with the copied file 
  (`CopiedSuperstore.csv`).
- **Result:** Pipeline executed successfully, data copied to destination, 
  and metadata validated end-to-end.

## ✅ Pipeline Flow
```
Blob Storage (input/Sample-Superstore.csv)
        ↓
  Get Metadata Activity (validates file existence)
        ↓
  Copy Data Activity
        ↓
Blob Storage (output/CopiedSuperstore.csv)
```


