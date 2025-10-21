# Profiling Scheduler using captured schedule cycle output
Scheduler periodically writes the most recent cycle output to local filesystem. Scheduler is design to be able to use the data (snapshot) from the output to replay the scheduling logic. Aside from troubleshooting, this can be used for profiling.

To get the cycle output from a Scheduler pod:
`kubectl cp baseten/baseten-mcm-scheduler-74b59554-pd9h2:/var/log/mcm/scheduler_output.json.gz /tmp/scheduler_output.json.gz`

Use the provided benchmark to replay from output and get the profile: `services/v1/mcs/scheduler/scheduler_computeschedule_profile_test.go`

Modify the benchmark to point to the downloaded cycle output file.

Example of command to run benchmark with cpuprofile: `go test -bench=. -run=^# -cpuprofile=/tmp/scheduler_profile.out`
This will run the ComputeSchedule logic N times with 1s period.

For visualization, one option is Google's pprof tool and Graphviz:
* Install pprof: `go install github.com/google/pprof@latest`
* Install graphviz: brew install graphviz
* Build scheduler binary for symbols: `cd /Users/williamlau/workspace/baseten/go/mcm/cmd/scheduler; go build`
* Create local web interface to see visualizations: `pprof -http=localhost:3121 scheduler /tmp/scheduler_profile.out -output /tmp/`
This tool provides the standard graph view and the flame graph view.

See [pprof for more details](https://github.com/google/pprof/blob/main/doc/README.md).