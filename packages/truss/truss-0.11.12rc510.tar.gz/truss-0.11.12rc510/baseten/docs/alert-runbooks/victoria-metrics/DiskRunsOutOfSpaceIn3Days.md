# DiskRunsOutOfSpaceIn3Days

## Meaning

The persistent storage volume on \<namespace>.\<pod> is running out of space in 3 days.

<details>
<summary>Full context</summary>

This can happen if:
- The daily metrics data volume has increased signaficantly. Old retention estimate is out of date.

</details>

## Impact

When the volumes across all VMStorage pods are all filled up, no more metrics can be stored.
- Customer metrics will not be updated, alerts will not fire
- Internal metrics will not be updated, alerts will not fire
- No metrics can be used to generate the bills.

## Diagnosis

Check the "VictoriaMetrics - vmcluster" dashboard in "General" folder on Grafana. Under the section "vmstorage (All)"
- `Ingestion rate (All)` should show a (almost) flat line unless we have added many scrape endpoints (pods, services). 
- `Storage Full ETA (All)` should show a flat line, unless the ingestion rate has increased noticeably.
- Run query `vm_data_size_bytes` for 90 days period, using `VictoriaMetrics` data source. The oldest metric should be no older than the `rention-period` + 1 days.

## Mitigation

- Re-evaluate the storage daily consumption, update `terraform/environment/<env>/monitoring.tf` file, set `vmstorage-pvcsize` value accordingly.
