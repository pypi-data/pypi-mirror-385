# HPC Integration Guide for Genomics Workflows

This guide explains how to run Vigil genomics pipelines on High-Performance Computing (HPC) clusters using SLURM, PBS/Torque, or SGE job schedulers.

## Quick Start

### SLURM

```bash
vigil run --profile slurm --cores 100
```

### PBS/Torque

```bash
vigil run --profile pbs --cores 100
```

### SGE (Sun Grid Engine)

```bash
vigil run --profile sge --cores 100
```

## Profile Overview

Each profile configures:
- Job submission commands (`sbatch`, `qsub`)
- Resource allocation (CPUs, memory, walltime)
- Queue/partition selection
- Log file locations
- Retry behavior

## Configuration

### SLURM

**Profile files:**
- `slurm.yaml` - Main configuration
- `slurm_cluster.yaml` - Per-rule resources
- `slurm_status.py` - Job status checker

**Customization:**

Edit `slurm_cluster.yaml` to adjust resources for specific rules:

```yaml
filter:
  partition: genomics      # Queue name
  mem: 16GB                # Memory per node
  time: 02:00:00           # Walltime (HH:MM:SS)
  cpus: 4                  # CPUs per task
```

**Available partitions** (check with `sinfo`):
- `genomics` - Standard genomics workloads
- `bigmem` - High-memory nodes (>256GB)
- `gpu` - GPU-accelerated tools
- `short` - Quick jobs (<4 hours)
- `long` - Extended jobs (>24 hours)

### PBS/Torque

**Profile file:**
- `pbs.yaml` - Main configuration

**Customization:**

Edit `pbs.yaml` default resources:

```yaml
default-resources:
  - queue=genomics         # Queue name
  - mem=8gb                # Memory (lowercase 'gb')
  - walltime=01:00:00      # Walltime (HH:MM:SS)
  - tmpdir=$TMPDIR         # Scratch directory
```

**Available queues** (check with `qstat -Q`):
- `genomics` - Standard queue
- `priority` - High-priority jobs
- `batch` - Long-running jobs

### SGE

**Profile file:**
- `sge.yaml` - Main configuration

**Customization:**

Edit `sge.yaml` default resources:

```yaml
default-resources:
  - queue=all.q            # Queue name
  - mem=8G                 # Memory per core
  - runtime=01:00:00       # Walltime (HH:MM:SS)
  - tmpdir=$TMPDIR         # Scratch directory
```

**Available queues** (check with `qconf -sql`):
- `all.q` - Default queue
- `genomics.q` - Genomics-specific queue
- `highmem.q` - High-memory nodes

## Resource Estimation

### Memory

**Rule of thumb for genomics:**

| Task | Input Size | Memory Needed |
|------|------------|---------------|
| Variant filtering | 10M variants | 8-16 GB |
| Annotation | 1M variants | 16-32 GB |
| Alignment (BWA) | 30x WGS | 32-64 GB |
| Variant calling (GATK) | 30x WGS | 64-128 GB |
| Structural variants (Manta) | 30x WGS | 32-64 GB |

**Calculate from file size:**
```
Memory (GB) = File Size (GB) × 2-3
```

### CPUs

**Parallelizable steps:**
- Variant calling: 4-8 CPUs per sample
- Alignment: 8-16 CPUs per sample
- Quality control: 2-4 CPUs

**Serial steps:**
- Annotation: 1-2 CPUs (limited by database I/O)
- Metrics calculation: 1-2 CPUs

### Walltime

**Typical runtimes (30x WGS, single sample):**

| Task | Runtime |
|------|---------|
| Alignment (BWA-MEM) | 12-24 hours |
| Variant calling (GATK) | 8-16 hours |
| Variant filtering | 30-60 minutes |
| Annotation | 2-4 hours |
| QC metrics | 10-30 minutes |

**Add 50% buffer:**
```
Walltime = Estimated Runtime × 1.5
```

## Advanced Configuration

### Array Jobs

For processing multiple samples in parallel:

```yaml
# slurm.yaml
cluster: |
  sbatch \
    --array=1-{params.n_samples} \
    --partition={cluster.partition} \
    ...
```

```python
# Snakefile
SAMPLES = ['sample1', 'sample2', 'sample3']

rule process_samples:
    input:
        expand("results/{sample}/variants.vcf", sample=SAMPLES)
    params:
        n_samples=len(SAMPLES)
```

### Job Dependencies

Snakemake automatically handles dependencies, but you can be explicit:

```yaml
# slurm.yaml
cluster: |
  sbatch \
    --dependency=afterok:{dependencies} \
    ...
```

### Multi-Node Parallelization

For large-scale analyses:

```yaml
# slurm.yaml
cluster: |
  sbatch \
    --nodes={cluster.nodes} \
    --ntasks-per-node={cluster.ntasks} \
    --cpus-per-task={threads} \
    ...
```

```yaml
# slurm_cluster.yaml
align_all_samples:
  nodes: 10              # Request 10 nodes
  ntasks: 100            # 100 tasks total
  cpus: 4                # 4 CPUs per task
  mem: 16GB              # 16GB per task
```

### GPU Acceleration

For GPU-enabled tools (DeepVariant, Parabricks):

```yaml
# slurm.yaml
cluster: |
  sbatch \
    --gres=gpu:{cluster.gpus} \
    --partition=gpu \
    ...
```

```yaml
# slurm_cluster.yaml
variant_calling:
  partition: gpu
  gpus: 2                # Request 2 GPUs
  mem: 64GB
  time: 04:00:00
```

## Monitoring Jobs

### SLURM

```bash
# List running jobs
squeue -u $USER

# Check job details
scontrol show job JOB_ID

# Check job efficiency
seff JOB_ID

# Cancel job
scancel JOB_ID

# View queue status
sinfo
```

### PBS/Torque

```bash
# List running jobs
qstat -u $USER

# Check job details
qstat -f JOB_ID

# Cancel job
qdel JOB_ID

# View queue status
qstat -Q
```

### SGE

```bash
# List running jobs
qstat -u $USER

# Check job details
qstat -j JOB_ID

# Cancel job
qdel JOB_ID

# View queue status
qstat -g c
```

## Log Files

Logs are written to:
- SLURM: `logs/slurm/{rule}.{wildcards}.{jobid}.{out|err}`
- PBS: `logs/pbs/{rule}.{wildcards}.{out|err}`
- SGE: `logs/sge/{rule}.{wildcards}.{out|err}`

**View logs:**
```bash
# Most recent error
tail -n 50 logs/slurm/filter.*.err

# Search for errors
grep -r "error\|Error\|ERROR" logs/

# Monitor in real-time
tail -f logs/slurm/filter.*.out
```

## Troubleshooting

### Issue: Jobs stay in pending state

**Possible causes:**
- Insufficient resources available
- Wrong partition/queue name
- Account limits exceeded

**Solution:**
```bash
# Check why job is pending (SLURM)
squeue -u $USER --start

# Check partition limits (SLURM)
sacctmgr show qos format=name,maxjobs,maxsubmit,maxwall

# Check available resources
sinfo -o "%P %a %C %m %t"
```

### Issue: Jobs fail with "Out of memory"

**Solution:** Increase memory in `slurm_cluster.yaml`:

```yaml
filter:
  mem: 32GB  # Increased from 16GB
```

### Issue: Jobs fail with "Time limit exceeded"

**Solution:** Increase walltime:

```yaml
filter:
  time: 04:00:00  # Increased from 02:00:00
```

### Issue: Shared filesystem lag

**Symptom:** Jobs report "File not found" even though file exists

**Solution:** Increase latency wait in profile:

```yaml
latency-wait: 120  # Increased from 60 seconds
```

## Best Practices

### 1. Test Locally First

```bash
# Test with 1 sample on login node
vigil run --cores 2 --until filter

# Then scale to cluster
vigil run --profile slurm --cores 100
```

### 2. Use Appropriate Resources

**Don't over-request:**
- Wastes cluster resources
- Longer queue times
- Annoys sysadmins

**Don't under-request:**
- Jobs fail mid-run
- Wasted time and compute

**Monitor and adjust:**
```bash
# Check actual usage (SLURM)
sacct -j JOB_ID --format=JobID,MaxRSS,MaxVMSize,CPUTime,Elapsed
```

### 3. Use Scratch Storage

Many clusters have fast scratch storage:

```bash
# Copy data to scratch
cp input.vcf $TMPDIR/
cd $TMPDIR

# Run analysis
samtools view ...

# Copy results back
cp output.bam $SLURM_SUBMIT_DIR/
```

Configure in profile:

```yaml
default-resources:
  - tmpdir=$TMPDIR
```

### 4. Checkpoint Long Runs

For multi-day analyses, use checkpoints:

```python
# Snakefile
checkpoint split_chromosomes:
    input: "genome.fa"
    output: directory("chromosomes/")
    shell: "split_genome.sh {input} {output}"
```

### 5. Monitor Costs

Some clusters charge for compute:

```bash
# Check usage (SLURM)
sreport cluster AccountUtilizationByUser Start=2025-01-01 End=2025-12-31

# Set budget limits
sacctmgr modify account YOUR_ACCOUNT set GrpTRES=cpu=1000,mem=100000
```

## Performance Optimization

### 1. Reduce I/O Bottlenecks

```python
# Use Parquet instead of CSV
df.to_parquet("output.parquet")  # 5-10x faster

# Compress intermediate files
shell: "gzip -c {input} > {output}"

# Use local scratch
shell: """
    cp {input} $TMPDIR/
    process $TMPDIR/input
    cp $TMPDIR/output {output}
"""
```

### 2. Parallelize Across Samples

```python
# Process samples in parallel
rule all:
    input:
        expand("results/{sample}/done", sample=SAMPLES)

# Each sample gets its own job
rule process_sample:
    input: "data/{sample}.bam"
    output: "results/{sample}/done"
    threads: 4
    shell: "process.sh {input} {output}"
```

### 3. Use Efficient Tools

| Slow | Fast | Speedup |
|------|------|---------|
| BWA-MEM | BWA-MEM2 | 2x |
| samtools (single thread) | samtools (multi-thread) | 4-8x |
| GATK3 | GATK4 | 2-3x |
| Python pandas | Polars/DuckDB | 5-10x |

### 4. Profile Your Pipeline

```bash
# Use Snakemake benchmarking
rule filter:
    benchmark: "benchmarks/{rule}.{wildcards}.txt"
    shell: "..."

# View results
cat benchmarks/filter.*.txt
# s h:m:s max_rss max_vms max_uss max_pss io_in io_out
```

## Example: Full WGS Pipeline on SLURM

```yaml
# slurm_cluster.yaml
align:
  partition: genomics
  mem: 64GB
  time: 24:00:00
  cpus: 16

mark_duplicates:
  partition: genomics
  mem: 32GB
  time: 04:00:00
  cpus: 4

variant_calling:
  partition: bigmem
  mem: 128GB
  time: 16:00:00
  cpus: 8

filter_variants:
  partition: genomics
  mem: 16GB
  time: 02:00:00
  cpus: 4

annotate_variants:
  partition: genomics
  mem: 32GB
  time: 04:00:00
  cpus: 8
```

```bash
# Submit to cluster
vigil run --profile slurm --cores 100

# Monitor progress
squeue -u $USER
watch -n 60 squeue -u $USER

# Check when complete
vigil verify app/code/receipts/receipt_*.json
```

## References

- [Snakemake Cluster Execution](https://snakemake.readthedocs.io/en/stable/executing/cluster.html)
- [SLURM Documentation](https://slurm.schedmd.com/)
- [PBS/Torque Guide](https://docs.adaptivecomputing.com/torque/)
- [SGE User Guide](http://gridscheduler.sourceforge.net/htmlman/)

## License

Apache-2.0
