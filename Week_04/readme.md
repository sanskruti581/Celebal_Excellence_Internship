
# Azure Cloud Fundamentals and Data Pipeline Implementation using ADF

## 📌 Overview
This repository contains the complete submission for the assignment **"Azure Cloud 
Fundamentals and Data Pipeline Implementation using ADF"**, where I explored core 
Azure cloud concepts and built an end-to-end data pipeline using **Azure Storage 
Account** and **Azure Data Factory (ADF)**.

## 🎯 Objective
To understand Azure cloud concepts and build a complete data pipeline using 
Storage Account and Azure Data Factory — covering resource provisioning, secure 
connectivity, pipeline orchestration, execution, and identity-based access control.

## 🗂️ Repository Contents
| File | Description |
|------|-------------|
| `Azure_Assignment.pdf` | Final report with all screenshots, explanations, and results |

## 🛠️ Tools & Services Used
- **Azure Resource Group** — logical container for all resources
- **Azure Storage Account (Blob Storage)** — source and destination for the CSV data
- **Azure Data Factory (ADF)** — pipeline orchestration
- **Linked Services & Datasets** — connectivity between ADF and Blob Storage
- **Get Metadata Activity** — validates file existence before processing
- **Copy Data Activity** — transfers data from source to destination
- **Azure IAM (RBAC)** — Reader and Storage Blob Data Contributor roles assigned 
  to ADF's Managed Identity

## 📋 Tasks Completed
- [x] **Task 1:** Created a Resource Group
- [x] **Task 2:** Created a Storage Account, Blob Container, and uploaded a CSV file
- [x] **Task 3:** Set up ADF, Linked Service, Datasets, and Get Metadata activity
- [x] **Task 4:** Built a pipeline using the Copy Data activity
- [x] **Task 5:** Executed the pipeline via Debug and confirmed success
- [x] **Task 6:** Assigned Reader and Storage Blob Data Contributor IAM roles to ADF
- [x] **Mini Project:** End-to-end pipeline — Blob → ADF → Destination, with 
      metadata validation

## ✅ Pipeline Flow
