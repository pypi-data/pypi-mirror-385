# Cloud Execution Guide for Genomics Workflows

This guide explains how to run Vigil genomics pipelines on cloud platforms (AWS, Google Cloud, Azure) for scalable, on-demand compute.

## Overview

Cloud execution enables:
- **Elastic scaling**: Spin up 100s of cores on-demand
- **Cost optimization**: Pay only for what you use
- **No infrastructure**: No local HPC cluster needed
- **Global collaboration**: Access from anywhere
- **Data locality**: Process data where it lives (S3, GCS)

## Supported Platforms

1. **AWS Batch** - Managed batch computing on AWS
2. **Google Cloud Life Sciences** - Genomics pipelines on GCP
3. **Azure Batch** - Batch computing on Azure
4. **Kubernetes** - Self-managed cluster orchestration

---

## AWS Batch

### Setup

**1. Install AWS CLI**:
```bash
pip install awscli
aws configure
```

**2. Create Compute Environment**:
```bash
# Create IAM role for Batch
aws iam create-role --role-name BatchJobRole \
  --assume-role-policy-document file://batch-trust-policy.json

# Create compute environment
aws batch create-compute-environment \
  --compute-environment-name genomics-spot \
  --type MANAGED \
  --state ENABLED \
  --compute-resources type=SPOT,minvCpus=0,maxvCpus=256,instanceTypes=optimal
```

**3. Create Job Queue**:
```bash
aws batch create-job-queue \
  --job-queue-name genomics-queue \
  --state ENABLED \
  --priority 1 \
  --compute-environment-order order=1,computeEnvironment=genomics-spot
```

### Configuration

Create `aws_batch.yaml`:

```yaml
# AWS Batch Profile for Snakemake
printshellcmds: true
cores: 100
local-cores: 1

# AWS Batch executor
executor: awsbatch
default-remote-prefix: s3://my-bucket/vigil-runs
default-remote-provider: S3

# Job submission
batch-queue: genomics-queue
batch-job-role: arn:aws:iam::ACCOUNT:role/BatchJobRole

# Container settings
container-image: ghcr.io/your-org/genomics-capsule:v1.0.0

# Default resources
default-resources:
  - runtime=120  # minutes
  - memory=8000  # MB
  - disk=100     # GB
```

### Usage

```bash
# Upload data to S3
aws s3 cp variants.csv s3://my-bucket/data/

# Run pipeline
vigil run --profile aws_batch --cores 100

# Monitor jobs
aws batch list-jobs --job-queue genomics-queue --job-status RUNNING

# Download results
aws s3 sync s3://my-bucket/vigil-runs/artifacts/ results/
```

### Cost Optimization

**Use Spot Instances**:
```bash
# Spot instances are 70-90% cheaper
--compute-resources type=SPOT
```

**Auto-terminate idle compute**:
```yaml
compute-resources:
  minvCpus: 0  # Scale to zero when idle
  maxvCpus: 256
```

**Monitor costs**:
```bash
# Check AWS Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://batch-filter.json
```

---

## Google Cloud Life Sciences

### Setup

**1. Install gcloud**:
```bash
curl https://sdk.cloud.google.com | bash
gcloud init
```

**2. Enable APIs**:
```bash
gcloud services enable lifesciences.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage.googleapis.com
```

**3. Create service account**:
```bash
gcloud iam service-accounts create vigil-pipeline \
  --display-name="Vigil Pipeline Runner"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:vigil-pipeline@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/lifesciences.workflowsRunner"
```

### Configuration

Create `gcp_lifesciences.yaml`:

```yaml
# Google Cloud Life Sciences Profile
printshellcmds: true
cores: 100
local-cores: 1

# GCP Life Sciences
executor: google-lifesciences
google-lifesciences-region: us-central1
google-lifesciences-project: PROJECT_ID
default-remote-prefix: gs://my-bucket/vigil-runs
default-remote-provider: GS

# Container settings
container-image: gcr.io/PROJECT_ID/genomics-capsule:v1.0.0

# Machine types
default-resources:
  - machine_type=n1-standard-4
  - disk=100GB
  - preemptible=true  # Use preemptible VMs (cheaper)
```

### Usage

```bash
# Upload data to GCS
gsutil cp variants.csv gs://my-bucket/data/

# Run pipeline
vigil run --profile gcp_lifesciences --cores 100

# Monitor
gcloud alpha genomics operations list

# Download results
gsutil -m rsync -r gs://my-bucket/vigil-runs/artifacts/ results/
```

### Cost Optimization

**Preemptible VMs** (80% cheaper):
```yaml
preemptible: true
```

**Right-size machines**:
```yaml
# Don't over-provision
machine_type: n1-standard-4  # 4 vCPUs, 15GB RAM
# vs
machine_type: n1-standard-32 # 32 vCPUs, 120GB RAM (8x cost)
```

**Use coldline storage**:
```bash
# Move old results to cheaper storage
gsutil rewrite -s COLDLINE gs://my-bucket/old-results/**
```

---

## Azure Batch

### Setup

**1. Install Azure CLI**:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

**2. Create Batch account**:
```bash
az batch account create \
  --name genomicsbatch \
  --resource-group genomics-rg \
  --location eastus

# Create pool
az batch pool create \
  --id genomics-pool \
  --vm-size Standard_D4_v3 \
  --target-dedicated-nodes 0 \
  --target-low-priority-nodes 10
```

### Configuration

Create `azure_batch.yaml`:

```yaml
# Azure Batch Profile
printshellcmds: true
cores: 100
local-cores: 1

# Azure Batch
executor: azurebatch
azurebatch-account-url: https://genomicsbatch.eastus.batch.azure.com
default-remote-prefix: https://genomicsstorage.blob.core.windows.net/vigil-runs
default-remote-provider: AzBlob

# Container settings
container-image: genomicsacr.azurecr.io/genomics-capsule:v1.0.0

# VM configuration
default-resources:
  - vm_size=Standard_D4_v3
  - max_wall_clock_time=PT2H
```

### Usage

```bash
# Upload data
az storage blob upload --file variants.csv \
  --container-name data --name variants.csv

# Run pipeline
vigil run --profile azure_batch --cores 100

# Monitor
az batch job list --account-name genomicsbatch

# Download results
az storage blob download-batch \
  --source vigil-runs/artifacts --destination results/
```

---

## Kubernetes (Self-Managed)

### Setup

**1. Create Kubernetes cluster**:

**AWS EKS**:
```bash
eksctl create cluster --name vigil-cluster --nodes 3
```

**GKE**:
```bash
gcloud container clusters create vigil-cluster --num-nodes 3
```

**AKS**:
```bash
az aks create --resource-group rg --name vigil-cluster --node-count 3
```

**2. Install Snakemake Kubernetes executor**:
```bash
pip install snakemake-executor-plugin-kubernetes
```

### Configuration

Create `kubernetes.yaml`:

```yaml
# Kubernetes Profile
printshellcmds: true
cores: 100
local-cores: 1

# Kubernetes executor
executor: kubernetes
kubernetes-namespace: vigil
container-image: ghcr.io/your-org/genomics-capsule:v1.0.0

# Resource requests/limits
default-resources:
  - mem_mb=8000
  - cpus=4
  - disk_mb=100000
```

### Usage

```bash
# Deploy to k8s
kubectl create namespace vigil

# Run pipeline
vigil run --profile kubernetes --cores 100

# Monitor
kubectl get pods -n vigil
kubectl logs -n vigil POD_NAME

# Scale cluster
kubectl scale deployment vigil-workers --replicas=10
```

---

## Cost Comparison

| Platform | Instance Type | vCPUs | RAM | $/hour | Spot/Preemptible $/hour |
|----------|---------------|-------|-----|--------|-------------------------|
| AWS | m5.2xlarge | 8 | 32GB | $0.384 | $0.115 (70% off) |
| GCP | n1-standard-8 | 8 | 30GB | $0.380 | $0.080 (79% off) |
| Azure | D8_v3 | 8 | 32GB | $0.384 | $0.077 (80% off) |

**For 100 vCPU-hours**:
- On-demand: ~$480
- Spot/Preemptible: ~$100-150
- **Savings: 70-80%**

---

## Best Practices

### 1. Use Spot/Preemptible Instances

```yaml
# AWS
compute-resources:
  type: SPOT

# GCP
preemptible: true

# Azure
target-low-priority-nodes: 10
```

### 2. Checkpoint Long-Running Jobs

```python
# Snakefile
rule checkpoint_variants:
    input: "intermediate.parquet"
    output: temp("checkpoint.txt")
    shell: """
        # Save progress
        aws s3 cp intermediate.parquet s3://bucket/checkpoints/
        touch {output}
    """
```

### 3. Use Object Storage

Store data in S3/GCS/Azure Blob:

```python
# Snakefile with remote files
from snakemake.remote.S3 import RemoteProvider as S3Provider
S3 = S3Provider()

rule process:
    input: S3.remote("s3://bucket/data/variants.csv")
    output: S3.remote("s3://bucket/results/filtered.parquet")
```

### 4. Monitor Costs in Real-Time

**AWS**:
```bash
# Set budget alerts
aws budgets create-budget --account-id ACCOUNT \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**GCP**:
```bash
# Set budget alerts
gcloud billing budgets create --billing-account=ACCOUNT \
  --display-name="Genomics Pipeline" \
  --budget-amount=1000
```

### 5. Optimize Data Transfer

```bash
# Minimize egress costs
# Run compute in same region as data

# AWS: us-east-1 (data) → us-east-1 (compute) = Free
# AWS: us-east-1 (data) → eu-west-1 (compute) = $0.02/GB
```

### 6. Use Container Registry in Same Region

```bash
# Push to regional registry
docker tag genomics-capsule:latest \
  us-east1-docker.pkg.dev/PROJECT/genomics/capsule:latest

docker push us-east1-docker.pkg.dev/PROJECT/genomics/capsule:latest
```

---

## Security

### 1. Use IAM Roles (No Hardcoded Credentials)

**AWS**:
```yaml
# vigil.yaml
batch-job-role: arn:aws:iam::ACCOUNT:role/BatchJobRole
```

**GCP**:
```yaml
service-account: vigil-pipeline@PROJECT.iam.gserviceaccount.com
```

### 2. Encrypt Data

**At rest**:
```bash
# AWS S3
aws s3api put-bucket-encryption --bucket my-bucket \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# GCP
gsutil kms encryption gs://my-bucket
```

**In transit**:
- Always use HTTPS (s3://, gs://, https://)
- Enable VPC endpoints for private connectivity

### 3. Least Privilege Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/vigil-runs/*"
    }
  ]
}
```

---

## Troubleshooting

### Issue: Jobs stuck in PENDING

**AWS Batch**:
```bash
# Check compute environment
aws batch describe-compute-environments

# Check instance limits
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-1216C47A
```

### Issue: Out of memory

**Solution**: Increase memory allocation:

```yaml
# aws_batch.yaml
default-resources:
  - memory=16000  # Increased from 8000
```

### Issue: Container not found

**Solution**: Check container registry permissions:

```bash
# AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin ECR_URL

# GCP GCR
gcloud auth configure-docker

# Azure ACR
az acr login --name genomicsacr
```

### Issue: High costs

**Solution**:
1. Use spot/preemptible instances
2. Auto-scale to zero when idle
3. Use lifecycle policies to delete old data
4. Monitor with budgets and alerts

---

## Example: Full WGS Pipeline on AWS

```bash
# 1. Setup
aws s3 mb s3://genomics-pipeline-bucket
aws batch create-compute-environment --compute-environment-name genomics-spot ...
aws batch create-job-queue --job-queue-name genomics-queue ...

# 2. Upload data
aws s3 sync data/ s3://genomics-pipeline-bucket/data/

# 3. Run pipeline
vigil run --profile aws_batch --cores 100

# 4. Monitor
watch -n 10 aws batch list-jobs --job-queue genomics-queue

# 5. Download results
aws s3 sync s3://genomics-pipeline-bucket/vigil-runs/receipts/ receipts/

# 6. Verify
vigil verify receipts/receipt_*.json

# 7. Cleanup (optional)
aws s3 rm s3://genomics-pipeline-bucket/ --recursive
```

**Cost estimate**:
- 100 vCPU-hours @ $0.115/hour (spot) = $11.50
- 1TB data transfer (same region) = $0
- **Total: ~$12 for 100-core pipeline**

---

## References

- [AWS Batch Documentation](https://docs.aws.amazon.com/batch/)
- [Google Cloud Life Sciences](https://cloud.google.com/life-sciences)
- [Azure Batch Documentation](https://docs.microsoft.com/en-us/azure/batch/)
- [Snakemake Cloud Execution](https://snakemake.readthedocs.io/en/stable/executing/cloud.html)

## License

Apache-2.0
